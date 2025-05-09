from utils.generators import generate_documents, load_documents_from_folder
from core.client import Client
from core.server import Server
import os
import time
import pickle
import csv

TOTAL = 10  # total number of documents to create
BATCH_SIZE = 10_000  # number of documents per processing batch
DOCUMENTS_FOLDER = "data/documents"  # folder where plaintext documents are stored
ENCRYPTED_FOLDER = "data/encrypted_docs"  # folder where encrypted documents are saved
INDEX_FILE = "data/index.pkl"  # path to the serialized index file
SUMMARY_FILE = "data/summary_times.csv"  # file to store summary of processing times


def main():
    os.makedirs(DOCUMENTS_FOLDER, exist_ok=True)
    os.makedirs(ENCRYPTED_FOLDER, exist_ok=True)

    # instanciate entities
    client = Client()
    server = Server()

    # initialize time variables
    total_encrypt_time = 0
    total_index_time = 0

    for i in range(0, TOTAL, BATCH_SIZE):
        current_batch_size = min(BATCH_SIZE, TOTAL - i)
        batch_num = (i // BATCH_SIZE) + 1

        print(f"Processing batch {batch_num} (creating {current_batch_size} documents)")

        # generate documents
        generate_documents(current_batch_size, output_folder=DOCUMENTS_FOLDER)

        # load documents
        docs = load_documents_from_folder(DOCUMENTS_FOLDER)

        # encrypt documents
        start_enc = time.time()
        for doc_id, (text, _) in docs.items():
            print(doc_id)
            print((text, _))
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
        for f in os.listdir(DOCUMENTS_FOLDER):
            os.remove(os.path.join(DOCUMENTS_FOLDER, f))

    # 6. Save full index to disk
    with open(INDEX_FILE, "wb") as f:
        pickle.dump(server.indices, f)

    print("Processing completed!")
    print(f"Total encryption time: {total_encrypt_time:.2f} seconds")
    print(f"Total indexing time: {total_index_time:.2f} seconds")

    # 7. Wait for user search
    search_duration = None

    while True:
        q = input("Search word (or 'exit'): ").strip().lower()
        if q == 'exit':
            break

        T = client.build_trapdoor(q)
        start = time.time()
        matches = server.search(T, client.K_priv, client.s)
        duration = time.time() - start
        search_duration = duration

        if matches:
            print(f"Matching documents: {', '.join(matches)}")
        else:
            print("No documents matched the search.")
        print(f"Search time: {duration:.4f} seconds")

        # Save final summary with search time
        with open(SUMMARY_FILE, "a", newline="") as f:
            writer = csv.writer(f)
            if f.tell() == 0:  # if file is empty, write header
                writer.writerow(["encrypt_time_sec", "index_time_sec", "search_time_sec"])
            writer.writerow([total_encrypt_time, total_index_time, search_duration])


if __name__ == "__main__":
    main()
