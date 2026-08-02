import networkx as nx
from pathlib import Path
from typing import Any, Dict, List

from .types import *


BASE_DIR = Path(__file__).resolve().parent
PATH = BASE_DIR / "files" / "graph.graphml"

PATH.parent.mkdir(parents=True, exist_ok=True)


def load_graph() -> nx.Graph:
    try:
        if PATH.exists():
            return nx.read_graphml(PATH)

        return _build_graph()
    except Exception as e:
        print(f'graph_builder.py (load_graph): {e}')
        raise


def _save_graph(G: nx.Graph) -> None:
    nx.write_graphml(G, PATH)


def _build_graph() -> nx.Graph:
    from .scraper import scrape

    G = nx.Graph()

    nodes = scrape()
    G.add_nodes_from(nodes.items())

    edges = _build_edges(nx.get_node_attributes(G, "resumo"))
    G.add_edges_from(edges)

    _save_graph(G)

    return G


def _build_edges(nodes: Dict[str, str]) -> List[Edge]:
    from .embedder import build_embeddings, build_similarity_matrix

    ids = list(nodes)
    resumos = list(nodes.values())

    embeddings = build_embeddings(resumos)
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


if __name__ == "__main__":
    print(load_graph().nodes(data=True))