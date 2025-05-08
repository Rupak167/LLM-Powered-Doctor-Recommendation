import os
import json
import pickle
import numpy as np
import faiss
from environs import Env
from sentence_transformers import SentenceTransformer

env=Env()
env.read_env()

class DoctorFaissIndex:
    def __init__(self, model_name='all-MiniLM-L6-v2', index_file=env.str("VECTOR_DATA_PATH"), meta_file=env.str("METADATA_PATH")):
        self.model = SentenceTransformer(model_name)
        self.index_file = index_file
        self.meta_file = meta_file
        self.index = None
        self.metadata = []

    def build_index(self, json_file):
        # Load doctor data
        with open(json_file, 'r') as f:
            doctors = json.load(f)

        texts = []
        self.metadata = []

        for doc in doctors:
            desc = f"{doc.get('name', '')}, {doc.get('designation', '')}, Specialization: {doc.get('specialization', 'N/A')}, " \
            f"Experience: {doc.get('yoe', '0')} years, Tags: {', '.join(doc.get('tags', []))}, " \
            f"Available: {', '.join([a for a in doc.get('availability', []) if a])}, " \
            f"Hospital: {doc.get('hospital_info', '')}"
            texts.append(desc)
            self.metadata.append(doc)

        # Generate embeddings
        embeddings = self.model.encode(texts, show_progress_bar=True).astype('float32')

        # Create FAISS index
        dim = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dim)
        self.index.add(embeddings)

        # Save both index and metadata
        faiss.write_index(self.index, self.index_file)
        with open(self.meta_file, 'wb') as f:
            pickle.dump(self.metadata, f)

        print(f"Index built and saved to {self.index_file}, metadata to {self.meta_file}")

    def load_index(self):
        if not os.path.exists(self.index_file) or not os.path.exists(self.meta_file):
            raise FileNotFoundError("Index or metadata file not found.")

        self.index = faiss.read_index(self.index_file)
        with open(self.meta_file, 'rb') as f:
            self.metadata = pickle.load(f)

        print("Index and metadata loaded successfully.")

    def search(self, query, k=10):
        if self.index is None or not self.metadata:
            raise ValueError("Index not loaded. Call load_index() first.")

        query_vector = self.model.encode([query]).astype('float32')
        distances, indices = self.index.search(query_vector, k)

        results = [self.metadata[i] for i in indices[0]]
        return results
