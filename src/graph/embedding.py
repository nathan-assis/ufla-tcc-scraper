from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

model = SentenceTransformer("all-MiniLM-L6-v2")


def generate_embeddings(text: list[str] | str):
    embeddings = model.encode(text, normalize_embeddings=True)

    return embeddings


def similarity_matrix(embeddings):
    similarity_matrix = cosine_similarity(embeddings)

    return similarity_matrix