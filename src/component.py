from adt import *
import itertools
from functools import reduce


def findsubsets(s, n):
    return list(itertools.combinations(s, n))


def allsubset(s):
    return reduce(lambda a, b: a+b, [findsubsets(s, i) for i in range(len(s)+1)])

def getIndexValue(index, n):
    if isinstance(index, Index):
        return index.value(n)
    else:
        return index
Uo = BitVec('f', MAXL)


class component:
    def __init__(self, name, registers=None, params=None) -> None:
        self.name = name
        self.params = params
        if not registers:
            self.registers = []
        else:
            self.registers = registers

    def getName(self):
        return self.name

    def qiskitName(self):
        return self.name

    def alpha(self, n, x, y):
        return None
    
    def claim(self):
        return False
    
    def source(self):
        return None

    def prog(self):
        return None
    
    def call(self):
        return None,None

    def Mx(self, n, x):
        raise(self.name+" does not have Mx")

    def decompose(self):
        return self
    
    def control(self, ctrl):
        return self

    def My(self, n, y):
        raise(self.name+" does not have My")
    
    def expandIndex(self, k=1):
        return [self]

    def __str__(self) -> str:
        return self.name


class CRZ0N(component):
    def alpha(self, n, x, y):
        Eq = Equal(BVtrunc(x, n), BVtrunc(y, n))
        return sumPhase([phase(Eq, BVref(x, 0))])

    def My(self, n, y):
        return [y]

    def Mx(self, n, x):
        return [x]


def decompose(gate):
    return gate.decompose()


class move1(component):
    def alpha(self, n, x, y):
        Eq = Equal(BVtrunc(x, n-1), BVtrunc(y, n, 1)) * \
            Equal(BVref(y, 0), bv(0))
        return getSumPhase([(Eq, bv(0))])

    def My(self, n, y):
        return [BVtrunc(y, n, 1), BVtrunc(y, n, 1) | 1 << n]

    def Mx(self, n, x):
        return [BVtrunc(x, n-1) << 1, BVtrunc(x, n-1) << 1 | bv(1)]


class CRZN(component):
    def alpha(self, n, x, y):
        Eq = Equal(BVtrunc(x, n-1), BVtrunc(y, n-1))
        d0 = Eq*Equal(BVref(y, n), bv(0))
        d1 = Eq*Equal(BVref(y, n), bv(1))
        return getSumPhase([(d0, bv(0)), (d1, BVtrunc(x, n))])

    def My(self, n, y):
        return [BVtrunc(y, n-1),
                BVtrunc(y, n-1) | (bv(1) << n)]

    def Mx(self, n, x):
        return [BVtrunc(x, n-1),
                BVtrunc(x, n-1) | (bv(1) << n)]

    def claim(self):
        return True

    def prog(self):
        return ISQIR({'base':[HN('h', [Index(1)])], 'inductive':([Ident('I')],[CRZ0N('cp', ['pi/2**n', Index(2, rev=True), Index(0)])])}, name='Zn')
    
    def call(self):
        size = Index(1)
        arg = f"range({Index(1,1)})"
        return size,arg


class Swap(component):
    def alpha(self, n, x, y):
        Eq = Equal(x, y)
        return getSumPhase([(Eq, bv(0))])

    def Mx(self, n, z):
        return [z]

    def My(self, n, z):
        return [z]

    def qiskitName(self):
        return "swap"


class Toffolin(component):
    def alpha(self, n, x, y):
        Eq1 = Equal(mask(x, [2*n]), mask(y, [2*n]))
        result = (BVref(x,n) & BVref(x, 2*n-1)) ^ BVref(x, 2*n)
        Eq2 = Equal(BVref(y,2*n), result)
        return getSumPhase([(Eq1*Eq2, bv(0))])

    def Mx(self, n, x):
        qubits = {2*n}
        return setbit(x, qubits)
    
    def My(self, n, y):
        return self.Mx(n, y)
    
    def expandIndex(self, k):
        return [Toffolin("toff", [Index(1), Index(2,-1), Index(2)])]

    def qiskitName(self):
        return "ccx"
    
class Toffoli(component):
    def alpha(self, n, x, y):
        r0 = getIndexValue(self.registers[0], n)
        r1 = getIndexValue(self.registers[1], n)
        r2 = getIndexValue(self.registers[2], n)

        Eq1 = Equal(mask(x, [r2]), mask(y, [r2]))
        result = (BVref(x,r0) & BVref(x, r1)) ^ BVref(x, r2)
        Eq2 = Equal(BVref(y,r2), result)
        return getSumPhase([(Eq1*Eq2, bv(0))])

    def Mx(self, n, x):
        qubits = {getIndexValue(self.registers[2], n)}
        return setbit(x, qubits)
    
    def My(self, n, y):
        return self.Mx(n, y)

    def qiskitName(self):
        return "ccx"
    
    def expandIndex(self, k):
        return [self, [Toffolin("toff", [Index(1), Index(2,-1), Index(2)])]]


