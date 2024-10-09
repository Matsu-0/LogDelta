from collections import Counter
from cmath import inf
from utils.utils import get_min, binary_search

def get_Qgram(str, k=3):
    Qgram_list = []
    str = "$" * (k-1) + str + "#" * (k-1)
    for i in range(len(str) - k + 1):
        Qgram_list.append(str[i: i+k])
    # print(Qgram_list)
    return Qgram_list


def get_Qgram_match_oplist(str1, str2, k=3):

    len_str1 = len(str1)
    len_str2 = len(str2)

    # t = perf_counter()
    Q_gram_1 = get_Qgram(str1, k)
    Q_gram_2 = get_Qgram(str2, k)
    Q1_counter = Counter(Q_gram_1)
    Q2_counter = Counter(Q_gram_2)
    common_Q_gram = list(Q1_counter & Q2_counter)
    common_Q_gram.sort()
    # print(common_Q_gram)
    # t_get_qram = perf_counter() - t

    Q_dict = dict()
    for index in range(len(common_Q_gram)):
        Q_dict[common_Q_gram[index]] = index
    
    # print(Q_dict)

    # t = perf_counter()
    Q1_to_common_map = []
    for item in Q_gram_1:
        # Q1_to_common_map.append(binary_search(common_Q_gram, item))
        if item in Q_dict:
            Q1_to_common_map.append(Q_dict[item])
        else:
            Q1_to_common_map.append(-1)
    Q1_common = []
    Q1_common_index = []
    for i in range(len(Q1_to_common_map)):
        item = Q1_to_common_map[i]
        if item != -1:
            Q1_common.append(item)
            Q1_common_index.append(i)
    # print(Q1_to_common_map)
    # print(Q1_common)
    # print(Q1_common_index)

    Q2_to_common_map = []
    for item in Q_gram_2:
        # Q2_to_common_map.append(binary_search(common_Q_gram, item))
        if item in Q_dict:
            Q2_to_common_map.append(Q_dict[item])
        else:
            Q2_to_common_map.append(-1)
    Q2_common = []
    Q2_common_index = []
    for i in range(len(Q2_to_common_map)):
        item = Q2_to_common_map[i]
        if item != -1:
            Q2_common.append(item)
            Q2_common_index.append(i)
    # print(Q2_to_common_map)
    # print(Q2_common)
    # print(Q2_common_index)
    # t_count_common = perf_counter() - t

    # t = perf_counter()
    match_list_in_Q_gram = []

    index1 = 0
    index2 = 0
    while(index1 < len(Q1_common)):
        Q_gram_index = Q1_common[index1]
        Q_gram = common_Q_gram[Q_gram_index]
        if Q2_counter[Q_gram] != 0:
            while(index2 < len(Q2_common) and Q2_common[index2] != Q_gram_index):
                Q2_counter[Q2_common[index2]] -= 1
                index2 += 1
            if (index2 >= len(Q2_common)):
                break
            elif (Q2_common[index2] == Q_gram_index):
                match_list_in_Q_gram.append([Q1_common_index[index1], Q2_common_index[index2]])
                Q2_counter[Q2_common[index2]] -= 1
                index2 += 1
        index1 += 1
    # print(match_list_in_Q_gram)
    # t_match = perf_counter() - t

    # t = perf_counter()
    match_list_in_Q_gram.reverse()
    merge_match_list = []
    pre_item = 0
    begin_item = 0
    for item in match_list_in_Q_gram:
        # begin
        if pre_item == 0:
            pre_item = item
            begin_item = item
        # continue
        elif pre_item[0] == item[0] + 1 and pre_item[1] == item[1] + 1:
            # merge
            pre_item = item
        # no repeat (new item)
        elif pre_item[0] > item[0] + (k-1) and pre_item[1] > item[1] + (k-1):
            merge_match_list.append([begin_item, pre_item])
            pre_item = item
            begin_item = item
    if (pre_item != 0):
        merge_match_list.append([begin_item, pre_item])
    # print(merge_match_list)
    # t_merge = perf_counter() - t

    # t = perf_counter()
    match_string_position = []
    for match_item in merge_match_list:
        x_begin = match_item[1][0] - (k-1)
        x_end = match_item[0][0]
        y_begin = match_item[1][1] - (k-1)
        y_end = match_item[0][1]
    
        # print(x_begin, x_end, y_begin, y_end)

        if x_begin < 0:
            x_begin = 0
        if y_begin < 0:
            y_begin = 0
        if x_end >= len_str1:
            x_end = len_str1 - 1
        if y_end >= len_str2:
            y_end = len_str2 - 1
        match_string_position.append([x_begin, x_end, y_begin, y_end])
    
    match_string_position.reverse()
    # print(match_string_position)

    pre_item = [-1, -1, -1, -1]
    operation_list = []
    for item in match_string_position:
        if (item[0] != 0 or item[2] != 0):
            position = pre_item[1] + 1
            length_1 = item[0] - pre_item[1] - 1
            length_2 = item[2] - pre_item[3] - 1
            substr = str2[pre_item[3] + 1: item[2]]
            operation_list.append([position, length_1, length_2, substr])
        pre_item = item
    if (len_str1 != pre_item[1] + 1 or len_str2 != pre_item[3] + 1):
        operation_list.append([pre_item[1] + 1, len_str1 - pre_item[1] - 1, len_str2 - pre_item[3] - 1, str2[pre_item[3] + 1:]])

    # t_get_oplist = perf_counter() - t
    # compute distance

    distance = 0
    for op in operation_list:
        distance += 3 + op[2]
    distance += 5

    # distance = 0
    # for op in operation_list:
    #     # size, position, length_1, length_2, string
    #     distance += 0.49052327 * 4 + op[2] * 0.01453658

    return operation_list, distance#, t_get_qram, t_count_common, t_match, t_merge, t_get_oplist

def recover_string(operation_list, str1):
    s = ""
    old_posi = 0
    new_posi = 0
    for op in operation_list:
        new_posi, sub_len1, sub_len2, substr = op
        s += str1[old_posi: new_posi]

        s += substr
        new_posi += sub_len1
        old_posi = new_posi
    s += str1[old_posi:]
    return s


def main():
    str1 = "Jun 11 09:46:15 combo sshd: authentication failure; logname= uid=0 euid=0 tty=NODEVssh ruser= rhost=unknown.sagonet.net  user=root"
    str2 = "Jun 11 09:46:18 combo sshd(pam_unix)[6488]: authentication failure; logname= uid=0 euid=0 tty=NODEVssh ruser= rhost=unknown.sagonet.net  user=root"
    
    # t_get_qram = 0
    # t_count_common = 0
    # t_match = 0
    # t_merge = 0
    # t_get_oplist = 0
    # for i in range(10000):
    #     operation_list, distance, t1, t2, t3, t4, t5= get_Qgram_match_oplist(str1, str2, 3)
    #     t_get_qram += t1
    #     t_count_common += t2
    #     t_match += t3
    #     t_merge += t4
    #     t_get_oplist += t5
    # print(t_get_qram, t_count_common, t_match, t_merge, t_get_oplist)

    operation_list, distance = get_Qgram_match_oplist(str1, str2, 3)
    print(operation_list, distance)
    s = recover_string(operation_list, str1)
    print(str2)
    print(s)

if __name__ == "__main__":
    main()