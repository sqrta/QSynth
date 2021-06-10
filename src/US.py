from z3 import *
from z3tool import *
from adt import *


def a_US(n, x, y):
    return sumPhase([phase(bv(1), bv(0))])


def b_US(n):
    return n + 1


def US(n, x, y):
    return sumPhase([phase(a_US(n, x, y), bv(0))])


def verify(alpha, target):
    x, y, n = BitVecs('x y n', MAXL)
    s = Solver()
    s.add(
        ForAll(
            [n, x, y], Implies(And(n >= 0, n < MAXL),
                               alpha(n, x, y) == target(n, x, y))
        )
    )



x, y, n = BitVecs('x y n', MAXL)
d0 = delta(BVtrunc(x, n-1), BVtrunc(y, n-1)) * delta(BVref(y,n), bv(0))
d1 = delta(BVtrunc(x, n-1), BVtrunc(y, n-1)) * delta(BVref(y,n), bv(1))
dn = delta(BVref(x,n), BVref(y,n))
s = Solver()
s.add(
    ForAll(
        [n, x, y], Implies(And(n > 0, n < MAXL),
                            a_US(n, x, y).z3exp() == dn*d0*a_US(n-1, BVtrunc(x, n-1), BVtrunc(y, n-1)).z3exp())
    )
)
z3Show(s)