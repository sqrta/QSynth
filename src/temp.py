from z3 import *
from adt import *
from component import *
from z3tool import *
# import time
from qsynth import synthesis, StandardGateSet, PPSA, Input, getSpec, SumVarClaim,SumExpr, OutputIndex

# Full Adder |A>|B>|c>|0> -> |A>|B>|A+B>|c> n = 1 
x = BitVec('x',16)
y = BitVec('y',16)
n = BitVec('y',16)
A, B, c0, C, intervals = Input(x, [1,1,1,1])
sum = A+B+c0
Output = [A, B, BVref(sum,0), BVref(sum,1)]
left = sumPhase([phase(p[0],p[1]) for p in getSpec(y, intervals, Output)])
cir = [Toffoli('ccx', [Index(0,0), Index(0,1), Index(0,3)]), CNOT('cx', [Index(0,0), Index(0,1)]), 
       Toffoli('ccx', [Index(0,1), Index(0,2), Index(0,3)]), CNOT('cx', [Index(0,1), Index(0,2)]), 
       CNOT('cx', [Index(0,0), Index(0,1)])]
fun0 = lambda n, x, y: Ident('I').alpha(n,x,y)
funcs = {0:fun0}
for i in range(1,len(cir)+1):
    item = cir[i-1]
    def f(n,x,y,j=i):
        return rightMultiAlpha(item, funcs[j-1], n, x, y)
    funcs[i] = f
right = funcs[5](1,x,y)
right = RecurPackRight(cir, fun0, n, x, y)
claim1 = Implies(And(BVref(x,2)==0,BVref(x,3)==0, ULT(x,16), ULT(y,16)),
                 And(left.z3exp() == right.z3exp(), left.deltas() == right.deltas()))
s1 = Solver()
s1.add(Not(claim1))
r1 = s1.check()
print (r1)
if r1==sat:

    print(s1.model())
    defuncs = {0:fun0}
    circ = cir[0:2]
    for i in range(1,len(circ)+1):
        item = cir[i-1]
        def f(n,x,y,j=i):
            return rightMultiAlpha(item, defuncs[j-1], n, x, y)
        defuncs[i] = f
    toTest = defuncs[len(circ)]
    debug0 = toTest(1,x,bv(0b1011)).deltas()

    bvprint(s1.model(), x, "x")
    bvprint(s1.model(), y, "y")
    bvprint(s1.model(), BVtrunc(x, 1)*reverse(BVtrunc(y, 1), 1), "left_should")
    bvprint(s1.model(), left.deltas(), "leftdelta")
    bvprint(s1.model(), right.deltas(), 'rightdelta')
    bvprint(s1.model(), left.z3exp(), "left")
    bvprint(s1.model(), right.z3exp(), "right")


# Eq1 = Equal(BVref(x,0), BVref(y,0))
# Eq2 = Equal(BVref(x,1), BVref(y,1))
# Eq3 = Equal(BVref(y, 2), BVref(BVref(x, 0) + BVref(x, 1) + BVref(x, 2), 0))
# Eq4 = Equal(BVref(y, 3), BVref(BVref(x, 0) + BVref(x, 1) + BVref(x, 2), 1))
# right_phase = getSumPhase([(Eq1*Eq2*Eq3*Eq4, bv(0))])
# claim = And(left_phase.z3exp() == right_phase.z3exp(), left_phase.deltas() == right_phase.deltas())
# s = Solver()
# s.add(Not(claim))
# r = s.check()
# print(r)