
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
    BVtrunc(01101, 2, 1) = 00010 (01 "10" 1)
    BVtrunc(01101, 3, 2) = 00011 (0 "11" 01)
    '''
    return LShR((vec << (MAXL - upper - 1)), (MAXL - upper - 1 + lower))


def BVref(vec, index):
    '''
    return vec[index]. still has the same length as vec. 
    BVref(00100, 2) = 00001
    BVref(00100, 3) = 00000
    '''
    return BVtrunc(vec, index, index)


def delta(a, b):
    return If(a == b, BitVecVal(1, MAXL), BitVecVal(0, MAXL))

def BVsum(f,n,init=0):
    bvSum = RecFunction('bvSum', BitVecSort(MAXL), BitVecSort(MAXL))
    RecAddDefinition(bvSum, n, If(n>0, f(n)+bvSum(n-1), BitVecVal(init,MAXL)))
    return bvSum

def bv(a):
    return BitVecVal(a, MAXL)