from z3tool import *

class phase:
    def __init__(self, delta, bv) -> None:
        self.delta = delta
        self.bv = bv

    def value(self):
        return self.delta*self.bv

    def multi(self, other):
        self.delta *= other.delta
        self.bv += other.bv

    def multiDelta(self, delta):
        self.delta*=delta

    def __str__(self) -> str:
        return str(self.delta, self.bv)

    def __repr__(self) -> str:
        return str(self)


def phaseMulti(a, b):
    return phase(a.delta * b.delta, a.bv + b.bv)

def sumPhaseMulti(a, b):
    '''
    multiplication of two sumPhase
    '''
    if not a or not b:
        return None
    phaselist = []
    for i in a.phases:
        for j in b.phases:
            phaselist.append(phaseMulti(i, j))
    return sumPhase(phaselist)

class sumPhase:
    def __init__(self, phases) -> None:
        self.phases = phases

    def z3exp(self):
        sumph = [p.value() for p in self.phases]
        return sum(sumph)

    def deltas(self):
        return sum([p.delta for p in self.phases])

    def multi(self, other):
        phase = []
        for i in self.phases:
            for j in other.phases:
                phase.append(phaseMulti(i, j))
        self.phases = phase

    def multiDelta(self, delta):
        for phase in self.phases:
            phase.multiDelta(delta)

def getSumPhase(phases):
    return sumPhase([phase(p[0],p[1]) for p in phases])

def leftMultiAlpha(compon, alpha, n, x, y):
    terms = sumPhase([])
    for z in compon.Mx(n,x):
        terms.phases+=sumPhaseMulti(compon.alpha(n, x, z), alpha(n, z, y)).phases
    return terms

def rightMultiAlpha(compon, alpha, n, x, y):
    '''
    multiply a sparse component on the right side of alpha
    '''
    terms = sumPhase([])
    for z in compon.My(n,y):
        terms.phases+=sumPhaseMulti(alpha(n, x, z),compon.alpha(n, z, y)).phases
    return terms

class Spec:
    def __init__(self) -> None:
        self.args = {}

    def alpha(self,n,x,y):
        raise NotImplementedError()
        