# src/services/embeddings.py
import logging
from typing import Optional

import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Serviço para gerar embeddings e calcular similaridade."""
    
    def __init__(self, model_name: str):
        logger.info(f"Carregando modelo de embeddings: {model_name}")
        self.model = SentenceTransformer(model_name)
    
    def encode(self, texts: list[str] | str) -> np.ndarray:
        """Gera embeddings para textos."""
        if isinstance(texts, str):
            texts = [texts]
        return self.model.encode(texts, normalize_embeddings=True)
    
    def similarity_matrix(self, embeddings: np.ndarray) -> np.ndarray:
        """Calcula matriz de similaridade (cosseno)."""
        return cosine_similarity(embeddings)