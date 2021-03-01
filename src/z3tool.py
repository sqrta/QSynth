
from z3 import *

MAXL = 16
SPACE = int(MAXL/2)

def z3Show(s):
    t=s.check()
    print(t)
    if t == sat:
        print(s.model())

def BVtrunc(vec, upper, lower=0):
    '''
    return vec[lower: upper](include upper) still has the same length as vec
    '''
    return LShR((vec << (MAXL - upper - 1)), (MAXL - upper - 1 + lower))


def BVref(vec, index):
    return BVtrunc(vec, index, index)


def delta(a, b):
    return If(a == b, BitVecVal(1, MAXL), BitVecVal(0, MAXL))

def BVsum(f,n,init=0):
    bvSum = RecFunction('bvSum', BitVecSort(MAXL), BitVecSort(MAXL))
    RecAddDefinition(bvSum, n, If(n>0, f(n)+bvSum(n-1), BitVecVal(init,MAXL)))
    return bvSum

def bv(a):
    return BitVecVal(a, MAXL)