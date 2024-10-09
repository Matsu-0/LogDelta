from cmath import inf
from collections import deque

def get_min(distanceList):
    '''
    Parameter:
        distanceList: List of edit distance
    Return Value:
        value: min value in distanceList
        index list: the index list of min value in distanceList
    '''
    value = min(distanceList)
    index_list = []
    for index in range(len(distanceList)):
        if distanceList[index] == value:
            index_list.append(index)
    return value, index_list

def get_pre_point(i, j, op):
    prex = 0
    prey = 0

    if op == 0 or op == 3:
        prex = i - 1
        prey = j - 1
    elif op == 1:
        prex = i
        prey = j - 1
    elif op == 2:
        prex = i - 1
        prey = j
    
    return prex, prey

def compute_edit_distance(str1, str2):
    '''
    Parameter:
        str1, str2: string
    Return Value:
        distance: edit distance between str1 and str2
        dp: dp matrix
    '''
    len1 = len(str1)
    len2 = len(str2)

    str1_position_cost = 1
    str1_length_cost = 1
    str2_length_cost = 1
    str2_subchar_cost = 1

    dp = [[[0, []] for i in range(len2 + 1)]for j in range(len1 + 1)]
    for i in range(1, len1 + 1):
        dp[i][0] = [str1_position_cost + str1_length_cost + str2_length_cost, [2]]  # delete
    for i in range(1, len2 + 1):
        dp[0][i] = [str1_position_cost + str1_length_cost + str2_length_cost + i * str2_subchar_cost, [1]]  # insert
    
    for i in range(1, len1 + 1):
        for j in range(1, len2 + 1):
            flag = True
            distanceList = [inf, inf, inf, inf, inf]
            preDistance = [dp[i-1][j-1][0], dp[i][j-1][0], dp[i-1][j][0]]

            # same
            if (str1[i-1] == str2[j-1]):
                if (0 in dp[i-1][j-1][1]) or (i == 1 and j == 1):
                    dp[i][j] = [preDistance[0], [0]]
                    flag = False
                elif (i+1 < len1 and j+1 < len2) and (str1[i] == str2[j] and str1[i+1] == str2[j+1]):
                    dp[i][j] = [preDistance[0], [0]]
                    flag = False
                elif (i+1 == len1 and j+1 == len2) and (str1[i] == str2[j]):
                    dp[i][j] = [preDistance[0], [0]]
                    flag = False
                elif (i == len1 and j == len2):
                    dp[i][j] = [preDistance[0], [0]]
                    flag = False
                # print(i, j,dp[i][j])

            if flag:
                # insert
                if (0 not in dp[i][j-1][1]) and (len(dp[i][j-1][1]) > 0):
                    distanceList[1] = preDistance[1] + str2_subchar_cost # char
                else:
                    distanceList[1] = preDistance[1] + str1_position_cost + str1_length_cost + str2_length_cost + str2_subchar_cost

                # delete
                if (0 not in dp[i-1][j][1]) and (len(dp[i-1][j][1]) > 0):
                    distanceList[2] = preDistance[2]  # none
                else:
                    distanceList[2] = preDistance[2] + str1_position_cost + str1_length_cost + str2_length_cost

                # substitute
                if (0 not in dp[i-1][j-1][1]) and (len(dp[i-1][j-1][1]) > 0):
                    distanceList[3] = preDistance[0] + str2_subchar_cost # char
                else:
                    distanceList[3] = preDistance[0] + str1_position_cost + str1_length_cost + str2_length_cost + str2_subchar_cost

                distance, index_list = get_min(distanceList)
                dp[i][j] = [distance, index_list]

    distance = dp[len1][len2][0]
    return distance, dp#, t_init, t_dp

def build_path(dp, str1, str2):
    '''
    Parameter:
        dp: dp matrix get from compute_edit_distance(str1, str2)
        str1, str2: string, parameter of compute_edit_distance(str1, str2)
    Return Value:
        list: [insertList, deleteList, substituteList]
        insertList: List, operation list of insertion
        deleteList: List, operation list of deletion
        substituteList: List, operation list of substitutement
    '''
    # rebuild the path
    len1 = len(str1)
    len2 = len(str2)
    i = len1
    j = len2
    pre_op = 0
    operation_list = [] # position, 
  
    while((i != 0) and (j != 0)):
        oplist = dp[i][j][1]
        # print(i,j,op)

        if pre_op in oplist:
            op = pre_op
        else:
            op = oplist[0]

        if (op == 1):
            operation_list.append([1, i, str2[j - 1]])
            # operationList.append([i, str2[j]])
        elif (op == 2):
            operation_list.append([2, i - 1])
            # operationList.append([i])
        elif (op == 3):
            operation_list.append([3, i - 1, str2[j - 1]])
            # operationList.append([i, str2[j]])
        
        i, j = get_pre_point(i, j, op)
        pre_op = op
    if (j != 0):
        operation_list.append([1, 0, str2[0:j]])
    if (i != 0):
        operation_list.extend([[2, x] for x in range(i-1, -1, -1)])

    # print(operation_list)
    operation_list.reverse()
    new_op_list = []
    posi = -1
    begin_posi = 0
    sub_length1 = 0
    sub_length2 = 0
    substring = ""
    for op in operation_list:
        # print(op, posi, begin_posi)
        now_posi = op[1]
        if op[0] == 1 and now_posi == posi:
            sub_length2 += 1
            substring += op[2]
            posi = now_posi
        elif op[0] == 2 and now_posi == posi:
            sub_length1 += 1
            posi = now_posi + 1
        elif op[0] == 3 and now_posi == posi: 
            sub_length1 += 1
            sub_length2 += 1
            substring += op[2]
            posi = now_posi + 1
        else:
            if sub_length1 != 0 or sub_length2 != 0:
                new_op_list.append([begin_posi, sub_length1, sub_length2, substring])
            begin_posi = now_posi
            if op[0] == 1:
                sub_length1 = 0
                sub_length2 = 1
                substring = op[2]
                posi = now_posi
            elif op[0] == 2:
                sub_length1 = 1
                sub_length2 = 0
                substring = ""
                posi = now_posi + 1
            elif op[0] == 3:
                sub_length1 = 1
                sub_length2 = 1
                substring = op[2]
                posi = now_posi + 1
    if sub_length1 != 0 or sub_length2 != 0:
        new_op_list.append([begin_posi, sub_length1, sub_length2, substring])
    return new_op_list

def recover_string(operation_list, str1):
    '''
    from str1 and opList get str2
    Parameter:
        opreation_list: List, operation list sorted by palce in string
        str1: string, old string
    Return Value:
        s: string, new string(str2)
    '''
    s = ""
    old_posi = 0
    new_posi = 0
    for op in operation_list:
        # print("op:", op)
        new_posi, sub_len1, sub_len2, substr = op
        s += str1[old_posi: new_posi]

        s += substr
        new_posi += sub_len1
        old_posi = new_posi
    s += str1[old_posi:]
    return s


def main():
    str1 = "Jun  9 06:06:20 combo syslogd 1.4.1: restart."
    str2 = "Jun  9 06:06:20 combo syslog: syslogd startup succeeded"

    # str1 = "11461145514"
    # str2 = "1147114566514"

    d, dp= compute_edit_distance(str1, str2)
    operation_list = build_path(dp, str1, str2)
    print(operation_list)

    s = recover_string(operation_list, str1)
    
    # print(str1)
    print(s)
    print(str2)

if __name__ == "__main__":
    main()