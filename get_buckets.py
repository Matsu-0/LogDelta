from time import perf_counter

from utils.bytearray import newOutArray
from algorithm.qgram import cosQgramDistance

def get_buckets_file(input_path, output_path, threshold = 0.035):
    t = perf_counter()

    with open(input_path, "rb" ) as input:

        buckets = []
        bucket_cnt = 0
        bucket_index_list = []

        index  = 0

        while True:

            line = input.readline().decode()

            if not line:
                break
            
            index += 1

            distance = 1
            bucket_index = -1

            for i in range(bucket_cnt):
                tmpd = cosQgramDistance(buckets[i][-1], line)
                if (tmpd < distance):
                    distance = tmpd
                    bucket_index = i

            if (bucket_index == -1 or distance >= threshold):
                buckets.append([line])
                bucket_cnt += 1
                bucket_index_list.append(bucket_cnt)
                # print(bucket_cnt)
            else:
                buckets[bucket_index].append(line)
                bucket_index_list.append(bucket_index)
        
        stream = newOutArray()
        for index in bucket_index_list:
            stream.encode(index, 8)

        for i in range(bucket_cnt):
            for s in buckets[i]:
                for byte in s.encode():
                    stream.encode(byte, 8)

        stream.write(output_path, 'wb', 'none')
    t = perf_counter() - t

    return t

def main():
    input_path = "./datasets/test1_data_size/Apache_2000.txt"
    output_path = "./result/buckets_dataset/Apache_2000_buckets"  
    get_buckets_file(input_path, output_path, 0.01)

if __name__ == "__main__":
    main()