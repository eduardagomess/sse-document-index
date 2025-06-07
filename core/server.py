from core.crypto import prf

class Server:
    def __init__(self):
        # dictionary to store Bloom filters per document
        self.indices = {}
        # dictionary to store encrypted documents
        self.documents = {}

    def store(self, D_id, encrypted_doc, index):
        """
        Stores the encrypted document and its secure index
        """
        self.documents[D_id] = encrypted_doc
        self.indices[D_id] = index

    def search(self, T_w, s):
        """
        Searches for a trapdoor T_w across all documents

        For each document:
        - Applies the PRF to each trapdoor token using the document ID
        - Checks if all resulting hash positions exist in the document's Bloom Filter
        - If so, includes the document ID in the results
        """
        results = []
        positive_count = 0

        for D_id in self.indices:
            # apply PRF to each trapdoor value using the document ID
            y = []
            for t in T_w:
                y_i = prf(D_id.encode(), str(t), s)
                y.append(y_i)
            
            bf = self.indices[D_id]
            # query the Bloom Filter with the computed hash positions
            if bf.query(y):
                results.append(D_id)
                positive_count += 1
        return results