class H0(component):
    def alpha(self, n, x, y):
        Eq = If(ULT(n, 0), Equal(BVtrunc(x, n, 1), BVtrunc(y, n, 1)), bv(1))
        d0 = Eq*Equal(BVref(y, 0), bv(0))
        d1 = Eq*Equal(BVref(y, 0), bv(1))
        return getSumPhase([(d0, bv(0)), (d1, BVref(x, 0))])

    def My(self, n, y):
        return [BVtrunc(y, n, 1) | bv(0),
                BVtrunc(y, n, 1) | bv(1)]

    def Mx(self, n, x):
        return [BVtrunc(x, n, 1) | bv(0),
                BVtrunc(x, n, 1) | bv(1)]

    def qiskitName(self):
        return "h"
    
    def expandIndex(self, k):
        return [self, HN("Hn", [Index(1)])]
    
class H(component):
    def alpha(self, n, x, y):
        targ = getIndexValue(self.registers[0], n)
        Eq = Equal(mask(x, [targ]), mask(y, [targ]))
        d0 = Eq*Equal(BVref(y, targ), bv(0))
        d1 = Eq*Equal(BVref(y, targ), bv(1))
        return sumPhase([phase(d0, bv(0)), phase(d1, BVref(x, n))])

    def My(self, n, y):
        return self.Mx(n, y)

    def Mx(self, n, x):
        targ = getIndexValue(self.registers[0], n)
        qubits = {targ}
        return setbit(x, qubits)

    def qiskitName(self):
        return "h"
    
    def expandIndex(self, k):
        return [H("Hn", [Index(1)]),H("H0", [Index(0)]), H("Hn-1", [Index(1,-1)])]


class HN(component):
    def alpha(self, n, x, y):
        Eq = If(ULT(n, 0), Equal(BVtrunc(x, n-1), BVtrunc(y, n-1)), bv(1))
        d0 = Eq*Equal(BVref(y, n), bv(0))
        d1 = Eq*Equal(BVref(y, n), bv(1))
        return sumPhase([phase(d0, bv(0)), phase(d1, BVref(x, n))])

    def My(self, n, y):
        return self.Mx(n, y)

    def Mx(self, n, x):
        qubits = {n}
        return setbit(x, qubits)

    def qiskitName(self):
        return "h"
    
class Xn(component):
    def alpha(self, n, x, y):
        reg = eval(str(self.registers[0]))
        Eq = Equal(x, y ^ (bv(1)<<reg))
        return getSumPhase([(Eq, bv(0))])
    
    def My(self, n, y):
        reg = eval(str(self.registers[0]))
        return [BVtrunc(y, n-1) ^ (bv(1) << reg)]

    def Mx(self, n, x):
        return [BVtrunc(x, n-1) ^ (bv(1) << n)]    

class X(component):
    def alpha(self, n, x, y):
        reg = eval(str(self.registers[0]))
        Eq = Equal(x ^ (bv(1)<<reg), y)
        return getSumPhase([(Eq, bv(0))])

    def My(self, n, y):
        reg = eval(str(self.registers[0]))
        return [y ^ (bv(1) << reg)]

    def Mx(self, n, x):
        return self.My(n,x)

    def qiskitName(self):
        return "x"
    
    def expandIndex(self, k):
        return [X('x', registers=['n+7'])]


# class CNOT(component):
#     def alpha(self, n, x, y):
#         Eq = If(n >= 1, Equal(BVtrunc(x, n-1), BVtrunc(y, n-1)), bv(1))
#         d0 = Eq*Equal(BVref(y, n), BVref(y, n-1) ^ BVref(x, n))
#         return sumPhase([phase(d0, bv(0))])

#     def Mx(self, n, x):
#         return [BVtrunc(x, n-1),
#                 BVtrunc(x, n-1) ^ (bv(1) << n)]

#     def My(self, n, y):
#         return [BVtrunc(y, n-1),
#                 BVtrunc(y, n-1) ^ (bv(1) << n)]

#     def qiskitName(self):
#         return self.name

#     def decompose(self):
#         return CNOT('cx', [Index(1,-1), Index(1)])
    
