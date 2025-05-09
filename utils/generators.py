import os
import random
from faker import Faker

fake = Faker('pt_BR')
DISEASES = ["diabetes", "hipertensao", "asma", "covid", "bronquite", "cancer", "dengue", "gripe", "hepatite", "alergia"]
AGE_RANGE = range(1, 100)

def generate_phone():
    return fake.phone_number()

def generate_patient_name():
    return fake.name()

def generate_documents(n, output_folder="data/documents"):
    os.makedirs(output_folder, exist_ok=True)
    for i in range(1, n + 1):
        name = generate_patient_name()
        disease = random.choice(DISEASES)
        age = str(random.choice(AGE_RANGE))
        neighborhood = fake.bairro()
        phone = generate_phone()

        content = (
            f"Nome: {name}\n"
            f"Doença: {disease}\n"
            f"Idade: {age}\n"
            f"Bairro: {neighborhood}\n"
            f"Telefone: {phone}\n"
        )

        file_path = os.path.join(output_folder, f"doc{i}.txt")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

def load_documents_from_folder(input_folder="/data/documents"):
    """
    Loads text documents and extracts field values as whole-word tokens for indexing.
    Each document is returned as (content, list of tokens).
    """
    documents = {}
    for filename in os.listdir(input_folder):
        if filename.endswith(".txt"):
            doc_id = os.path.splitext(filename)[0]
            file_path = os.path.join(input_folder, filename)
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read().lower()

            tokens = []
            for line in content.splitlines():
                parts = line.split(":", 1)
                if len(parts) == 2:
                    value = parts[1].strip()
                    tokens.append(value)  # Extract full field value as one token
            documents[doc_id] = (content, tokens)
    return documents
