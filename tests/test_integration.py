from core.client import Client
from core.server import Server
from core.crypto import trapdoor


def test_search_finds_word_in_document():
    """
    Searching for a word that exists in the document should return its ID
    """

    print("\n[Integration Test] Search should find words in a document.")
    client = Client()
    server = Server()

    doc_id = "doc1"
    content = "Name: Ana\nDisease: diabetes\nAge: 35\nNeighborhood: Centro\nPhone: 9999-0000"
    tokens = ["Ana", "diabetes", "35", "Centro", "9999-0000"]

    # Encrypt and index the document
    encrypted = client.encrypt_document(doc_id, content, output_folder="data/encrypted_docs")
    index = client.create_index(doc_id, tokens)
    server.store(doc_id, encrypted, index)

    # Search for the word "diabetes"
    T = client.build_trapdoor("diabetes")
    result = server.search(T, client.s)

    print(f"  - Search result for 'diabetes': {result}")
    assert doc_id in result

def test_search_returns_multiple_matches():
    """
    If the same word is in two documents, both IDs should be returned
    """
      
    print("\n[Integration Test] Same word in two documents should return both IDs.")
    client = Client()
    server = Server()

    content1 = "Name: Ana\nDisease: dengue"
    content2 = "Name: Beto\nDisease: dengue"
    tokens1 = ["Ana", "dengue"]
    tokens2 = ["Beto", "dengue"]

    # Encrypt and index both documents
    encrypted1 = client.encrypt_document("doc1", content1, output_folder="data/encrypted_docs")
    encrypted2 = client.encrypt_document("doc2", content2, output_folder="data/encrypted_docs")
    index1 = client.create_index("doc1", tokens1)
    index2 = client.create_index("doc2", tokens2)

    server.store("doc1", encrypted1, index1)
    server.store("doc2", encrypted2, index2)

    # Search for "dengue"
    T = client.build_trapdoor("dengue")
    result = server.search(T, client.s)

    print(f"  - Search result for 'dengue': {result}")
    assert "doc1" in result and "doc2" in result
    assert len(result) == 2

def test_search_returns_nothing_for_absent_word():
    """
    Searching for a word not in any document should return an empty list
    """

    print("\n[Integration Test] Search for a word not in any document should return empty list.")
    client = Client()
    server = Server()

    content = "Name: Clara\nDisease: flu"
    tokens = ["Clara", "flu"]

    # Encrypt and index one document
    encrypted = client.encrypt_document("doc3", content, output_folder="data/encrypted_docs")
    index = client.create_index("doc3", tokens)
    server.store("doc3", encrypted, index)

    # Try searching for a word that wasn't added
    T = client.build_trapdoor("covid")
    result = server.search(T, client.s)

    print(f"  - Search result for 'covid': {result}")
    assert result == []


def test_search_with_wrong_key_fails():
    """
    This test verifies that search using an incorrect secret key
    does not return any results, ensuring that only authorized users
    with the correct key can generate valid trapdoors for queries.
    """

    print("\n[Security Test] Search with wrong key should not return matches.")

    from core.client import Client
    from core.server import Server
    from core.crypto import keygen, trapdoor

    client = Client()
    server = Server()

    doc_id = "doc1"
    content = "Name: Alice\nDisease: cancer"
    tokens = ["Alice", "cancer"]

    encrypted = client.encrypt_document(doc_id, content, output_folder="data/encrypted_docs")
    index = client.create_index(doc_id, tokens)
    server.store(doc_id, encrypted, index)

    # Attacker generates a different key and trapdoor
    fake_key = keygen(client.s, client.r)
    fake_trap = trapdoor(fake_key, "cancer", client.s)

    result = server.search(fake_trap, client.s)
    print(f"  - Search result with wrong key: {result}")
    assert doc_id not in result, "Search with wrong key should not match document"
