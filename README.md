# Synthesis

## Install
This framework is based on z3py, you can install it by
```
pip install z3-solver
```

## Execution
run the command below to reproduce the results in paper.
```
python src/main.py
```
Four result program files, `FullAdder.py`, `GHZ.py`, `RippleAdder.py` and `QFT.py` will be synthesized. They are Qiskit functions that can generate the corresponding circuits. 