from symbol import yield_stmt
from z3 import *
from adt import phase, sumPhase, sumPhaseMulti
from component import *
from z3tool import *
import time


def basek(foo, intk, n, x, y, size=lambda x: x):
    if intk < 0:
        return None
    k = bv(intk)

    xk = BVtrunc(x, size(k))
    yk = BVtrunc(y, size(k))
    sumph = foo(k, xk, yk)
    return sumPhase([phase(p[0], p[1]) for p in sumph])


def inductk(foo, k, n, x, y, move=0, size=lambda x: x):
    if k < 0:
        return None
    if k == 0:
        return sumPhase([phase(p[0], p[1]) for p in foo(n, x, y)])
    indsumph = None
    if k == 1:
        xk = BVtrunc(x, n-k) << move
        yk = BVtrunc(y, n-k) << move
        sumph = foo(n-k, xk, yk)
        truncEq = 1
        if move < k:
            truncEq *= delta(BVtrunc(x, n, n-k+1+move),
                             BVtrunc(y, n, n-k+1+move))
        if move > 0:
            truncEq *= delta(BVtrunc(x, move-1, 0), BVtrunc(y, move-1, 0))
        indsumph = [phase(truncEq*p[0], p[1] << k) for p in sumph]

    elif k == 2:
        # if move == 'n':
        x1 = BVtrunc(x,n,1)
        x2 = BVtrunc(x, 2*n, n+2) <<n
        y1 = BVtrunc(y,n,1)
        y2 = BVtrunc(y, 2*n, n+2) <<n
        truncEq = delta(BVref(x, 0), BVref(y, 0)) * \
            delta(BVref(x, n+1), BVref(y, n+1))  
        # else:
        #     x1 = BVtrunc(x, n-1)
        #     x2 = BVtrunc(x, 2*n-1, n+1) << n          
        #     y1 = BVtrunc(y, n-1)
        #     y2 = BVtrunc(y, 2*n-1, n+1) << n
        #     truncEq = delta(BVref(x, n), BVref(y, n)) * \
        #         delta(BVref(x, 2*n), BVref(y, 2*n))            
        xk = x1 | x2
        yk = y1 | y2
        # if move == 'n':
        sumph = foo(n-1, xk, yk)
        # else:
        #     sumph = foo(n-k, xk, yk)

        indsumph = [phase(truncEq*p[0], p[1] << k) for p in sumph]
    elif k == 3:
        xk = BVtrunc(x, n-1) | (BVtrunc(x, 2*n-1, n+1) <<
                                n) | (BVtrunc(x, 3*n-1, 2*n+1) << (2*n-1))
        yk = BVtrunc(y, n-1) | (BVtrunc(y, 2*n-1, n+1) <<
                                n) | (BVtrunc(y, 3*n-1, 2*n+1) << (2*n-1))
        sumph = foo(n-1, xk, yk)
        truncEq = delta(BVref(x, n), BVref(y, n)) * delta(BVref(x, 2*n),
                                                          BVref(y, 2*n)) * delta(BVref(x, 3*n), BVref(y, 3*n))
        indsumph = [phase(truncEq*p[0], p[1] << k) for p in sumph]
    return sumPhase(indsumph)


def verifyBase(compon, spec, pre, k, size):
    if k < 0:
        return unsat
    xo, yo, n = BitVecs('x y n', MAXL)
    x = BVtrunc(xo, size(n))
    y = BVtrunc(yo, size(n))
    precondition = pre(n, x, y) if pre else True
    left = basek(spec, k, n, x, y, size)
    right = compon.alpha(n, x, y)
    Claim = Implies(And(n == k, precondition),
                    And(left.z3exp() == right.z3exp(), left.deltas() == right.deltas()))
    s = Solver()
    s.add(Not(Claim))
    r = s.check()

    if r == unsat:
        return sat
    else:
        ''' 
        if compon.name=='H':
            print(k, compon.name, compon.registers)
            print(s.model())
            bvprint(s.model(), x, "x")
            bvprint(s.model(), y, "y")
            bvprint(s.model(), BVtrunc(x, n)*reverse(BVtrunc(y, n), n), "left_should")
            bvprint(s.model(), left.deltas(), "leftdelta")
            bvprint(s.model(), right.deltas(), 'rightdelta')
            bvprint(s.model(), left.z3exp(), "left")
            bvprint(s.model(), right.z3exp(), "right")

        '''
        return unsat


