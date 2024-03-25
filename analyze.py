import matplotlib.pyplot as plt
import numpy as np


middle = 0
threshold = 75
diff_threshold = 40
confidence = 0.9


def dofilter(filtered2, times):
    for it in range(times):
        for i in range(1, len(filtered2)-1):
            if((filtered2[i] > middle) and (2*filtered2[i] < (filtered2[i-1]+filtered2[i+1])) or \
            (filtered2[i] < middle) and (2*filtered2[i] > (filtered2[i-1]+filtered2[i+1]))):
                filtered2[i] = (filtered2[i-1]+filtered2[i+1])/2
    return filtered2

def find_depth(ang, dot):
    inc_left = 0
    inc_right = 0
    left = dot
    right = dot
    for j in range(dot-1, -1, -1):
        inc_left += (ang[j] >= ang[j + 1])
        if(inc_left >= confidence * (dot-j)):
            left = j
    for j in range(dot+1, len(ang)-1, +1):
        inc_right += (ang[j] >= ang[j - 1])
        if(inc_right >= confidence * (j-dot)):
            right = j

    if(dot != left):
        left_height = np.max(ang[left:dot])
    else:
        left_height = ang[dot]

    if(dot != right):
        right_height = np.max(ang[dot:right])
    else:
        right_height = ang[dot]

    if(abs(left_height - right_height) > diff_threshold):
        return False
    duration = right - left
    return [ang[dot], duration]

def find_pitfalls(ang):
    ans = []
    for i in range(1, ang.shape[0]-1):
        if(ang[i-1] >= ang[i] and ang[i] <= ang[i + 1] and ang[i] <= threshold):
            ans.append(i)
    return ans






