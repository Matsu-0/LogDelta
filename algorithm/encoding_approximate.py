import gzip
import lzma
import pandas as pd
from time import perf_counter
from collections import deque
from math import ceil
from cmath import inf
from struct import pack

from utils.encoding import rle_compress, bit_packing_compress
from utils.bytearray import newOutArray
from algorithm.approximate_algorithm import get_Qgram_match_oplist
from algorithm.qgram import cosQgramDistance

def get_encoding_byte_array(df, output_path):

    encoding_block = 1024

    stream = newOutArray()

    df0 = df[df['method'] == 0]
    df1 = df[df['method'] == 1]

    stream.encode(len(df0), 16)
    stream.encode(len(df1), 16)

    # encode method by rle
    method = df['method'].tolist()

    method_string = ''
    for i in method:
        method_string += str(i)
    rle_string = rle_compress(method_string)
    method_length = ceil(len(rle_string) / 8)
    while (len(rle_string) < method_length * 8):
        rle_string += '0'
    stream.encode(method_length, 16)
    for i in range(method_length):
        bf = int(rle_string[i * 8: (i + 1) * 8], 2)
        stream.encode(bf, 8)

    # encode another_line by rle
    another_line = df['another_line'].tolist()

    another_line_string = ''
    for i in another_line:
        another_line_string += str(i)
    rle_string = rle_compress(another_line_string)
    line_length = ceil(len(rle_string) / 8)
    while (len(rle_string) < line_length * 8):
        rle_string += '0'
    stream.encode(line_length, 16)
    for i in range(line_length):
        bf = int(rle_string[i * 8: (i + 1) * 8], 2)
        stream.encode(bf, 8)

    df0 = df[df['method'] == 0]
    df1 = df[df['method'] == 1]

    # encode begin by bit packing
    begins = df0['begin'].tolist()

    begins_bytes = bytes()
    if len(begins) == 0:
        stream.encode(0, 16)
    else:
        bit_packing_string = bit_packing_compress(begins)
        length = ceil(len(bit_packing_string) / 8)
        while (len(bit_packing_string) < length * 8):
            bit_packing_string += '0'
        begins_bytes += pack('h', length)
        for i in range(length):
            bf = int(bit_packing_string[i * 8: (i + 1) * 8], 2)
            begins_bytes += pack('B', bf)
        begins_bytes = gzip.compress(begins_bytes)

        stream.encode(len(begins_bytes), 16)
        for byte in begins_bytes:
            stream.encode(byte, 8)

    # encode operation size by bit packing
    operation_size = df0['operation_size'].tolist()

    operation_bytes = bytes()
    if len(operation_size) == 0:
        stream.encode(0, 16)
    else:
        bit_packing_string = bit_packing_compress(operation_size)
        length = ceil(len(bit_packing_string) / 8)
        while (len(bit_packing_string) < length * 8):
            bit_packing_string += '0'
        operation_bytes += pack('h', length)
        for i in range(length):
            bf = int(bit_packing_string[i * 8: (i + 1) * 8], 2)
            operation_bytes += pack('B', bf)
        operation_bytes = gzip.compress(operation_bytes)

        stream.encode(len(operation_bytes), 16)
        for byte in operation_bytes:
            stream.encode(byte, 8)

    # encode length by bit packing and gzip
    d_length = df0['d_length'].tolist()
    i_length = df0['i_length'].tolist()
    length_list = d_length + i_length

    length_bytes = bytes()
    if len(length_list) == 0:
        stream.encode(0 ,16)
    else:
        leng_list = []
        for length in length_list:
            for l in length:
                leng_list.append(l)

        for i in range(max(int((len(leng_list) - 1) / encoding_block), 1)):
            l_bytes = bytes()
            l_list = leng_list[i * encoding_block: (i + 1) * encoding_block]
            bit_packing_string = bit_packing_compress(l_list)
            length = ceil(len(bit_packing_string) / 8)
            while (len(bit_packing_string) < length * 8):
                bit_packing_string += '0'
            l_bytes += pack('H', length)
            stream.encode(length, 16)
            for i in range(length):
                bf = int(bit_packing_string[i * 8: (i + 1) * 8], 2)
                l_bytes += pack('B', bf)

            length_bytes += l_bytes
        length_bytes = gzip.compress(length_bytes)

        stream.encode(len(length_bytes), 16)
        for byte in length_bytes:
            stream.encode(byte, 8)

    # encode position by bit packing and gzip
    position_list = df0['position_list'].tolist()
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

        p_begin_bytes = bytes()

        for i in range(max(int((len(p_begin_list) - 1) / encoding_block), 1)):
            p_bytes = bytes()
            p_list = p_begin_list[i * encoding_block : (i+1) * encoding_block]
            bit_packing_string = bit_packing_compress(p_list)
            length = ceil(len(bit_packing_string) / 8)
            while (len(bit_packing_string) < length * 8):
                bit_packing_string += '0'
            p_bytes += pack('h', length)
            for i in range(length):
                bf = int(bit_packing_string[i * 8: (i + 1) * 8], 2)
                p_bytes += pack('B', bf)
            p_begin_bytes += p_bytes
        p_begin_bytes = gzip.compress(p_begin_bytes)

        stream.encode(len(p_begin_bytes), 16)
        for byte in p_begin_bytes:
            stream.encode(byte, 8)

        p_delta_bytes = bytes()
        for i in range(max(int((len(p_delta_list) - 1) / encoding_block), 1)):
            p_bytes = bytes()
            p_list = p_delta_list[i * encoding_block : (i+1) * encoding_block]
            bit_packing_string = bit_packing_compress(p_list)
            length = ceil(len(bit_packing_string) / 8)
            while (len(bit_packing_string) < length * 8):
                bit_packing_string += '0'
            p_bytes += pack('h', length)
            for i in range(length):
                bf = int(bit_packing_string[i * 8: (i + 1) * 8], 2)
                # print("bf:",bf)
                p_bytes += pack('B', bf)
            p_delta_bytes += p_bytes
        p_delta_bytes = gzip.compress(p_delta_bytes)

        stream.encode(len(p_delta_bytes), 16)
        for byte in p_delta_bytes:
            stream.encode(byte, 8)

    # encoding strings
    sub_string = ''

    sub_string_list = df0['sub_string'].tolist()
    for st_list in sub_string_list:
        for s in st_list:
            sub_string += s

    sub_string_1 = df1['sub_string'].tolist()
    for s in sub_string_1:
        sub_string += s
    
    string_compress = lzma.compress(sub_string.encode())

    for byte in string_compress:
        stream.encode(byte, 8)
    
    stream.write(output_path, "ab")
    return 
    # return stream


