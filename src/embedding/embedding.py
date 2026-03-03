from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")


def generate_embedding(chunks: list[str] | str):
    if not chunks or chunks == []:
        return []

    embeddings = model.encode(chunks, normalize_embeddings=True)
    return embeddings
