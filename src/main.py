
import time
from z3tool import *
from qsynth import synthesis, StandardGateSet, PPSA

def QFTspec(n, x, y):
    u = BVtrunc(x, n)*reverse(BVtrunc(y, n), n)
    return [(bv(1), BVtrunc(u, n))]

def FullAdderSpec(n,x,y):
    Eq1 = delta(BVtrunc(x, 2*n, 1), BVtrunc(y, 2*n, 1))
    addone = BVtrunc(x, n, 1) + BVtrunc(x,2*n,n+1) + BVref(x,0)
    result = BVtrunc(y, 3*n, 2*n + 1) | BVref(y,0)<<n
    Eq2 = delta(BVtrunc(addone, n),  BVtrunc(result, n))
    return [(Eq1*Eq2, bv(0))]


def GHZspec(n, x, y):
    Eq = delta(BVtrunc(y,n), bv(0)) | delta(BVtrunc(y,n), (bv(1)<<(n+1)) -1)
    return [(Eq, bv(0))]

def IDspec(n,x,y):
    return [(delta(x,y), bv(0))]

def rippleAdderSpec(n,x,y):
    Eq1 = delta(BVtrunc(x, n), BVtrunc(y, n))
    add = BVtrunc(x, n, 1) + BVtrunc(x,2*n,n+1) + BVref(x,0)
    result = BVtrunc(y, 2*n, n + 1)
    Eq2 = delta(BVtrunc(add, n),  BVtrunc(result, n))
    return [(Eq1*Eq2, bv(0))]

def filewrite(string, path):
    with open(path, 'w') as f:
        f.write(string)

if __name__ == "__main__":
    # base gate for synthesis

    start = time.time()
    spec = PPSA(beta=lambda n: 1, phaseSum=rippleAdderSpec)
    prog = synthesis(spec, StandardGateSet, hypothesis =lambda n,x,y : BVref(x,0)==0)
    end =time.time()
    print(f'RippleAdder case uses {end-start}s')
    filewrite(prog.toQiskit('RippleAdder'), 'RippleAdder.py')

    start = time.time()
    spec = PPSA(beta=lambda n: 2, phaseSum=GHZspec)
    prog = synthesis(spec, StandardGateSet, hypothesis = lambda n,x,y : x==bv(0))
    end =time.time()
    print(f'GHZ case uses {end-start}s')
    filewrite(prog.toQiskit('GHZ'), 'GHZ.py')

    start = time.time()
    spec = PPSA(beta=lambda n: 1, phaseSum=FullAdderSpec)
    prog = synthesis(spec, StandardGateSet, hypothesis = lambda n,x,y : And(BVref(x,0)==0, ULT(x, bv(1)<<2*n+1)))
    end =time.time()
    print(f'FullAdder case uses {end-start}s')
    filewrite(prog.toQiskit('FullAdder'), 'FullAdder.py')

    start = time.time()
    spec = PPSA(beta=lambda n: 2<<n, phaseSum=QFTspec)
    prog = synthesis(spec, StandardGateSet, hypothesis = lambda n,x,y : And(ULT(x,(bv(2)<<n)), ULT(y, (bv(2)<<n))))
    end =time.time()
    print(f'QFT case uses {end-start}s')
    filewrite(prog.toQiskit('QFT'), 'QFT.py')