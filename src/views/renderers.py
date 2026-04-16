import matplotlib

matplotlib.use("TkAgg")

import matplotlib.pyplot as plt
import networkx as nx
import textwrap
from adjustText import adjust_text
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output
import webbrowser
from threading import Timer


def get_layout(G: nx.Graph, layout_type: str = "spring"):
    """Retorna o layout da rede baseado no algoritmo especificado."""
    if layout_type == "circular":
        return nx.circular_layout(G)
    elif layout_type == "kawai":
        return nx.kamada_kawai_layout(G)
    else:  # "spring" é o padrão
        return nx.spring_layout(G, k=0.5, iterations=50)


def render_graph(G: nx.Graph, title="graph.png", layout: str = "spring") -> None:
    plt.figure(figsize=(14, 14))
    pos = get_layout(G, layout)

    weights = [G[u][v]["weight"] for u, v in G.edges()]

    nx.draw(G, pos, node_size=50, width=weights, with_labels=True, font_size=6)

    plt.title(title)

    plt.savefig(title, dpi=300, bbox_inches="tight")
    plt.show()


def render_graph_png(G: nx.Graph, title="graph.png", layout: str = "spring") -> None:
    plt.figure(figsize=(14, 14))

    # Layout baseado no parâmetro
    pos = get_layout(G, layout)

    # Edge weights
    weights = [G[u][v]["weight"] for u, v in G.edges()]

    # --- Função para formatar texto ---
    def format_label(text, width=20, max_lines=3):
        wrapped = textwrap.wrap(str(text), width=width)
        wrapped = wrapped[:max_lines]
        if len(wrapped) == max_lines:
            wrapped[-1] += "..."
        return "\n".join(wrapped)

    labels = {node: format_label(node) for node in G.nodes()}

    # --- Tamanho do nó proporcional ao texto ---
    node_sizes = []
    for node in G.nodes():
        length = len(str(node))
        size = 300 + min(length * 20, 2000)
        node_sizes.append(size)

    # --- Desenha nós e arestas ---
    nx.draw_networkx_edges(G, pos, width=weights, alpha=0.3)
    nx.draw_networkx_nodes(G, pos, node_size=node_sizes, node_color="lightblue")

    # --- Labels como objetos ajustáveis ---
    texts = []
    for node, (x, y) in pos.items():
        txt = plt.text(x, y, labels[node], fontsize=7, ha="center", va="center")
        texts.append(txt)

    # --- Evita sobreposição automaticamente ---
    adjust_text(
        texts,
        arrowprops=dict(arrowstyle="-", color="gray", lw=0.5),
        expand_points=(1.2, 1.4),
    )

    plt.title(title)
    plt.axis("off")
    plt.savefig(title, dpi=300, bbox_inches="tight")
    plt.show()


def render_graph_plotly(G, title="Graph", layout: str = "spring"):
    # Layout baseado no parâmetro
    pos = get_layout(G, layout)

    # --- Arestas ---
    edge_x = []
    edge_y = []
    edge_weights = []

    for u, v, data in G.edges(data=True):
        x0, y0 = pos[u]
        x1, y1 = pos[v]

        edge_x += [x0, x1, None]
        edge_y += [y0, y1, None]
        edge_weights.append(data.get("weight", 1))

    edge_trace = go.Scatter(
        x=edge_x,
        y=edge_y,
        line=dict(width=0.5, color="#888"),
        hoverinfo="none",
        mode="lines",
    )

    # --- Nós ---
    node_x = []
    node_y = []
    texts = []
    sizes = []

    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)

        text = str(node)
        texts.append(text)

        # tamanho baseado no texto
        sizes.append(10 + min(len(text) * 0.8, 40))

    node_trace = go.Scatter(
        x=node_x,
        y=node_y,
        mode="markers",
        hovertemplate="%{text}<extra></extra>",
        text=texts,  # aparece no hover
        marker=dict(
            size=sizes, color="lightblue", line=dict(width=1, color="darkblue")
        ),
    )

    # --- Figura ---
    fig = go.Figure(
        data=[edge_trace, node_trace],
        layout=go.Layout(
            title=title,
            showlegend=False,
            hovermode="closest",
            margin=dict(b=20, l=5, r=5, t=40),
            xaxis=dict(showgrid=False, zeroline=False, visible=False),
            yaxis=dict(showgrid=False, zeroline=False, visible=False),
        ),
    )

    fig.show()
