# QSynth

This is repository for implementation of paper "**A Case for Synthesis of Recursive Quantum Unitary Programs**". It is based on Python3.8. All commands in this document are runned in the root folder (e.g. `QSynth`)

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

- We present QSynth, the first recursive quantum program synthesis framework. We evaluate QSynth with a benchmark of 10 quantum programs, and show that QSynth is able to synthesize practical recursive quantum programs in a reasonable time. The first column of Table 
- QSynth successfully captures the inductive structure of the targeting problem and produces better
programs than human-written programs in Qiskit. (Fig.14)

## Reproduce The result
  
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

## Run QFast and Qsyn

In Table 3 we demonstrate that QFast and Qsyn, two circuit synthesizers can only synthesize fixed-size quantum circuits and cannot handle cases for >= 6 qubits in a reasonable time.

### QFast Setup

Run the command below to setup Qfast
```
pip install qfast
```
Run the following command to test that QFast is successfully installed. It needs about 17s.
```
cd qfast
python3 -m qfast qfast/examples/GHZ4.unitary output.qasm
cd ../
```

### Qsyn Setup

Run the following command to setup Qsyn

```
pip3 install -r qsyn/requirements.txt
```

 Run the command below to generate the specifications of QFast and Qsyn from the ten programs synthesized by QSynth

```
cd qsyn
python3 qsyn/run_single.py --benchmark GHZ3  --mode Ours
cd ../
```

### Test QFast and Qsyn for 6-qubit circuits

Run the following command to generate the specifications of the ten programs synthesized by QSynth for QFast and Qsyn

```
python3 get_spec.py
```

Specifications for QFast and Qsyn will be generated in the folder `qfast/examples` and `qsyn/benchmarks`.
Try to synthesize each benchmark with QFast and Qsyn with the following command respectively:
```
cd qfast
python3 -m qfast qfast/examples/[Benchmark].unitary output.qasm
```
```
cd qsyn
python3 qsyn/run_single.py --benchmark [Benchmark]  --mode Ours
```
`[Benchmark]` is one of following items
```
Inversion, GHZ, CondAdder, FullAdder, QFT, Uniform , RippleAdder, RippleSubtractor, ToffoliN, Teleportation
```

None of these benchmark can be synthesized by QFast or Qsyn within one hour. This step is to test that QFast and Qsyn are not scalable when the circuit size >=6.

## File Structure

The source code is located in `src` and is structured as follows:

- `main`: Specification and synthesis procedure of the example programs in the paper
- `z3tool`: Useful z3py solver interface.
- `adt.py`: Abstract data structure for PPSA functions and other program tools
- `search`: Enumerative search.
- `component`: Predefined quantum gates and modules.