import pandas as pd
from time import perf_counter
from math import ceil
from cmath import inf
from struct import pack

from utils.encoding import rle_compress, bit_packing_compress
from utils.bytearray import newOutArray
from algorithm.approximate_algorithm import get_Qgram_match_oplist
from algorithm.qgram import cosQgramDistance

def get_encoding_byte_array(bucket_index_list, df, output_path, compressor):

    encoding_block = 1024

    stream = newOutArray()
    stream_length = 0

    df0 = df[df['method'] == 0]
    df1 = df[df['method'] == 1]

    # encode bucket index
    if len(bucket_index_list) == 0:
        stream.encode(0, 16)
    else:
        for i in range(max(int((len(bucket_index_list) - 1) / encoding_block), 1)):
            b_list = bucket_index_list[i * encoding_block: (i + 1) * encoding_block]
            bit_packing_string = bit_packing_compress(b_list)
            leng = ceil(len(bit_packing_string) / 8)
            while (len(bit_packing_string) < leng * 8):
                bit_packing_string += '0'
            stream.encode(leng, 16)
            for i in range(leng):
                bf = int(bit_packing_string[i * 8: (i + 1) * 8], 2)
                stream.encode(bf, 8)

    # print("bucket index:", newOutArray.length(stream) - stream_length)
    # stream_length = newOutArray.length(stream)

    # encode method by rle
    method = df['method'].tolist()

    method_string = ''
    for i in method:
        method_string += str(i)
    rle_string = rle_compress(method_string)
    leng = ceil(len(rle_string) / 8)
    while (len(rle_string) < leng * 8):
        rle_string += '0'
    stream.encode(leng, 16)
    for i in range(leng):
        bf = int(rle_string[i * 8: (i + 1) * 8], 2)
        stream.encode(bf, 8)

    # print("method:",newOutArray.length(stream) - stream_length)
    # stream_length = newOutArray.length(stream)

    # encode another_line by rle
    another_line = df['another_line'].tolist()

    another_line_string = ''
    for i in another_line:
        another_line_string += str(i)
    rle_string = rle_compress(another_line_string)
    leng = ceil(len(rle_string) / 8)
    while (len(rle_string) < leng * 8):
        rle_string += '0'
    stream.encode(leng, 16)
    for i in range(leng):
        bf = int(rle_string[i * 8: (i + 1) * 8], 2)
        stream.encode(bf, 8)

    # print("line:",newOutArray.length(stream) - stream_length)
    # stream_length = newOutArray.length(stream)

    df0 = df[df['method'] == 0]
    df1 = df[df['method'] == 1]

    # encode operation size by bit packing
    operation_size = df0['operation_size'].tolist()

    if len(operation_size) == 0:
        stream.encode(0, 16)
    else:
        bit_packing_string = bit_packing_compress(operation_size)
        leng = ceil(len(bit_packing_string) / 8)
        while (len(bit_packing_string) < leng * 8):
            bit_packing_string += '0'
        stream.encode(leng, 16)
        for i in range(leng):
            bf = int(bit_packing_string[i * 8: (i + 1) * 8], 2)
            stream.encode(bf, 8)

    # print("operation:",newOutArray.length(stream) - stream_length)
    # stream_length = newOutArray.length(stream)

    # encode length by bit packing
    d_length = df0['d_length'].tolist()
    i_length = df0['i_length'].tolist()
    length_list = d_length + i_length

    # print(length_list)
    if len(length_list) == 0:
        stream.encode(0, 16)
    else:
        leng_list = []
        for length in length_list:
            for l in length:
                leng_list.append(l)

        # print(len(leng_list))
        
        for i in range(max(int((len(leng_list) - 1) / encoding_block), 1)):
            l_list = leng_list[i * encoding_block: (i + 1) * encoding_block]
            bit_packing_string = bit_packing_compress(l_list)
            leng = ceil(len(bit_packing_string) / 8)
            while (len(bit_packing_string) < leng * 8):
                bit_packing_string += '0'
            stream.encode(leng, 16)
            for i in range(leng):
                bf = int(bit_packing_string[i * 8: (i + 1) * 8], 2)
                stream.encode(bf, 8)

    # print("length:",newOutArray.length(stream) - stream_length)
    # stream_length = newOutArray.length(stream)

    # encode position by bit packing
    position_list = df0['position_list'].tolist()
    # print(len(position_list))
    if len(position_list) == 0:
        stream.encode(0, 16)
    else:
        p_begin_list = []
        p_delta_list = []
        for p_list in position_list:
            oldp = -1
            for p in p_list:
                if oldp == -1:
                    p_begin_list.append(p)
                else:
                    p_delta_list.append(p - oldp)
                oldp = p

        block_num = ceil(len(p_begin_list) / encoding_block)
        stream.encode(block_num, 16)
        for i in range(block_num):
            p_list = p_begin_list[i * encoding_block : (i+1) * encoding_block]
            bit_packing_string = bit_packing_compress(p_list)
            while (len(bit_packing_string) < leng * 8):
                bit_packing_string += '0'
            stream.encode(leng, 16)
            for i in range(leng):
                bf = int(bit_packing_string[i * 8: (i + 1) * 8], 2)
                stream.encode(bf, 8)

        for i in range(max(int((len(p_delta_list) - 1) / encoding_block), 1)):
            p_list = p_delta_list[i * encoding_block : (i+1) * encoding_block]
            bit_packing_string = bit_packing_compress(p_list)
            leng = ceil(len(bit_packing_string) / 8)
            while (len(bit_packing_string) < leng * 8):
                bit_packing_string += '0'
            stream.encode(leng, 16)
            for i in range(leng):
                bf = int(bit_packing_string[i * 8: (i + 1) * 8], 2)
                stream.encode(bf, 8)

    # print("position:",newOutArray.length(stream) - stream_length)
    # stream_length = newOutArray.length(stream)

    # encoding strings
    sub_string = ''

    sub_string_list = df0['sub_string'].tolist()
    for st_list in sub_string_list:
        for s in st_list:
            sub_string += s

    sub_string_1 = df1['sub_string'].tolist()
    for s in sub_string_1:
        sub_string += s

    for byte in sub_string.encode():
        stream.encode(byte, 8)

    # print("string:",newOutArray.length(stream) - stream_length)
    # stream_length = newOutArray.length(stream)
    
    stream.write(output_path, mode="ab", compressor=compressor)

    return 


