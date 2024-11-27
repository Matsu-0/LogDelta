import sys
import os
import argparse
import pandas as pd
from utils.utils import mkdir
from warnings import filterwarnings
import algorithm.encoding_accurate as exact
import algorithm.encoding_approximate as approx

def add_arguments(argparser):
    argparser.add_argument("-i",
                           default=None,
                           type=str,
                           required=True,
                           help="Input file path")
    
    argparser.add_argument("-o",
                           default=None,
                           type=str,
                           required=True,
                           help="Output dir")

    argparser.add_argument("-e",
                           default='A',
                           type=str,
                           help="Encode mode, E for accurate and A for approx")
    
    argparser.add_argument("-c",
                           default='lzma',
                           type=str,
                           help="General compressor, now support [lzma, gzip, zstd]")
    
    argparser.add_argument("-w",
                           type=int,
                           default='8',
                           help="Sliding window size")
    
    argparser.add_argument("-l",
                           type=int,
                           default='256',
                           help="Uniform log length")
    
    argparser.add_argument("-b",
                           type=int,
                           default='32768',
                           help="Block size")
    
    argparser.add_argument("-t",
                           type=float,
                           default='0.035',
                           help="Distance threshold")
    
    

def main():
    filterwarnings("ignore", category= RuntimeWarning)
    argparser = argparse.ArgumentParser()

    add_arguments(argparser)
    args = argparser.parse_args()

    input_path = args.i
    output_dir= args.o    
    encoding_type = args.e
    sliding_window_size = args.w
    log_length = args.l
    block_size = args.b
    distance_threshold = args.t
    compressor = args.c

    file_name = os.path.splitext(os.path.basename(input_path))[0]

    mkdir(output_dir)
    output_path = os.path.join(output_dir, file_name)

    if encoding_type == 'A':
        time = approx.main_encoding_compress(input_path=input_path,
                                             output_path=output_path,
                                             window_size=sliding_window_size,
                                             log_length=log_length,
                                             threshold=distance_threshold,
                                             block_size=block_size,
                                             compressor=compressor)
    elif encoding_type == 'E':
        time = exact.main_encoding_compress(input_path=input_path,
                                            output_path=output_path,
                                            window_size=sliding_window_size,
                                            log_length=log_length,
                                            threshold=distance_threshold,
                                            block_size=block_size,
                                            compressor=compressor)

    print("Encoding time is:", time, "s")

if __name__ == "__main__":
    main()