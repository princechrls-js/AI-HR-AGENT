import faiss
import numpy as np
import pickle
import os
from app.core.config import settings

class FAISSService:
    def __init__(self, index_path: str = settings.FAISS_INDEX_PATH, metadata_path: str = settings.FAISS_METADATA_PATH):
        self.index_path = index_path
        self.metadata_path = metadata_path
        self.dimension = 768 # Default for bge-base-en
        self.index = None
        self.metadata = [] # List of job IDs
        self._load_or_create_index()

    def _load_or_create_index(self):
        if os.path.exists(self.index_path):
            self.index = faiss.read_index(self.index_path)
            with open(self.metadata_path, 'rb') as f:
                self.metadata = pickle.load(f)
        else:
            self.index = faiss.IndexFlatL2(self.dimension)
            self.metadata = []

    def add_job_vector(self, vector: np.ndarray, job_id: int):
        if vector.shape[0] != self.dimension:
            # Re-initialize index if dimension mismatch (unlikely with same model)
            self.dimension = vector.shape[0]
            self.index = faiss.IndexFlatL2(self.dimension)
        
        self.index.add(vector.reshape(1, -1).astype('float32'))
        self.metadata.append(job_id)
        self.save_index()

    def save_index(self):
        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
        faiss.write_index(self.index, self.index_path)
        with open(self.metadata_path, 'wb') as f:
            pickle.dump(self.metadata, f)

    def search_similar_jobs(self, query_vector: np.ndarray, top_k: int = 5):
        D, I = self.index.search(query_vector.reshape(1, -1).astype('float32'), top_k)
        results = []
        for idx in I[0]:
            if idx != -1 and idx < len(self.metadata):
                results.append(self.metadata[idx])
        return results

faiss_service = FAISSService()
