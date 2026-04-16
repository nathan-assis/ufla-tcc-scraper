from sklearn.metrics.pairwise import cosine_similarity

def similarity_matrix(embeddings):
    sim_matrix = cosine_similarity(embeddings)

    return sim_matrix