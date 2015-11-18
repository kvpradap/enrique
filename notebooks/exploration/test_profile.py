# impl1

import magellan as mg
def my_bb(l, r):
    t1 = l['title']
    t2 = r['title']
    res = mg.lev(t1, t2)
    if res < 0.6:
        return False
    else:
        return True

def fn1(A, B):
    x = []
    for i, l in A.iterrows():
        for j, r in B.iterrows():
            if my_bb(l, r) == True:
                x.append([i, j])
    return x

from collections import OrderedDict
def fn2(A, B):
    dA = OrderedDict()
    dB = OrderedDict()
    for i, l in A.iterrows():
        dA[i] = l
    for i, l in B.iterrows():
        dB[i] = l
    x = []
    for i in dA.keys():
        for j in dB.keys():
            a = dA[i]
            b = dB[j]
            if my_bb(a, b) == True:
                x.append([i, j])
    return x



