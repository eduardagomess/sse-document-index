import pytest
from core.crypto import keygen, prf, trapdoor

def test_keygen_size_and_count():
    s = 16
    r = 4
    keys = keygen(s, r)
    print(f"[Keygen Test] Generated {len(keys)} keys with {s} bits each.")
    assert len(keys) == r, f"Expected {r} keys, got {len(keys)}"
    for i, k in enumerate(keys):
        assert 0 <= k < (1 << s), f"Key {i} is not within {s}-bit range: {k}"

def test_prf_output_size():
    s = 16
    key = 12345
    msg = "doc1"
    result = prf(key, msg, s)
    print(f"[PRF Size Test] Output of PRF is {result}, should fit in {s} bits.")
    assert 0 <= result < (1 << s), f"PRF result out of {s}-bit range: {result}"

def test_prf_deterministic():
    s = 16
    key = 12345
    msg = "test"
    a = prf(key, msg, s)
    b = prf(key, msg, s)
    print(f"[PRF Determinism Test] Two executions with same key/message returned {a} and {b}")
    assert a == b, "PRF is not deterministic — same inputs produced different outputs"

def test_prf_changes_on_input():
    s = 16
    key = 12345
    msg1 = "a"
    msg2 = "b"
    out1 = prf(key, msg1, s)
    out2 = prf(key, msg2, s)
    print(f"[PRF Input Sensitivity Test] PRF('{msg1}') = {out1}, PRF('{msg2}') = {out2}")
    assert out1 != out2, "PRF produced same output for different inputs — lacks variability"
