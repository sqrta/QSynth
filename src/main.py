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
    return [(1, BVtrunc(u, n))]


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


examples = QFTex(1)


def examplesFunc(n, x, y):
    global examples
    result = reduce(lambda a, b: If(
        And(n == b[1], x == b[2], y == b[3]), bv(b[0]), a), examples, bv(0))
    return result


def examplespec(n, x, y):
    tmp = examplesFunc(n, x, y)
    return [(1, tmp)]


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


if __name__ == "__main__":
    database = [H0("H 0"), HN("H n"), CRZN("C_RZN n"), move1("move 1")]
    '''
    print(search(Hnspec, database, "left"))
    '''
    print("Examples: list[0] = alpha(n,x,y)")
    exStr = [strEx(i) for i in examples]
    for ex in exStr:
        print(', '.join(ex))
    
    print('')
    x, y, n = BitVecs("x y n", MAXL)
    #print(examplesFunc(n,x,y))
    a = [And(x == 0, y == 1), And(x == 1, y == 2)]
    
    prog=search(examplespec, database,'left', lambda n, x, y: And(getpre(n, x, y)))
    print("\nResult Program:")
    crznProg = showProg(H0("H 0"), CRZ0N("move 1; C_RZ 0 n"), 'right', "C_RZN")
    print(crznProg + "\n")    
    print(prog)
    