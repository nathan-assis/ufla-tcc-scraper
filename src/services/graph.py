# src/services/graph.py
import logging
from typing import Optional

import networkx as nx
from networkx.algorithms.community import leiden_communities
from networkx.algorithms import community
import numpy as np

logger = logging.getLogger(__name__)


class GraphService:
    """Construtor de grafos a partir de matrizes de similaridade."""

    @staticmethod
    def _leiden_communities(G: nx.Graph, seed: int = 42):
        """Tenta detectar comunidades com Leiden e faz fallback se o backend não existir."""
        try:
            return list(leiden_communities(G, seed=seed, weight="weight"))
        except NotImplementedError as exc:
            return list(community.greedy_modularity_communities(G, weight="weight"))
        except Exception as exc:
            logger.warning(
                "Erro ao executar Leiden: %s. "
                "Usando fallback greedy_modularity_communities.",
                exc,
            )
            return list(community.greedy_modularity_communities(G, weight="weight"))

    @staticmethod
    def threshold(
        nodes: list[str],
        similarity_matrix: np.ndarray,
        threshold: float = 0.75
    ) -> nx.Graph:
        """Cria grafo conectando nós acima do threshold."""
        G = nx.Graph()
        G.add_nodes_from(nodes)
        
        for i in range(len(nodes)):
            for j in range(i + 1, len(nodes)):
                if similarity_matrix[i, j] > threshold:
                    G.add_edge(nodes[i], nodes[j], weight=similarity_matrix[i, j])
        
        logger.info(f"Grafo threshold criado: {G.number_of_nodes()} nós, {G.number_of_edges()} arestas")
        return G
    
    @staticmethod
    def knn(
        nodes: list[str],
        similarity_matrix: np.ndarray,
        k: int = 3
    ) -> nx.Graph:
        """Cria grafo KNN."""
        G = nx.Graph()
        G.add_nodes_from(nodes)
        
        for i in range(len(nodes)):
            row = similarity_matrix[i]
            neighbors = np.argsort(row)[::-1]
            neighbors = neighbors[neighbors != i]
            top_k = neighbors[:k]
            
            for j in top_k:
                G.add_edge(nodes[i], nodes[j], weight=similarity_matrix[i, j])
        
        logger.info(f"Grafo KNN criado: {G.number_of_nodes()} nós, {G.number_of_edges()} arestas")
        return G
    
    @staticmethod
    def symmetric_knn(
        nodes: list[str],
        similarity_matrix: np.ndarray,
        k: int = 4
    ) -> nx.Graph:
        """Cria grafo KNN simétrico (conexão mútua)."""
        G = nx.Graph()
        G.add_nodes_from(nodes)
        
        for i in range(len(nodes)):
            neighbors_i = set(np.argsort(similarity_matrix[i])[::-1][1:k + 1])
            
            for j in neighbors_i:
                neighbors_j = set(np.argsort(similarity_matrix[j])[::-1][1:k + 1])
                
                if i in neighbors_j:
                    G.add_edge(nodes[i], nodes[j], weight=float(similarity_matrix[i, j]))
        
        logger.info(f"Grafo KNN simétrico criado: {G.number_of_nodes()} nós, {G.number_of_edges()} arestas")
        return G
    
    @staticmethod
    def detect_communities(G: nx.Graph, seed: int = 42) -> dict[str, int]:
        """Detecta comunidades usando Leiden ou fallback se necessário."""
        if G.number_of_nodes() == 0:
            return {}

        communities_gen = GraphService._leiden_communities(G, seed=seed)

        node_to_community = {}
        for idx, comm in enumerate(communities_gen):
            for node in comm:
                node_to_community[node] = idx

        return node_to_community


class GraphStats:
    """Calcula estatísticas de grafos."""
    
    @staticmethod
    def compute(G: nx.Graph) -> dict:
        """Retorna dicionário with estatísticas do grafo."""
        stats = {
            "num_vertices": G.number_of_nodes(),
            "num_edges": G.number_of_edges(),
            "density": nx.density(G),
            "avg_clustering": nx.average_clustering(G),
        }
        
        degrees = dict(G.degree())
        if degrees:
            stats["avg_degree"] = sum(degrees.values()) / len(degrees)
            stats["max_degree"] = max(degrees.values())
            stats["min_degree"] = min(degrees.values())
        
        components = list(nx.connected_components(G))
        stats["num_components"] = len(components)
        stats["largest_component"] = len(max(components, key=len)) if components else 0
        
        if nx.is_connected(G):
            stats["diameter"] = nx.diameter(G)
            stats["avg_shortest_path"] = nx.average_shortest_path_length(G)
        
        # Modularidade
        try:
            communities_gen = GraphService._leiden_communities(G, seed=42)
            modularity = community.modularity(G, communities_gen, weight="weight")
            stats["modularity"] = modularity
            stats["num_communities"] = len(communities_gen)
        except Exception as e:
            logger.debug(f"Erro ao calcular modularidade: {e}")
        
        return stats