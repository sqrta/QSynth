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
    if k == 0:
        return sumPhase([phase(p[0], p[1]) for p in foo(n, x, y)])
    indsumph = None
    if k==1:
        xk = BVtrunc(x, n-k)
        yk = BVtrunc(y, n-k)
        sumph = foo(n-k, xk, yk)
        truncEq = delta(BVtrunc(x, n, n-k+1), BVtrunc(y, n, n-k+1))
        indsumph = [phase(truncEq*p[0], p[1] << k) for p in sumph]
        
    elif k==2:
        x1 = BVtrunc(x, n/2-1)
        x2 = BVtrunc(x, n-1, n/2+1)<<(n/2)
        xk = x1 | x2
        y1 = BVtrunc(y, n/2-1)
        y2 = BVtrunc(y, n-1, n/2+1)<<(n/2)
        yk = y1 | y2
        sumph = foo(n-k, xk, yk)
        truncEq = delta(BVref(x,n), BVref(y,n))* delta(BVref(x,n/2),BVref(y,n/2))
        indsumph = [phase(truncEq*p[0], p[1] << k) for p in sumph]
    return sumPhase(indsumph)

def leftMultiAlpha(compon, alpha, n, x, y):
    terms = []
    for foo in compon.My():
        z = foo(n, x)
        terms.append(compon.alpha(n, x, z)*alpha(n, z, y))
    return sum(terms)


def verifyBase(compon, spec, pre, k):
    if k < 0:
        return unsat
    xo, yo, n = BitVecs('x y n', MAXL)
    x = BVtrunc(xo, n)
    y = BVtrunc(yo, n)
    precondition = pre(n, x, y) if pre else True
    left = basek(spec, k, n, x, y)
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
        if k==0 and compon.name=='I':
            print(k, compon.name)
            print(s.model())
            bvprint(s.model(), left.deltas())
            bvprint(s.model(), right.deltas())
            bvprint(s.model(), left.z3exp())
            bvprint(s.model(), right.z3exp())
        '''
        return unsat


def verifyInduct(compon, spec, pre,dir, k=1):
    xo, yo, n = BitVecs('x y n', MAXL)
    x = BVtrunc(xo, n)
    y = BVtrunc(yo, n)
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
    Claim = Implies(And(n >= k, n < SPACE, precondition),
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
        if compon.name == "MAJ n/2 n":
            
            print(s.model())     
             
            for foo in compon.Mx():
                z = foo(n, y)
                bvprint(s.model(), z, "z")
                x1 = BVtrunc(z, n/2-1)
                x2 = BVtrunc(z, n-1, n/2+1)<<(n/2)
                zk = x1 | x2
                bvprint(s.model(), zk, "zk")
                bvprint(s.model(), compon.alpha(n, z, y).deltas(),"zdelta")
                bvprint(s.model(),inductk(spec, k, n, x, z).deltas(), 'induct')
                bvprint(s.model(), compon.alpha(n, z, y).z3exp(),"zdelta2")
                bvprint(s.model(),inductk(spec, k, n, x, z).z3exp(), 'induct2')
                #terms.append(sumPhaseMulti(compon.alpha(n, z, y),
                                        #inductk(spec, k, n, x, z)))   
            bvprint(s.model(), left)
            bvprint(s.model(), right)
            bvprint(s.model(), leftDelta)
            #bvprint(s.model(), rightDelta)
        '''   
        return unsat


def showProg(base, induct, dir, name="foo", inductExp="-1"):
    if not base or not induct:
        print(base, induct)
        return "No solutions"
    prog = "Fixpoint "+name + " (n : nat) : Unitary :=\n"
    prog += "\t match n with\n"
    for i in range(len(base)):
        prog += "\t\t | " + str(i)+ " => " + base[i].name + "\n"
    if dir == 'right':
        prog += "\t\t | _ => " + name + " n" + inductExp +"; " + induct.name + "\n"
    else:
        prog += "\t\t | S n' => " + induct.name + '; ' + name + " n" + inductExp + "\n"
    prog += "\t end."
    return prog


def search(spec, database, dir,  pre=None,b=1, k=1):
    gb = []
    gi = component('None')
    start = time.time()
    for i in range(b):
        tmp = None
        for item in database:
            rb = verifyBase(item, spec, pre, i)
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
    for item in database:
        ri = verifyInduct(item, spec, pre, dir, k)
        if ri == sat:
            gi = item
            break
    end = time.time()
    print("Induction step uses {0}s".format(end-start))
    return gb,gi


def strEx(example):
    def binw(n):
        return '{:0{width}b}'.format(n, width=example[1]+1)
    return ("exp(2pi*j*0."+binw(example[0]) + ')', "n="+str(example[1]+1), "x="+binw(example[2]), "y="+binw(example[3]))
