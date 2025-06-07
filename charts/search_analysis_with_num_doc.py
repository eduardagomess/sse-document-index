import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.client import Client
from core.server import Server
from utils.generators import generate_documents, load_documents_from_folder
import time, os, shutil, csv
import matplotlib.pyplot as plt

# max diseases per document = 5
def run_test(n_docs, r=18, bloom_size=128):
    print(f"Running test with {n_docs} documents...")

    # Clean up previous data
    shutil.rmtree("data/documents", ignore_errors=True)
    shutil.rmtree("data/encrypted_docs", ignore_errors=True)
    os.makedirs("data/documents", exist_ok=True)
    os.makedirs("data/encrypted_docs", exist_ok=True)

    # Generate and load documents
    generate_documents(n_docs)
    docs = load_documents_from_folder()

    # Initialize client and server
    client = Client(r=r, bloom_size=bloom_size)
    server = Server()

    # Encrypt documents and store them on the server
    for doc_id, (plaintext, _) in docs.items():
        encrypted = client.encrypt_document(doc_id, plaintext, "data/encrypted_docs")
        server.documents[doc_id] = encrypted

    # Build secure index for each document
    for doc_id, (_, tokens) in docs.items():
        index = client.create_index(doc_id, tokens)
        server.indices[doc_id] = index

    # Generate trapdoor and perform search multiple times to get average time
    T = client.build_trapdoor("hepatite")
    durations = []
    for _ in range(5):
        start = time.perf_counter()
        _ = server.search(T, client.s)
        durations.append(time.perf_counter() - start)

    avg_time = sum(durations) / len(durations)
    print(f"Average search time: {avg_time:.6f} s")

    return avg_time

# Run tests for different document volumes
results = []
for size in [200000, 500000, 1000000, 2000000, 5000000]:
    t = run_test(size)
    results.append((size, t))

with open("search_time.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["num_documents", "search_time_sec"])
    writer.writerows(results)

num_documents, search_times = zip(*results)
plt.figure(figsize=(10, 6))
plt.plot(num_documents, search_times, marker='o')
plt.title("Tempo de busca vs Número de documentos (formato 'k')")
plt.xlabel("Número de documentos")
plt.ylabel("Tempo médio de busca (s)")
plt.xticks(num_documents, [f'{int(x/1000)}k' for x in num_documents])  # Ex: 100k, 200k...
plt.grid(True)
plt.tight_layout()
plt.show()
