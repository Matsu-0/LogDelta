def rle_decompress(rle_string, index):
    bit_list =[]
    now_len = 0
    now_bit = int(rle_string[0])
    bit_position = 1
    rle_len = len(rle_string)
    while (bit_position < rle_len):
        l = 2
        while (rle_string[bit_position] == '1'):
            l += 1
            bit_position += 1
        num_string = rle_string[bit_position + 1 : bit_position + l + 1]
        bit_position += l + 1
        number = int('0b' + num_string, 2) + 1
        for i in range(number):
            bit_list.append(now_bit)
        now_bit = 1 - now_bit
        now_len += number
        if (now_len >= index):
            break
        
    # print(bit_list)
    return bit_list


def bit_packing_decompress(bit_packing_string, index):
    number_list = []
    bit_save = bit_packing_string[0:4]
    # print(bit_save)
    bit_length = int('0b' + bit_save, 2)
    # print(bit_length)
    bit_position = 4
    bit_packing_length = len(bit_packing_string)
    now_len = 0
    while(bit_position < bit_packing_length):
        tmp_num_str = bit_packing_string[bit_position: bit_position + bit_length]
        bit_position += bit_length
        tmp_num =  int('0b' + tmp_num_str, 2)
        number_list.append(tmp_num)
        now_len += 1
        if (now_len >= index):
            break
    return number_list