import networkx as nx

def graph_stats(G: nx.Graph):
    """
    Calcula estatísticas estruturais básicas de um grafo.

    As métricas incluem número de vértices e arestas, densidade,
    distribuição de graus, componentes conexas, coeficiente de clustering
    e, quando possível, medidas de caminho mínimo.

    :param G: Grafo do NetworkX a ser analisado.
    :type G: nx.Graph

    :return: Dicionário contendo estatísticas do grafo, incluindo:
             - num_vertices: número de nós
             - num_edges: número de arestas
             - density: densidade do grafo
             - avg_degree: grau médio
             - max_degree: maior grau
             - min_degree: menor grau
             - num_connected_components: número de componentes conexas
             - largest_component_size: tamanho da maior componente
             - avg_clustering: coeficiente médio de clustering
             - diameter: diâmetro do grafo (ou None se não conexo)
             - avg_shortest_path: caminho médio (ou None se não conexo)
    :rtype: dict[str, float | int | None]
    """
    stats = {}

    # Básico
    stats["num_vertices"] = G.number_of_nodes()
    stats["num_edges"] = G.number_of_edges()

    # Densidade
    stats["density"] = nx.density(G)

    # Grau
    degrees = dict(G.degree())
    stats["avg_degree"] = sum(degrees.values()) / len(degrees) if degrees else 0
    stats["max_degree"] = max(degrees.values()) if degrees else 0
    stats["min_degree"] = min(degrees.values()) if degrees else 0

    # Componentes conexas
    if nx.is_connected(G):
        stats["num_connected_components"] = 1
    else:
        stats["num_connected_components"] = nx.number_connected_components(G)

    stats["largest_component_size"] = len(max(nx.connected_components(G), key=len))

    # Coeficiente de clustering
    stats["avg_clustering"] = nx.average_clustering(G)

    # Caminhos (somente se conexo)
    if nx.is_connected(G):
        stats["diameter"] = nx.diameter(G)
        stats["avg_shortest_path"] = nx.average_shortest_path_length(G)
    else:
        stats["diameter"] = None
        stats["avg_shortest_path"] = None

    return stats