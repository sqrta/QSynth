
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

def reverse(vec, n=MAXL-1):
    b= vec
    '''
    b = LShR(b & 0xffff0000 ,16) | ((b & 0x0000ffff) << 16)
    b= LShR(b & 0xff00ff00, 8) | ((b & 0x00ff00ff) << 8)
    b = LShR(b & 0xf0f0f0f0, 4) | ((b & 0x0f0f0f0f) << 4)
    b = LShR(b & 0xcccccccc,2) | ((b & 0x33333333) << 2)
    b = LShR(b & 0xaaaaaaaa,1) | ((b & 0x55555555) << 1)
    '''
    b= LShR(b & 0xff00, 8) | ((b & 0x00ff) << 8)
    b = LShR(b & 0xf0f0, 4) | ((b & 0x0f0f) << 4)
    b = LShR(b & 0xcccc,2) | ((b & 0x3333) << 2)
    b = LShR(b & 0xaaaa,1) | ((b & 0x5555) << 1)
    return BVtrunc(b, MAXL-1, MAXL-n-1)

def foo(vec):
    tmp = vec
    a=12
    for i in range(a):
        tmp = tmp + 1
    return tmp

if __name__ == '__main__':
    s = Solver()
    x = BitVec('x', MAXL)
    solve(reverse(x,6)==0xf)
