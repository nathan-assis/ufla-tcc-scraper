import networkx as nx
from pathlib import Path
from typing import Any, Dict, List

from ..types import *

def build_graph(nodes: Dict[str, Node], model) -> nx.Graph:
    def _build_edges(nodes: Dict[str, str]) -> List[Edge]:
        from .embedder import build_embeddings, build_similarity_matrix

        ids = list(nodes)
        resumos = list(nodes.values())

        embeddings = build_embeddings(model, resumos)
        matrix = build_similarity_matrix(embeddings)
        edges = _build_knn_edges(
            ids,
            matrix,
            k=3,
        )

        return edges

    def _build_knn_edges(
        nodes: List[str],
        similarity_matrix: Any,
        k: int = 3
    ) -> List[Edge]:
        import numpy as np
        edges: List[Edge] = []
        for i, source in enumerate(nodes):
            neighbors = np.argsort(similarity_matrix[i])[::-1]
            neighbors = neighbors[neighbors != i]

            for j in neighbors[:k]:
                target = nodes[j]

                edges.append(
                    (source, target, { "weight": float(similarity_matrix[i, j]) })
                )

        return edges

    G = nx.Graph()
    G.add_nodes_from(nodes.items())

    edges = _build_edges(nx.get_node_attributes(G, "resumo"))
    G.add_edges_from(edges)

    return G


def save_graph(G: nx.Graph, path: Path) -> None:
    nx.write_graphml(G, path)


def load_graph(path: Path) -> nx.Graph:
    return nx.read_graphml(path)


def to_json(G: nx.Graph) -> Dict[str, Any]:
    return nx.node_link_data(G, edges="edges")


def build_subgraph(
    graph: nx.Graph,
    top_k: list[str],
) -> nx.Graph:
    if not top_k:
        return nx.Graph()

    nodes = [
        node
        for node in top_k
        if node in graph
    ]

    return graph.subgraph(nodes).copy()