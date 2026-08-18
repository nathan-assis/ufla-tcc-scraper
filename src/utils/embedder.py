import numpy as np
from typing import List
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


MODEL_NAME = "all-MiniLM-L6-v2"


def get_embedding_model() -> SentenceTransformer:
    return SentenceTransformer(MODEL_NAME)


def build_embeddings(model: SentenceTransformer, texts: List[str] | str) -> np.ndarray:
    is_str = isinstance(texts, str)
    if is_str:
        texts = [texts]

    embeddings = model.encode(texts, normalize_embeddings=True)

    return embeddings[0] if is_str else embeddings


def build_similarity_matrix(embeddings: np.ndarray):
    return cosine_similarity(embeddings)