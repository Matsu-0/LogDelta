import time
import gzip
import lzma
import pandas as pd
from collections import deque
from struct import unpack, pack
from utils.decoding import rle_decompress, bit_packing_decompress
from approximate_algorithm import recover_string

def recover_byte_array(input_filepath, output_filepath, block_size = 256):
    window_size = 0
    index = 0

    method = []
    another_line = []
    begins = []
    operation_size = []
    d_length = []
    i_length = []
    position_list = []
    substring_0 = []
    substring_1 = []

    # df = pd.DataFrame(columns=('method','another_line','begin', 'operation_size', 
    #                     'position_list', 'd_length', 'i_length', 'sub_string'))

    with open(input_filepath, 'rb') as handle:
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
        if (begin_length != 0):
            bit_packing_string = ''
            for i in range(begin_length):
                bf = unpack('B', handle.read(1))[0]
                tmp_str = str(bin(bf))[2:]
                bit_packing_string += '0' * (8 - len(tmp_str)) + str(bin(bf))[2:]
            begins = bit_packing_decompress(bit_packing_string, df0_len)
        # print(begins)

        operation_length = unpack('h', handle.read(2))[0]
        if (operation_length != 0):
            gzip_string = handle.read(operation_length)
            operation_bytes = gzip.decompress(gzip_string)
            for op_size in operation_bytes:
                operation_size.append(op_size)
        # print(operation_size)

        # length_length = unpack('h', handle.read(2))[0]
        # length_list = []
        # if (length_length != 0):
        #     gzip_string = handle.read(length_length)
        #     length_bytes = gzip.decompress(gzip_string)
        #     for length in length_bytes:
        #         length_list.append(length)
        length_length = unpack('h', handle.read(2))[0]
        length_list = []
        if (length_length != 0): 
            gzip_string = handle.read(length_length)
            length_bytes = gzip.decompress(gzip_string)
            print(length_bytes)
            # for i in range(length_bytes):
            #     bf = unpack('B', handle.read(1))[0]
            #     tmp_str = str(bin(bf))[2:]
            #     bit_packing_string += '0' * (8 - len(tmp_str)) + str(bin(bf))[2:]
            # length_bytes = bit_packing_decompress(bit_packing_string, df0_len)
        
        # print(length_list)

        tmp_index = 0
        for op_size in operation_size:
            d_length.append(length_list[tmp_index: tmp_index + op_size])
            tmp_index += op_size
        for op_size in operation_size:
            i_length.append(length_list[tmp_index: tmp_index + op_size])
            tmp_index += op_size
        # print(d_length, i_length)

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
        # print(position_list)

        string_compress = handle.read()
        sub_string = lzma.decompress(string_compress).decode()
        # print(sub_string)
        sub_string_len = len(sub_string)

        tmp_index = 0
        substring_0 = []
        for i in range(df0_len):
            op_size = operation_size[i]
            # delete_len_list = d_length[i]
            insert_len_list = i_length[i]
            substring_list = []
            for le in insert_len_list:
                substring_list.append(sub_string[tmp_index: tmp_index + le])
                tmp_index += le
            substring_0.append(substring_list)
        # print(substring_0)

        substring_1 = []
        for i in range(index):
            if method[i] == 1:
                if another_line[i] == 0:
                    new_index = tmp_index
                    while(new_index < sub_string_len and sub_string[new_index] != '\n'):
                        new_index += 1
                    new_index += 1
                    substring_1.append(sub_string[tmp_index: new_index])
                    # print(sub_string[tmp_index: new_index])
                    tmp_index = new_index
                elif another_line[i] == 1:
                    substring_1.append(sub_string[tmp_index: tmp_index + (block_size - 1)])
                    # print(sub_string[tmp_index: tmp_index + (block_size - 1)])
                    tmp_index += block_size - 1
        # print(substring_1)
        
        # print(index)
        # print(len(method))
        # print(len(another_line))

        # print(df0_len)
        # print(len(begins))
        # print(len(operation_size))
        # print(len(position_list))
        # print(len(d_length))
        # print(len(i_length))
        # print(len(substring_0))
    
        # print(df1_len)
        # print(len(substring_1))


        # index0 = 0
        # index1 = 0

        # for i in range(index):
        #     if method[i] == 0:
        #         df = pd.concat([df,pd.DataFrame({'method':[0],'another_line':[another_line[i]],'begin':[begins[index0]], 'operation_size':[operation_size[index0]], 
        #                         'position_list':[position_list[index0]], 'd_length':[d_length[index0]],'i_length':[i_length[index0]], 'sub_string':[substring_0[index0]]})], ignore_index = True)
        #         index0 += 1
        #     elif method[i] == 1:
        #         df = pd.concat([df,pd.DataFrame({'method':[method[i]],'another_line':[another_line[i]],
        #                                 'sub_string':[substring_1[index1]]})], ignore_index=True)
        #         index1 += 1
                    
    q = deque()
    index0 = 0
    index1 = 0
    with open(output_filepath, 'wb') as handle:
        q_line = ''
        line = ''
        for i in range(index):
            if method[i] == 0:
                op_list = []
                p_list = position_list[index0]
                d_len_list = d_length[index0]
                i_len_list = i_length[index0]
                substr_list = substring_0[index0]

                for j in range(operation_size[index0]):
                    op_list.append([p_list[j], d_len_list[j], i_len_list[j], substr_list[j]])
                q_line = recover_string(op_list, q[begins[index0]])
                index0 += 1

            elif method[i] == 1:
                q_line = substring_1[index1]
                index1 += 1

            line += q_line

            if another_line[i] == 0:
                handle.write(line.encode())
                line = ''

            if (len(q) < window_size):
                q.append(q_line)
            else:
                q.popleft()
                q.append(q_line)
    return

def test():
    input_path = "./result/approximate"
    output_path = "./result/Apache_7000.txt"

    recover_byte_array(input_path, output_path)

def main():
    input_path = input('请输入待解压文件的路径：')
    output_path = input('请输入解压后文件的路径：')

    recover_byte_array(input_path, output_path)


if __name__ == "__main__":
    # main()
    test()