#     def control(self, ctrl):
#         for index in self.registers:
#             index.addOffset(1)
#         return CNOT('ccx', [ctrl]+ self.registers)
    
class CNOT(component):
    def alpha(self, n, x, y):
        targ = getIndexValue(self.registers[1], n)
        ctrl = getIndexValue(self.registers[0], n)
        Eq = Equal(mask(x, [targ]), mask(y, [targ]))
        d0 = Eq*Equal(BVref(y, targ), BVref(y, ctrl) ^ BVref(x, targ))
        return sumPhase([phase(d0, bv(0))])

    def Mx(self, n, x):
        targ = getIndexValue(self.registers[1], n)
        qubits = {targ}
        return setbit(x, qubits)

    def My(self, n, y):
        return self.Mx(n, y)

    def qiskitName(self):
        return self.name

    def decompose(self):
        return self
    
    def control(self, ctrl):
        for index in self.registers:
            index.addOffset(1)
        return CNOT('ccx', [ctrl]+ self.registers)
    
    def expandIndex(self, k=1):
        if k==1:
            return [CNOT('cx', [Index(1, -1), Index(1)]), CNOT('cx', [Index(1), Index(1, -1)])]
        if k>=2:
            return [CNOT('cx', [Index(1), Index(2)])]
            

class Xmaj(component):
    def alpha(self, n, x, y):
        params=[]
        for reg in self.registers:
            params.append(eval(str(reg)))
        return xmaj(n, x, y, *params)

    def Mx(self, n, x):
        qubits = {0, 1, n+1}
        return setbit(x, qubits)

    def My(self, n, y):
        return self.Mx(n, y)

    def decompose(self):
        return [X("x",[Index(3,1,True)]),CNOT('cx', [Index(2,1,True),Index(3,1,True)]), CNOT('cx', [Index(2,1,True), Index(2,0,True)]), Toffoli('ccx', [Index(2,0,True), Index(3,1,True), Index(2,1,True)])]
    
    def expandIndex(self, k=1):
        if k>=2:
            return [self]
        return []
    
class Xuma(component):
    def alpha(self, n, x, y):
        params=[]
        for reg in self.registers:
            params.append(eval(str(reg)))
        return xuma(n, x, y, *params)

    def Mx(self, n, x):
        qubits = {0, 1, n+1}
        return setbit(x, qubits)

    def My(self, n, y):
        return self.Mx(n, y)

    def decompose(self):
        return [Toffoli('ccx', [Index(2,0,True), Index(3,1,True), Index(2,1,True)]),  CNOT('cx', [Index(2,1,True), Index(2,0,True)]), CNOT('cx', [Index(2,0,True), Index(3,1,True)]), X("x", [Index(3,1,True)])]
    
    def expandIndex(self, k=1):
        if k>=2:
            return [self]
        return []
    
class nparH(component):
    def alpha(self, n, x, y):
        return getSumPhase([(If(andSum(x, y) == 1, bv(-1), bv(1)), bv(0))])
    
def oracleFunc(x, length=MAXL):
    global Uo
    return BVref(Uo, 0)


class DeuJozsaOracle(component):
    def alpha(self, n, x, y):
        Eqtrivial = Equal(BVtrunc(x, n, 1), BVtrunc(y, n, 1))
        Eqoracle = Equal(BVref(y, 0), BVref(x, 0) ^
                         oracleFunc(BVtrunc(x, n, 1)))
        return getSumPhase([(Eqtrivial*Eqoracle, bv(0))])

    def Mx(self, n, x):
        return [lambda n, y: BVref(y, 0) ^ oracleFunc(BVtrunc(y, n, 1)) | (BVtrunc(y, n, 1) << 1)]

    def My(self):
        return [lambda n, x: BVref(x, 0) ^ oracleFunc(BVtrunc(x, n, 1)) | (BVtrunc(x, n, 1) << 1)]



class Y(component):
    def alpha(self, n, x, y):
        Eq = If(ULT(n, 0), Equal(BVtrunc(x, n-1), BVtrunc(y, n-1)), bv(1))
        d0 = Eq*Equal(BVref(y, n), bv(0))
        d1 = Eq*Equal(BVref(y, n), bv(1))
        return sumPhase([phase(d0, bv(0)), phase(d1, BVref(x, n))])

    def Mx(self, n, x):
        return [BVtrunc(x, n-1, 1) << 1 | bv(1), BVtrunc(x, n-1, 1) << 1, BVtrunc(x, n-1, 1) << 1 | bv(1) << n, BVtrunc(x, n-1, 1) << 1 | (bv(1) | bv(1) << n)]

    def My(self, n, y):
        return [BVtrunc(y, n-1, 1) << 1 | bv(1), BVtrunc(y, n-1, 1) << 1, BVtrunc(y, n-1, 1) << 1 | bv(1) << n, BVtrunc(y, n-1, 1) << 1 | (bv(1) | bv(1) << n)]

