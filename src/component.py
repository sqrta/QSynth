from adt import *

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

    def Mx(self):
        raise(self.name+" does not have Mx")
        

    def My(self):
        raise(self.name+" does not have My")

    def __str__(self) -> str:
        return self.name


class CRZ0N(component):
    def alpha(self, n, x, y):
        Eq = delta(BVtrunc(x, n), BVtrunc(y, n))
        return sumPhase([phase(Eq, BVref(x, 0))])

    def Mx(self):
        return [lambda n, y: y]

    def My(self):
        return [lambda n, x: x]


class move1(component):
    def alpha(self, n, x, y):
        Eq = delta(BVtrunc(x, n-1), BVtrunc(y, n, 1)) * \
            delta(BVref(y, 0), bv(0))
        return getSumPhase([(Eq, bv(0))])

    def Mx(self):
        return [lambda n, y: BVtrunc(y, n, 1), lambda n, y: BVtrunc(y, n, 1) | 1 << n]

    def My(self):
        return [lambda n, x: BVtrunc(x, n-1) << 1, lambda n, x: BVtrunc(x, n-1) << 1 | bv(1)]


class CRZN(component):
    def alpha(self, n, x, y):
        Eq = delta(BVtrunc(x, n-1), BVtrunc(y, n-1))
        d0 = Eq*delta(BVref(y, n), bv(0))
        d1 = Eq*delta(BVref(y, n), bv(1))
        return getSumPhase([(d0, bv(0)), (d1, BVtrunc(x, n))])

    def Mx(self):
        return [lambda n, y: BVtrunc(y, n-1),
                lambda n, y: BVtrunc(y, n-1) | (bv(1) << n)]

    def My(self):
        return [lambda n, x: BVtrunc(x, n-1),
                lambda n, x: BVtrunc(x, n-1) | (bv(1) << n)]



class H0(component):
    def alpha(self, n, x, y):
        Eq = If(ULT(n,0), delta(BVtrunc(x, n, 1), BVtrunc(y, n, 1)), bv(1))
        d0 = Eq*delta(BVref(y, 0), bv(0))
        d1 = Eq*delta(BVref(y, 0), bv(1))
        return getSumPhase([(d0, bv(0)), (d1, BVref(x, 0))])

    def Mx(self):
        return [lambda n, y: BVtrunc(y, n, 1) | bv(0),
                lambda n, y: BVtrunc(y, n, 1) | bv(1)]

    def My(self):
        return [lambda n, x: BVtrunc(x, n, 1) | bv(0),
                lambda n, x: BVtrunc(x, n, 1) | bv(1)]


class HN(component):
    def alpha(self, n, x, y):
        Eq = If(ULT(n , 0), delta(BVtrunc(x, n-1), BVtrunc(y, n-1)), bv(1))
        d0 = Eq*delta(BVref(y, n), bv(0))
        d1 = Eq*delta(BVref(y, n), bv(1))
        return sumPhase([phase(d0, bv(0)), phase(d1, BVref(x, n))])

    def Mx(self):
        return [lambda n, y: BVtrunc(y, n-1) | bv(0) << n,
                lambda n, y: BVtrunc(y, n-1) | bv(1) << n]

    def My(self):
        return [lambda n, x: BVtrunc(x, n-1) | bv(0) << n,
                lambda n, x: BVtrunc(x, n-1) | bv(1) << n]

class CNOT(component):
    def alpha(self, n, x, y):
        Eq = If(n >= 1, delta(BVtrunc(x, n-1), BVtrunc(y, n-1)), bv(1))
        d0 = Eq*delta(BVref(y, n), BVref(y,n-1) ^ BVref(x,n))
        return sumPhase([phase(d0, bv(0))])

    def Mx(self):
        return [lambda n, y: BVtrunc(y, n-1) | bv(0) << n,
                lambda n, y: BVtrunc(y, n-1) | bv(1) << n]

    def My(self):
        return [lambda n, x: BVtrunc(x, n-1) | bv(0) << n,
                lambda n, x: BVtrunc(x, n-1) | bv(1) << n]

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
    
    def Mx(self):
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

    def Mx(self):
        return [lambda n, y: BVtrunc(y, n-1, 1)<<1 | bv(1), lambda n, y: BVtrunc(y, n-1, 1)<<1, lambda n, y: BVtrunc(y, n-1, 1)<<1 | bv(1) << n, lambda n, y: BVtrunc(y, n-1, 1)<<1 | (bv(1) | bv(1) << n)]

    def My(self):
        return [lambda n, y: BVtrunc(y, n-1, 1)<<1 | bv(1), lambda n, y: BVtrunc(y, n-1, 1)<<1, lambda n, y: BVtrunc(y, n-1, 1)<<1 | bv(1) << n, lambda n, y: BVtrunc(y, n-1, 1)<<1 | (bv(1) | bv(1) << n)]

class rippleAdder(component):
    def alpha(self, n, x, y):
        Eq1 = delta(BVtrunc(x, 3*n-1, 1), BVtrunc(y, 3*n-1, 1))
        Eq2 = delta(BVref(y, 3*n), BVref(BVref(x, n) + BVref(x, 2*n) + BVref(x, 0), 0))
        Eq3 = delta(BVref(y,0), BVref(BVref(x, n) + BVref(x, 2*n) + BVref(x, 0), 1))
        return getSumPhase([(Eq1*Eq2*Eq3, bv(0))])

    def Mx(self):
        return [lambda n, y: BVtrunc(y, 3*n-1, 1)<<1 | bv(1), lambda n, y: BVtrunc(y, 3*n-1, 1)<<1, lambda n, y: BVtrunc(y, 3*n-1, 1)<<1 | bv(1) << (3*n), lambda n, y: BVtrunc(y, 3*n-1, 1)<<1 | (bv(1) | bv(1) << (3*n))]

    def My(self):
        return [lambda n, y: BVtrunc(y, 3*n-1, 1)<<1 | bv(1), lambda n, y: BVtrunc(y, 3*n-1, 1)<<1, lambda n, y: BVtrunc(y, 3*n-1, 1)<<1 | bv(1) << (3*n), lambda n, y: BVtrunc(y, 3*n-1, 1)<<1 | (bv(1) | bv(1) << (3*n))]

class Ident(component):
    def alpha(self, n, x, y):
        Eq = delta(x, y)
        return getSumPhase([(Eq, bv(0))])

    def Mx(self):
        return [lambda n,z : z]

    def My(self):
        return [lambda n,z : z]

if __name__ == '__main__':
    a = nparH('nparH')
    b = DeuJozsaOracle('Uo')
    f = b.Mx()[0]
    
    n,x,y = BitVecs('n x y', MAXL)
    terms = rightMultiAlpha(b, lambda n,x,y: a.alpha(n,x,y),n,bv(1),y)
    solve(b.alpha(n,x,y).deltas()==1)
    simplify(terms[0].z3exp())
    z3term = sum([term.deltas() for term in terms])
    s=Solver()
    s.add(ForAll([n,y,Uo], z3term == If(BVref(y,0)^ oracleFunc(BVtrunc(y,n,1))==0, bv(1),bv(-1))))
    print(s.check())

database = [Ident('I'),H0("H", ['0']), HN("H", ['n']), CRZN("C_RZN", ['n']), move1("move 1"),  MAJN("OneBitAdd n-1 n 0 ; SWAP n-1 n/2"), CNOT('CNOT', ['n-1', 'n']), rippleAdder("SJ")]

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