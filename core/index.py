from core.crypto import trapdoor, prf
import random

class BloomFilter:
    def __init__(self, size: int):
        self.size = size
        self.bit_array = [0] * size  # initialize bit array with 0s

    def insert(self, hashes: list):
        # for each hash, map it to a valid index in the bit array using modulo and set that position to 1
        for h in hashes:
            self.bit_array[h % self.size] = 1

    def query(self, hashes: list) -> bool:
        for h in hashes:
            pos = h % self.size  # get valid position in the bit array
            if self.bit_array[pos] == 0:
                return False  # if any bit is 0, the item is not present
        return True  # all bits are 1 the item might be present

class SecureIndex:
    def __init__(self, K_priv, bloom_size=2048, r=3, s=16):
        self.K_priv = K_priv
        self.r = r
        self.s = s
        self.bloom_size = bloom_size
        self.indices = {}

    def build_index(self, D_id: str, words: list):
        bf = BloomFilter(self.bloom_size)
        unique_words = set(words)

        for w in unique_words:
            trap = trapdoor(self.K_priv, w, self.s)  # [x1, ..., xr]

            hashes = []
            for x_i in trap:
                y_i = prf(D_id.encode(), str(x_i), self.s)  # key = D_id, message = x_i
                hashes.append(y_i)

            bf.insert(hashes)

        u = len(words)
        v = len(unique_words)
        fake_ones = ((u - v) * self.r)
        for _ in range(fake_ones):
            pos = random.randint(0, self.bloom_size - 1)
            bf.bit_array[pos] = 1

        self.indices[D_id] = bf
