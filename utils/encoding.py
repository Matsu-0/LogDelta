def rle_compress(bit_list):
    bit_string = ''
    for i in bit_list:
        bit_string += str(i)
    
    rle_string = ''
    now_bit = bit_string[0]
    now_count = 0
    rle_string += now_bit
    count_list = []
    for i in range(len(bit_string)):
        if (bit_string[i] == now_bit):
            now_count += 1
        else:
            count_list.append(now_count)
            now_bit = bit_string[i]
            now_count = 1
    count_list.append(now_count)

    for count in count_list:
        d = 4   # check max
        l = 2   # 1 num
        while (count > d):
            d *= 2
            l += 1
        for i in range(l - 2):
            rle_string += '1'
        rle_string += '0'
        if (count <= 2):
            rle_string += '0'
        rle_string += str(bin(count - 1))[2:]
        # print(rle_string)
    return rle_string


def bit_packing_compress(number_list, mult = 2):
    max_bit = 0
    for number in number_list:
        if number > max_bit:
            max_bit = number
    bit_length = max_bit.bit_length()
    if bit_length % 2 == 1:
        bit_length += 1
    # print(bit_length)
    bit_save = str(bin(bit_length))[2:]
    while(len(bit_save) < 4):
        bit_save = '0' + bit_save
    # print(bit_save)
    bit_packing_string = bit_save
    for number in number_list:
        # print(number)
        tmp_bit = str(bin(number))[2:]
        while(len(tmp_bit) < bit_length):
            tmp_bit = '0' + tmp_bit
        bit_packing_string += tmp_bit
        # print(tmp_bit)

    return bit_packing_string
