import numpy as np
import networkx as nx
from sentence_transformers import SentenceTransformer
from .utils.embedder import build_embeddings
from .utils.graph_builder import build_subgraph


def retrieval(
    message: str,
    graph: nx.Graph,
    embeddings: dict[str, np.ndarray],
    model: SentenceTransformer
) -> nx.Graph:
    print(".:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.")
    print("                   .:. Retrieval .:.                   ")
    print(".:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.")

    print(".:. Gerando embedding .:.")
    msg_embedding = build_embeddings(model, message)

    print(".:. Busca semântica .:.")
    top_k = get_tok_k(
        msg_embedding,
        embeddings,
        5
    )
    print(".:.:.:.:.:.:.:.:.:.:.:.:.")
    print("top_k:", top_k)
    print(".:.:.:.:.:.:.:.:.:.:.:.:.")

    print(".:. Construindo subgrafo .:.")
    subgraph = build_subgraph(graph, top_k)
    print(".:.:.:.:.:.:.:.:.:.:.:.:.")
    print("subgraph:", subgraph)
    print(".:.:.:.:.:.:.:.:.:.:.:.:.")

    return subgraph


    
def get_tok_k(
    msg_embedding: np.ndarray,
    embeddings: dict[str, np.ndarray],
    k: int = 10,
) -> list[str]:
    ids = list(embeddings.keys())
    matrix = np.stack(list(embeddings.values()))

    scores = matrix @ msg_embedding

    k = min(k, len(ids))
    top_indices = np.argpartition(scores, -k)[-k:]
    top_indices = top_indices[np.argsort(scores[top_indices])[::-1]]

    return [ids[i] for i in top_indices]