from main import *

if __name__ == "__main__":

    start = time.time()
    spec = PPSA(beta=lambda n: 2, phaseSum=GHZspec)
    prog = synthesis(spec, StandardGateSet, hypothesis = lambda n,x,y : x==bv(0))
    end =time.time()
    print(f'GHZ case uses {end-start}s')
    filewrite(prog.toQiskit('GHZ'), 'GHZ.py')