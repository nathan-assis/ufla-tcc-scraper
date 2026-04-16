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


def render_graph(G: nx.Graph, title="graph.png") -> None:
    plt.figure(figsize=(14, 14))
    pos = nx.spring_layout(G, k=0.6)

    weights = [G[u][v]["weight"] for u, v in G.edges()]

    nx.draw(G, pos, node_size=50, width=weights, with_labels=True, font_size=6)

    plt.title(title)

    plt.savefig(title, dpi=300, bbox_inches="tight")
    plt.show()


def render_graph_test(G: nx.Graph, title="graph.png") -> None:
    plt.figure(figsize=(14, 14))

    # Layout mais espaçado
    pos = nx.spring_layout(G, k=0.6, iterations=50)

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


def render_graph_plotly(G, title="Graph"):
    # Layout
    pos = nx.spring_layout(G, k=0.5, iterations=50)

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
        hoverinfo="text",
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


def render_graph_interactive(G):
    import networkx as nx
    import plotly.graph_objects as go
    from dash import Dash, dcc, html, Input, Output
    import webbrowser
    from threading import Timer

    pos = nx.spring_layout(G, k=0.5, iterations=50)
    # nx.forceatlas2_layout
    nodes = list(G.nodes())

    def create_figure(highlight_node=None):
        edge_x, edge_y = [], []

        for u, v in G.edges():
            x0, y0 = pos[u]
            x1, y1 = pos[v]
            edge_x += [x0, x1, None]
            edge_y += [y0, y1, None]

        edge_trace = go.Scatter(
            x=edge_x,
            y=edge_y,
            mode="lines",
            line=dict(color="#CCCCCC", width=1),
            hoverinfo="none",
        )

        node_x, node_y = [], []
        node_colors, node_sizes, texts = [], [], []

        for node in nodes:
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)
            texts.append(str(node))

            if highlight_node:
                if node == highlight_node:
                    node_colors.append("red")
                    node_sizes.append(22)
                elif node in G.neighbors(highlight_node):
                    node_colors.append("orange")
                    node_sizes.append(16)
                else:
                    node_colors.append("lightgray")
                    node_sizes.append(8)
            else:
                node_colors.append("lightblue")
                node_sizes.append(10)

        node_trace = go.Scatter(
            x=node_x,
            y=node_y,
            mode="markers",
            text=texts,
            hoverinfo="text",
            marker=dict(
                size=node_sizes, color=node_colors, line=dict(width=1, color="black")
            ),
        )

        return go.Figure(
            data=[edge_trace, node_trace],
            layout=go.Layout(
                title="Interactive Graph (click a node)",
                showlegend=False,
                hovermode="closest",
                xaxis=dict(visible=False),
                yaxis=dict(visible=False),
            ),
        )

    app = Dash(__name__)

    app.layout = html.Div([dcc.Graph(id="graph", figure=create_figure())])

    @app.callback(Output("graph", "figure"), Input("graph", "clickData"))
    def update_graph(clickData):
        if clickData is None:
            return create_figure()

        point_index = clickData["points"][0]["pointIndex"]
        clicked_node = nodes[point_index]

        return create_figure(highlight_node=clicked_node)

    # 🔥 abre automaticamente no navegador
    Timer(1, lambda: webbrowser.open("http://127.0.0.1:8050")).start()

    app.run(debug=True)