class tele(component):
    def alpha(self, n, x, y):
        result = BVref(x,n) ^ BVref(y,3*n)
        Eq = Equal(result, BVref(y,2*n))
        baseEq = Equal(BVtrunc(x, n-1, 0), BVtrunc(y,n-1, 0))*Equal(BVtrunc(x, 2*n-1, n+1), BVtrunc(y,2*n-1, n+1))*Equal(BVtrunc(x, 3*n-1, 2*n+1), BVtrunc(y,3*n-1, 2*n+1))
        return getSumPhase([(baseEq*Eq, BVref(y,n)<<(n-1))])

    def Mx(self, n, x):
        qubits = {n, 2*n, 3*n}
        return setbit(x, qubits)

    def My(self, n, y):
        return self.Mx(n, y)

    def decompose(self):
        return [H0("h",[Index(2)]),CNOT('cx', [Index(2),Index(3)]), CNOT('cx', [Index(1), Index(2)]), H0('h', [Index(1)])]
    
    def expandIndex(self, k=1):
        if k>=3:
            return [self]
        return []

class CCX_N(component):
    def alpha(self, n, x, y):
        Eq1 = Equal(BVtrunc(x, 3*n-1, 1), BVtrunc(y, 3*n-1, 1))
        Eq2 = Equal(BVref(y, 3*n), BVref(BVref(x, n) +
                                         BVref(x, 2*n) + BVref(x, 0), 0))
        Eq3 = Equal(BVref(y, 0), BVref(
            BVref(x, n) + BVref(x, 2*n) + BVref(x, 0), 1))
        return getSumPhase([(Eq1*Eq2*Eq3, bv(0))])

    def Mx(self, n, x):
        return [BVtrunc(x, 3*n-1, 1) << 1 | bv(1), BVtrunc(x, 3*n-1, 1) << 1, BVtrunc(x, 3*n-1, 1) << 1 | bv(1) << (3*n), BVtrunc(x, 3*n-1, 1) << 1 | (bv(1) | bv(1) << (3*n))]

    def My(self, n, y):
        return [BVtrunc(y, 3*n-1, 1) << 1 | bv(1), BVtrunc(y, 3*n-1, 1) << 1, BVtrunc(y, 3*n-1, 1) << 1 | bv(1) << (3*n), BVtrunc(y, 3*n-1, 1) << 1 | (bv(1) | bv(1) << (3*n))]

    def decompose(self):
        return [Toffoli('ccx', [Index(1), Index(2), Index(3)]), CNOT('cx', [Index(1), Index(2)]), Toffoli('ccx', [Index(2), 0, Index(3)]),
                CNOT('cx', [Index(2), 0]), CNOT('cx', [Index(1), Index(2)]), Swap('swap', [0, Index(3)])]
    
    def expandIndex(self, k=1):
        if k>=3:
            return [self]
        return []


class MAJ(component):
    def alpha(self, n, x, y):
        params=[]
        for reg in self.registers:
            params.append(eval(str(reg)))
        return maj(n, x, y, *params)

    def Mx(self, n, x):
        qubits = {0, 1, n+1}
        return setbit(x, qubits)

    def My(self, n, y):
        return self.Mx(n, y)

    def decompose(self):
        return [CNOT('cx', [Index(2,1,True),Index(3,1,True)]), CNOT('cx', [Index(2,1,True), Index(2,0,True)]), Toffoli('ccx', [Index(2,0,True), Index(3,1,True), Index(2,1,True)])]
    
    def expandIndex(self, k):
        return [MAJ("maj", [0,1,Index(1,1)])]


class UMA(component):
    def alpha(self, n, x, y):
        params=[]
        for reg in self.registers:
            params.append(eval(str(reg)))
        return uma(n, x, y, *params)

    def Mx(self, n, x):
        qubits = {0, 1, n+1}
        return setbit(x, qubits)

    def My(self, n, y):
        return self.Mx(n, y)

    def decompose(self):
        return [Toffoli('ccx', [Index(2,0,True), Index(3,1,True), Index(2,1,True)]),  CNOT('cx', [Index(2,1,True), Index(2,0,True)]), CNOT('cx', [Index(2,0,True), Index(3,1,True)])]
    
    def expandIndex(self, k):
        return [UMA("uma",[0,1,Index(1,1)])]


