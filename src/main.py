
import time
from z3tool import *
from qsynth import synthesis, StandardGateSet, PPSA
from component import Subtractor,Cadder

def QFTspec(n, x, y):
    u = BVtrunc(x, n)*reverse(BVtrunc(y, n), n)
    return [(bv(1), BVtrunc(u, n))]

def FullAdderSpec(n,x,y):
    Eq1 = Equal(BVtrunc(x, 2*n, 1), BVtrunc(y, 2*n, 1))
    addone = BVtrunc(x, n, 1) + BVtrunc(x,2*n,n+1) + BVref(x,0)
    result = BVtrunc(y, 3*n, 2*n + 1) | BVref(y,0)<<n
    Eq2 = Equal(BVtrunc(addone, n),  BVtrunc(result, n))
    return [(Eq1*Eq2, bv(0))]


def GHZspec(n, x, y):
    Eq = Equal(BVtrunc(y,n), bv(0)) | Equal(BVtrunc(y,n), (bv(1)<<(n+1)) -1)
    return [(Eq, bv(0))]

def IDspec(n,x,y):
    return [(Equal(x,y), bv(0))]

def rippleAdderSpec(n,x,y):
    Eq1 = Equal(BVtrunc(x, n, 0), BVtrunc(y, n, 0))
    add = BVtrunc(x, n, 1) + BVtrunc(x,2*n,n+1) + BVref(x,0)
    result = BVtrunc(y, 2*n, n + 1)
    Eq2 = Equal(BVtrunc(add, n),  BVtrunc(result, n))
    return [(Eq1*Eq2, bv(0))]

def rippleSubtractSpec(n,x,y):
    Eq1 = Equal(BVtrunc(x, n, 0), BVtrunc(y, n, 0))
    add =  BVtrunc(x,2*n,n+1) - BVtrunc(x, n, 1) - BVref(x,0)
    result = BVtrunc(y, 2*n, n + 1)
    Eq2 = Equal(BVtrunc(add, n-1),  BVtrunc(result, n-1))
    return [(Eq1*Eq2, bv(0))]

c = 4

def inversionSpec(n,x,y): 
    Eq1 = Equal(BVtrunc(x,c,0), BVtrunc(y,c,0))
    r = BVtrunc(y,2*c-1, c+1)
    quet = BVtrunc(y,2*c+n-1, 2*c)
    lamb = BVtrunc(x,c-1,1)
    Eq2 = Equal(bv(1)<<(n-1), quet*lamb+r)
    return [(Eq1*Eq2, bv(0))]


def filewrite(string, path):
    with open(path, 'w') as f:
        f.write(string)

if __name__ == "__main__":  

    start = time.time()
    spec = PPSA(beta=lambda n: 2<<n, phaseSum=QFTspec)
    prog = synthesis(spec, StandardGateSet, hypothesis = lambda n,x,y : True)
    end =time.time()
    print(f'QFT case uses {end-start}s')
    filewrite(prog.toQiskit('QFT'), 'QFT.py')

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
    prog = synthesis(spec, StandardGateSet, hypothesis = lambda n,x,y : And(BVref(x,0)==0))
    end =time.time()
    print(f'FullAdder case uses {end-start}s')
    filewrite(prog.toQiskit('FullAdder'), 'FullAdder.py')

    start = time.time()
    spec = PPSA(beta=lambda n: 1, phaseSum=rippleSubtractSpec)
    prog = synthesis(spec, StandardGateSet, hypothesis =lambda n,x,y : BVref(x,0)==0)
    end =time.time()
    print(f'RippleSubtractor case uses {end-start}s')
    filewrite(prog.toQiskit('RippleSubtractor'), 'RippleSubtractor.py')
    
    # Insert the c-qubit subtractor and conditional adder into the gateset
    GateSet = [Subtractor('sub', params={'c':c}), Cadder('c-add', params={'c':c})] + StandardGateSet
    start = time.time()
    spec = PPSA(beta=lambda n: 1, phaseSum=inversionSpec)
    prog = synthesis(spec, GateSet, hypothesis = lambda n,x,y : And(n>0,BVtrunc(x,2*c+n-1,c)==(bv(1)<<(c+n))))
    end =time.time()
    print(f'inversion case uses {end-start}s')
    filewrite(prog.toQiskit('inversion'), 'inversion.py')  