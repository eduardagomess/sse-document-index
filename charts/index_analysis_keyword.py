import os
import sys
import time
import shutil
import matplotlib.pyplot as plt

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core.client import Client
from core.server import Server
from utils.generators import generate_documents_fixed_keywords, load_documents_from_folder

def measure_avg_index_time_per_doc(keywords_per_doc, num_docs=1, r=18, bloom_size=128):
    """Measures the total index creation time for 1 document with a fixed number of keywords."""
    # Clean and recreate document folder
    shutil.rmtree("data/documents", ignore_errors=True)
    os.makedirs("data/documents", exist_ok=True)

    # Generate documents with a fixed number of keywords
    generate_documents_fixed_keywords(
        n=num_docs,
        keywords_per_doc=keywords_per_doc,
        output_folder="data/documents"
    )

    # Load documents
    documents = load_documents_from_folder("data/documents")
    client = Client(r=r, bloom_size=bloom_size)
    server = Server()

    # Measure indexing time
    start = time.time()
    for doc_id, (_, tokens) in documents.items():
        index = client.create_index(doc_id, tokens)
        server.indices[doc_id] = index
    total_time = time.time() - start
    return total_time

# Number of keywords per document to test
keyword_counts = [25, 50, 75, 100, 125, 150, 175]
times = []

# Run the experiment for each keyword count
for k in keyword_counts:
    t = measure_avg_index_time_per_doc(k)
    print(f"{k} keywords → {t:.6f} s")
    times.append(t)

plt.figure(figsize=(10, 6))
plt.plot(keyword_counts, times, marker='o')
plt.title("Tempo de criação do índice vs Número de palavras-chave por documento")
plt.xlabel("Número de palavras-chave por documento")
plt.ylabel("Tempo total (s)")
plt.grid(True, linestyle='--', linewidth=0.5)
plt.tight_layout()
plt.show()
