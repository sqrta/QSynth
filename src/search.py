from z3 import *
from adt import phase, sumPhase, sumPhaseMulti
from component import *
from z3tool import *
import time


def basek(foo, intk, n, x, y):
    if intk < 0:
        return None
    k = bv(intk)

    xk = BVtrunc(x, k)
    yk = BVtrunc(y, k)
    sumph = foo(k, xk, yk)
    return sumPhase([phase(p[0], p[1]) for p in sumph])


def inductk(foo, k, n, x, y):
    if k < 0:
        return None
    xk = BVtrunc(x, n-k)
    yk = BVtrunc(y, n-k)
    sumph = foo(n-k, xk, yk)

    if k == 0:
        return sumPhase([phase(p[0], p[1]) for p in sumph])
    else:
        truncEq = delta(BVtrunc(x, n, n-k+1), BVtrunc(y, n, n-k+1))
        indsumph = [phase(truncEq*p[0], p[1] << k) for p in sumph]
        return sumPhase(indsumph)


def leftMultiAlpha(compon, alpha, n, x, y):
    terms = []
    for foo in compon.My():
        z = foo(n, x)
        terms.append(compon.alpha(n, x, z)*alpha(n, z, y))
    return sum(terms)


def verifyBase(compon, spec, pre, k=1):
    if k < 1:
        return unsat
    x, y, n = BitVecs('x y n', MAXL)
    precondition = pre(n, x, y) if pre else True
    left = basek(spec, k-1, n, x, y)
    right = compon.alpha(n, x, y)
    Claim = Implies(And(n >= 0, n < 1, precondition),
                    And(left.z3exp() == right.z3exp(), left.deltas() == right.deltas()))
    s = Solver()
    s.add(Not(Claim))
    r = s.check()

    if r == unsat:
        return sat
    else:
        return unsat


def verifyInduct(compon, spec, pre,dir, k=1):
    x, y, n = BitVecs('x y n', MAXL)
    start = time.time()
    precondition = pre(n, x, y) if pre else True
    left = inductk(spec, 0, n, x, y).z3exp()
    terms = []
    if dir=='left':
        for foo in compon.My():
            z = foo(n, x)
            terms.append(sumPhaseMulti(compon.alpha(n, x, z),
                                    inductk(spec, k, n, z, y)))
    elif dir=='right':
        for foo in compon.Mx():
            z = foo(n, y)
            terms.append(sumPhaseMulti(compon.alpha(n, z, y),
                                    inductk(spec, k, n, x, z)))        

    right = sum([term.z3exp() for term in terms])
    rightDelta = sum([term.deltas() for term in terms])
    leftDelta = inductk(spec, 0, n, x, y).deltas()
    s = Solver()
    ''''''
    Claim = Implies(And(n > 0, n < SPACE, precondition),
                    And(BVtrunc(left, n) == BVtrunc(right, n), rightDelta == leftDelta))
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
        if compon.name == "move 1":
            print(s.model())
            for foo in compon.Mx():
                z = foo(n, y)
                bvprint(s.model(), z, "z")
                bvprint(s.model(), compon.alpha(n, z, y).deltas(),"zdelta")
                bvprint(s.model(),inductk(spec, k, n, x, z).deltas(), 'induct')
                bvprint(s.model(), compon.alpha(n, z, y).z3exp(),"zdelta2")
                bvprint(s.model(),inductk(spec, k, n, x, z).z3exp(), 'induct2')
                #terms.append(sumPhaseMulti(compon.alpha(n, z, y),
                                        #inductk(spec, k, n, x, z)))    
            bvprint(s.model(), left)
            bvprint(s.model(), right)
            bvprint(s.model(), leftDelta)
            bvprint(s.model(), rightDelta)
            '''
        return unsat


def showProg(base, induct, dir, name="foo"):
    if not base or not induct:
        print(base, induct)
        return "No solutions"
    prog = "Fixpoint "+name + " (n : nat) : Unitary :=\n"
    prog += "\t match n with\n"
    prog += "\t\t | 0 => " + base.name + "\n"
    if dir == 'right':
        prog += "\t\t | S n' => " + name + " n'; " + induct.name + "\n"
    else:
        prog += "\t\t | S n' => " + induct.name + '; ' + name + " n' " + "\n"
    prog += "\t end."
    return prog


def search(spec, database, dir,  pre=None, k=1):
    gb = None
    gi = None
    start = time.time()
    for item in database:
        rb = verifyBase(item, spec, pre, k)
        # print(rb,item.name)
        if rb == sat:
            gb = item
            break

    end = time.time()
    print("Base step uses {0}s".format(end-start))
    start = time.time()
    for item in database:
        ri = verifyInduct(item, spec, pre, dir, k)
        if ri == sat:
            gi = item
            break
    end = time.time()
    print("Induction step uses {0}s".format(end-start))
    return showProg(gb, gi,dir, "QFT")


def strEx(example):
    def binw(n):
        return '{:0{width}b}'.format(n, width=example[1]+1)
    return ("exp(2pi*j*0."+binw(example[0]) + ')', "n="+str(example[1]+1), "x="+binw(example[2]), "y="+binw(example[3]))
