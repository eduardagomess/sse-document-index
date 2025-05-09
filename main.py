from utils.generators import generate_documents, load_documents_from_folder
from core.client import Client
from core.server import Server
import os
import time
import pickle
import csv

# Configuration
TOTAL = 10
BATCH_SIZE = 10_000
NUM_BATCHES = max(1, (TOTAL + BATCH_SIZE - 1) // BATCH_SIZE)
DOCUMENTS_FOLDER = "data/documents"
ENCRYPTED_FOLDER = "data/encrypted_docs"
INDEX_FILE = "data/index.pkl"
SUMMARY_FILE = "data/summary_times.csv"

def main():
    os.makedirs(DOCUMENTS_FOLDER, exist_ok=True)
    os.makedirs(ENCRYPTED_FOLDER, exist_ok=True)

    client = Client()
    server = Server()

    print(f"📦 Starting processing in {NUM_BATCHES} batches of {BATCH_SIZE} documents...")

    total_encrypt_time = 0
    total_index_time = 0

    for batch in range(NUM_BATCHES):
        print(f"\n🚀 Processing batch {batch + 1}/{NUM_BATCHES}")

        # 1. Generate documents
        generate_documents(BATCH_SIZE, output_folder=DOCUMENTS_FOLDER)

        # 2. Load documents
        docs = load_documents_from_folder(DOCUMENTS_FOLDER)

        # 3. Encrypt documents
        start_enc = time.time()
        for doc_id, (text, _) in docs.items():
            encrypted = client.encrypt_document(doc_id, text, output_folder=ENCRYPTED_FOLDER)
            server.documents[doc_id] = encrypted
        end_enc = time.time()
        enc_time = end_enc - start_enc
        total_encrypt_time += enc_time

        # 4. Index documents
        start_idx = time.time()
        for doc_id, (_, tokens) in docs.items():
            index = client.create_index(doc_id, tokens)
            server.indices[doc_id] = index
        end_idx = time.time()
        idx_time = end_idx - start_idx
        total_index_time += idx_time

        # 5. Delete clear-text files to save disk space
        #for f in os.listdir(DOCUMENTS_FOLDER):
            #os.remove(os.path.join(DOCUMENTS_FOLDER, f))

    # 6. Save full index to disk
    with open(INDEX_FILE, "wb") as f:
        pickle.dump(server.indices, f)

    print("\n✅ Processing completed!")
    print(f"🔐 Total encryption time: {total_encrypt_time:.2f} seconds")
    print(f"🧠 Total indexing time: {total_index_time:.2f} seconds")

    # 7. Wait for user search
    search_duration = None

    while True:
        q = input("\n🔍 Search word (or 'exit'): ").strip().lower()
        if q == 'exit':
            break

        T = client.build_trapdoor(q)
        start = time.time()
        matches = server.search(T, client.K_priv, client.s)
        duration = time.time() - start
        search_duration = duration

        if matches:
            print(f"📂 Matching documents: {', '.join(matches)}")
        else:
            print("❌ No documents matched the search.")
        print(f"⏱️ Search time: {duration:.4f} seconds")

        # Save final summary with search time
        with open(SUMMARY_FILE, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["encrypt_time_sec", "index_time_sec", "search_time_sec"])
            writer.writerow([total_encrypt_time, total_index_time, search_duration])

if __name__ == "__main__":
    main()
