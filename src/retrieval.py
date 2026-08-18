import numpy as np
import networkx as nx
from sentence_transformers import SentenceTransformer
from .utils.embedder import build_embeddings
from utils.graph_builder import build_subgraph


def retrieval(message: str, graph: nx.Graph, model: SentenceTransformer) -> nx.Graph:
    print(".:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.")
    print("                   .:. Retrieval .:.                   ")
    print(".:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.")

    print(".:. Gerando embedding .:.")
    msg_embedding = build_embeddings(model, message)

    print(".:. Busca semântica .:.")
    top_k = get_tok_k(
        msg_embedding,
        graph,
        model,
        5
    )

    print(".:. Construindo subgrafo .:.")
    subgraph = build_subgraph(graph, top_k)

    return subgraph


    
def get_tok_k(
    msg_embedding: np.ndarray,
    graph: nx.Graph,
    model: SentenceTransformer,
    k: int = 10,
) -> list[str]:
    nodes, resumos = [], []
    for node_id, node in graph.nodes(data=True):
        resumo = node.get("resumo")
        if not resumo:
            continue

        nodes.append(node_id)
        resumos.append(resumo)

    embeddings = build_embeddings(model, resumos)
    scores = embeddings @ msg_embedding

    k = min(k, len(nodes))
    top_indices = np.argpartition(
        scores,
        -k,
    )[-k:]

    top_indices = top_indices[
        np.argsort(scores[top_indices])[::-1]
    ]

    return [
        nodes[i]
        for i in top_indices
    ]