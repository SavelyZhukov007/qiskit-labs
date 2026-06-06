"""BB84 and QKD helper functions."""

from __future__ import annotations

import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector


def generate_random_bits(n: int, seed: int | None = None) -> list[int]:
    """Generate n random bits (0 or 1)."""
    rng = np.random.default_rng(seed)
    return rng.integers(0, 2, size=n).tolist()


def generate_random_bases(n: int, seed: int | None = None) -> list[str]:
    """Generate n random measurement bases: 'Z' or 'X'."""
    rng = np.random.default_rng(seed)
    return ["Z" if b == 0 else "X" for b in rng.integers(0, 2, size=n)]


def prepare_bb84_state(bit: int, basis: str) -> QuantumCircuit:
    """
    Prepare one-qubit BB84 state.

    Z: |0>, |1>
    X: |+>, |->
    """
    if bit not in (0, 1):
        raise ValueError("bit must be 0 or 1")
    if basis not in ("Z", "X"):
        raise ValueError("basis must be 'Z' or 'X'")

    qc = QuantumCircuit(1, 1)
    if basis == "Z":
        if bit == 1:
            qc.x(0)
    else:
        qc.h(0)
        if bit == 1:
            qc.z(0)
    return qc


def measure_bb84(qc: QuantumCircuit, basis: str) -> QuantumCircuit:
    """Append measurement in Bob's chosen basis."""
    measured = qc.copy()
    if basis == "X":
        measured.h(0)
    measured.measure(0, 0)
    return measured


def simulate_bb84_measurement(bit: int, alice_basis: str, bob_basis: str) -> int:
    """Deterministic single-shot outcome via statevector (noiseless)."""
    prep = prepare_bb84_state(bit, alice_basis)
    sv = Statevector.from_instruction(prep)
    meas = QuantumCircuit(1)
    if bob_basis == "X":
        meas.h(0)
    sv = sv.evolve(meas)
    # Born rule: probability of |0>
    p0 = abs(sv.data[0]) ** 2
    return 0 if p0 >= 0.5 else 1


def sift_key(
    alice_bases: list[str],
    bob_bases: list[str],
    alice_bits: list[int],
    bob_bits: list[int],
) -> tuple[list[int], list[int]]:
    """Keep positions where Alice and Bob used the same basis."""
    if not (len(alice_bases) == len(bob_bases) == len(alice_bits) == len(bob_bits)):
        raise ValueError("All BB84 lists must have the same length")

    alice_key: list[int] = []
    bob_key: list[int] = []
    for ab, bb, a_bit, b_bit in zip(alice_bases, bob_bases, alice_bits, bob_bits):
        if ab == bb:
            alice_key.append(a_bit)
            bob_key.append(b_bit)
    return alice_key, bob_key


def calculate_qber(alice_key: list[int], bob_key: list[int]) -> float:
    """Quantum bit error rate between two keys of equal length."""
    if len(alice_key) != len(bob_key):
        raise ValueError("Keys must have the same length")
    if len(alice_key) == 0:
        return 0.0
    errors = sum(1 for a, b in zip(alice_key, bob_key) if a != b)
    return errors / len(alice_key)


def run_bb84_session(n: int, seed: int = 42) -> dict:
    """Run a full noiseless BB84 skeleton session."""
    rng = np.random.default_rng(seed)
    alice_bits = generate_random_bits(n, seed=seed)
    alice_bases = generate_random_bases(n, seed=seed + 1)
    bob_bases = generate_random_bases(n, seed=seed + 2)

    bob_bits = [
        simulate_bb84_measurement(bit, ab, bb)
        for bit, ab, bb in zip(alice_bits, alice_bases, bob_bases)
    ]
    alice_key, bob_key = sift_key(alice_bases, bob_bases, alice_bits, bob_bits)
    qber = calculate_qber(alice_key, bob_key)

    return {
        "alice_bits": alice_bits,
        "alice_bases": alice_bases,
        "bob_bases": bob_bases,
        "bob_bits": bob_bits,
        "alice_key": alice_key,
        "bob_key": bob_key,
        "raw_key_length": len(alice_key),
        "qber": qber,
    }
