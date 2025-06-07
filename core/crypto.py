import hmac
import hashlib
import os

def prf(key: bytes, message: str, s: int) -> int:
    """
    This function implements the pseudorandom function f described in the SSE scheme
    It uses HMAC-SHA256 to compute f(w, k), where:
    - w is the input word (n bits)
    - k is the secret key (s bits)
    """
    # key is already bytes, so no need to convert
    hmac_result = hmac.new(key, message.encode(), hashlib.sha256).digest()
    full_int = int.from_bytes(hmac_result, 'big')

    # truncate to s bits
    mask = (1 << s) - 1
    return full_int & mask

def keygen(s: int, r: int) -> list:
    """
    The master key K_priv = (k1, ..., kr) consists of r subkeys.
    Each subkey ki is generated randomly with exactly s bits of entropy.
    These subkeys are later used as inputs to pseudorandom functions (PRFs)
    for generating trapdoors and other cryptographic values.
    """

    num_bytes = (s + 7) // 8  # get full bytes
    bitmask = (1 << s) - 1  # bitmask to keep only the lowest s bits

    keys = []
    for _ in range(r):
        random_bytes = os.urandom(num_bytes) # secure random bytes
        value = int.from_bytes(random_bytes, 'big') & bitmask  # apply bitmask
        masked_bytes = value.to_bytes(num_bytes, 'big') # convert back to bytes
        keys.append(masked_bytes)
    return keys


def trapdoor(K_priv: list, w: str, s: int) -> list:
    """
    Generates the trapdoor T_w = [f(w, k1), ..., f(w, kr)]
    using the secret keys K_priv and word w.
    """
    trapdoor_list = []
    for k in K_priv:
        result = prf(k, w, s)  # apply PRF with key k and word w
        trapdoor_list.append(result)
    return trapdoor_list