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

def IDspec(n,x,y):
    return [(delta(x,y), bv(0))]


if __name__ == "__main__":
    database = [H0("H 0"), HN("H n"), CRZN("C_RZN n"), move1("move 1"), Ident('I'), MAJN("OneBitAdd n-1 n 0 ; SWAP n-1 n/2")]
    '''     
    print("Examples: list[0] = alpha(n,x,y)")
    exStr = [strEx(i) for i in examples]
    for ex in exStr:
        print(', '.join(ex))
    
    print('')
    x, y, n = BitVecs("x y n", MAXL)
    #print(examplesFunc(n,x,y))
    a = [And(x == 0, y == 1), And(x == 1, y == 2)]
    
    gb,gi=search(examplespec, database,'left', lambda n, x, y: And(getpre(n, x, y)),1)
    print("\nResult Program:")
    crznProg = showProg([H0("H 0")], CRZ0N("move 1; C_RZ 0 n"), 'right', "C_RZN")
    print(crznProg + "\n")    
    print(showProg(gb, gi, 'left', 'QFT'))
    '''
    gb, gi = search(Adderspec, database, 'right', lambda n,x,y : BVref(n,0)==0, 2, 2)
    print(showProg(gb,gi,'right', 'Adder', "-2"))
   