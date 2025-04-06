import faiss
import numpy as np

def create_faiss_index(embeddings: np.ndarray) -> faiss.Index:
    d = embeddings.shape[1]  # Dimenze embeddingů
    index = faiss.IndexFlatL2(d)  # Index založený na L2 vzdálenosti
    index.add(embeddings)
    return index

def search_similar(query_embedding: np.ndarray, index: faiss.Index, k=5):
    distances, indices = index.search(query_embedding, k)
    return distances, indices

def save_index(index: faiss.Index, path: str = "faiss_index.bin"):
    faiss.write_index(index, path)

def load_index(path: str = "faiss_index.bin") -> faiss.Index:
    return faiss.read_index(path)
