# ---------------------------------------------------------------
# This script was used to generate the search time values for the
# document-based index (Algorithm 2), which are later compared 
# against the results of the keyword-based index (Algorithm 1).
# It simulates encrypted search using per-document Bloom Filters,
# as described in Goh’s z-idx scheme.
# ---------------------------------------------------------------

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.client import Client
from core.server import Server
from utils.generators import generate_documents, load_documents_from_folder
import time, shutil, csv
import matplotlib.pyplot as plt

# Set this path to the folder where documents were generated
DOCUMENTS_FOLDER = "" 
CSV_OUTPUT = "charts/search_time_result.csv"

def run_test(r=18, bloom_size=128):
    docs = load_documents_from_folder(DOCUMENTS_FOLDER)

    # Initialize client and server
    client = Client(r=r, bloom_size=bloom_size)
    server = Server()

    # Encrypt documents and store them on the server
    for doc_id, (plaintext, _) in docs.items():
        encrypted = client.encrypt_document(doc_id, plaintext, "data/encrypted_docs")
        server.documents[doc_id] = encrypted

    # Build a local secure index (e.g., Bloom Filter) for each document
    for doc_id, (_, tokens) in docs.items():
        index = client.create_index(doc_id, tokens)
        server.indices[doc_id] = index

    # Generate trapdoor and perform search multiple times to calculate average
    T = client.build_trapdoor("hepatite")
    durations = []
    for _ in range(5):
        start = time.perf_counter()
        _ = server.search(T, client.s)
        durations.append(time.perf_counter() - start)

    avg_time = sum(durations) / len(durations)
    return len(docs), avg_time

if __name__ == "__main__":
    results = [run_test()]

    os.makedirs("charts", exist_ok=True)
    with open(CSV_OUTPUT, "a", newline="") as f:
        writer = csv.writer(f)

        # Write the header only if the file is empty
        if os.stat(CSV_OUTPUT).st_size == 0:
            writer.writerow(["total_documents", "avg_search_time_sec"])

        writer.writerows(results)
