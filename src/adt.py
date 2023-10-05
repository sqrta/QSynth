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
    
class Index:
    def __init__(self, slope, offset=0,rev=False):
        self.slope = slope
        self.offset = offset
        self.rev = rev

    def addOffset(self, num):
        self.offset+=num

    def addSlope(self,num):
        self.slope+=num

    def __str__(self) -> str:
        result = "n"
        if self.slope>1:
            tmp = "N" if self.slope==2 else f"{self.slope-1}*N"
            result = tmp + f"{'-' if self.rev else '+'}"+result
        if self.offset>0:
            result += f"+{self.offset}"
        elif self.offset<0:
            result += f"{self.offset}"
        return result


def maj(n, x, y, a, b, c):
    Eq1 = Equal(mask(x, [a, b, c]), mask(y, [a, b, c]))
    Eq2 = Equal(BVref(y, a), BVref(x, b) ^ BVref(x, a))
    Eq3 = Equal(BVref(y, c), BVref(x, c) ^ BVref(x, b))
    Eq4 = Equal(BVref(y, b), (BVref(x, b)*BVref(x, c)) ^
                (BVref(x, b) * BVref(x, a)) ^ (BVref(x, a)*BVref(x, c)))
    return getSumPhase([(Eq1*Eq2*Eq3*Eq4, bv(0))])

def xmaj(n,x,y,a,b,c):
    Eq1 = Equal(mask(x, [a, b, c]), mask(y, [a, b, c]))
    Eq2 = Equal(BVref(y, a), BVref(x, b) ^ BVref(x, a))
    Eq3 = Equal(BVref(y, c), (BVref(~x, c)) ^ BVref(x, b))
    Eq4 = Equal(BVref(y, b), (BVref(x, b)* (BVref(~x, c))) ^
                (BVref(x, b) * BVref(x, a)) ^ (BVref(x, a)*(BVref(~x, c))))
    return getSumPhase([(Eq1*Eq2*Eq3*Eq4, bv(0))])

def xuma(n, x, y, a, b, c):
    Eq1 = Equal(mask(x, [a, b, c]), mask(y, [a, b, c]))
    Eq2 = Equal(BVref(y, a), BVref(x, a) ^ BVref(y, b))
    Eq3 = Equal(BVref(~y, c), BVref(x, c) ^ BVref(y, a))
    Eq4 = Equal(BVref(y, b), BVref(x, b) ^ (BVref(x, a)*BVref(x, c)))
    return getSumPhase([(Eq1*Eq2*Eq3*Eq4, bv(0))])


def uma(n, x, y, a, b, c):
    Eq1 = Equal(mask(x, [a, b, c]), mask(y, [a, b, c]))
    Eq2 = Equal(BVref(y, a), BVref(x, a) ^ BVref(y, b))
    Eq3 = Equal(BVref(y, c), BVref(x, c) ^ BVref(y, a))
    Eq4 = Equal(BVref(y, b), BVref(x, b) ^ (BVref(x, a)*BVref(x, c)))
    return getSumPhase([(Eq1*Eq2*Eq3*Eq4, bv(0))])

def showProg(base, gi, name="foo", inductExp=1, backend="sqir", offset=1):
    if not base:
        return "No solutions"
    left,right = gi
    prog = ""
    if backend == 'sqir':
        def sqirName(ins):
            return ins.name + " " + " ".join([str(i) for i in ins.registers])

        prog += "Fixpoint "+name + " (n : nat) : Unitary :=\n"
        prog += "\t match n with\n"
        for i in range(len(base)):
            prog += "\t\t | " + str(i) + " => " + sqirName(base[i]) + "\n"
        prog += "\t\t | _ => "
        if left:
            prog += sqirName(left) + ";"
        prog += name + " n-1;"
        if right:
            prog += sqirName(right)
        prog += "\n\t end."
    elif backend == 'qiskit':
        prog = qiskitbackend(base,left,right, name, inductExp,offset)
    elif backend == 'qsharp':
        def qsharpName(ins):
            nameMap = {'CZ': "(Controlled Z)"}
            gate = nameMap.get(ins.name, ins.name)
            return gate + "(" + ",".join(["q["+str(i)+"]" for i in ins.registers]) + ");"
        prog += "Operation " + name + "(q : Qubit[], n : Int) : Unit{\n"
        for i in range(len(base)):
            prog += "\tif (n==" + str(i) + "){\n"
            prog += "\t"*2+qsharpName(base[i]) + "\n\t\treturn ();\n\t}\n"
        if left:
            prog += "\t" + qsharpName(left) + "\n"
        prog += "\t" + name + "(q,n-1);\n"
        if right:
            prog += "\t" + qsharpName(right) + "\n"
        prog += "}"
    return prog

