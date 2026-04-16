import networkx as nx
import numpy as np


def create_threshold_graph(nodes, similarity_matrix, threshold=0.75) -> nx.Graph:
    G = nx.Graph()

    for i in range(len(nodes)):
        G.add_node(nodes[i])

    for i in range(len(nodes)):
        for j in range(i + 1, len(nodes)):
            similarity = similarity_matrix[i][j]

            if similarity > threshold:
                G.add_edge(nodes[i], nodes[j], weight=similarity)

    return G


def create_knn_graph(nodes, similarity_matrix, k=3) -> nx.Graph:
    G = nx.Graph()

    for node in nodes:
        G.add_node(node)

    n = len(nodes)

    for i in range(n):
        row_sim = similarity_matrix[i]

        neighbors = np.argsort(row_sim)[::-1]
        neighbors = neighbors[neighbors != i]

        top_k = neighbors[:k]

        for j in top_k:
            sim = row_sim[j]
            G.add_edge(nodes[i], nodes[j], weight=sim)

    return G


def create_symmetric_knn_graph(nodes, similarity_matrix, k=4) -> nx.Graph:
    G = nx.Graph()

    for node in nodes:
        G.add_node(node)

    n = len(nodes)

    for i in range(n):
        neighbors_i = set(np.argsort(similarity_matrix[i])[::-1][1 : k + 1])

        for j in neighbors_i:
            neighbors_j = set(np.argsort(similarity_matrix[j])[::-1][1 : k + 1])

            if i in neighbors_j:
                sim = similarity_matrix[i, j]
                G.add_edge(nodes[i], nodes[j], weight=float(sim))

    return G
