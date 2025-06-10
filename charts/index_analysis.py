# ---------------------------------------------------------------
# This script was used to measure the index creation time for the
# document-based index (Algorithm 2), which will later be compared 
# with the index creation time of the keyword-based index (Algorithm 1).
# It simulates the process of building per-document Bloom Filters,
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

def run_test(r=10, bloom_size=256):
    documents = load_documents_from_folder(DOCUMENTS_FOLDER)
    client = Client(r=r, bloom_size=bloom_size)
    server = Server()

    # Measure indexing time
    start = time.time()
    for doc_id, (_, tokens) in documents.items():
        index = client.create_index(doc_id, tokens)
        server.indices[doc_id] = index
    total_time = time.time() - start
    # change the total documents dinamic
    return 10, total_time

if __name__ == "__main__":
    results = [run_test()]

    os.makedirs("charts", exist_ok=True)
    with open(CSV_OUTPUT, "a", newline="") as f:
        writer = csv.writer(f)

        # Write the header only if the file is empty
        if os.stat(CSV_OUTPUT).st_size == 0:
            writer.writerow(["total_documents", "avg_search_time_sec"])
        writer.writerows(results)
