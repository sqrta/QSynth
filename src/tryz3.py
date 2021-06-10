from z3 import *
from z3tool import *


def Usn(n, x, y):
    return If(And(y >= 0, y < 2**n), 1, 0)


def z3Max(x, y):
    return If(x > y, x, y)


def z3Min(x, y):
    return If(x < y, x, y)


def spec(i, j, n):
    return If(And(i >= 0, j >= 0, i<=j), z3Min(j, 2**n-1) - z3Min(i, 2**n-1) + 1, 0) 

def beta(n):
    return n

def z3H(x, y, n):
    return 2**(-0.5) * (delta(x, y) + delta(x + 2**(n-1), y))


def getD(f):
    n,d = Ints('n d')
    s=Solver()
    s.add(ForAll(
        [n],
        f(n-1) - f(n) == d
    ))
    if s.check() == sat:
        m=s.model()
        return m[d].as_long()
    else:
        print('Unsatisfied f')
        return None

def ladd(n):
    return If(n<=1, 1, 1+ladd(n-1))

n = BitVec('n', MAXL)
z = Int('z')
s = Solver()
xb, yb = BitVecs('xb yb',100)
#
#s.add(spec(y,n) == 9)
x, y = BitVecs('x y', MAXL)
solve(x>>4==y)

g = BVsum(lambda m: BVref(bv(0), m), n)
bvSum = RecFunction('bvSum', BitVecSort(MAXL), BitVecSort(MAXL))
f= Function('f', BitVecSort(MAXL), BitVecSort(MAXL))
RecAddDefinition(bvSum, n, If(n > 0, BVref(x, n)+bvSum(n-1), BitVecVal(0, MAXL)))
s.add(x>0)
s.add(ForAll(
    [n], n + n == x*n
    ))
z3Show(s)
'''
y = BV2Int(yb)
x = BV2Int(xb)
s.add(ForAll([z],
    Implies(And(z>0, z<10),
    LShR(yb,3)==1
    )))
'''
    
'''
dis = getD(beta)
tmp = y-2**(n-1)
s.add(ForAll([yb, n],
             Implies(And(n < 100, n > 0, y < 2**n, y >= 0),
                     2**(0.5 * dis) * spec(y, y, n) == (spec(y, y, n-1) *
                                                   z3H(y, y, n) + spec(tmp, tmp, n-1)) * z3H(tmp, tmp, n)
                     )
             ))
'''
