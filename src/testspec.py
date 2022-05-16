from z3 import *
from z3tool import *
import time

n, x, y = BitVecs('n x y', MAXL)

s=Solver()
Eq = If(n >= 1, delta(BVtrunc(x, n-1), BVtrunc(y, n-1)), bv(1))
Eq = Eq*delta(BVref(y, n), BVref(y,n-1) ^ BVref(x,n))
s.add(Eq==1, n<=SPACE, n==1, x==2)
print(s.check())
bvprint(s.model(), y, 'y')
bvprint(s.model(), x, 'x')