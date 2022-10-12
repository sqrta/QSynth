from adt import *
import itertools
from functools import reduce
 
def findsubsets(s, n):
    return list(itertools.combinations(s, n))

def allsubset(s):
    return reduce(lambda a,b: a+b, [findsubsets(s, i) for i in range(len(s)+1)])

Uo=BitVec('f', MAXL)
class component:
    def __init__(self, name, registers=None) -> None:
        self.name = name
        if not registers:
            self.registers = []
        else:
            self.registers = registers

    def getName(self):
        return self.name

    def alpha(self, n, x, y):
        return None

    def Mx(self,n,x):
        raise(self.name+" does not have Mx")
        

    def My(self,n,y):
        raise(self.name+" does not have My")

    def __str__(self) -> str:
        return self.name


class CRZ0N(component):
    def alpha(self, n, x, y):
        Eq = delta(BVtrunc(x, n), BVtrunc(y, n))
        return sumPhase([phase(Eq, BVref(x, 0))])

    def My(self, n, y):
        return [ y]

    def Mx(self, n, x):
        return [x]


class move1(component):
    def alpha(self, n, x, y):
        Eq = delta(BVtrunc(x, n-1), BVtrunc(y, n, 1)) * \
            delta(BVref(y, 0), bv(0))
        return getSumPhase([(Eq, bv(0))])

    def My(self, n, y):
        return [BVtrunc(y, n, 1), BVtrunc(y, n, 1) | 1 << n]

    def Mx(self, n, x):
        return [BVtrunc(x, n-1) << 1, BVtrunc(x, n-1) << 1 | bv(1)]


class CRZN(component):
    def alpha(self, n, x, y):
        Eq = delta(BVtrunc(x, n-1), BVtrunc(y, n-1))
        d0 = Eq*delta(BVref(y, n), bv(0))
        d1 = Eq*delta(BVref(y, n), bv(1))
        return getSumPhase([(d0, bv(0)), (d1, BVtrunc(x, n))])

    def My(self, n, y):
        return [BVtrunc(y, n-1),
                BVtrunc(y, n-1) | (bv(1) << n)]

    def Mx(self, n, x):
        return [BVtrunc(x, n-1),
                BVtrunc(x, n-1) | (bv(1) << n)]



class H0(component):
    def alpha(self, n, x, y):
        Eq = If(ULT(n,0), delta(BVtrunc(x, n, 1), BVtrunc(y, n, 1)), bv(1))
        d0 = Eq*delta(BVref(y, 0), bv(0))
        d1 = Eq*delta(BVref(y, 0), bv(1))
        return getSumPhase([(d0, bv(0)), (d1, BVref(x, 0))])

    def My(self, n, y):
        return [BVtrunc(y, n, 1) | bv(0),
                BVtrunc(y, n, 1) | bv(1)]

    def Mx(self, n, x):
        return [BVtrunc(x, n, 1) | bv(0),
                BVtrunc(x, n, 1) | bv(1)]


class HN(component):
    def alpha(self, n, x, y):
        Eq = If(ULT(n , 0), delta(BVtrunc(x, n-1), BVtrunc(y, n-1)), bv(1))
        d0 = Eq*delta(BVref(y, n), bv(0))
        d1 = Eq*delta(BVref(y, n), bv(1))
        return sumPhase([phase(d0, bv(0)), phase(d1, BVref(x, n))])

    def My(self, n ,y):
        return [BVtrunc(y, n-1) | bv(0) << n,
                BVtrunc(y, n-1) | bv(1) << n]

    def Mx(self,n,x):
        return [BVtrunc(x, n-1) | bv(0) << n,
                BVtrunc(x, n-1) | bv(1) << n]

class CNOT(component):
    def alpha(self, n, x, y):
        Eq = If(n >= 1, delta(BVtrunc(x, n-1), BVtrunc(y, n-1)), bv(1))
        d0 = Eq*delta(BVref(y, n), BVref(y,n-1) ^ BVref(x,n))
        return sumPhase([phase(d0, bv(0))])

    def Mx(self, n, x):
        return [BVtrunc(x, n-1) | bv(0) << n,
                BVtrunc(x, n-1) | bv(1) << n]

    def My(self, n ,y):
        return [BVtrunc(y, n-1) | bv(0) << n,
                BVtrunc(y, n-1) | bv(1) << n]

class nparH(component):
    def alpha(self, n, x, y):
        return getSumPhase([(If(andSum(x,y)==1, bv(-1), bv(1)),bv(0))])

def oracleFunc(x, length = MAXL):
    global Uo
    return BVref(Uo,0)

class DeuJozsaOracle(component):
    def alpha(self, n, x, y):
        Eqtrivial = delta(BVtrunc(x,n,1), BVtrunc(y,n,1))    
        Eqoracle = delta(BVref(y,0), BVref(x,0) ^ oracleFunc(BVtrunc(x,n,1)))
        return getSumPhase([(Eqtrivial*Eqoracle, bv(0))])
    
    def Mx(self, n, x):
        return [lambda n,y: BVref(y,0)^oracleFunc(BVtrunc(y,n,1)) | (BVtrunc(y,n,1)<<1)]
    def My(self):
        return [lambda n,x: BVref(x,0)^oracleFunc(BVtrunc(x,n,1)) | (BVtrunc(x,n,1)<<1)]

