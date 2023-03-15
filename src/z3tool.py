
from functools import reduce
from z3 import *

MAXL = 16
SPACE = 10
ORACLEL = 2**SPACE

def z3Show(s):
    t=s.check()
    print(t)
    if t == sat:
        print(s.model())

def BVtrunc(vec, upper, lower=0, length = MAXL):
    '''
    return vec[lower: upper](include upper) still has the same length as vec
    BVtrunc(01101, 2, 1) = 00010 (01 "10" 1)
    BVtrunc(01101, 3, 2) = 00011 (0 "11" 01)
    '''
    try:
        correctr = LShR((vec << (length - upper - 1)), (length - upper - 1 + lower))
    except:
        print(vec, length, upper, lower)
        exit(0)
    return (If(upper>= lower, correctr, bv(0,length)))

def BVReductAnd(vec,n):
    one = RepeatBitVec(MAXL, BitVecVal(1, 1)) 
    return BVReductOr(vec ^ one, n) ^ bv(1)
    
def BVReductOr(vec, n):
    return Concat(RepeatBitVec(MAXL-1, BitVecVal(0, 1)), BVRedOr(BVtrunc(vec,n)))

def BVref(vec, index, length = MAXL):
    '''
    return vec[index]. still has the same length as vec. 
    BVref(00100, 2) = 00001
    BVref(00100, 3) = 00000
    '''
    return BVtrunc(vec, index, index, length)

def OracleRef(vector, index, length = ORACLEL):
    newIndex = ZeroExt(length - MAXL,index)
    return BVref(vector, newIndex, length)

def Equal(a, b):
    return If(a == b, BitVecVal(1, MAXL), BitVecVal(0, MAXL))

def bvalue(term):
    return If(term, BitVecVal(1, MAXL), BitVecVal(0, MAXL))

def nEqual(a, b):
    return If(a != b, BitVecVal(1, MAXL), BitVecVal(0, MAXL))

def BVsum(f,n,init=0):
    bvSum = RecFunction('bvSum', BitVecSort(MAXL), BitVecSort(MAXL))
    RecAddDefinition(bvSum, n, If(n>0, f(n)+bvSum(n-1), BitVecVal(init,MAXL)))
    return bvSum

def bv(a, length = MAXL):
    try:
        return BitVecVal(a, length)
    except:
        print(a, length)
        exit(0)

def reverse(vec, n=MAXL-1):
    b= vec
    if MAXL == 32:
        b = LShR(b & 0xffff0000 ,16) | ((b & 0x0000ffff) << 16)
        b= LShR(b & 0xff00ff00, 8) | ((b & 0x00ff00ff) << 8)
        b = LShR(b & 0xf0f0f0f0, 4) | ((b & 0x0f0f0f0f) << 4)
        b = LShR(b & 0xcccccccc,2) | ((b & 0x33333333) << 2)
        b = LShR(b & 0xaaaaaaaa,1) | ((b & 0x55555555) << 1)
    elif MAXL == 16:
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

def bvprint(model, a, msg=""):
    if not model:
        return
    result = model.evaluate(a)
    if isinstance(result, BoolRef):
        print(result, msg)
    else:
        tmp = result.as_binary_string()
        print(tmp, len(tmp), msg)

def mask(x, numlist):
    vec = reduce(lambda a,b : a | b, [bv(1)<<i for i in numlist])
    return x& (~vec)

def count(vector,length):
    counter = 0
    # expr = '\n'.join(['counter+=ZeroExt(MAXL-1, Extract({0},{0},vector))'.format(i) for i in range(ORACLEL)])
    # print(expr)
    # exec(expr)
    for i in range(length):
        counter += ZeroExt(length-1, Extract(i,i,vector))
    return counter

def xorSum(x,y,length=MAXL):
    return BVref(count(x^y, length), 0)

def andSum(x,y,length=MAXL):
    return BVref(count(x&y, length), 0)

def setZero(x,high,low):
    tunc = BVtrunc(x,high,low)<<low
    return x ^ tunc

def setVec(x, y, high, low):
    return setZero(x, high, low) ^ BVtrunc(y << low, high)

if __name__ == '__main__':
    s = Solver()
    x,y,z = BitVecs('x y z', MAXL)
    
    solve(y==0b1111,z==0b01, x==setVec(y,z, 1, 0))
