
import time
from z3tool import *
from qsynth import synthesis, StandardGateSet, PPSA, Input, getSpec, SumVarClaim,SumExpr, OutputIndex
from component import *

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
    c0, A, B, C, intervals = Input(x, [1,n,n,n])
    sum = A+B+c0
    Output = [BVref(sum, n), A, B,  BVtrunc(sum, n-1)]
    return getSpec(y, intervals, Output)

def GHZspec(n, x, y):
    Eq = Equal(BVtrunc(y,n), bv(0)) | Equal(BVtrunc(y,n), (bv(1)<<(n+1)) -1)
    return [(Eq, bv(0))]

def IDspec(n,x,y):
    return [(Equal(x,y), bv(0))]

def RipAddSpec(n,x,y):
    c0, A, B, intervals = Input(x, [1,n,n])
    Output = [c0, A, A+B+c0]
    return getSpec(y, intervals, Output)

def stack_ww(n, x, y):
    Eq0 = Equal(BVref(x,0), BVref(y,0))
    Eq = Equal(BVtrunc(y, n, 1), BVtrunc(y, 2*n, n+1))
    return [(Eq0*Eq, bv(0))]

def RipSubSpec(n,x,y):
    c0, A, B, intervals = Input(x, [1,n,n])
    Output = [c0, A, B-A-c0]
    return getSpec(y, intervals, Output)

c = 4

def inversionSpec(n,x,y): 
    Eq1 = Equal(BVtrunc(x,c,0), BVtrunc(y,c,0))
    r = BVtrunc(y,2*c-1, c+1)
    quet = BVtrunc(y,2*c+n-1, 2*c)
    lamb = BVtrunc(x,c-1,1)
    Eq2 = Equal(bv(1)<<(n-1), quet*lamb+r)
    return [(Eq1*Eq2, bv(0))]

def teleportation(n,x,y):
    c0, phi, zero1, zero2, intervals = Input(x, [1,n,n,n])
    z = SumVarClaim(n,x,y, [1,3*n])
    expr = SumExpr(BVtrunc(z, 2*n-1, n)==BVtrunc(phi,n-1) ^ BVtrunc(z,3*n-1,2*n), BVtrunc(z, n-1))
    Output = [c0, expr]
    intervals = OutputIndex([1, 3*n])
    return getSpec(y, intervals, Output)

# Toffoli gate with n+1 control qubits
def toff_nPlus1(n,x,y):
    control = BVReductAnd(x, n)
    Eq = Equal(BVref(y,2*n), control ^ BVref(x, 2*n))
    BaseEq = Equal(BVtrunc(x,n), BVtrunc(y,n))
    return [(Eq*BaseEq, bv(0))]

def Even_num(n, x, y):
    Eq = Equal(BVref(y,0), bv(0))
    return [(Eq, bv(0))]

def Odd_num(n, x, y):
    Eq = Equal(BVref(y,0), bv(1))
    return [(Eq, bv(0))]

def Uniform(n, x, y):
    return [(bv(1), bv(0))]

def filewrite(string, path):
    with open(path, 'w') as f:
        f.write(string)

if __name__ == "__main__":

    start = time.time()
    spec = PPSA(beta=lambda n: 2<<(n-1), phaseSum=Even_num)
    prog = synthesis(spec, StandardGateSet, hypothesis =lambda n,x,y : And(BVtrunc(x,n)==0))
    end =time.time()
    print(f'Even case uses {end-start}s')
    filewrite(prog.toQiskit('Even'), 'Even.py')

    start = time.time()
    spec = PPSA(beta=lambda n: 2<<(n-1), phaseSum=Odd_num)
    prog = synthesis(spec, StandardGateSet, hypothesis =lambda n,x,y : And(BVtrunc(x,n)==0))
    end =time.time()
    print(f'Odd case uses {end-start}s')
    filewrite(prog.toQiskit('Odd'), 'Odd.py')

    start = time.time()
    spec = PPSA(beta=lambda n: 2<<n, phaseSum=stack_ww)
    prog = synthesis(spec, StandardGateSet, hypothesis =lambda n,x,y : And(BVtrunc(x,2*n)==0, n>0))
    end =time.time()
    print(f'stack_ww case uses {end-start}s')
    filewrite(prog.toQiskit('stack_ww'), 'Stack_ww.py')

    start = time.time()
    spec = PPSA(beta=lambda n: 2, phaseSum=GHZspec)
    prog = synthesis(spec, StandardGateSet, hypothesis = lambda n,x,y : x==bv(0))
    end =time.time()
    print(f'GHZ case uses {end-start}s')
    filewrite(prog.toQiskit('GHZ'), 'GHZ.py')


    start = time.time()
    spec = PPSA(beta=lambda n: 1, phaseSum=teleportation)
    prog = synthesis(spec, StandardGateSet, hypothesis =lambda n,x,y : And(BVtrunc(x,3*n, n+1)==0, n>1))
    end =time.time()
    print(f'Teleportation case uses {end-start}s')
    filewrite(prog.toQiskit('Teleportation'), 'Teleportation.py')

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

    caseSet = [MAJ("maj"), UMA("uma")]
    start = time.time()
    spec = PPSA(beta=lambda n: 1, phaseSum=RipAddSpec)
    prog = synthesis(spec, caseSet+StandardGateSet, hypothesis =lambda n,x,y : BVref(x,0)==0)
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
    spec = PPSA(beta=lambda n: 1, phaseSum=toff_nPlus1)
    prog = synthesis(spec, StandardGateSet, hypothesis =lambda n,x,y : And(BVtrunc(x,2*n-1,n+1)==0, n>0,BVref(y,2*n-1)==BVReductAnd(x, n-1)), base=2)
    end =time.time()
    print(f'ToffoliN case uses {end-start}s')
    filewrite(prog.toQiskit('ToffoliN'), 'ToffoliN.py')

    caseSet = [CRZN("Zn", [Index(1)]),]
    start = time.time()
    spec = PPSA(beta=lambda n: 2<<n, phaseSum=QFTspec)
    prog = synthesis(spec, caseSet + StandardGateSet, hypothesis = lambda n,x,y : True)
    end =time.time()
    print(f'QFT case uses {end-start}s')
    filewrite(prog.toQiskit('QFT'), 'QFT.py')  
    
    caseSet = [[Subtractor('sub', params={'c':c}), Cadder('cadd', params={'c':c}), X('x')]]
    start = time.time()
    spec = PPSA(beta=lambda n: 1, phaseSum=inversionSpec)
    prog = synthesis(spec, caseSet+StandardGateSet, hypothesis = lambda n,x,y : And(n>0,BVtrunc(x,2*c+n-1,c)==(bv(1)<<(c+n))))
    end =time.time()
    print(f'inversion case uses {end-start}s')
    filewrite(prog.toQiskit('Inversion', offset=2*c), 'Inversion.py')      


