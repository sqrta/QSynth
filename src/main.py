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

def USspec(n, x, y):
    return 


if __name__ == "__main__":
    database = [H0("H 0"), HN("H n"), CRZN("C_RZ n")]
    print(search(QFTspec, database, lambda n,x : True))