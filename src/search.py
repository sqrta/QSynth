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
        if move == 'n':
            x1 = BVtrunc(x,n,1)
            x2 = BVtrunc(x, 2*n, n+2) <<n
            y1 = BVtrunc(y,n,1)
            y2 = BVtrunc(y, 2*n, n+2) <<n
            truncEq = delta(BVref(x, 0), BVref(y, 0)) * \
                delta(BVref(x, n+1), BVref(y, n+1))  
        else:
            x1 = BVtrunc(x, n-1)
            x2 = BVtrunc(x, 2*n-1, n+1) << n          
            y1 = BVtrunc(y, n-1)
            y2 = BVtrunc(y, 2*n-1, n+1) << n
            truncEq = delta(BVref(x, n), BVref(y, n)) * \
                delta(BVref(x, 2*n), BVref(y, 2*n))            
        xk = x1 | x2
        yk = y1 | y2
        if move == 'n':
            sumph = foo(n-1, xk, yk)
        else:
            sumph = foo(n-k, xk, yk)

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
    xo, yo, n = BitVecs('x y n', MAXL)
    x = BVtrunc(xo, size(n))
    y = BVtrunc(yo, size(n))
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
    Claim = Implies(And(UGE(n, k), ULT(n,SPACE), ULT(size(n), SPACE), precondition),
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
        '''
        if compon.name == "SJ":



        '''
        return unsat


def showProg(base, left=None, right=None, name="foo", inductExp="-1", backend="sqir"):
    if not base:
        return "No solutions"
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
        prog += name + " n" + inductExp + "; "
        if right:
            prog += sqirName(right)
        prog += "\n\t end."
    elif backend == 'qiskit':
        def qiskitName(ins):
            nameMap = {'CNOT': "cx", "H": 'h'}
            gate = nameMap.get(ins.name, ins.name)
            return gate + "(" + ",".join([str(i) for i in ins.registers]) + ")"

        def circCall(ins, circ="circ"):
            return circ+"." + qiskitName(ins)

        prog += "def " + name + "(circ, n):\n"
        for i in range(len(base)):
            prog += "\tif(n==" + str(i) + "):\n"
            prog += "\t"*2+circCall(base[i]) + "\n\t\treturn\n"
        if left:
            prog += "\tcirc." + qiskitName(left) + "\n"
        prog += "\t" + name + "(circ,n-1)\n"
        if right:
            prog += "\tcirc." + qiskitName(right) + "\n"
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


def search(spec, database, dir,  pre=None, base=1, k=1, move=0, size=lambda x: x):
    gb = []
    gi = (component('None'), component('None'))
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

    end = time.time()
    print("Base step uses {0}s".format(end-start))
    start = time.time()
    if dir == 'both':
        compon = (MAJ("MAJ"), UMA("UMA"))
        ri = verifyInduct(compon, spec, pre, dir, k, move, size)
        if ri==sat:
            gi=compon
        return gb,gi

    for item in database:
        compon = (Ident('I'),item) if dir == "right" else (item,Ident('I'))
        ri = verifyInduct(compon, spec, pre, dir, k, move, size)
        if ri == sat:
            gi = compon
            break
    end = time.time()
    print("Induction step uses {0}s".format(end-start))
    return gb, gi


def strEx(example):
    def binw(n):
        return '{:0{width}b}'.format(n, width=example[1]+1)
    return ("exp(2pi*j*0."+binw(example[0]) + ')', "n="+str(example[1]+1), "x="+binw(example[2]), "y="+binw(example[3]))