def main_encoding_compress(input_path, output_path, window_size= 8, log_length = 256, 
                           threshold = 0.035, block_size = 32768, compressor="lzma"):
    t = perf_counter()

    new_line_flag = 0
    
    input = open(input_path, "rb" )

    # write encoding head
    stream = newOutArray()
    stream.encode(window_size, 16)
    stream.encode(log_length, 16)
    stream.encode(block_size, 16)
    stream.write(output_path)

    loop_end = False
    block_cnt = 0

    while (True):
        if loop_end:
            break

        print("Block", block_cnt, "is being compressed.")

        line_flag = []
        line_list = []

        index = 0

        while index < block_size:
            line = input.readline().decode()

            if (len(line) == 0):
                loop_end = True
                break

            while len(line) >= log_length:
                line_list.append(line[0:(log_length - 1)])
                line = line[(log_length - 1):]
                line_flag.append(1)
                index += 1
            
            line_list.append(line)
            line_flag.append(0)
            index += 1

        buckets = []
        bucket_cnt = 0
        bucket_index_list = []

        # get bucket
        for line in line_list:
            # data init
            distance = 1
            bucket_index = -1

            # estimating the begin of min edit distance
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
        
        line_sum = 0
        for b in buckets:
            line_sum += len(b)
        print(line_sum, "lines are devided into", bucket_cnt, "buckets.")

        df = pd.DataFrame(columns=('method',
                                   'another_line',
                                   'operation_size', 
                                   'position_list', 
                                   'd_length', 
                                   'i_length', 
                                   'sub_string'))

        for i in range(bucket_cnt):

            encoding_bucket = buckets[i]
            # print(i)

            for j in range(len(encoding_bucket)):
                line = encoding_bucket[j]
                if j == 0:
                    df = pd.concat([df,pd.DataFrame({'method':[1],
                                                     'another_line':[new_line_flag],
                                                     'sub_string':[line]})], ignore_index=True)
                else:
                    # print(encoding_bucket[j])
                    op_list, new_distance = get_Qgram_match_oplist(encoding_bucket[j-1], line, 3)
                    operation_size = len(op_list)
                    position_list = []
                    d_length = []
                    i_length = []
                    sub_string = []
                    for op in op_list:
                        position_list.append(op[0])
                        d_length.append(op[1])
                        i_length.append(op[2])
                        sub_string.append(op[3])
                    df2 = pd.DataFrame({'method':[0],
                                        'another_line':[new_line_flag],
                                        'operation_size':[operation_size], 
                                        'position_list':[position_list], 
                                        'd_length':[d_length],
                                        'i_length':[i_length], 
                                        'sub_string':[sub_string]})
                    df = pd.concat([df, df2], ignore_index=True)

        get_encoding_byte_array(bucket_index_list, df, output_path, compressor)
        block_cnt += 1

    t = perf_counter() - t

    return t