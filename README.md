# Synthesis

## Install
This framework is based on z3py, you can install it by
```
pip install z3-solver
```
run the command below to reproduce the results in paper.
```
python src/main.py
```
Four result program files, `FullAdder.py`, `GHZ.py`, `RippleAdder.py` and `QFT.py` will be synthesized. They are Qiskit functions that can generate the corresponding circuits. 

## Usage

We assume the users have some knowledge about the [Z3 Python API](https://ericpony.github.io/z3py-tutorial/guide-examples.htm) to give specifications to QSynth. Please read the [z3py tutorial](https://ericpony.github.io/z3py-tutorial/guide-examples.htm) if you have no knowledge about it.

To use QSynth, first import z3tool and the necessary functions form QSynth
```python
from z3tool import *
from qsynth import synthesis, StandardGateSet, PPSA
```
Function `synthesis` is used to generate target programs given the specification. `StandardGateSet` is the gateset which QSynth uses for synthesis. Class `PPSA` is used to give specification.

The function `synthesis` needs three inputs:
```python
synthesis(amplitude, gateset,  hypothesis=lambda n,x,y:True)
```
The input `gateset` suggests the gate set which QSynth search during the synthesis. Inputs `amplitude` and `hypothesis` are the hypothesis-amplitude specification (see the paper for their meaning).
The input `amplitude` should be a `PPSA` variable (a PPSA function as discussed in paper), indicating the amplitude function in the specification. A PPSA function should be in the form
![](document/PPSA.jpg)
A `PPSA` variable is created by two functions `beta` and `pathsum`
```python
PPSA(beta, phaseSum)
```
`beta` should be a function from a z3py `BitVec(32)` variable to a z3py `BitVec(32)` variable, indicating the function \beta(n) in PPSA's definition. For example
```
beta=lambda n: LShR(2, n)
```
where `LShR` is the unsigned right shift operators in z3py.