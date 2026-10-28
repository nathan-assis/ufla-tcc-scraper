import numpy as np
from typing import List
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

MODEL_NAME = "Qwen/Qwen3-Embedding-4B"


def get_embedding_model() -> SentenceTransformer:
    return SentenceTransformer(MODEL_NAME)


def build_embeddings(model, texts, is_query: bool = False):
    is_str = isinstance(texts, str)
    if is_str:
        texts = [texts]
    embeddings = model.encode(
        texts,
        prompt_name="query" if is_query else None,
        normalize_embeddings=True,
    )
    return embeddings[0] if is_str else embeddings


def build_similarity_matrix(embeddings: np.ndarray):
    return cosine_similarity(embeddings)