def oneBitAdder(x, y, a, b, c):
    Eq1 = delta(BVref(x, a), BVref(y, a))
    Eq2 = delta(BVref(y, b), BVref(BVref(x, a) + BVref(x, b) + BVref(x, c), 0))
    Eq3 = delta(BVref(y, c), BVref(BVref(x, a) + BVref(x, b) + BVref(x, c), 1))
    return getSumPhase([(Eq1*Eq2*Eq3, bv(0))])

class MAJN(component):
    def alpha(self, n, x, y):
        return oneBitAdder(x, y, n/2, n, 0)

    def Mx(self, n, x):
        return [BVtrunc(x, n-1, 1)<<1 | bv(1), BVtrunc(x, n-1, 1)<<1, BVtrunc(x, n-1, 1)<<1 | bv(1) << n, BVtrunc(x, n-1, 1)<<1 | (bv(1) | bv(1) << n)]

    def My(self, n, y):
        return [BVtrunc(y, n-1, 1)<<1 | bv(1),BVtrunc(y, n-1, 1)<<1, BVtrunc(y, n-1, 1)<<1 | bv(1) << n, BVtrunc(y, n-1, 1)<<1 | (bv(1) | bv(1) << n)]

class rippleAdder(component):
    def alpha(self, n, x, y):
        Eq1 = delta(BVtrunc(x, 3*n-1, 1), BVtrunc(y, 3*n-1, 1))
        Eq2 = delta(BVref(y, 3*n), BVref(BVref(x, n) + BVref(x, 2*n) + BVref(x, 0), 0))
        Eq3 = delta(BVref(y,0), BVref(BVref(x, n) + BVref(x, 2*n) + BVref(x, 0), 1))
        return getSumPhase([(Eq1*Eq2*Eq3, bv(0))])

    def Mx(self, n, x):
        return [BVtrunc(x, 3*n-1, 1)<<1 | bv(1), BVtrunc(x, 3*n-1, 1)<<1, BVtrunc(x, 3*n-1, 1)<<1 | bv(1) << (3*n), BVtrunc(x, 3*n-1, 1)<<1 | (bv(1) | bv(1) << (3*n))]

    def My(self, n,y):
        return [BVtrunc(y, 3*n-1, 1)<<1 | bv(1), BVtrunc(y, 3*n-1, 1)<<1, BVtrunc(y, 3*n-1, 1)<<1 | bv(1) << (3*n), BVtrunc(y, 3*n-1, 1)<<1 | (bv(1) | bv(1) << (3*n))]

class Ident(component):
    def alpha(self, n, x, y):
        Eq = delta(x, y)
        return getSumPhase([(Eq, bv(0))])

    def Mx(self, n,z):
        return [z]

    def My(self, n,z):
        return [z]

def setbit(x, qubits):
    allset = allsubset(qubits)
    result = []
    for item in allset:
        xtmp = mask(x, qubits)
        for i in item:
            xtmp = xtmp | (bv(1)<<i)
        result.append(xtmp)
    return result    

def maj(n,x,y,a,b,c):
    Eq1 = delta(mask(x, [a, b, c]), mask(y, [a, b, c]))
    Eq2 = delta(BVref(y,a), BVref(x, b)^BVref(x, a))
    Eq3 = delta(BVref(y,c), BVref(x, c)^BVref(x, b))
    Eq4 = delta(BVref(y,b), (BVref(x,b)*BVref(x, c)) ^ (BVref(x,b)* BVref(x,a)) ^ (BVref(x,a)*BVref(x, c)))
    return getSumPhase([(Eq1*Eq2*Eq3*Eq4, bv(0))])

def uma(n,x,y,a,b,c):
    Eq1 = delta(mask(x, [a, b, c]), mask(y, [a, b, c]))
    Eq2 = delta(BVref(y,a), BVref(x, a)^BVref(y,b))
    Eq3 = delta(BVref(y,c), BVref(x, c)^BVref(y,a))
    Eq4 = delta(BVref(y,b), BVref(x,b)^ (BVref(x,a)*BVref(x, c)))
    return getSumPhase([(Eq1*Eq2*Eq3*Eq4, bv(0))])    

class MAJ(component):
    def alpha(self, n, x, y):
        return maj(n,x,y,0,1,n+1)


    def Mx(self,n,x):
        qubits = {0,1,n+1}
        return setbit(x, qubits)
    
    def My(self,n,y):
        return self.Mx(n,y)

class UMA(component):
    def alpha(self, n, x, y):
        return uma(n,x,y,0,1,n+1)

    def Mx(self,n,x):
        qubits = {0,1,n+1}
        return setbit(x, qubits)
    
    def My(self,n,y):
        return self.Mx(n,y)

database = [Ident('I'),H0("H", ['0']), HN("H", ['n']), CRZN("C_RZN", ['n']), move1("move 1"),  MAJN("OneBitAdd n-1 n 0 ; SWAP n-1 n/2"), CNOT('CNOT', ['n-1', 'n']), rippleAdder("SJ")]


if __name__ == "__main__":
    print(allsubset({1,2,3}))
'''     
print("Examples: list[0] = alpha(n,x,y)")
exStr = [strEx(i) for i in examples]
for ex in exStr:
    print(', '.join(ex))

print('')
x, y, n = BitVecs("x y n", MAXL)
#print(examplesFunc(n,x,y))
a = [And(x == 0, y == 1), And(x == 1, y == 2)]

gb,gi=search(examplespec, database,'left', lambda n, x, y: And(getpre(n, x, y)),1)
print("\nResult Program:")
crznProg = showProg([H0("H 0")], CRZ0N("move 1; C_RZ 0 n"), 'right', "C_RZN")
print(crznProg + "\n")    
print(showProg(gb, gi, 'left', 'QFT'))
'''