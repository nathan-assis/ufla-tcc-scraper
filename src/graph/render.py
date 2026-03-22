import matplotlib.pyplot as plt
import networkx as nx
from networkx.algorithms import community
import numpy as np

"""
def render_graph(G: nx.Graph):
    pos = nx.spring_layout(G)
    nx.draw(G, pos, with_labels=True, node_size=2000, font_size=8)
    plt.show()
"""

def render_graph(G: nx.Graph, output_file: str = "graph.png", show=False):
    """
    Renderiza grafo com cores por comunidade, tamanho proporcional ao grau
    e espessura de aresta proporcional à similaridade.
    """
    nx.write_gexf(G, "grafo.gexf")
    
    # Layout otimizado
    pos = nx.kamada_kawai_layout(G)
    
    # Detectar comunidades
    communities = list(community.greedy_modularity_communities(G))
    
    # Mapear nós para cores
    node_colors = []
    color_map = plt.cm.Set3(np.linspace(0, 1, len(communities)))
    
    node_to_community = {}
    for idx, comm in enumerate(communities):
        for node in comm:
            node_to_community[node] = idx
    
    node_colors = [color_map[node_to_community[node]] for node in G.nodes()]
    
    # Tamanho dos nós proporcional ao grau
    node_sizes = [300 + G.degree(node) * 100 for node in G.nodes()]
    
    # Pesos das arestas
    weights = [G[u][v].get('weight', 1.0) for u, v in G.edges()]
    weights_normalized = np.array(weights)
    weights_normalized = (weights_normalized - weights_normalized.min()) / (weights_normalized.max() - weights_normalized.min() + 1e-8)
    edge_widths = 0.5 + weights_normalized * 3
    
    # Criar figura
    fig, ax = plt.subplots(figsize=(16, 12), dpi=150)
    
    # Desenhar arestas
    nx.draw_networkx_edges(
        G, pos,
        width=edge_widths,
        alpha=0.3,
        edge_color='gray',
        ax=ax
    )
    
    # Desenhar nós
    nx.draw_networkx_nodes(
        G, pos,
        node_color=node_colors,
        node_size=node_sizes,
        alpha=0.9,
        ax=ax
    )
    
    # Desenhar rótulos
    nx.draw_networkx_labels(
        G, pos,
        font_size=7,
        font_weight='bold',
        ax=ax
    )
    
    ax.set_title(f"Grafo de Similaridade de Projetos ({len(G.nodes())} nós, {len(G.edges())} arestas)\n{len(communities)} comunidades detectadas", fontsize=14, fontweight='bold')
    ax.axis('off')
    plt.tight_layout()
    
    plt.savefig(output_file, dpi=300, bbox_inches="tight")
    if show:
        plt.show()
    plt.close()
    
    # Estatísticas
    print(f"✓ Grafo renderizado: {output_file}")
    print(f"  • Nós: {len(G.nodes())}")
    print(f"  • Arestas: {len(G.edges())}")
    print(f"  • Comunidades: {len(communities)}")
    print(f"  • Densidade: {nx.density(G):.3f}")
    print(f"  • Diâmetro: {nx.diameter(G) if nx.is_connected(G) else 'Grafo desconexo'}")
    
    return communities