def main_encoding_compress(input_path, output_path, window_size= 8, log_length = 256, threshold = 0.035, block_size = 32768):
    t = perf_counter()
    q = deque()

    new_line_flag = 0

    df = pd.DataFrame(columns=('method','another_line','begin', 'operation_size', 
                        'position_list', 'd_length', 'i_length', 'sub_string'))
    input = open(input_path, "rb" )

    # write encoding head
    stream = newOutArray()
    stream.encode(window_size, 16)
    stream.encode(log_length, 16)
    stream.encode(block_size, 16)
    stream.write(output_path)

    loop_end = False
    while (True):
        if loop_end:
            break

        for index in range(block_size):  
            if new_line_flag == 1:
                line = next_line
            else:
                line = input.readline().decode()

            if (len(line) >= log_length):
                next_line = line[(log_length - 1):]
                line = line[0:(log_length - 1)]
                new_line_flag = 1
            else:
                new_line_flag = 0

            # check if loop end
            if (len(line) == 0):
                loop_end = True
                break

            # data init
            distance = 1
            begin = -1

            # estimating the begin of min edit distance
            for i in range(len(q)):
                tmpd = cosQgramDistance(q[i], line)
                if (tmpd < distance):
                    distance = tmpd
                    begin = i

            if (begin == -1 or distance >= threshold):
                df = pd.concat([df,pd.DataFrame({'method':[1],'another_line':[new_line_flag],
                                            'sub_string':[line]})], ignore_index=True)
            else:
                op_list, new_distance = get_Qgram_match_oplist(q[begin], line, 3)
                if (new_distance > len(line)):
                    df = pd.concat([df,pd.DataFrame({'method':[1],'another_line':[new_line_flag],
                                            'sub_string':[line]})], ignore_index=True)
                else:
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
                    df2 = pd.DataFrame({'method':[0],'another_line':[new_line_flag],'begin':[begin], 'operation_size':[operation_size], 
                                    'position_list':[position_list], 'd_length':[d_length],'i_length':[i_length], 'sub_string':[sub_string]})

                    df = pd.concat([df, df2], ignore_index=True)
            

            if (len(q) < window_size):
                q.append(line)
            else:
                q.popleft()
                q.append(line)

        get_encoding_byte_array(df, output_path)

    t = perf_counter() - t

    return t
