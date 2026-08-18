import numpy as np
import networkx as nx
from pathlib import Path
from typing import Any, Dict, List, Tuple
from networkx.algorithms.approximation import steiner_tree

from ..types import *


def build_graph(nodes: Dict[str, Node], model) -> Tuple[nx.Graph, Dict[str, np.ndarray]]:
    from .embedder import build_embeddings, build_similarity_matrix

    ids = list(nodes)
    resumos = [n["resumo"] for n in nodes.values()]

    embeddings = build_embeddings(model, resumos)
    embeddings_dict = {node_id: emb for node_id, emb in zip(ids, embeddings)}

    matrix = build_similarity_matrix(embeddings)
    edges = _build_knn_edges(ids, matrix, k=3)

    G = nx.Graph()
    G.add_nodes_from(nodes.items())
    G.add_edges_from(edges)

    return G, embeddings_dict


def _build_knn_edges(nodes: List[str], similarity_matrix: Any, k: int = 3) -> List[Edge]:
    edges: List[Edge] = []
    for i, source in enumerate(nodes):
        neighbors = np.argsort(similarity_matrix[i])[::-1]
        neighbors = neighbors[neighbors != i]
        for j in neighbors[:k]:
            target = nodes[j]
            edges.append((source, target, {"weight": float(similarity_matrix[i, j])}))
    return edges


def save_graph(G: nx.Graph, embeddings: Dict[str, np.ndarray], path: Path) -> None:
    nx.write_graphml(G, path)

    ids = np.array(list(embeddings.keys()))
    matrix = np.stack(list(embeddings.values())).astype(np.float32)
    np.savez_compressed(path.with_suffix(".npz"), ids=ids, embeddings=matrix)


def load_graph(path: Path) -> Tuple[nx.Graph, Dict[str, np.ndarray]]:
    G = nx.read_graphml(path)

    emb_path = path.with_suffix(".npz")
    embeddings: Dict[str, np.ndarray] = {}
    if emb_path.exists():
        data = np.load(emb_path)
        ids, matrix = data["ids"], data["embeddings"]
        embeddings = {node_id: matrix[i] for i, node_id in enumerate(ids)}

    return G, embeddings


def to_json(G: nx.Graph) -> Dict[str, Any]:
    return nx.node_link_data(G, edges="edges")


def build_subgraph(graph: nx.Graph, top_k: list[str]) -> nx.Graph:
    if not top_k:
        return nx.Graph()

    terminals = set([node for node in top_k if node in graph])

    if len(terminals) <= 1:
        return graph.subgraph(terminals).copy()

    steiner_graph = graph.copy()
    for u, v, data in steiner_graph.edges(data=True):
        # print(u, v)
        similarity = max(-1.0, min(1.0, data.get("weight", 0.0)))
        data["cost"] = max(0.0, 1.0 - similarity)

    subgraph = nx.Graph()
    for component in nx.connected_components(steiner_graph):
        component_terminals = terminals.intersection(component)
        if not component_terminals:
            continue

        component_graph = steiner_graph.subgraph(component)
        if len(component_terminals) == 1:
            subgraph.add_node(next(iter(component_terminals)))
        else:
            subgraph = nx.compose(
                subgraph,
                steiner_tree(component_graph, component_terminals, weight="cost"),
            )

    return subgraph