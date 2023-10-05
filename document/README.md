# QSynth

This is repository for implementation of paper "**A Case for Synthesis of Recursive Quantum Unitary Programs**". It is based on Python3.8

## Setup

Environment for our program also can be prepared, only by installing required python libraries listed in `requirements.txt` via `pip3` (or `pip`).
Installation will be done by following command :

```
pip3 install -r requirements.txt
```

## Verifying Install

If the environment is properly prepared, under entry directory we will be able to run following command (which synthesizes our working example `GHZ` appeared Section 3 in our paper).

```
python3 src/run_single.py
```
The result will be something like
```
GHZ case uses 0.2749965190887451s
```

## List of claims

- We present QSynth, the first recursive quantum program synthesis framework. We evaluate QSynth with a benchmark of 10 quantum programs, and show that QSynth is able to synthesize practical recursive quantum programs in a reasonable time. (The first column of Table 3)
- QSynth successfully captures the inductive structure of the targeting problem and produces better
programs than human-written programs in Qiskit. (Fig.14)

### Reproduce The result
  
To produce the first column of Table 3 and synthesize the example programs in the paper, run the command
```
python3 src/main.py
```
This procedure needs 15~30 minutes to complete. Ten result program files: `Uniform.py`,`GHZ.py`, `FullAdder.py`, `RippleAdder.py`, `RippleSubtractor.py`, `CondAdder.py`,`ToffoliN.py`, `QFT.py`, `Inversion.py` and `Teleportation.py` will be synthesized in the root folder. They are Qiskit functions that can generate the corresponding circuits. This will also print the synthesis time for all cases. 
The example programs appeared in the paper are:

- Fig 5(c) == `GHZ.py`
- Fig 10(a) == `FullAdder.py`
- Fig 10(b) == `RippleAdder.py`
- Fig 11 == `RippleSubtractor.py`
- Fig 12 == `CondAdder.py`
- Fig 15 == `Inversion.py`
- Fig 17~18 == `QFT.py`
- Fig 19 == `Teleportation.py`

After generating the example programs, run the command below to reproduce the result in Fig 14.

```
python3 evaluateGate.py
```