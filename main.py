from utils.generators import generate_documents, load_documents_from_folder
from core.client import Client
from core.server import Server
import os
import time
import pickle
import csv
import gc  
import statistics

# Configuration
TOTAL = 100 # Total number of documents to generate
BATCH_SIZE = 10000 # Process documents in batches
DOCUMENTS_FOLDER = "data/documents"
ENCRYPTED_FOLDER = "data/encrypted_docs"
SUMMARY_FILE = "data/summary_times.csv"

def main():
    # Create necessary folders
    os.makedirs(DOCUMENTS_FOLDER, exist_ok=True)
    os.makedirs(ENCRYPTED_FOLDER, exist_ok=True)

    # Generate all documents at once
    print( "Generating documents...")
    generate_documents(TOTAL, output_folder=DOCUMENTS_FOLDER)

    # Initialize client (for encryption and indexing) and server (for storage and search)
    print( "Initializing client and server...")
    client = Client()
    server = Server()

    total_encrypt_time = 0
    total_index_time = 0

    # Load all documents into memory
    all_docs = load_documents_from_folder(DOCUMENTS_FOLDER)
    all_doc_ids = list(all_docs.keys())

    # Process in batches to avoid memory overload
    for i in range(0, TOTAL, BATCH_SIZE):
        current_batch_size = min(BATCH_SIZE, TOTAL - i)
        batch_num = (i // BATCH_SIZE) + 1

        print(f"Processing batch {batch_num} with {current_batch_size} documents")

        batch_doc_ids = all_doc_ids[i:i+current_batch_size]
        batch_docs = {doc_id: all_docs[doc_id] for doc_id in batch_doc_ids}

        # Encrypt each document and store it
        for doc_id, (plaintext, _) in batch_docs.items():
            encrypted = client.encrypt_document(doc_id, plaintext, output_folder=ENCRYPTED_FOLDER)
            server.documents[doc_id] = encrypted

        # Create a secure index for each document
        start_idx = time.time()
        for doc_id, (_, tokens) in batch_docs.items():
            index = client.create_index(doc_id, tokens)
            server.indices[doc_id] = index
        total_index_time += time.time() - start_idx

    print("Processing completed")
    print(f"Total indexing time: {total_index_time:.2f} seconds")

    while True:
        q = input("Search word (or 'exit'): ").strip().lower()
        if q == 'exit':
            break

        # Generate trapdoor for the keyword
        T = client.build_trapdoor(q)
        durations = []

        # Perform the same search multiple times and calculate average time
        for _ in range(50):
            start = time.perf_counter()
            matches = server.search(T, client.s)
            durations.append(time.perf_counter() - start)

        search_duration = statistics.mean(durations)

        # Display matching documents
        if matches:
            print(f"Matching documents: {', '.join(matches)}")

            # Ask user if they want to decrypt and view them
            view = input("Do you want to decrypt and view the matching documents? (yes/no): ").strip().lower()
            if view == 'yes':
                for doc_id in matches:
                    decrypted = client.decrypt_document(doc_id, input_folder=ENCRYPTED_FOLDER)
                    print(f"\n📄 Document {doc_id} content:\n{'-'*40}\n{decrypted}\n{'-'*40}")
        else:
            print("No documents matched.")

        print(f"Average search time: {search_duration:.6f} seconds")

        # Save result to CSV
        with open(SUMMARY_FILE, "a", newline="") as f:
            writer = csv.writer(f)
            if f.tell() == 0:
                writer.writerow(["num_documents", "encrypt_time_sec", "index_time_sec", "search_time_sec"])
            row = [TOTAL, f"{total_encrypt_time:.3f}", f"{total_index_time:.3f}", f"{search_duration:.3f}"]
            writer.writerow(row)

if __name__ == "__main__":
    main()
