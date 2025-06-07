from cryptography.fernet import Fernet
from core.crypto import keygen, trapdoor
from core.index import SecureIndex
import os

class Client:
    def __init__(self, s=16, r=18, bloom_size=128):
        """
        Initializes the client:
        - Generates r secret keys of s bits (K_priv)
        - Sets Bloom filter size
        - Generates a symmetric encryption key (AES via Fernet)
        """
        self.K_priv = keygen(s, r)             # list of r secret subkeys of s bits
        self.r = r                             # number of hash functions / PRFs
        self.s = s                             # security parameter (bit length of each key)
        self.bloom_size = bloom_size           # size of the Bloom filter
        self.enc_key = Fernet.generate_key()   # symmetric key for encryption/decryption
        self.cipher = Fernet(self.enc_key)     # AES cipher initialized with the symmetric key

    def build_trapdoor(self, word):
        """
        Builds a trapdoor for the given word using the PRF with all keys in K_priv
        """
        return trapdoor(self.K_priv, word, self.s)

    def encrypt_document(self, doc_id, raw_text, output_folder):
        """
        Encrypts the raw text using Fernet (AES) and saves it to a file named {doc_id}.enc
        """
        os.makedirs(output_folder, exist_ok=True)
        encrypted = self.cipher.encrypt(raw_text.encode())
        with open(os.path.join(output_folder, f"{doc_id}.enc"), "wb") as f:
            f.write(encrypted)
        return encrypted

    def decrypt_document(self, doc_id, input_folder="data/encrypted_docs"):
        """
        Decrypts a previously encrypted document using the same symmetric key
        """
        file_path = os.path.join(input_folder, f"{doc_id}.enc")
        with open(file_path, "rb") as f:
            encrypted = f.read()
        decrypted = self.cipher.decrypt(encrypted).decode()
        return decrypted

    def create_index(self, D_id, words):
        """
        Builds a secure Bloom filter index for a document
        """
        index = SecureIndex(self.K_priv, self.bloom_size, self.r, self.s)
        index.build_index(D_id, words)
        return index.indices[D_id]
