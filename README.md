# 🔐 Searchable Encryption System

This implementation is based on the searchable encryption scheme described in:

**Secure Indexes**  
Eu-Jin Goh  
[eu-jin@cs.stanford.edu](mailto:eujin@cs.stanford.edu)

This paper introduces the concept of using Bloom Filters and pseudorandom functions to support efficient and secure keyword search over encrypted data. Our project adapts the construction and ideas from this work using modern cryptographic primitives such as HMAC-SHA256.

## Quick Setup

If you're running on a VM or fresh environment, you can auto-setup everything by running:

```bash
bash setup_vm.sh
```
This script will:

- Create a Python virtual environment

- Install all dependencies (requirements.txt)

- Create necessary folders (data/)

- Set up your project to run immediately

## Run the system

```bash
python main.py
```

This will:

- Generate synthetic documents

- Encrypt them with AES

- Build secure Bloom filter indices

- Allow you to search on encrypted data

Example Search Output

```bash
Search word (or 'exit'): diabetes
Matching documents: doc3, doc12, doc57
Search time: 0.0021 seconds
```

## Running Tests

```bash
PYTHONPATH=. pytest tests/
```

This runs:

- test_crypto.py: unit tests for key generation and PRF

- test_index.py: tests for secure index correctness

- test_integration.py: full encryption + indexing + search validation

## Technologies Used

- cryptography.fernet — AES-based symmetric encryption

- HMAC + SHA256 — Pseudorandom Function (PRF)

- pytest — Python testing framework

- Faker — Fake data generation (patients, diseases, etc.)
