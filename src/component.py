from adt import *


class component:
    def __init__(self, name) -> None:
        self.name = name

    def alpha(self, n, x, y):
        return None

    def Mx(self):
        return None

    def My(self):
        return None

    def __str__(self) -> str:
        return self.name

class CRZ0N(component):
    def alpha(self, n, x, y):
        Eq = delta(BVtrunc(x, n), BVtrunc(y, n))
        return sumPhase([phase(Eq, BVref(x,0))])

    def Mx(self):
        return [lambda n,y : y]

    def My(self):
        return [lambda n,x : x]

class move1(component):
    def alpha(self, n, x, y):
        Eq = delta(BVtrunc(x, n-1), BVtrunc(y, n, 1)) * delta(BVref(y,0), bv(0))
        return sumPhase([phase(Eq, bv(0))])

    def Mx(self):
        return [lambda n,y : BVtrunc(y, n, 1), lambda n,y : BVtrunc(y, n, 1) | 1 << n]

    def My(self):
        return [lambda n,x : BVtrunc(x, n-1)<<1, lambda n,x : BVtrunc(x, n-1)<<1 | bv(1)]

class CRZN(component):
    def alpha(self, n, x, y):
        Eq = delta(BVtrunc(x, n-1), BVtrunc(y, n-1))
        d0 = Eq*delta(BVref(y, n), bv(0))
        d1 = Eq*delta(BVref(y, n), bv(1))
        return sumPhase([phase(d0, bv(0)), phase(d1, BVtrunc(x, n))])

    def Mx(self):
        return [lambda n, y: BVtrunc(y, n-1),
                lambda n, y: BVtrunc(y, n-1) | (bv(1) << n)]

    def My(self):
        return [lambda n, x: BVtrunc(x, n-1),
                lambda n, x: BVtrunc(x, n-1) | (bv(1) << n)]


class H0(component):
    def alpha(self, n, x, y):
        Eq = If(n > 0, delta(BVtrunc(x, n, 1), BVtrunc(y, n, 1)), bv(1))
        d0 = Eq*delta(BVref(y, 0), bv(0))
        d1 = Eq*delta(BVref(y, 0), bv(1))
        return sumPhase([phase(d0, bv(0)), phase(d1, BVref(x,0))])

    def Mx(self):
        return [lambda n, y: BVtrunc(y, n, 1) | bv(0),
                lambda n, y: BVtrunc(y, n, 1) | bv(1)]
    def My(self):
        return [lambda n, x: BVtrunc(x, n, 1) | bv(0),
                lambda n, x: BVtrunc(x, n, 1) | bv(1)]

class HN(component):
    def alpha(self, n, x, y):
        Eq = If(n > 0, delta(BVtrunc(x, n-1), BVtrunc(y, n-1)), bv(1))
        d0 = Eq*delta(BVref(y, n), bv(0))
        d1 = Eq*delta(BVref(y, n), bv(1))
        return sumPhase([phase(d0, bv(0)), phase(d1, BVref(x,n))])

    def Mx(self):
        return [lambda n, y: BVtrunc(y, n-1) | bv(0)<<n,
                lambda n, y: BVtrunc(y, n-1) | bv(1)<<n]
    def My(self):
        return [lambda n, x: BVtrunc(x, n-1) | bv(0)<<n,
                lambda n, x: BVtrunc(x, n-1) | bv(1)<<n]
