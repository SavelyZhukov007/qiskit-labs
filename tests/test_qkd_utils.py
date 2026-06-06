from qkd_utils import (
    calculate_qber,
    generate_random_bases,
    generate_random_bits,
    run_bb84_session,
    sift_key,
)


def test_generate_random_bits_length():
    bits = generate_random_bits(50, seed=1)
    assert len(bits) == 50
    assert all(b in (0, 1) for b in bits)


def test_generate_random_bases_values():
    bases = generate_random_bases(30, seed=2)
    assert len(bases) == 30
    assert set(bases).issubset({"Z", "X"})


def test_sift_key_keeps_only_matching_bases():
    alice_bases = ["Z", "X", "Z", "X"]
    bob_bases = ["Z", "X", "X", "Z"]
    alice_bits = [1, 0, 1, 0]
    bob_bits = [1, 0, 0, 1]
    a_key, b_key = sift_key(alice_bases, bob_bases, alice_bits, bob_bits)
    assert a_key == [1, 0]
    assert b_key == [1, 0]


def test_qber_zero_for_identical_keys():
    key = [1, 0, 1, 1, 0]
    assert calculate_qber(key, key) == 0.0


def test_qber_nonzero_for_different_keys():
    assert calculate_qber([0, 0, 0], [0, 1, 0]) > 0.0


def test_bb84_session_noiseless_qber():
    result = run_bb84_session(200, seed=42)
    assert result["raw_key_length"] > 0
    assert result["qber"] == 0.0
