import numpy as np

from circuits import (
    bell_statevector,
    create_bell_state_circuit,
    create_bernstein_vazirani_circuit,
    create_deutsch_jozsa_circuit,
    create_grover_circuit,
    create_single_qubit_hadamard_circuit,
    run_circuit,
    teleportation_fidelity,
)
from qiskit.quantum_info import Statevector


def test_bell_circuit_has_two_qubits():
    qc = create_bell_state_circuit()
    assert qc.num_qubits == 2


def test_bell_statevector_only_00_11():
    sv = bell_statevector()
    amps = np.abs(sv.data)
    # |Phi+> = (|00> + |11>)/sqrt(2) -> indices 0 and 3 for 2 qubits
    assert amps[1] < 1e-9 and amps[2] < 1e-9
    assert abs(amps[0] - 1 / np.sqrt(2)) < 1e-9
    assert abs(amps[3] - 1 / np.sqrt(2)) < 1e-9


def test_single_qubit_hadamard_runs():
    counts = run_circuit(create_single_qubit_hadamard_circuit(), shots=512)
    assert set(counts.keys()).issubset({"0", "1"})


def test_deutsch_jozsa_balanced_vs_constant():
    shots = 512
    balanced = run_circuit(create_deutsch_jozsa_circuit(2, "balanced"), shots=shots)
    constant = run_circuit(create_deutsch_jozsa_circuit(2, "constant"), shots=shots)
    # Constant f=0 -> |00...0>; balanced oracle should not peak on the same outcome
    assert constant.get("00", 0) > shots * 0.5
    assert balanced.get("00", 0) < shots * 0.2


def test_bernstein_vazirani_recovers_secret():
    secret = "1011"
    qc = create_bernstein_vazirani_circuit(secret)
    sv = Statevector.from_instruction(qc.remove_final_measurements(inplace=False))
    # After measurement-free BV, input register should peak on secret
    # Use shots instead for robustness
    counts = run_circuit(create_bernstein_vazirani_circuit(secret), shots=1024)
    top = max(counts, key=counts.get)
    assert top.replace(" ", "") == secret[::-1] or top == secret


def test_grover_marks_target_probability():
    marked = "10"
    before = run_circuit(create_grover_circuit(marked, iterations=0), shots=1024)
    after = run_circuit(create_grover_circuit(marked, iterations=1), shots=1024)
    p_before = before.get(marked, 0) / 1024
    p_after = after.get(marked, 0) / 1024
    assert p_after > p_before


def test_teleportation_fidelity_near_one():
    fid = teleportation_fidelity(1.1, 0.4)
    assert fid > 0.99