def qiskitbackend(base, left=None, right=None, name="foo", spec=1, offset=1):
    prog = ""
    def qiskitName(ins):
        nameMap = {'CNOT': "cx", "H": 'h'}
        gate = ins.qiskitName()
        return gate + "(" + ",".join([str(i) for i in ins.registers]) + ")"

    def circCall(ins, circ="circ"):
        if ins.claim():
            return f"{circ}.append({qiskitName(ins)})"
        else:
            return circ+"." + qiskitName(ins)

    def gatelist(gates,tabnum, circ="circ"):
        instructions = gates
        if not isinstance(gates, list):
            instructions = [gates]
        ops = [circCall(gate, circ) for gate in instructions]
        return ntab(tabnum)+ f"\n{ntab(tabnum)}".join(ops) + "\n"
    
    def flatten(module, cont):
        insList = []
        for item in module:
            ins = item.decompose()
            if isinstance(ins, list):
                ins = [item.control(0) if cont==2 else item for item in ins]
                insList+=ins
            else:
                insList.append(ins)
        return insList

    prog += "def " + name + "(N):\n"
    size = f"N+{offset}" if spec==1 else f"{spec}*N+{offset}"
    prog+=f"\tcircuit=QuantumCircuit({size})\n"     
    prog += "\tdef S(circ, n):\n"   
    for i in range(len(base)):       
        prog += "\t\tif(n==" + str(i) + "):\n"
        prog += gatelist(base[i], 3)
    prog += f"\t\telse:\n"
    if not (len(left)==1 and left[0].name=="I"):
        prog += gatelist(flatten(left, offset), 3)
    prog += f"{ntab(3)}S(circ,n-1)\n"
    if not (len(right)==1 and right[0].name=="I"):
        prog += gatelist(flatten(right, offset), 3)
    prog+="\tS(circuit,N)\n\treturn circuit\n\n"
    return prog

def ntab(n):
    return "\t"*n

def strEx(example):
    def binw(n):
        return '{:0{width}b}'.format(n, width=example[1]+1)
    return ("exp(2pi*j*0."+binw(example[0]) + ')', "n="+str(example[1]+1), "x="+binw(example[2]), "y="+binw(example[3]))

def reverseb(n, width):
    b = '{:0{width}b}'.format(n, width=width)
    return int(b[::-1], 2)

class ISQIR:
    def __init__(self, gates, name="foo", k=1) -> None:
        self.gb = gates['base']
        self.gi = gates['inductive']
        self.name = name
        self.k=k

    def toQiskit(self, name=None, offset=1, head=True):
        if name == None:
            name = self.name
        result=""
        if head:
            result = "from qiskit import QuantumCircuit\n"
            result += "from math import pi\n\n"
        for gate in self.gb:
            if gate.claim():
                result += gate.prog().toQiskit(head=False)
        for gates in self.gi:
            for gate in gates:
                if gate.claim():
                    result += gate.prog().toQiskit(head=False)
                # print('here',result)
        return result + showProg(self.gb, self.gi, name, self.k, "qiskit", offset)

class PPSA:
    def __init__(self, beta, phaseSum) -> None:
        self.beta = beta
        self.phaseSum = phaseSum