def verifyInduct(compon, spec, pre, dir, k=1, move=0, size=lambda x: x):
    x, y, n = BitVecs('x y n', MAXL)
    # x = BVtrunc(xo, 2*n)
    # y = BVtrunc(yo, 2*n)
    t= Solver()
    t.add(And(x==0b00110, n==3, y==0b00110))

    start = time.time()
    precondition = pre(n, x, y) if pre else True
    left = inductk(spec, 0, n, x, y).z3exp()
    leftcompon = compon[0]
    rightcompon = compon[1]
    terms = leftMultiAlpha(leftcompon, lambda n, x, y: rightMultiAlpha(
        rightcompon, lambda n, x, y: inductk(spec, k, n, x, y, move), n, x, y), n, x, y)
    # if dir == 'left':
    #     terms = leftMultiAlpha(compon, lambda n, x, y: inductk(
    #         spec, k, n, x, y, move), n, x, y)
    # elif dir == 'right':
    #     terms = rightMultiAlpha(compon, lambda n, x, y: inductk(
    #         spec, k, n, x, y, move), n, x, y)


    right = terms.z3exp()
    rightDelta = terms.deltas()
    leftDelta = inductk(spec, 0, n, x, y).deltas()
    s = Solver()
    ''''''
    Claim = Implies(And(UGE(n, 1), ULT(n,SPACE), ULT(size(n), SPACE), precondition),
                    # And(left==right, rightDelta == leftDelta))
                    And(BVtrunc(left, size(n)) == BVtrunc(right, size(n)), rightDelta == leftDelta))
    s.add(Not(Claim))
    r = s.check()

    '''
    end = time.time()
    print("Induction step uses {0}s".format(end-start))
    '''
    if r == unsat:

        return sat
    else:
        '''
        if dir == 'both':
            print(s.model())
            bvprint(s.model(), x, 'x')       
            bvprint(s.model(), y, "y")
            # bvprint(s.model(), left, "left")
            # bvprint(s.model(), right, "right")
            bvprint(s.model(), leftDelta, "leftdelta")
            bvprint(s.model(), rightDelta, "rightdelta")
            print("left")
            for z in leftcompon.Mx(n,x):
                bvprint(s.model(),z, 'z')
                bvprint(s.model(), leftcompon.alpha(n,x,z).deltas(), "zdelta")  
            print("right")   
            for z in rightcompon.My(n,y):
                bvprint(s.model(),z, 'z')
                bvprint(s.model(), rightcompon.alpha(n,z,y).deltas(), "zdelta")        
        
        if compon.name == "SJ":
        '''
        return unsat

def inductcase(spec, database, dir,  pre=None, base=1, k=1):
    start = time.time()
    size = lambda x: k*x
    gi = (component('None'), component('None'))
    move = 'n' if k==3 else 0
    # Add gate no need for base case
    if k>1:
        database=[Fredkin("fredkin", ['n']), Peres("peres", ['n']), HN("H", ['n']), CCX_N("ccxn")] + database
    if dir == 'both':  
        for leftone in database:
            for rightone in database:
                compon = (leftone, rightone)
                ri = verifyInduct(compon, spec, pre, dir, k, move, size)
                if ri==sat:
                    gi=compon
                    return gi
        return gi
    for item in database:
        compon = (Ident('I'),item) if dir == "right" else (item,Ident('I'))
        ri = verifyInduct(compon, spec, pre, dir, k, move, size)

        if ri == sat:
            gi = compon
            return gi

    end = time.time()
    return gi
    # print("Induction step uses {0}s".format(end-start))

def showProg(base, gi, name="foo", inductExp=1, backend="sqir"):
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
        prog = qiskitbackend(base,left,right, name, inductExp)
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

