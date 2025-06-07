import os
import random
import math
from faker import Faker

fake = Faker('pt_BR')
DISEASES = ["diabetes", "hipertensao", "asma", "covid", "bronquite", "cancer", "dengue", "gripe", "hepatite", "alergia"]
AGE_RANGE = range(1, 100)

DISEASE_PROPORTIONS = {
    "bronquite": 0.08,
    "gripe": 0.02,
    "hepatite": 0.40,
    "cancer": 0.10,
    "covid": 0.10,
    "dengue": 0.10,
    "hipertensao": 0.10,
    "diabetes": 0.05,
    "asma": 0.02,
    "alergia": 0.01
}

def compute_bloom_parameters(n_keywords_per_doc, false_positive_rate=0.01):
    """
    Computes the ideal Bloom filter size (in bits) and number of hash functions.
    """
    if n_keywords_per_doc <= 0 or false_positive_rate <= 0 or false_positive_rate >= 1:
        raise ValueError("Invalid input parameters.")
    ln2_squared = (math.log(2)) ** 2
    m = -(n_keywords_per_doc * math.log(false_positive_rate)) / ln2_squared
    r = (m / n_keywords_per_doc) * math.log(2)
    return int(round(m)), int(round(r))

def generate_phone():
    return fake.phone_number()

def generate_patient_name():
    return fake.name()

def generate_documents(n, output_folder="data/documents", max_diseases_per_patient=5, fixed_disease="hepatite", fixed_proportion=0.4):
    os.makedirs(output_folder, exist_ok=True)
    total_diseases_needed = n * max_diseases_per_patient

    # Step 1: Allocate fixed disease
    num_fixed = round(total_diseases_needed * fixed_proportion)
    disease_pool = [fixed_disease] * num_fixed

    # Step 2: Normalize remaining proportions
    remaining_diseases = {k: v for k, v in DISEASE_PROPORTIONS.items() if k != fixed_disease}
    total_remaining = sum(remaining_diseases.values())
    normalized_remaining = {k: v / total_remaining for k, v in remaining_diseases.items()}

    # Step 3: Allocate other diseases proportionally
    num_remaining = total_diseases_needed - num_fixed
    for disease, weight in normalized_remaining.items():
        count = round(num_remaining * weight)
        disease_pool.extend([disease] * count)

    # Adjust for exact length
    while len(disease_pool) < total_diseases_needed:
        disease_pool.append(random.choice(list(normalized_remaining.keys())))
    disease_pool = disease_pool[:total_diseases_needed]
    random.shuffle(disease_pool)

    for i in range(1, n + 1):
        name = generate_patient_name()
        age = str(random.choice(AGE_RANGE))
        neighborhood = fake.bairro()
        phone = generate_phone()

        # Select diseases for the patient
        num_diseases = random.randint(1, max_diseases_per_patient)
        diseases = set()
        while len(diseases) < num_diseases and disease_pool:
            diseases.add(disease_pool.pop())

        content = (
            f"Name: {name}\n"
            f"Disease: {', '.join(diseases)}\n"
            f"Age: {age}\n"
            f"Neighborhood: {neighborhood}\n"
            f"Phone: {phone}\n"
        )

        file_path = os.path.join(output_folder, f"doc{i}.txt")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

def generate_documents_fixed_keywords(n, output_folder="data/documents", keywords_per_doc=5):
    """
    Generates `n` documents, each containing exactly `keywords_per_doc` diseases (keywords).
    """

    os.makedirs(output_folder, exist_ok=True)

    total_needed = n * keywords_per_doc
    disease_pool = DISEASES * ((total_needed // len(DISEASES)) + 1)
    disease_pool = disease_pool[:total_needed]
    random.shuffle(disease_pool)

    for i in range(1, n + 1):
        name = generate_patient_name()
        age = str(random.choice(AGE_RANGE))
        neighborhood = fake.bairro()
        phone = generate_phone()

        # Select exactly `keywords_per_doc` diseases
        diseases = [disease_pool.pop() for _ in range(keywords_per_doc)]

        content = (
            f"Name: {name}\n"
            f"Disease: {', '.join(diseases)}\n"
            f"Age: {age}\n"
            f"Neighborhood: {neighborhood}\n"
            f"Phone: {phone}\n"
        )

        file_path = os.path.join(output_folder, f"doc{i}.txt")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

def load_documents_from_folder(input_folder="data/documents"):
    """
    Loads text documents and extracts only the 'Disease' field as tokens for indexing.
    Returns a dictionary of the form: doc_id → (full_plaintext_content, [disease1, disease2, ...])
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
                if line.lower().startswith("disease:"):
                    value = line.split(":", 1)[1].strip()
                    diseases = [d.strip().lower() for d in value.split(",")]
                    tokens.extend(diseases)

            documents[doc_id] = (content, tokens)

    return documents

