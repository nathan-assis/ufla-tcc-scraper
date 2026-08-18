import numpy as np
from typing import List
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


MODEL_NAME = "all-MiniLM-L6-v2"


def get_embedding_model() -> SentenceTransformer:
    return SentenceTransformer(MODEL_NAME)


def build_embeddings(model: SentenceTransformer, texts: List[str] | str) -> np.ndarray:
    if isinstance(texts, str):
        texts = [texts]
    return model.encode(texts, normalize_embeddings=True)


def build_similarity_matrix(embeddings: np.ndarray):
    return cosine_similarity(embeddings)