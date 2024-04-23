from adt import *
from component import *
from search import *

class Variable:
    def __init__(self, name, length= lambda n : n) -> None:
        self.length = length
        self.name = name

class Specification:
    def __init__(self) -> None:
        pass

    def setInput(self, varList):
        self.input = varList

    def setOutput(self, expr):
        self.expr = expr

def QsynthSpec(func, n, x, y):
    pass

class SumExpr:
    def __init__(self, expr, phase) -> None:
        self.expr = expr
        self.phase = phase


def Input(x, lenList):
    start = 0
    varList = []
    interval = []
    for length in lenList:
        end = start + length-1
        varList.append(BVtrunc(x, end, start))
        interval.append((start, end))
        start += length
    varList.append(interval)
    # print(varList)
    return tuple(varList)

def getSpec(y, intervals, Output):
    index = [BVtrunc(y, item[1], item[0]) for item in intervals]
    return getbind(index, Output)

def getbind(Input, Output):
    phase = bv(0)
    Eqs = []
    for i in range(len(Output)):
        O = Output[i]
        I = Input[i]
        if isinstance(O, SumExpr):
            Eqs.append(bvalue(O.expr))
            phase += O.phase
        else:
            Eqs.append(Equal(I, O))
    return [(Product(*Eqs), phase)]

def OutputIndex(lenList):
    start = 0
    interval = []
    for length in lenList:
        end = start + length -1
        interval.append((start, end))
        start += length
    return interval

def SumVarClaim(n,x,y, index):
    return BVtrunc(y, index[1], index[0])