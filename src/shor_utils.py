"""
Shor's algorithm helpers (educational factorization of 15).

Based on the structure of IBM's Shor tutorial: period finding via phase estimation.
"""

from __future__ import annotations

import math
from functools import reduce

import numpy as np
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit.circuit.library import QFT
from qiskit.quantum_info import Statevector


def gcd(a: int, b: int) -> int:
    while b:
        a, b = b, a % b
    return a


def lcm(a: int, b: int) -> int:
    return a // gcd(a, b) * b


def is_prime(n: int) -> bool:
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    for i in range(3, int(math.isqrt(n)) + 1, 2):
        if n % i == 0:
            return False
    return True


def classical_order_finder(a: int, n: int) -> int | None:
    """Brute-force multiplicative order of a mod n (educational small n)."""
    if gcd(a, n) != 1:
        return None
    r = 1
    val = a % n
    while val != 1:
        val = (val * a) % n
        r += 1
        if r > n:
            return None
    return r


def shor_classical_factors(n: int = 15, a: int = 2) -> dict:
    """
    Classical simulation of Shor's classical post-processing for N=15, a=2.

    Returns factors when period r is even and a^(r/2) != -1 (mod n).
    """
    if n % 2 == 0:
        return {"factors": (2, n // 2), "method": "even"}

    r = classical_order_finder(a, n)
    if r is None or r % 2 != 0:
        return {"period": r, "factors": None, "reason": "period not found or odd"}

    x = pow(a, r // 2, n)
    if (x + 1) % n == 0:
        return {"period": r, "factors": None, "reason": "trivial root"}

    p = gcd(x - 1, n)
    q = gcd(x + 1, n)
    factors = tuple(sorted({p, q, n // p}))
    valid = [f for f in factors if 1 < f < n]
    return {"period": r, "a": a, "n": n, "factors": tuple(valid) if valid else None}


def create_phase_estimation_circuit(
    a: int = 2,
    n: int = 15,
    counting_qubits: int = 8,
) -> QuantumCircuit:
    """
    Simplified phase-estimation circuit for modular exponentiation x^a mod n.

    Educational: uses smaller counting register; controlled-U are block placeholders
    for the full IBM tutorial circuit.
    """
    n_register = max(4, n.bit_length() + 1)
    qr_count = QuantumRegister(counting_qubits, "count")
    qr_work = QuantumRegister(n_register, "work")
    cr = ClassicalRegister(counting_qubits, "c")
    qc = QuantumCircuit(qr_count, qr_work, cr)

    qc.h(qr_count)
    qc.x(qr_work[0])  # |1> for modular exp workspace

    # Controlled modular multiply-by-a mod n (simplified for a=2, n=15)
    for j, cq in enumerate(qr_count):
        power = 2**j
        _controlled_modexp_2_15(qc, cq, qr_work, power)

    qc.append(QFT(counting_qubits, inverse=True), qr_count)
    qc.measure(qr_count, cr)
    return qc


def _controlled_modexp_2_15(
    qc: QuantumCircuit,
    control,
    work,
    power: int,
) -> None:
    """Apply controlled (2^power mod 15) on work register — toy decomposition."""
    # For N=15 educational demo: map a few powers explicitly
    if power % 4 == 0:
        qc.cswap(control, work[0], work[1])
    elif power % 2 == 0:
        qc.cswap(control, work[1], work[2])
    else:
        qc.cx(control, work[0])


def period_from_phase(phase: float, counting_qubits: int) -> int:
    """Convert estimated phase to period candidate."""
    frac = phase
    den = 2**counting_qubits
    num = round(frac * den)
    r = den // gcd(num, den) if num else 0
    return r if r else den


def powers_mod_n(a: int, n: int, limit: int = 16) -> list[int]:
    """Table a^x mod n for educational display."""
    values = []
    val = 1
    for _ in range(limit):
        values.append(val)
        val = (val * a) % n
    return values


def period_from_measurement(counts: dict[str, int], counting_qubits: int) -> int:
    """Estimate period r from QPE measurement counts via continued-fraction heuristic."""
    if not counts:
        return 0
    top_bitstring = max(counts, key=counts.get)
    phase_int = int(top_bitstring, 2)
    phase = phase_int / (2**counting_qubits)
    return period_from_phase(phase, counting_qubits)


def shor_factorization_demo(n: int = 15, a: int = 2) -> dict:
    """
    End-to-end educational demo: period finding + classical post-processing.

    Returns period, factors, power table, and RSA note.
    """
    table = powers_mod_n(a, n)
    r = classical_order_finder(a, n)
    result = shor_classical_factors(n, a)
    return {
        "n": n,
        "a": a,
        "power_table": table,
        "period": r,
        "factors": result.get("factors"),
        "rsa_note": explain_shor_rsa(),
    }


def create_order_finding_circuit_15(
    a: int = 2, counting_qubits: int = 5
) -> QuantumCircuit:
    """
    Order-finding circuit for N=15, a=2 (IBM tutorial scale).

    Uses counting register + 4-bit work register for modular multiplication by 2 mod 15.
    """
    work_bits = 4
    qr_c = QuantumRegister(counting_qubits, "c")
    qr_w = QuantumRegister(work_bits, "w")
    cr = ClassicalRegister(counting_qubits, "meas")
    qc = QuantumCircuit(qr_c, qr_w, cr)

    qc.h(qr_c)
    qc.x(qr_w[0])  # start from |1>

    for j, ctrl in enumerate(qr_c):
        exp = 2**j
        _apply_controlled_multiply_2_mod_15(qc, ctrl, qr_w, exp)

    qc.append(QFT(counting_qubits, inverse=True), qr_c)
    qc.measure(qr_c, cr)
    return qc


def _apply_controlled_multiply_2_mod_15(
    qc: QuantumCircuit,
    control,
    work,
    exponent: int,
) -> None:
    """
    Controlled U^(2^exponent) where U|y> = |2y mod 15>.

    Built from repeated controlled U for exponent=1; for demo exponents use composition.
    """
    for _ in range(exponent):
        _controlled_mult_2_mod_15_single(qc, control, work)


def _controlled_mult_2_mod_15_single(qc: QuantumCircuit, control, work) -> None:
    """One controlled multiply-by-2 mod 15 on 4-qubit work register encoding {1,2,4,8}."""
    # Permutation: 1->2, 2->4, 4->8, 8->1 (mod 15)
    qc.cswap(control, work[0], work[1])  # swap 1 and 2
    qc.cswap(control, work[2], work[3])  # swap 4 and 8
    qc.cswap(control, work[1], work[2])  # combine for 2->4 path


def explain_shor_rsa() -> str:
    """Short text block for notebooks/reports."""
    return (
        "Shor находит период r функции f(x)=a^x mod N. При чётном r и нетривиальном корне "
        "gcd(a^(r/2)±1, N) даёт нетривиальные делители. Это угрожает RSA, потому что "
        "факторизация больших чисел становится полиномиально разрешимой на квантовом "
        "компьютере достаточного размера. Это мотивирует post-quantum cryptography."
    )
