import time
import gzip
import lzma
import pandas as pd
from struct import unpack, pack
from utils.decoding import rle_decompress, bit_packing_decompress
from improved_edit_distance import recover_string

def recover_byte_array(file_path):
    window_size = 0
    index = 0

    method = []
    another_line = []
    begins = []
    operation_size = []
    length_list = []
    position_list = []
    sub_string = []

    with open(file_path, 'rb') as handle:
        window_size = unpack('h', handle.read(2))[0]
        df0_len = unpack('h', handle.read(2))[0]
        df1_len = unpack('h', handle.read(2))[0]
        index = df0_len + df1_len

        method_length = unpack('h', handle.read(2))[0]
        rle_string = ''
        for i in range(method_length):
            bf = unpack('B', handle.read(1))[0]
            tmp_str = str(bin(bf))[2:]
            rle_string += '0' * (8 - len(tmp_str)) + str(bin(bf))[2:]
        # print(rle_string)
        method = rle_decompress(rle_string, index)
        # print(method)

        line_length = unpack('h', handle.read(2))[0]
        rle_string = ''
        for i in range(line_length):
            bf = unpack('B', handle.read(1))[0]
            tmp_str = str(bin(bf))[2:]
            rle_string += '0' * (8 - len(tmp_str)) + str(bin(bf))[2:]
        # print(rle_string)
        another_line = rle_decompress(rle_string, index)
        # print(another_line)

        begin_length = unpack('h', handle.read(2))[0]
        begins = []
        if (begin_length != 0):
            bit_packing_string = ''
            for i in range(begin_length):
                bf = unpack('B', handle.read(1))[0]
                tmp_str = str(bin(bf))[2:]
                bit_packing_string += '0' * (8 - len(tmp_str)) + str(bin(bf))[2:]
            begins = bit_packing_decompress(bit_packing_string, df0_len)
        # print(begins)

        operation_length = unpack('h', handle.read(2))[0]
        operation_size = []
        if (operation_length != 0):
            gzip_string = handle.read(operation_length)
            operation_bytes = gzip.decompress(gzip_string)
            for op_size in operation_bytes:
                operation_size.append(op_size)
        # print(operation_size)

        d_length_length = unpack('h', handle.read(2))[0]
        if (d_length_length != 0):
            gzip_string = handle.read(d_length_length)
            length_bytes = gzip.decompress(gzip_string)
            for length in length_bytes:
                length_list.append(length)
        print(length_list)

        position_length = unpack('h', handle.read(2))[0]
        if (position_length != 0):
            p_begin_length = position_length
            p_begin_list = []
            gzip_string = handle.read(p_begin_length)
            p_begin_bytes = gzip.decompress(gzip_string)
            for p_begin in p_begin_bytes:
                p_begin_list.append(p_begin)
            # print(p_begin_list)
            
            p_delta_length = unpack('h', handle.read(2))[0]
            p_delta_list = []
            gzip_string = handle.read(p_delta_length)
            p_delta_bytes = gzip.decompress(gzip_string)
            for p_delta in p_delta_bytes:
                p_delta_list.append(p_delta)
    

            tmp_begin_index = 0
            tmp_delta_index = 0
            for op_size in operation_size:
                p_list = []
                if op_size > 0:
                    position = p_begin_list[tmp_begin_index]
                    tmp_begin_index += 1
                    p_list.append(position)
                    for j in range(op_size - 1):
                        position += p_delta_list[tmp_delta_index]
                        p_list.append(position)
                        tmp_delta_index += 1
                position_list.append(p_list)
        print(position_list)

        string_compress = handle.read()
        sub_string = lzma.decompress(string_compress).decode()
        # print(sub_string)
        sub_string_len = len(sub_string)
    
    tmp_index = 0
    


def main():
    recover_byte_array("D:/useful/DDL/homework/data_compression/result/result_new/new_file")


if __name__ == "__main__":
    main()