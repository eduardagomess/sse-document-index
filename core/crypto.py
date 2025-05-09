import hmac
import math
import hashlib
import os

def prf(key: bytes, message: str, s: int) -> int:
    """
    Applies a pseudorandom function using HMAC-SHA256.
    Returns an integer containing exactly s bits of entropy.
    """
    # key is already bytes, so no need to convert
    hmac_result = hmac.new(key, message.encode(), hashlib.sha256).digest()
    full_int = int.from_bytes(hmac_result, 'big')

    # Truncate to s bits
    mask = (1 << s) - 1
    return full_int & mask

def keygen(s: int, r: int) -> list:
    """
    Since Python generates randomness in bytes (8 bits), we use math.ceil(s / 8)
    to ensure that we generate at least s bits of entropy. After that, we apply a 
    bitmask using (1 << s) - 1 to remove any extra bits and guarantee that each value 
    k_i belongs to the space {0,1}^s, as required by the theoretical definition.
    """

    # Calculate how many bytes are needed to cover s bits
    # 13 bits needs 2 bytes (16 bits) since Python only generates full bytes
    num_bytes = (s + 7) // 8  # Round up to the nearest full byte
    keys = []
    for _ in range(r):
        random_bytes = os.urandom(num_bytes)  # Secure random byte string
        keys.append(random_bytes)
    return keys


def trapdoor(K_priv: list, w: str, s: int) -> list:
    """
    Generates the trapdoor T_w = [f(w, k1), ..., f(w, kr)]
    using the secret keys K_priv and word w.

    """
    trapdoor_list = []
    for k in K_priv:
        result = prf(k, w, s)  # Apply PRF with key k and word w
        trapdoor_list.append(result)
    return trapdoor_list