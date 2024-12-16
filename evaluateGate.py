from qiskit.circuit import QuantumCircuit, QuantumRegister, AncillaRegister
from qiskit.compiler import transpile
from qiskit.providers.aer import QasmSimulator
from qiskit.circuit.library import CDKMRippleCarryAdder
from result.CondAdder import CondAdder

simulator = QasmSimulator()


for n in range(4, 8):
    print(f"n={n}")
    rippleAdder = CDKMRippleCarryAdder(n).to_gate()
    conditonalAdder = rippleAdder.control(1)

    qr = QuantumRegister(conditonalAdder.num_qubits)
    circuit = QuantumCircuit(qr)
    circuit.append(conditonalAdder, qr)
    circuit = transpile(circuit, basis_gates=["id", "u3", "cx"], optimization_level=3)
    print("Qiskit count:", str(circuit.count_ops()))

    circuit = CondAdder(n).decompose()
    circuit = transpile(circuit, basis_gates=["id", "u3", "cx"], optimization_level=3)
    print("QSynth count:", str(circuit.count_ops()))
    print("")
