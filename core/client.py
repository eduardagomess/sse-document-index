from cryptography.fernet import Fernet
from core.crypto import keygen, trapdoor
from core.index import SecureIndex
import os

class Client:
    def __init__(self, s=16, r=3, bloom_size=2048):
        """
        Initializes the client with a pseudorandom function key and a Bloom filter size.
        """
        self.K_priv = keygen(s, r)
        self.r = r
        self.s = s  # Save the security parameter s for use in PRF and trapdoor
        self.bloom_size = bloom_size
        self.enc_key = Fernet.generate_key()
        self.cipher = Fernet(self.enc_key)

    def build_trapdoor(self, word):
        return trapdoor(self.K_priv, word, self.s)

    def encrypt_document(self, doc_id, raw_text, output_folder):
        os.makedirs(output_folder, exist_ok=True)
        encrypted = self.cipher.encrypt(raw_text.encode())
        with open(os.path.join(output_folder, f"{doc_id}.enc"), "wb") as f:
            f.write(encrypted)
        return encrypted

    def create_index(self, D_id, words):
        index = SecureIndex(self.K_priv, self.bloom_size, self.r, self.s)
        index.build_index(D_id, words)
        return index.indices[D_id]
