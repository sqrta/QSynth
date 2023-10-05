
import time
from z3tool import *
from qsynth import synthesis, StandardGateSet, PPSA, varDef, getSpec
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

def FullAddSpec(n,x,y):
    c0, A, B, C, intervals = varDef(x, [1,n,n,n])
    sum = A+B+c0
    Output = [BVref(sum, n), A, B,  BVtrunc(sum, n-1)]
    return getSpec(y, intervals, Output)

def GHZspec(n, x, y):
    Eq = Equal(BVtrunc(y,n), bv(0)) | Equal(BVtrunc(y,n), (bv(1)<<(n+1)) -1)
    return [(Eq, bv(0))]

def IDspec(n,x,y):
    return [(Equal(x,y), bv(0))]

def RipAddSpec(n,x,y):
    c0, A, B, intervals = varDef(x, [1,n,n])
    Output = [c0, A, A+B+c0]
    return getSpec(y, intervals, Output)

def RipSubSpec(n,x,y):
    c0, A, B, intervals = varDef(x, [1,n,n])
    Output = [c0, A, B-A-c0]
    return getSpec(y, intervals, Output)


def cAdderSpec(n,x,y):
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

def teleportation(n,x,y):
    Eqbase = Equal(BVref(x,0), BVref(y,0))
    result = BVtrunc(x,n,1) ^ BVtrunc(y,3*n,2*n+1)
    Eq = Equal(result, BVtrunc(y,2*n,n+1))
    phase = BVtrunc(x, n, 1)
    return [(Eqbase*Eq, phase)]

# Toffoli gate with n+1 control qubits
def toff_nPlus1(n,x,y):
    control = BVReductAnd(x, n)
    Eq = Equal(BVref(y,2*n), control ^ BVref(x, 2*n))
    BaseEq = Equal(BVtrunc(x,n), BVtrunc(y,n))
    return [(Eq*BaseEq, bv(0))]

def Uniform(n, x, y):
    return [(bv(1), bv(0))]

def filewrite(string, path):
    with open(path, 'w') as f:
        f.write(string)

if __name__ == "__main__":

    start = time.time()
    spec = PPSA(beta=lambda n: 2, phaseSum=GHZspec)
    prog = synthesis(spec, StandardGateSet, hypothesis = lambda n,x,y : x==bv(0))
    end =time.time()
    print(f'GHZ case uses {end-start}s')
    filewrite(prog.toQiskit('GHZ'), 'GHZ.py')

    start = time.time()
    spec = PPSA(beta=lambda n: 1, phaseSum=Uniform)
    prog = synthesis(spec, StandardGateSet, hypothesis =lambda n,x,y : And(BVtrunc(x,n)==0))
    end =time.time()
    print(f'Uniform case uses {end-start}s')
    filewrite(prog.toQiskit('Uniform'), 'Uniform.py')

    start = time.time()
    spec = PPSA(beta=lambda n: 1, phaseSum=FullAddSpec)
    prog = synthesis(spec, StandardGateSet, hypothesis = lambda n,x,y : And(BVref(x,0)==0))
    end =time.time()
    print(f'FullAdder case uses {end-start}s')
    filewrite(prog.toQiskit('FullAdder'), 'FullAdder.py')

    start = time.time()
    spec = PPSA(beta=lambda n: 1, phaseSum=RipAddSpec)
    prog = synthesis(spec, StandardGateSet, hypothesis =lambda n,x,y : BVref(x,0)==0)
    end =time.time()
    print(f'RippleAdder case uses {end-start}s')
    filewrite(prog.toQiskit('RippleAdder'), 'RippleAdder.py')

    start = time.time()
    spec = PPSA(beta=lambda n: 1, phaseSum=RipSubSpec)
    prog = synthesis(spec, StandardGateSet, hypothesis =lambda n,x,y : BVref(x,0)==0)
    end =time.time()
    print(f'RippleSubtractor case uses {end-start}s')
    filewrite(prog.toQiskit('RippleSubtractor'), 'RippleSubtractor.py')

    start = time.time()
    spec = PPSA(beta=lambda n: 1, phaseSum=cAdderSpec)
    prog = synthesis(spec, StandardGateSet, hypothesis =lambda n,x,y : BVref(x,0)==0)
    end =time.time()
    print(f'Cond-Adder case uses {end-start}s')
    filewrite(prog.toQiskit('CondAdder', offset=2), 'CondAdder.py')

    start = time.time()
    spec = PPSA(beta=lambda n: 1, phaseSum=toff_nPlus1)
    prog = synthesis(spec, StandardGateSet, hypothesis =lambda n,x,y : And(BVtrunc(x,2*n-1,n+1)==0, n>0,BVref(y,2*n-1)==BVReductAnd(x, n-1)), base=2)
    end =time.time()
    print(f'ToffoliN case uses {end-start}s')
    filewrite(prog.toQiskit('ToffoliN'), 'ToffoliN.py')

    start = time.time()
    spec = PPSA(beta=lambda n: 2<<n, phaseSum=QFTspec)
    prog = synthesis(spec, StandardGateSet, hypothesis = lambda n,x,y : True)
    end =time.time()
    print(f'QFT case uses {end-start}s')
    filewrite(prog.toQiskit('QFT'), 'QFT.py')  
    
    # Insert the c-qubit subtractor and conditional adder into the gateset
    GateSet = [Subtractor('sub', params={'c':c}), Cadder('c-add', params={'c':c})] + StandardGateSet
    start = time.time()
    spec = PPSA(beta=lambda n: 1, phaseSum=inversionSpec)
    prog = synthesis(spec, GateSet, hypothesis = lambda n,x,y : And(n>0,BVtrunc(x,2*c+n-1,c)==(bv(1)<<(c+n))))
    end =time.time()
    print(f'inversion case uses {end-start}s')
    filewrite(prog.toQiskit('inversion', offset=2*c), 'Inversion.py')      

    start = time.time()
    spec = PPSA(beta=lambda n: 1, phaseSum=teleportation)
    prog = synthesis(spec, StandardGateSet, hypothesis =lambda n,x,y : And(BVtrunc(x,3*n, n+1)==0, n>1))
    end =time.time()
    print(f'Teleportation case uses {end-start}s')
    filewrite(prog.toQiskit('Teleporation'), 'Teleporation.py')