def qiskitbackend(base, left=None, right=None, name="foo", spec=1):
    prog = ""
    def qiskitName(ins):
        nameMap = {'CNOT': "cx", "H": 'h'}
        gate = ins.qiskitName()
        return gate + "(" + ",".join([str(i) for i in ins.registers]) + ")"

    def circCall(ins, circ="circ"):
        return circ+"." + qiskitName(ins)

    def gatelist(gates,tabnum, circ="circ"):
        instructions = gates
        if not isinstance(gates, list):
            instructions = [gates]
        ops = [circCall(gate, circ) for gate in instructions]
        return ntab(tabnum)+ f"\n{ntab(tabnum)}".join(ops) + "\n"

    prog += "def " + name + "(N):\n"
    size = "N+1" if spec==1 else f"{spec}*N+1"
    prog+=f"\tcircuit=QuantumCircuit({size})\n"     
    prog += "\tdef S(circ, n):\n"   
    for i in range(len(base)):       
        prog += "\t\tif(n==" + str(i) + "):\n"
        prog += gatelist(base[i], 3)
    prog += f"\t\telse:\n"
    if left:
        prog += gatelist(left.decompose(), 3)
    prog += f"{ntab(3)}S(circ,n-1)\n"
    if right:
        prog += gatelist(right.decompose(), 3)
    prog+="\tS(circuit,N)\n\treturn circuit"
    return prog

def success(gb,gi):
    for gate in gb:
        if gate.name == 'None':
            return False
    for gate in gi:
        if gate.name == 'None':
            return False
    return True

def synthesis(spec, database,  pre=None):
    for dir in ['right','left', 'both']:
        for depth in range(1,4):
            gb,gi = search(spec,database, dir, pre, k=depth)
            if success(gb,gi):
                return gb,gi
    return None,None

def ntab(n):
    return "\t"*n

def strEx(example):
    def binw(n):
        return '{:0{width}b}'.format(n, width=example[1]+1)
    return ("exp(2pi*j*0."+binw(example[0]) + ')', "n="+str(example[1]+1), "x="+binw(example[2]), "y="+binw(example[3]))

def reverseb(n, width):
    b = '{:0{width}b}'.format(n, width=width)
    return int(b[::-1], 2)


def QFTex(k):
    examples = []
    for i in range(1, k+1):
        for j in range(2**i):
            for t in range(2**i):
                examples.append([j*reverseb(t, i) % 2**k, i-1, j, t])
    return examples

def Adderex(k):
    examples = []
    for i in range(1, k+1):
        for j in range(2**i):
            for t in range(2**i):
                examples.append([j*reverseb(t, i) % 2**k, i-1, j, t])    

# examples = [[0, 0, 1, 1], [0,0,0,0], [0, 2, 0b011, 0b011], [0, 2, 0b010, 0b110], [0,4,0b00101, 0b11100]]

def examplesFunc(n, x, y):
    global examples
    result = reduce(lambda a, b: If(
        And(n == b[1], x == b[2], y == b[3]), bv(b[0]), a), examples, bv(0))
    return result


def examplespec(n, x, y):
    tmp = examplesFunc(n, x, y)
    return [(bv(1), tmp)]


def getpre(n, x, y):
    pre = []
    global examples
    for ex in examples:
        pre.append(And(n == ex[1], x == ex[2], y == ex[3]))
    return Or(pre)

def Hnspec(n, x, y):
    Eq = delta(BVtrunc(x,n-1), BVtrunc(y,n-1))
    result = BVref(x,n) & BVref(y,n)
    return [(Eq, result << n)]

def Adderspec(n, x, y):
    Eq1 = delta(BVtrunc(x, n/2, 1), BVtrunc(y, n/2, 1))
    addone = BVtrunc(x, n/2, 1) + BVtrunc(x,n,n/2+1) + BVref(x,0)
    result = BVtrunc(y,n, n/2 + 1) | BVref(y,0)<<(n/2)
    Eq2 = delta(BVtrunc(addone, n/2),  BVtrunc(result, n/2))
    return [(Eq1*Eq2, bv(0))]

def C_RZN(t, x, y, n, m):
    truncEq = delta(BVtrunc(x, t-1), BVtrunc(y, t-1))
    cond = truncEq * delta(BVref(y, t), 1) * (BVtrunc(x, t, t-n) << (m-n-1))
    return cond

def C_RZ(y, t, n, m):
    return delta(BVref(y, t), 1)*(BVref(y, t-n) << (m-n-1))

def search(spec, database, dir,  pre=None, base=1, k=1):
    size = lambda x: k*x
    gb = []
    
    start = time.time()
    for i in range(base):
        tmp = None
        for item in database:
            rb = verifyBase(item, spec, pre, i, size)
            # print(rb,item.name)
            if rb == sat:
                tmp = item
                break
        if tmp:
            gb.append(tmp)
        else:
            gb.append(component('None'))
    gi = inductcase(spec, database, dir,  pre, k=k)
    end = time.time()
    # print("Base step uses {0}s".format(end-start))

    return gb, gi