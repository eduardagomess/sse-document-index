import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.generators import generate_documents, load_documents_from_folder, compute_bloom_parameters
from core.client import Client
from core.server import Server
import os, time, csv, statistics

def run_experiment(num_documents, diseases_per_doc, prop_hepatite, experiment_name):
    print(f"Running {experiment_name} | docs={num_documents}, diseases/doc={diseases_per_doc}, p(hepatite)={prop_hepatite}")

    # Define folders for this experiment
    folder = f"data/exp_{experiment_name}"
    os.makedirs(folder, exist_ok=True)
    encrypted_folder = os.path.join(folder, "encrypted")
    docs_folder = os.path.join(folder, "docs")

    # Generate documents with the specified parameters
    generate_documents(
        num_documents,
        max_diseases_per_patient=diseases_per_doc,
        fixed_proportion=prop_hepatite,
        output_folder=docs_folder
    )
    documents = load_documents_from_folder(docs_folder)

    # Initialize client and server
    client = Client(r=10, bloom_size=128)
    server = Server()

    # Encrypt documents
    start_enc = time.time()
    for doc_id, (plain, _) in documents.items():
        server.documents[doc_id] = client.encrypt_document(doc_id, plain, encrypted_folder)
    encrypt_time = time.time() - start_enc

    # Index documents
    start_idx = time.time()
    for doc_id, (_, tokens) in documents.items():
        server.indices[doc_id] = client.create_index(doc_id, tokens)
    index_time = time.time() - start_idx

    # Measure average search time
    T = client.build_trapdoor("hepatite")
    durations = []
    for _ in range(5):
        start = time.perf_counter()
        _ = server.search(T, client.s)
        durations.append(time.perf_counter() - start)
    avg_search_time = statistics.mean(durations)

    print(f"{experiment_name} complete — avg search time: {avg_search_time:.6f}s")

    return 128, 10, round(encrypt_time, 3), round(index_time, 3), round(avg_search_time, 6)