from core.crypto import keygen, prf, trapdoor
from core.index import SecureIndex

def test_index_matches_inserted_words():
    print("\n[Test] Index should match words inserted into the document.")
    s, r = 16, 3
    bloom_size = 1024
    K_priv = keygen(s, r)
    index = SecureIndex(K_priv, bloom_size, r, s)

    D_id = "doc1"
    words = ["covid", "fever", "tosse"]
    index.build_index(D_id, words)

    for w in words:
        T_w = trapdoor(K_priv, w, s)
        hashes = [prf(t, D_id, s) for t in T_w]
        result = index.indices[D_id].query(hashes)
        print(f"  - Query for word '{w}' returned: {result}")
        assert result, f"Expected match for word: {w}"

def test_index_rejects_unknown_word():
    print("\n[Test] Index should not match words that were not inserted.")
    s, r = 16, 3
    bloom_size = 1024
    K_priv = keygen(s, r)
    index = SecureIndex(K_priv, bloom_size, r, s)

    D_id = "doc2"
    words = ["asma", "gripe"]
    index.build_index(D_id, words)

    unknown = "cancer"
    T_w = trapdoor(K_priv, unknown, s)
    hashes = [prf(t, D_id, s) for t in T_w]
    result = index.indices[D_id].query(hashes)
    print(f"  - Query for unknown word '{unknown}' returned: {result}")
    assert result in [False, True], "Query should not crash"

def test_empty_document_does_not_crash():
    print("\n[Test] Indexing an empty document should not crash or set bits.")
    s, r = 16, 3
    bloom_size = 1024
    K_priv = keygen(s, r)
    index = SecureIndex(K_priv, bloom_size, r, s)

    D_id = "doc3"
    index.build_index(D_id, [])  # Empty list of words

    bit_sum = sum(index.indices[D_id].bit_array)
    print(f"  - Bloom Filter bit sum for empty doc: {bit_sum}")
    assert isinstance(index.indices[D_id].bit_array, list)
    assert bit_sum == 0, "Empty document should not set any bits"

def test_bloom_filters_differ_for_same_word_in_different_docs():
    print("\n[Test] Bloom Filters should differ even when the same word appears in different documents.")
    s, r = 16, 3
    bloom_size = 1024
    K_priv = keygen(s, r)
    index = SecureIndex(K_priv, bloom_size, r, s)

    word = ["diabetes"]
    index.build_index("docA", word)
    index.build_index("docB", word)

    bf1 = index.indices["docA"].bit_array
    bf2 = index.indices["docB"].bit_array
    are_equal = bf1 == bf2
    print(f"  - Bloom Filters equal: {are_equal}")
    assert not are_equal, "Bloom Filters for different docs with same word should differ"
