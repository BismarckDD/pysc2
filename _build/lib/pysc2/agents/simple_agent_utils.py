import numpy as np
from pysc2.lib.colors import unit_type
from pysc2.lib.units import Terran

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
                return (i - height + 1, j - width + 1)
    return (-1, -1)

# pattern is a tuple that has 3 attributes below.
# 0: w
# 1: h
# 2: digi
# src is a np.array
def pattern_match2(src, pattern):
    src_w = src.shape[1]
    src_h = src.shape[0]
    pattern_w = pattern[0]
    pattern_h = pattern[1]
    sums = np.zeros([src_h, src_w]).astype(np.int32)
    for i in range(src_h):
        for j in range(src_w):
            if src[i, j] != pattern[2]:
                item = 0
            else:
                item = pattern[2]
            if i == 0 and j == 0:
                sums[i, j] = item
            elif i == 0:
                sums[i, j] = sums[i, j-1] + item
            elif j == 0:
                sums[i, j] = sums[i-1, j] + item
            else:
                sums[i, j] = item + sums[i-1, j] + sums[i, j-1] - sums[i-1, j-1]
            if i - pattern_h >= 0:
                sums[i, j] = sums[i, j] - (pattern[2] if src[i - pattern_h, j] == pattern[2] else 0)
            if j - pattern_w >= 0:
                sums[i, j] = sums[i, j] - (pattern[2] if src[i, j - pattern_w] == pattern[2] else 0)
            if i - pattern_h >= 0 and j - pattern_w >= 0:
                sums[i, j] = sums[i, j] + (pattern[2] if src[i - pattern_h, j - pattern_w] == pattern[2] else 0)
            if sums[i, j] == pattern[2] * pattern_w * pattern_h:
                return (i - pattern_h + 1, j - pattern_w + 1) # return the coordinate of left-top
    return (-1, -1)

def match_in(mat, coll):
    for i in range(len(mat)):
        for j in range(len(mat[0])):
            if mat[i][j] in coll:
                return (i, j)
    return (-1, -1)

# 获得当前screen可以建造建筑的位置
# buildable: 1, buildable
# unit_type: 0, without any unit on this pos
# visibility: 1 or 2, has been searched ever.
def get_buildable_area(obs):
    unit_type = obs.feature_screen.unit_type
    buildable = obs.feature_screen.buildable
    visible = obs.feature_screen.visibility_map
    h = len(unit_type)
    w = len(unit_type[0])
    res = np.zeros([h, w]).astype(np.int32)
    for i in range(h):
        for j in range(w):
            # visible can be 1 or 2.
            if buildable[i][j] == 1 and unit_type[i][j] == 0 and visible[i][j] == 2:
                res[i, j] = 1
    return res

def get_building_area(obs):
    unit_type = obs.feature_screen.unit_type
    relative = obs.feature_screen.player_relative

def get_mode_by_unit_type(unit_type):
    if unit_type == Terran.Barracks\
        or unit_type == Terran.Factory\
        or unit_type == Terran.Starport\
        or unit_type == Terran.CommandCenter:
        return (18, 18, 1)
    elif unit_type == Terran.SupplyDepot:
        return (9, 9, 1)
    elif unit_type == Terran.EngineeringBay\
        or unit_type == Terran.TechLab\
        or unit_type == Terran.Armory:
        return (13, 13, 1)