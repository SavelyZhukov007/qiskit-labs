"""Reusable quantum circuits for qiskit-labs."""

from __future__ import annotations

import math
from typing import Literal

import numpy as np
from qiskit import ClassicalRegister, QuantumCircuit, QuantumRegister
from qiskit.circuit import Gate
from qiskit.circuit.library import RYGate
from qiskit.quantum_info import Statevector


OracleType = Literal["constant", "balanced"]


def run_circuit(circuit: QuantumCircuit, shots: int = 1024) -> dict[str, int]:
    """Run a circuit on AerSimulator and return measurement counts."""
    from qiskit_aer import AerSimulator

    simulator = AerSimulator()
    job = simulator.run(circuit, shots=shots)
    return job.result().get_counts()


def create_single_qubit_hadamard_circuit() -> QuantumCircuit:
    """Single qubit: H then measure in computational basis."""
    qc = QuantumCircuit(1, 1)
    qc.h(0)
    qc.measure(0, 0)
    return qc


def create_bell_state_circuit() -> QuantumCircuit:
    """Bell state |Phi+> = (|00> + |11>) / sqrt(2)."""
    qc = QuantumCircuit(2, 2)
    qc.h(0)
    qc.cx(0, 1)
    qc.measure([0, 1], [0, 1])
    return qc


def bell_statevector() -> Statevector:
    """Return the ideal Bell statevector without measurement."""
    qc = QuantumCircuit(2)
    qc.h(0)
    qc.cx(0, 1)
    return Statevector.from_instruction(qc)


def create_teleportation_circuit_diagram() -> QuantumCircuit:
    """Teleportation circuit for visualization (no dynamic classical if)."""
    qc = QuantumCircuit(3, 2)
    qc.ry(1.1, 0)
    qc.rz(0.4, 0)
    qc.h(1)
    qc.cx(1, 2)
    qc.cx(0, 1)
    qc.h(0)
    qc.barrier()
    qc.measure(0, 0)
    qc.measure(1, 1)
    qc.barrier(label="corrections")
    qc.z(2)
    qc.x(2)
    return qc


def create_teleportation_circuit(
    theta: float = 1.1,
    phi: float = 0.4,
) -> QuantumCircuit:
    """
    Standard 3-qubit teleportation.

    Qubit 0: state to teleport (prepared via RY/ RZ angles).
    Qubits 1,2: Bell pair; qubit 2 receives the teleported state after corrections.
    """
    qr = QuantumRegister(3, "q")
    cr = ClassicalRegister(2, "c")
    qc = QuantumCircuit(qr, cr)

    # Prepare arbitrary state on q[0]
    qc.ry(theta, qr[0])
    qc.rz(phi, qr[0])

    # Bell pair on q[1], q[2]
    qc.h(qr[1])
    qc.cx(qr[1], qr[2])

    # Bell measurement on q[0], q[1]
    qc.cx(qr[0], qr[1])
    qc.h(qr[0])
    qc.measure(qr[0], cr[0])
    qc.measure(qr[1], cr[1])

    # Corrections on q[2] conditioned on classical bits.
    # Use the control-flow builder `if_test` with a (Clbit, value) condition.
    # Measure results were stored into `cr[0]` and `cr[1]` above.
    with qc.if_test((cr[0], 1)):
        qc.z(qr[2])
    with qc.if_test((cr[1], 1)):
        qc.x(qr[2])

    return qc


def prepare_qubit_state(theta: float, phi: float) -> Statevector:
    """State on one qubit: RY(theta) RZ(phi) on |0>."""
    qc = QuantumCircuit(1)
    qc.ry(theta, 0)
    qc.rz(phi, 0)
    return Statevector.from_instruction(qc)


def teleportation_fidelity(theta: float = 1.1, phi: float = 0.4) -> float:
    """Statevector fidelity between input and teleported qubit (noiseless)."""
    input_sv = prepare_qubit_state(theta, phi)

    full = QuantumCircuit(3)
    full.ry(theta, 0)
    full.rz(phi, 0)
    full.h(1)
    full.cx(1, 2)
    full.cx(0, 1)
    full.h(0)
    sv_full = Statevector.from_instruction(full)

    fid = 0.0
    for m0 in (0, 1):
        for m1 in (0, 1):
            p, q2 = _project_qubit2(sv_full, m0, m1)
            if p < 1e-12:
                continue
            corr = QuantumCircuit(1)
            if m0:
                corr.z(0)
            if m1:
                corr.x(0)
            out = Statevector(q2).evolve(corr)
            fid += p * abs(input_sv.inner(out)) ** 2
    return float(min(1.0, fid.real))


