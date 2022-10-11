from functools import reduce
from sys import prefix
from search import *


def C_RZN(t, x, y, n, m):
    truncEq = delta(BVtrunc(x, t-1), BVtrunc(y, t-1))
    cond = truncEq * delta(BVref(y, t), 1) * (BVtrunc(x, t, t-n) << (m-n-1))
    return cond


def C_RZ(y, t, n, m):
    return delta(BVref(y, t), 1)*(BVref(y, t-n) << (m-n-1))


def QFT(n, x, y):
    u = BVtrunc(x, n)*reverse(BVtrunc(y, n), n)
    return BVtrunc(u, n)


def QFTspec(n, x, y):
    u = BVtrunc(x, n)*reverse(BVtrunc(y, n), n)
    return [(bv(1), BVtrunc(u, n))]

def Adderspec(n, x, y):
    Eq1 = delta(BVtrunc(x, n/2, 1), BVtrunc(y, n/2, 1))
    addone = BVtrunc(x, n/2, 1) + BVtrunc(x,n,n/2+1) + BVref(x,0)
    result = BVtrunc(y,n, n/2 + 1) | BVref(y,0)<<(n/2)
    Eq2 = delta(BVtrunc(addone, n/2),  BVtrunc(result, n/2))
    return [(Eq1*Eq2, bv(0))]

def rippleAdderSpec(n,x,y):
    Eq1 = delta(BVtrunc(x, 2*n, 1), BVtrunc(y, 2*n, 1))
    addone = BVtrunc(x, n, 1) + BVtrunc(x,2*n,n+1) + BVref(x,0)
    result = BVtrunc(y, 3*n, 2*n + 1) | BVref(y,0)<<n
    Eq2 = delta(BVtrunc(addone, n),  BVtrunc(result, n))
    return [(Eq1*Eq2, bv(0))]

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

examples = [[0, 0, 1, 1], [0,0,0,0], [0, 2, 0b011, 0b011], [0, 2, 0b010, 0b110], [0,4,0b00101, 0b11100]]


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

def GHZspec(n, x, y):
    Eq = delta(BVtrunc(y,n), bv(0)) | delta(BVtrunc(y,n), (bv(1)<<(n+1)) -1)
    return [(Eq, bv(0))]

def IDspec(n,x,y):
    return [(delta(x,y), bv(0))]


if __name__ == "__main__":
    from component import database

    gb, gi = search(QFTspec, database, 'left', lambda n,x,y : And(ULT(x,(bv(2)<<n)), ULT(y, (bv(2)<<n))), 1, 1)
    print(showProg(gb, gi,None, 'QFT', "-1"))
    gb, gi = search(GHZspec, database, 'right', lambda n,x,y : x==bv(0), 1, 1)
    print(showProg(gb, None,gi, 'GHZ', "-1"))
    gb, gi = search(Adderspec, database, 'right', lambda n,x,y : n%2==0, 1, 2,1)
    print(showProg(gb, None,gi, 'adder', "-1"))
    gb, gi = search(rippleAdderSpec, database, 'right', lambda n,x,y : And(BVref(x,0)==0, ULT(x, bv(1)<<2*n+1)), 1, 3, size=lambda x: 3*x)
    print(showProg(gb, None,gi, 'adder', "-1"))
   