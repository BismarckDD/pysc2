


# if match, return right-bottom match pos
# else return (-1, -1)
def pattern_match(src, width, height, digit):
    w = len(src[0])
    h = len(src)
    wm = [[0] * w] * h 
    hm = [[0] * w] * h
    for i in range(h):
        for j in range(w):
            if src[i][j] != digit: 
                wm[i][j] = 0
                hm[i][j] = 0
            else:
                if i == 0 and j == 0:
                    wm[i][j] = hm[i][j] = 1
                elif i == 0:
                    wm[i][j] = wm[1][j-1] + 1 
                    hm[i][j] = 1
                elif j == 0:
                    wm[i][j] = 1
                    hm[i][j] = hm[i-1][j] + 1
                else:
                    if hm[i-1][j] >= hm[i-1][j-1]:
                        w0 = wm[i-1][j-1] + 1
                    else:
                        w0 = wm[i-1][j]
                    if wm[i][j-1] >= wm[i-1][j-1]:
                        h0 = hm[i-1][j-1] + 1
                    else:
                        h0 = hm[i][j-1]
                    w1 = wm[i][j-1] + 1
                    if hm[i-1][j] >= hm[i][j-1] + 1:
                        h1 = hm[i][j-1]
                    else:
                        h1 = hm[i-1][j] + 1
                    h2 = hm[i-1][j] + 1
                    if wm[i][j-1] >= wm[i-1][j] + 1:
                        w2 = wm[i-1][j]
                    else:
                        w2 = wm[i][j-1] + 1
                    s0 = w0 * h0 # left-top
                    s1 = w1 * h1 # left warning: left 在前
                    s2 = w2 * h2 # top
                    if s0 >= s1 and s0 >= s2:
                        wm[i][j] = w0
                        hm[i][j] = h0
                    elif s1 >= s2 and s1 >= s0:
                        wm[i][j] = w1
                        hm[i][j] = h1
                    else:
                        wm[i][j] = w2
                        hm[i][j] = h2
            if wm[i][j] >= width and hm[i][j] >= height:
                return (i, j)
    return (-1, -1)

def match_in(mat, coll):
    for i in range(len(mat)):
        for j in range(len(mat[0])):
            if mat[i][j] in coll:
                return (i, j)
    return (-1, -1)

# cond1: buildable: 1, buildable
# cond2: unit_type: 0, without unit
def buildable_without_unit(cond1, cond2):
    res = [[0] * len(cond1[0])] * len(cond1)
    for i in range(len(cond1)):
        for j in range(len(cond2)):
            if cond1[i][j] == 1 and cond2[i][j] == 0:
                res[i][j] = 1
    return res