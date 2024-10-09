def binary_search(list, item):
    l = 0
    h = len(list) - 1
    while(l <= h):
        m = (l + h) // 2
        if list[m] == item:
            return m
        elif list[m] > item:
            h = m - 1
        else:
            l = m + 1
    return -1

def get_min(distanceList):
    value = min(distanceList)
    index = distanceList.index(value)
    return value, index