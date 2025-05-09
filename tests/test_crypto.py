import pytest
from core.crypto import keygen, prf, trapdoor

def test_prf_deterministic():
    """
    This test verifies that the PRF is deterministic: the same key 
    and input must always return the same output.
    """
    s = 16
    key = 12345
    msg = "test"
    a = prf(key, msg, s)
    b = prf(key, msg, s)
    print(f"[PRF Determinism Test] Two executions with same key/message returned {a} and {b}")
    assert a == b, "PRF is not deterministic — same inputs produced different outputs"

def test_prf_changes_on_input():
    """
    This test checks that small changes in the input (message) lead to 
    different PRF outputs, validating sensitivity and randomness properties.
    """
     
    s = 16
    key = 12345
    msg1 = "abc"
    msg2 = "abd"
    out1 = prf(key, msg1, s)
    out2 = prf(key, msg2, s)
    print(f"[PRF Input Sensitivity Test] PRF('{msg1}') = {out1}, PRF('{msg2}') = {out2}")
    assert out1 != out2, "PRF produced same output for different inputs — lacks variability"
