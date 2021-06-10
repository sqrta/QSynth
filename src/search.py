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
    if k<1:
        return unsat
    x, y, n = BitVecs('x y n', MAXL)
    precondition = pre(n, x) if pre else True
    Claim = Implies(And(n >= 0, n < 1, precondition),
                         basek(spec, k-1, n, x, y).z3exp() == compon.alpha(n, x, y).z3exp())
    s = Solver()
    s.add(Not(Claim))
    r = s.check()

    if r == unsat:
        return sat
    else:
        return unsat

def verifyInduct(compon, spec, pre, k=1):
    x, y, n = BitVecs('x y n', MAXL)
    start = time.time()
    precondition = pre(n, x) if pre else True
    left = inductk(spec, 0, n, x, y).z3exp()
    terms = []
    for foo in compon.My():
        z = foo(n, x)
        terms.append(sumPhaseMulti(compon.alpha(n, x, z),
                                   inductk(spec, k, n, z, y)).z3exp())

    right = sum(terms)
    s = Solver()
    ''''''
    Claim = Implies(And(n > 0, n < SPACE, precondition),
                    BVtrunc(left, n) == BVtrunc(right, n))
    s.add(Not(Claim))
    r = s.check()
    '''
    end = time.time()
    print("Induction step uses {0}s".format(end-start))
    '''
    
    if r == unsat:
        return sat
    else:
        return unsat

def showProg(base, induct, name="foo"):
    if not base or not induct:
        return "No solutions"
    prog = "Inductive "+name + " (n : nat) : Unitary :=\n"
    prog += "\t match n with\n"
    prog += "\t\t | 0 => " + base.name + "\n"
    prog += "\t\t | S n' => " + induct.name + "\n"
    prog += "\t end."
    return prog

def search(spec, database, pre=None, k=1):
    gb=None
    gi=None
    start = time.time()
    for item in database:
        rb = verifyBase(item, spec, pre, k)
        print(rb,item.name)
        if rb == sat:
            gb=item
            break
    print(gb.name)    
    end = time.time()
    print("Base step uses {0}s".format(end-start))
    start = time.time()
    for item in database:
        ri = verifyInduct(item, spec, pre, k)
        if ri == sat:
            gi = item
            break
    end = time.time()
    print("Induction step uses {0}s".format(end-start))
    return showProg(gb,gi,"QFT")

