from symbol import yield_stmt
from z3 import *
from adt import phase, sumPhase, sumPhaseMulti
from component import *
from z3tool import *
import time
import copy


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
            truncEq *= Equal(BVtrunc(x, n, n-k+1+move),
                             BVtrunc(y, n, n-k+1+move))
        if move > 0:
            truncEq *= Equal(BVtrunc(x, move-1, 0), BVtrunc(y, move-1, 0))
        indsumph = [phase(truncEq*p[0], p[1] << k) for p in sumph]

    elif k == 2:
        # if move == 'n':
        x1 = BVtrunc(x,n,1)
        x2 = BVtrunc(x, 2*n, n+2) <<n
        y1 = BVtrunc(y,n,1)
        y2 = BVtrunc(y, 2*n, n+2) <<n
        truncEq = Equal(BVref(x, 0), BVref(y, 0)) * \
            Equal(BVref(x, n+1), BVref(y, n+1))  
        # else:
        #     x1 = BVtrunc(x, n-1)
        #     x2 = BVtrunc(x, 2*n-1, n+1) << n          
        #     y1 = BVtrunc(y, n-1)
        #     y2 = BVtrunc(y, 2*n-1, n+1) << n
        #     truncEq = Equal(BVref(x, n), BVref(y, n)) * \
        #         Equal(BVref(x, 2*n), BVref(y, 2*n))            
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
        truncEq = Equal(BVref(x, n), BVref(y, n)) * Equal(BVref(x, 2*n),
                                                          BVref(y, 2*n)) * Equal(BVref(x, 3*n), BVref(y, 3*n))
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
    leftcompon = compon[0][-1::-1]
    rightcompon = compon[1]
    func0 = lambda n, x, y: inductk(spec, k, n, x, y, move)
    # recall = lambda n, x, y: rightMultiAlpha(rightcompon, tmp, n, x, y)
    # print("length",len(compon[1]))
    funcs = {0:func0}
    for i in range(1,len(rightcompon)+1):
        item = rightcompon[i-1]
        funcs[i] = lambda n, x, y: rightMultiAlpha(item, funcs[i-1], n, x, y)
    
    lfuncs = {0:funcs[len(rightcompon)]}
    for i in range(1,len(leftcompon)+1):
        comp = leftcompon[i-1]
        lfuncs[i]= lambda n, x, y: leftMultiAlpha(comp, lfuncs[i-1], n, x, y)
    terms = lfuncs[len(leftcompon)](n,x,y)


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
        if leftcompon[0].name == "xmaj" and rightcompon[0].name=="xuma" and k==2:
            print(s.model())
            bvprint(s.model(), x, 'x')       
            bvprint(s.model(), y, "y")
            bvprint(s.model(), left, "left")
            bvprint(s.model(), right, "right")
            bvprint(s.model(), leftDelta, "leftdelta")
            bvprint(s.model(), rightDelta, "rightdelta")
            print("left")
            a=0
            b=1
            c=n+1
            
            for z in leftcompon[0].Mx(n,x):
                bvprint(s.model(),z, 'z')
                bvprint(s.model(), leftcompon[0].alpha(n,x,z).deltas(), "zdelta")  

                bvprint(s.model(), Equal(BVref(z, a), BVref(x, b) ^ BVref(x, a)), "eq2")
                bvprint(s.model(), Equal(BVref(z, c), (BVref(~x, c)) ^ BVref(x, b)), "eq3")
                bvprint(s.model(), Equal(BVref(z, b), (BVref(x, b)* (BVref(~x, c))) ^
                (BVref(x, b) * BVref(x, a)) ^ (BVref(x, a)*(BVref(~x, c)))), "eq4")  

        '''
        return unsat

def inductcase(spec, database, dir,  pre=None, base=1, k=1):
    start = time.time()
    size = lambda x: k*x
    gi = None
    move = 'n' if k==3 else 0
    # Add gate no need for base case
    if k>1:
        # database = [Xmaj("xmaj",[0,1,'n+1']), Xuma("xuma", [0,1,'n+1'])]
        database=[Fredkin("fredkin", [0,1,'n+1']), Peres("peres",[0,1,'n+1']), HN("H", ['n']), CCX_N("ccxn"), Xmaj("xmaj",[0,1,'n+1']), Xuma("xuma", [0,1,'n+1'])] + database
    # comp = ([Xn("X", "n+1"), Fredkin("fredkin", [0,1,'n+1'])], [Peres("peres",[0,1,'n+1']), Xn("X", "n+1")])
    
    # ri = verifyInduct(comp, spec, pre, dir, k, move, size)
    # if ri==sat:
    #     return comp
    # else:
    #     return None
    if dir == 'both':  
        for leftone in database:
            for rightone in database:
                compon = ([leftone], [rightone])
                ri = verifyInduct(compon, spec, pre, dir, k, move, size)
                if ri==sat:
                    gi=compon
                    return gi
        return None
    for item in database:
        compon = ([Ident('I')],[item]) if dir == "right" else ([item],[Ident('I')])
        ri = verifyInduct(compon, spec, pre, dir, k, move, size)

        if ri == sat:
            gi = compon
            return gi

    end = time.time()
    return gi
    # print("Induction step uses {0}s".format(end-start))

def success(gb,gi):
    for gate in gb:
        if gate.name == 'None':
            return False
    if gi==None:
        return False
    return True

def synthesis(amplitude, gateset,  hypothesis=lambda n,x,y:True):
    for dir in ['right','left', 'both']:
        for depth in range(1,4):
            gb,gi = search(amplitude,gateset, dir, hypothesis, k=depth)
            if success(gb,gi):
                return ISQIR({'base':gb, 'inductive':gi}, k= depth)
                
    return ISQIR({'base':None, 'inductive':None}, k=1)


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
    Eq = Equal(BVtrunc(x,n-1), BVtrunc(y,n-1))
    result = BVref(x,n) & BVref(y,n)
    return [(Eq, result << n)]

def Adderspec(n, x, y):
    Eq1 = Equal(BVtrunc(x, n/2, 1), BVtrunc(y, n/2, 1))
    addone = BVtrunc(x, n/2, 1) + BVtrunc(x,n,n/2+1) + BVref(x,0)
    result = BVtrunc(y,n, n/2 + 1) | BVref(y,0)<<(n/2)
    Eq2 = Equal(BVtrunc(addone, n/2),  BVtrunc(result, n/2))
    return [(Eq1*Eq2, bv(0))]

def C_RZN(t, x, y, n, m):
    truncEq = Equal(BVtrunc(x, t-1), BVtrunc(y, t-1))
    cond = truncEq * Equal(BVref(y, t), 1) * (BVtrunc(x, t, t-n) << (m-n-1))
    return cond

def C_RZ(y, t, n, m):
    return Equal(BVref(y, t), 1)*(BVref(y, t-n) << (m-n-1))

def search(specification, database, dir,  pre=None, base=1, k=1, offset=0):
    size = lambda x: k*x+offset
    gb = []
    spec = specification.phaseSum
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