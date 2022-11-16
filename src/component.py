from adt import *
import itertools
from functools import reduce


def findsubsets(s, n):
    return list(itertools.combinations(s, n))


def allsubset(s):
    return reduce(lambda a, b: a+b, [findsubsets(s, i) for i in range(len(s)+1)])


Uo = BitVec('f', MAXL)


class component:
    def __init__(self, name, registers=None) -> None:
        self.name = name
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

    def prog(self):
        return None

    def Mx(self, n, x):
        raise(self.name+" does not have Mx")

    def decompose(self):
        return self

    def My(self, n, y):
        raise(self.name+" does not have My")

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
        return ISQIR({'base':[HN('h', ['N'])], 'inductive':[Ident('I'),CRZ0N('cp', ['pi/2**n', 'N-n', 'n'])]}, 'Zn')


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


class Toffoli(component):
    def alpha(self, n, x, y):
        Eq = Equal(x, y)
        return getSumPhase([(Eq, bv(0))])

    def Mx(self, n, z):
        return [z]

    def My(self, n, z):
        return [z]

    def qiskitName(self):
        return "ccx"


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


class HN(component):
    def alpha(self, n, x, y):
        Eq = If(ULT(n, 0), Equal(BVtrunc(x, n-1), BVtrunc(y, n-1)), bv(1))
        d0 = Eq*Equal(BVref(y, n), bv(0))
        d1 = Eq*Equal(BVref(y, n), bv(1))
        return sumPhase([phase(d0, bv(0)), phase(d1, BVref(x, n))])

    def My(self, n, y):
        return [BVtrunc(y, n-1) | bv(0) << n,
                BVtrunc(y, n-1) | bv(1) << n]

    def Mx(self, n, x):
        return [BVtrunc(x, n-1) | bv(0) << n,
                BVtrunc(x, n-1) | bv(1) << n]

    def qiskitName(self):
        return "h"

class X(component):
    def alpha(self, n, x, y):
        Eq = If(ULT(n, 0), Equal(BVtrunc(x, n-1), BVtrunc(y, n-1)), bv(1))
        d0 = Eq*Equal(BVref(y, n), bv(0))
        d1 = Eq*Equal(BVref(y, n), bv(1))
        return sumPhase([phase(d0, bv(0)), phase(d1, BVref(x, n))])

    def My(self, n, y):
        return [BVtrunc(y, n-1) | bv(0) << n,
                BVtrunc(y, n-1) | bv(1) << n]

    def Mx(self, n, x):
        return [BVtrunc(x, n-1) | bv(0) << n,
                BVtrunc(x, n-1) | bv(1) << n]

    def qiskitName(self):
        return "h"


class CNOT(component):
    def alpha(self, n, x, y):
        Eq = If(n >= 1, Equal(BVtrunc(x, n-1), BVtrunc(y, n-1)), bv(1))
        d0 = Eq*Equal(BVref(y, n), BVref(y, n-1) ^ BVref(x, n))
        return sumPhase([phase(d0, bv(0))])

    def Mx(self, n, x):
        return [BVtrunc(x, n-1) | bv(0) << n,
                BVtrunc(x, n-1) | bv(1) << n]

    def My(self, n, y):
        return [BVtrunc(y, n-1) | bv(0) << n,
                BVtrunc(y, n-1) | bv(1) << n]

    def qiskitName(self):
        return "cx"

    def decompose(self):
        return CNOT('cnot', ['n-1', 'n'])


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
        return [Toffoli('ccnot', ['n', 'N+n', '2*N+n']), CNOT('cnot', ['n', 'N+n']), Toffoli('ccnot', ['N+n', 0, '2*N+n']),
                CNOT('cnot', ['N+n', 0]), CNOT('cnot', ['n', 'N+n']), Swap('swap', [0, '2*N+n'])]


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


def setbit(x, qubits):
    allset = allsubset(qubits)
    result = []
    for item in allset:
        xtmp = mask(x, qubits)
        for i in item:
            xtmp = xtmp | (bv(1) << i)
        result.append(xtmp)
    return result



class Fredkin(component):
    def alpha(self, n, x, y):
        return fredkin(n, x, y, 0, 1, n+1)

    def Mx(self, n, x):
        qubits = {0, 1, n+1}
        return setbit(x, qubits)

    def My(self, n, y):
        return self.Mx(n, y)

    def decompose(self):
        return [CNOT('cnot', ['2*N-n', 'N-n']), CNOT('cnot', ['2*N-n', 0]), Toffoli('ccnot', [0, 'N-n', '2*N-n'])]


class Peres(component):
    def alpha(self, n, x, y):
        return peres(n, x, y, 0, 1, n+1)

    def Mx(self, n, x):
        qubits = {0, 1, n+1}
        return setbit(x, qubits)

    def My(self, n, y):
        return self.Mx(n, y)

    def decompose(self):
        return [Toffoli('ccnot', [0, 'N-n', '2*N-n']),  CNOT('cnot', ['2*N-n', 0]), CNOT('cnot', [0, 'N-n'])]


StandardGateSet = [Ident('I'), H0("H", ['0']), CRZN("C_RZN", ['n']), CNOT('CNOT', [0,1]), Toffoli('ccx', [0,1,2]),  Swap('swap', [0,1]), X('x', [0])]


if __name__ == "__main__":
    print(allsubset({1, 2, 3}))

