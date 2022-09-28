import numpy as np


def pattern_match2(src, pattern):
    src_w = len(src[0])
    src_h = len(src)
    pattern_w = pattern[0]
    pattern_h = pattern[1]
    sums = [[0] * src_w] * src_h 
    sums = np.zeros([src_h, src_w]).astype(np.int32)
    for i in range(src_h):
        for j in range(src_w):
            if src[i][j] != pattern[2]:
                item = 0
            else:
                item = pattern[2]
            if i == 0 and j == 0:
                #print("1:"+str(i)+","+str(j)+","+str(sums))
                sums[i, j] = item
                #print("1-2:"+str(i)+","+str(j)+","+str(sums))
                #print(str(type(item)))
                #print(str(type(sums)))
                #print(str(type(sums[0])))
                #print(str(type(sums[0, 0])))
            elif i == 0:
                # print("2:"+str(i)+","+str(j)+","+str(sums))
                sums[i, j] = sums[i, j-1] + item
            elif j == 0:
                # print("3:"+str(i)+","+str(j)+","+str(sums))
                sums[i, j] = sums[i-1, j] + item
            else:
                # print("4:"+str(i)+","+str(j)+","+str(sums))
                sums[i, j] = item + sums[i-1, j] + sums[i, j-1] - sums[i-1, j-1]
            if i - pattern_h >= 0:
                # print("5:"+str(i)+","+str(j)+","+str(sums))
                sums[i, j] = sums[i, j] - (pattern[2] if src[i - pattern_h][j] == pattern[2] else 0)
            if j - pattern_w >= 0:
                # print("6:"+str(i)+","+str(j)+","+str(sums))
                sums[i, j] = sums[i, j] - (pattern[2] if src[i][j - pattern_w] == pattern[2] else 0)
            if i - pattern_h >= 0 and j - pattern_w >= 0:
                # print("7:"+str(i)+","+str(j)+","+str(sums))
                sums[i, j] = sums[i, j] + (pattern[2] if src[i - pattern_h][j - pattern_w] == pattern[2] else 0)
            if sums[i, j] == pattern[2] * pattern_w * pattern_h:
                return (i - pattern_h + 1, j - pattern_w + 1) # return the coordinate of left-top
    return (-1, -1)

if __name__ == '__main__':
    src = [[1, 1, 1],[1, 1, 1],[1, 1, 1]]
    pattern = (2, 2, 1)
    print(str(pattern_match2(src, pattern)))