class Ident(component):
    def alpha(self, n, x, y):
        Eq = Equal(x, y)
        return getSumPhase([(Eq, bv(0))])

    def Mx(self, n, z):
        return [z]

    def My(self, n, z):
        return [z]

    def qiskitName(self):
        return "id"

class Subtractor(component):
    def alpha(self, n, x, y):
        c = self.params["c"]
        Eq1 = Equal(BVtrunc(x, n+c-1, 0), BVtrunc(y, n+c-1, 0))
        add =  BVtrunc(x,2*c+n-1,n+c) - BVtrunc(x, c, 1) - BVref(x,0)
        result = BVtrunc(y,2*c+n-1,n+c)
        Eq2 = Equal(BVtrunc(add, c-1),  BVtrunc(result, c-1))
        return getSumPhase([(Eq1*Eq2, bv(0))])

    def Mx(self, n, x):
        c = self.params["c"]
        add = BVtrunc(x,2*c+n-1,n+c) - BVtrunc(x, c, 1) - BVref(x,0)
        return [setVec(x,add,2*c+n-1,n+c)]
    
    def My(self,n,y):
        c = self.params["c"]
        add = BVtrunc(y,2*c+n-1,n+c) + BVtrunc(y, c, 1) + BVref(y,0)
        return [setVec(y,add,2*c+n-1,n+c)]

    def claim(self):
        return True
    
    def qiskitName(self):
        c = self.params["c"]
        return f"RippleSubtractor"
    
    def source(self):
        return "from RippleSubtractor import RippleSubtractor\n"
    
    def call(self):
        size = self.params["c"]-1

        arg = f"list(range(0, {size+1}))+list(range({Index(0)}+{size}, {Index(0)}+{2*size}))"
        return size, arg
    
    def expandIndex(self, k):
        return [Subtractor('sub', [0,1,Index(1)], params={'c':self.params["c"]})]

class Cadder(component):
    def alpha(self, n, x, y):
        c = self.params["c"]
        Eq1 = Equal(BVtrunc(x, n+c-1, 0), BVtrunc(y, n+c-1, 0))
        ctrl = BVref(x,2*c+n-1)
        add =  BVtrunc(x,2*c+n-2,n+c) + ctrl*BVtrunc(x, c-1, 1) + BVref(x,0)
        result = BVtrunc(y,2*c+n-1,n+c)
        Eq2 = Equal(BVtrunc(add, c-2),  BVtrunc(result, c-2))
        return getSumPhase([(Eq1*Eq2, bv(0))])
    
    def Mx(self,n,x):
        c = self.params["c"]
        ctrl = BVref(x,2*c+n-1)
        add =  BVtrunc(x,2*c+n-2,n+c) + ctrl*BVtrunc(x, c-1, 1) + BVref(x,0)
        return [setVec(x,add,2*c+n-2,n+c)]
    
    def My(self, n, y):
        c = self.params["c"]
        ctrl = BVref(y,2*c+n-1)
        add =  BVtrunc(y,2*c+n-2,n+c) - ctrl*BVtrunc(y, c-1, 1) - BVref(y,0)
        return [setVec(y,add,2*c+n-2,n+c)]
    
    def claim(self):
        return True
    
    def qiskitName(self):
        return f"CondAdder"
    
    def call(self):
        size = self.params["c"]-1
        arg = f"list(range(0, {size+1}))+list(range({Index(0)}+{size}, {Index(0)}+{2*size+1}))"
        return size, arg
    
    def source(self):
        return "from CondAdder import CondAdder\n"
    
    def expandIndex(self, k):
        return [Cadder('cadd', [0,1,Index(1)], params={'c':self.params["c"]})]

def setbit(x, qubits):
    allset = allsubset(qubits)
    result = []
    for item in allset:
        xtmp = mask(x, qubits)
        for i in item:
            xtmp = xtmp ^ (bv(1) << i)
        result.append(xtmp)
    return result

StandardGateSet = [H("H", [Index(0)]),  CNOT('cx', [Index(0), Index(0,1)]), Toffoli('ccx', [0,1,2]),  Swap('swap', [0,1]), X('x', [0])]


if __name__ == "__main__":
    s = Solver()
    x,y,n = BitVecs('x y n', MAXL)
    component = Cadder('sub',registers=[0,1,"n"], params={'c':4})
    start = "0000000000110"
    start = int(start,2)
    term = component.alpha(n,x,y)[0][0]
    solve(x==0b10000110,n==3, term==1)

