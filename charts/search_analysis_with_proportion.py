import os
import sys
import time
import shutil
import csv

# Add project directories to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core.client import Client
from core.server import Server
from utils.generators import generate_documents, load_documents_from_folder

def run_search_experiment(num_docs, prop_hepatite, r=18, bloom_size=128, keywords_per_doc=5):
    """
    Runs a search experiment varying the proportion of documents containing the keyword 'hepatite'.
    """
    # Prepare folders
    shutil.rmtree("data/documents", ignore_errors=True)
    shutil.rmtree("data/encrypted", ignore_errors=True)
    os.makedirs("data/documents", exist_ok=True)
    os.makedirs("data/encrypted", exist_ok=True)

    # Generate documents with a fixed proportion of the target keyword
    generate_documents(
        n=num_docs,
        max_diseases_per_patient=keywords_per_doc,
        output_folder="data/documents",
        fixed_disease="hepatite",
        fixed_proportion=prop_hepatite
    )

    documents = load_documents_from_folder("data/documents")
    client = Client(r=r, bloom_size=bloom_size)
    server = Server()

    # Encrypt documents and build indices
    for doc_id, (plaintext, tokens) in documents.items():
        server.documents[doc_id] = client.encrypt_document(doc_id, plaintext, "data/encrypted")
        server.indices[doc_id] = client.create_index(doc_id, tokens)

    # Build trapdoor and measure search time
    T = client.build_trapdoor("hepatite")
    durations = []
    for _ in range(5):
        start = time.perf_counter()
        _ = server.search(T, client.s)
        durations.append(time.perf_counter() - start)

    avg_time = sum(durations) / len(durations)
    return round(avg_time, 6)

# Define the proportions of documents containing 'hepatite'
proportions = [0.1, 0.25, 0.5, 0.75, 1.0]
results = []

# Execute the experiment for each proportion
for p in proportions:
    print(f"Running experiment for {int(p*100)}% of the documents with 'hepatite'")
    t = run_search_experiment(num_docs=1000, prop_hepatite=p)
    results.append((int(p * 100), t))

with open("search_time_by_proportion.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["proporcao_documentos_com_hepatite", "tempo_medio_busca_s"])
    writer.writerows(results)