# 🔐 Document-Based Searchable Encryption System

This project implements a **document-based searchable encryption scheme**, inspired by the construction in:

**Secure Indexes**  
*Eu-Jin Goh*  
[eu-jin@cs.stanford.edu](mailto:eujin@cs.stanford.edu)

The implemented model supports **searching for a single keyword at a time** over encrypted documents using **Bloom Filters** and **pseudorandom functions (PRFs)**. It ensures that searches can be performed without decrypting the content, and that the search tokens (trapdoors) reveal minimal information about the queried words.

This implementation follows the structure proposed in Goh's paper and adapts it using modern cryptographic primitives like **HMAC-SHA256**, while maintaining the theoretical properties of **searchable symmetric encryption (SSE)**.

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

## 📚 Reference

Goh, E.-J. (2004). Secure Indexes.
https://eprint.iacr.org/2003/216.pdf
