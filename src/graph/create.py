import networkx as nx


def create_graph(nodes, similarity_matrix) -> nx.Graph:
    G = nx.Graph()

    for i in range(len(nodes)):
        G.add_node(nodes[i])

    for i in range(len(nodes)):
        for j in range(i + 1, len(nodes)):
            similarity = similarity_matrix[i][j]

            if similarity > 0.8:
                G.add_edge(nodes[i], nodes[j], weight=similarity)

    return G


def create_knn_graph(nodes, similarity_matrix, k=3) -> nx.Graph:
    G = nx.Graph()

    for node in nodes:
        G.add_node(node)

    n = len(nodes)

    for i in range(n):
        similarities = similarity_matrix[i]

        neighbors = [(j, similarities[j]) for j in range(n) if j != i]
        neighbors.sort(key=lambda x: x[1], reverse=True)

        top_k = neighbors[:k]

        for j, sim in top_k:
            G.add_edge(nodes[i], nodes[j], weight=sim)

    return G