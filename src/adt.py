from z3tool import *

def bvprint(model, a, msg=""):
    if not model:
        return
    tmp = model.evaluate(a).as_binary_string()
    print(tmp, len(tmp), msg)

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

    def multi(self, other):
        phase = []
        for i in self.phases:
            for j in other.phases:
                phase.append(phaseMulti(i, j))
        self.phases = phase

    def multiDelta(self, delta):
        for phase in self.phases:
            phase.multiDelta(delta)

