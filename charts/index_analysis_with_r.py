import os
import sys
import time
import shutil
import matplotlib.pyplot as plt

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core.client import Client
from core.server import Server
from utils.generators import generate_documents_fixed_keywords, load_documents_from_folder

def measure_index_time(r, num_docs=1000, keywords_per_doc=10, bloom_size=128):
    """
    Measures total index creation time by varying the number of hash functions (r).
    """
    # Clean and prepare directory
    shutil.rmtree("data/documents", ignore_errors=True)
    os.makedirs("data/documents", exist_ok=True)

    # Generate documents with fixed number of keywords
    generate_documents_fixed_keywords(
        n=num_docs,
        keywords_per_doc=keywords_per_doc,
        output_folder="data/documents"
    )

    documents = load_documents_from_folder("data/documents")
    client = Client(r=r, bloom_size=bloom_size)
    server = Server()

    # Measure index creation time
    start = time.time()
    for doc_id, (_, tokens) in documents.items():
        index = client.create_index(doc_id, tokens)
        server.indices[doc_id] = index
    return time.time() - start

# Varying number of hash functions (r)
r_values = [1, 2, 4, 8, 12, 16, 20, 24, 28, 32]
times = []

for r in r_values:
    elapsed = measure_index_time(r)
    print(f"r = {r} ->  Total time: {elapsed:.4f}s")
    times.append(elapsed)

plt.figure(figsize=(10, 6))
plt.plot(r_values, times, marker='o')
plt.title("Tempo de criação do índice vs Número de funções de hash (r)")
plt.xlabel("Número de funções de hash (r)")
plt.ylabel("Tempo total de criação do índice (s)")
plt.grid(True)
plt.tight_layout()
plt.show()