def _project_qubit2(sv: Statevector, m0: int, m1: int) -> tuple[float, np.ndarray]:
    """Probability and normalized qubit-2 state after projecting q0=m0, q1=m1 (Qiskit bit order)."""
    amps = sv.data
    vec = np.zeros(2, dtype=complex)
    prob = 0.0
    for i in range(8):
        q0 = i & 1
        q1 = (i >> 1) & 1
        q2 = (i >> 2) & 1
        if q0 == m0 and q1 == m1:
            prob += abs(amps[i]) ** 2
            vec[q2] += amps[i]
    norm = np.linalg.norm(vec)
    if norm > 1e-12:
        vec /= norm
    return prob, vec


def create_superdense_coding_circuit(message: str) -> QuantumCircuit:
    """
    Encode two classical bits on qubit 0 of a shared Bell pair (q0,q1).

    message: one of '00', '01', '10', '11'
    """
    if message not in {"00", "01", "10", "11"}:
        raise ValueError("message must be one of 00, 01, 10, 11")

    qc = QuantumCircuit(2, 2)
    qc.h(0)
    qc.cx(0, 1)

    ops = {"00": [], "01": [("x", 0)], "10": [("z", 0)], "11": [("z", 0), ("x", 0)]}
    for gate, qubit in ops[message]:
        getattr(qc, gate)(qubit)

    qc.cx(0, 1)
    qc.h(0)
    qc.measure([0, 1], [0, 1])
    return qc


def create_deutsch_jozsa_circuit(
    n: int = 2,
    oracle_type: OracleType = "balanced",
) -> QuantumCircuit:
    """Deutsch–Jozsa for n input qubits (plus one ancilla)."""
    if oracle_type not in ("constant", "balanced"):
        raise ValueError("oracle_type must be 'constant' or 'balanced'")

    qc = QuantumCircuit(n + 1, n)
    qc.x(n)
    qc.h(range(n + 1))

    if oracle_type == "constant":
        # f(x) = 0 for all x (phase kickback via ancilla already in |->)
        pass
    else:
        # Balanced: flip phase for half the inputs — CNOT from each input to ancilla
        for i in range(n):
            qc.cx(i, n)

    qc.h(range(n))
    qc.measure(range(n), range(n))
    return qc


def create_bernstein_vazirani_circuit(secret_string: str) -> QuantumCircuit:
    """Recover a hidden bit string s with one oracle query."""
    n = len(secret_string)
    if any(b not in "01" for b in secret_string):
        raise ValueError("secret_string must contain only 0 and 1")

    qc = QuantumCircuit(n + 1, n)
    qc.x(n)
    qc.h(range(n + 1))

    for i, bit in enumerate(secret_string):
        if bit == "1":
            qc.cx(i, n)

    qc.h(range(n))
    qc.measure(range(n), range(n))
    return qc


def create_grover_circuit(
    marked_state: str,
    num_qubits: int | None = None,
    iterations: int | None = None,
) -> QuantumCircuit:
    """
    Grover search on ``num_qubits`` qubits marking computational basis state ``marked_state``.
    """
    n = num_qubits or len(marked_state)
    if len(marked_state) != n:
        raise ValueError("marked_state length must match num_qubits")
    if any(b not in "01" for b in marked_state):
        raise ValueError("marked_state must be a bit string")

    qc = QuantumCircuit(n, n)
    qc.h(range(n))

    iters = (
        iterations
        if iterations is not None
        else max(1, int(round(math.pi / 4 * 2 ** (n / 2))))
    )
    for _ in range(iters):
        _apply_grover_oracle(qc, marked_state, n)
        _apply_diffuser(qc, n)

    qc.measure(range(n), range(n))
    return qc


def _apply_grover_oracle(qc: QuantumCircuit, marked: str, n: int) -> None:
    """Phase flip on |marked>."""
    # Flip bits so marked becomes |11...1>
    for i, b in enumerate(reversed(marked)):
        if b == "0":
            qc.x(i)
    qc.h(n - 1)
    qc.mcx(list(range(n - 1)), n - 1)
    qc.h(n - 1)
    for i, b in enumerate(reversed(marked)):
        if b == "0":
            qc.x(i)


def _apply_diffuser(qc: QuantumCircuit, n: int) -> None:
    qc.h(range(n))
    qc.x(range(n))
    qc.h(n - 1)
    qc.mcx(list(range(n - 1)), n - 1)
    qc.h(n - 1)
    qc.x(range(n))
    qc.h(range(n))
