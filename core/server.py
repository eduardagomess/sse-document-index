from core.crypto import prf

class Server:
    def __init__(self):
        self.indices = {}
        self.documents = {}

    def store(self, D_id, encrypted_doc, index):
        self.documents[D_id] = encrypted_doc
        self.indices[D_id] = index

    def search(self, T_w, K_priv, s):
        results = []
        for D_id in self.indices:
            y = [prf(D_id.encode(), str(t), s) for t in T_w]
            bf = self.indices[D_id]
            if bf.query(y):
                results.append(D_id)
        return results