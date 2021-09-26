from z3 import *
from z3tool import *
import time


def Usn(n, x, y):
    return If(And(y >= 0, y < 2**n), 1, 0)


def z3Max(x, y):
    return If(x > y, x, y)


def z3Min(x, y):
    return If(x < y, x, y)


def spec(i, j, n):
    return If(And(i >= 0, j >= 0, i <= j), z3Min(j, 2**n-1) - z3Min(i, 2**n-1) + 1, 0)


def beta(n):
    return n


def z3H(x, y, n):
    return 2**(-0.5) * (delta(x, y) + delta(x + 2**(n-1), y))


def getD(f):
    n, d = Ints('n d')
    s = Solver()
    s.add(ForAll(
        [n],
        f(n-1) - f(n) == d
    ))
    if s.check() == sat:
        m = s.model()
        return m[d].as_long()
    else:
        print('Unsatisfied f')
        return None


def ladd(n):
    return If(n <= 1, 1, 1+ladd(n-1))


n = BitVec('n', MAXL)
z = Int('z')
s = Solver()
xb, yb = BitVecs('xb yb', 100)
l = 128
oracle = BitVec('o', l)
#
#s.add(spec(y,n) == 9)

x, y = BitVecs('x y', MAXL)
start = time.time()
s.add(0 < x, x < 10, 0 < y, y < 10)
#s.add(ForAll([oracle], OracleRef(oracle,x)==OracleRef(oracle,y)))
s.add(ForAll
      ([oracle],
       Implies(count(oracle, l) == l/2,
               OracleRef(oracle, x, l) != OracleRef(oracle, y, l))))

z3Show(s)
end = time.time()
print('use {0}s'.format(end-start))

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
