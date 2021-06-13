from pkg_resources import ResolutionError
from z3tool import *
from functools import reduce
import time
instSet = {1: (2, 'bvadd'), 2: (2, 'bvsub'), 3: (2, 'bvmul'), 4: (2, 'bvrev'),
           5: (2, 'bvand'), 6: (2, 'bvor'), 7: (1, 'bvneg'), 8: (0, "setZero"), 9: (3, "ite"), 10: (2, "bveq"), 11: (2, "bvneq"), 12:(1,"Nonzero")}

prog = [[1, 0, 1], [2, 3, 2], [8]]


def combine(a, b):
    return [i + [j] for i in a for j in b]


def oneInst(k, maxline):
    arity = instSet[k][0]
    inst = [[k]]
    for i in range(arity):
        inst = combine(inst, list(range(maxline)))
    return inst


def allInst(instSet, maxline):
    insts = []
    for k in instSet:
        insts += oneInst(k, maxline)
    return insts


def interpret(prog, inputs):
    for i in range(len(prog)):
        inst = prog[i]
        s = inst[0]
        a = inputs[inst[1]] if len(inst) > 1 else 0
        b = inputs[inst[2]] if len(inst) > 2 else 0
        c = inputs[inst[3]] if len(inst) > 3 else 0
        result = 0
        if s == 1:
            result = a + b
        elif s == 2:
            result = a - b
        elif s == 3:
            result = a * b
        elif s == 4:
            result = reverse(a, b)
        elif s == 5:
            result = a & b
        elif s == 6:
            result = a | b
        elif s == 7:
            result = - a
        elif s == 8:
            result = 0
        elif s == 9:
            result = b if a == 1 else c
        elif s == 10:
            result = 1 if a == b else 0
        elif s == 11:
            result = 0 if a == b else 1
        elif s==12:
            result = 0 if a==0 else 1

        inputs.append(result)
    return inputs[-1]


def verify(prog, examples):

    for example in examples:
        if example[0] != interpret(prog, example[1:]):
            return False
    return True


def search(instSet, maxline, arity, examples):
    candidates = [[]]
    for i in range(1, maxline+1):
        print(i)
        candidates = combine(candidates, allInst(instSet, arity + i - 1))
        for prog in candidates:
            if verify(prog, examples):
                return prog
    return None


def genPrepare(k, foo):
    examples = []
    for i in range(k):
        for j in range(2**k):
            examples.append([foo(j), i, 0, j])
    return examples


def wstate(x):
    return 1 if x & (-x) == x and x != 0 else 0


examples = genPrepare(3, wstate)
print(examples)
prog = [[7,2],[5,3,2], [10,2,4], [12,2],[10,5,6]]
for ex in examples:
    if ex[0]!=interpret(prog, ex[1:]):
        print(ex)
        print(interpret(prog, ex[1:]))
        exit(0)
start = time.time()
print(verify(prog,examples))
candidates = [[]]
for i in range(1,6):
    print(i)
    candidates = combine(candidates, allInst([5, 7, 10, 12], 3 + i - 1))
print(candidates[0])
if prog in candidates:
    print("yes")
#print(search([5, 7, 10, 12], 7, 3, examples))
end =  time.time()
print('Ues {0}s'.format(start-end))
print(interpret(prog, [5, 6, 7]))
