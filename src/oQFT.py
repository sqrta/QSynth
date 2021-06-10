from z3 import *
from z3tool import *


def C_RZN(t, x, y, n, m):
    truncEq = delta(BVtrunc(x, t-1), BVtrunc(y, t-1))
    cond = truncEq * delta(BVref(y, t), 1) * (BVtrunc(x, t, t-n) << (m-n-1))
    return cond


def C_RZ(y, t, n, m):
    return delta(BVref(y, t), 1)*(BVref(y, t-n) << (m-n-1))


def QFT(x, y, n, m):
    u = BVtrunc(x, n)*BVtrunc(y, m, m-n)
    return BVtrunc(u, n) << (m-n)


def QFTfr(x, y, n, m):
    return delta(BVref(x, n+1), BVref(y, m-n))


x, y, n, t, i, m = BitVecs('x y n t i m', MAXL)
truncEq = delta(BVtrunc(x, t-1), BVtrunc(y, t-1))

#d0 = delta(BVtrunc(x, n-1), BVtrunc(y, n-1)) * delta(BVref(y, n), bv(0))
#d1 = delta(BVtrunc(x, n-1), BVtrunc(y, n-1)) * delta(BVref(y, n), bv(1))

s = Solver()
s.push()
s.add(ForAll(
    [t, x, y, i, n], Implies(And([n > 2, n <= SPACE, 0 < i, i <= t, t < n]),
                             C_RZN(t, x, y, i, n) == C_RZN(
                                 t, x, y, i-1, n) + truncEq*C_RZ(y, t, i, n)
                             )
))

z3Show(s)
s.pop()
s.push()
x1 = x | (bv(1) << (n+1))
x0 = x & ~(bv(1) << (n+1))
left0 = QFT(x, y, n-1, m)
left1 = left0 + (BVtrunc(x, n) << (m-n))
left = QFT(x, y, n, m)
right = QFTfr(x0, y, n, m) * left0 + QFTfr(x1, y, n, m) * left1
'''
left = QFT(x,y,n,m)
right = delta(bv(0), BVref(y,m-n))*QFT(x, y, n-1, m) + delta(bv(1), BVref(y,m-n))*(QFT(x, y, n-1, m) + BVtrunc(x, n) << (m-n))
right0 = BVtrunc(BVtrunc(x, n) * ((BVtrunc(y, m, m-n+1) << 1)), n) << (m-n)
right1 = BVtrunc(BVtrunc(x, n) * ((BVtrunc(y, m, m-n+1) << 1)+1 ), n) << (m-n)

'''
s.add(ForAll(
    [x, y, n, m], Implies(And(m > 2, m < SPACE, 0 < n, n < m-1),
                          BVtrunc(left, m) == BVtrunc(right, m)
                          )
))
z3Show(s)
# s.add(BVtrunc(x,4,2)==3) delta(bv(0), BVref(y,m-n))*QFT(x, y, n-1, m) + delta(bv(1), BVref(y,m-n))*(QFT(x, y, n-1, m) + (BVtrunc(x, n+1) << (m-n) ))

'''
g = BVsum(lambda m: BVref(bv(0), m), i)
bvSum = RecFunction('bvSum', BitVecSort(MAXL), BitVecSort(MAXL))
RecAddDefinition(bvSum, n, If(n > 0, BVref(
    x, n)+bvSum(n-1), BitVecVal(0, MAXL)))
s.add(ForAll(
    [n], Implies(And(n<10,n>4, x>=0,x<10), bvSum(n)==0)
))'''
