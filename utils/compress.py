import lzma
import gzip
import zstandard as zstd

from time import perf_counter

def general_compress(input_path, output_path, compressor):
    t = perf_counter()

    with open(input_path, 'rb') as input, open(output_path, 'wb') as output:
        if compressor == "lzma":
            comp_bytes = lzma.compress(input.read())
            output.write(comp_bytes)
        elif compressor == "gzip":
            comp_bytes = gzip.compress(input.read())
            output.write(comp_bytes)
        elif compressor == "zstd":
            comp_bytes = gzip.compress(input.read())
            output.write(comp_bytes)
        else:
            print("No such compressor or not be supported")
            return
        
    t = perf_counter() - t
    size = len(comp_bytes)

    print("The size of compress file is", size, "bytes.")
    print("The compress process cost", t, "s")

def general_decompress(input_path, output_path, compressor):
    t = perf_counter()

    with open(input_path, 'rb') as input, open(output_path, 'wb') as output:
        if compressor == "lzma":
            decomp_bytes = lzma.decompress(input.read())
            output.write(decomp_bytes)
        elif compressor == "gzip":
            decomp_bytes = gzip.decompress(input.read())
            output.write(decomp_bytes)
        elif compressor == "zstd":
            decomp_bytes = gzip.decompress(input.read())
            output.write(decomp_bytes)
        else:
            print("No such compressor or not be supported")
            return
        
    t = perf_counter() - t
    size = len(decomp_bytes)

    print("The size of decompress file is", size, "bytes.")
    print("The decompress process cost", t, "s")

def main():
    compressor = "lzma"
    input_path = "./datasets/test1_data_size/Linux_2000.txt"
    # input_path = "./result/buckets_dataset/Linux_1000" 
    output_path = "./result/tmp/Linux_2000_" + compressor
    general_compress(input_path, output_path, compressor)
    # general_decompress(output_path, input_path, compressor)
    

if __name__ == "__main__":
    main()