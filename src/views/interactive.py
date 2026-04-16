# src/views/interactive.py
import networkx as nx
import plotly.graph_objects as go
import plotly.express as px
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


def render_graph_interactive(graphs_dict, layout: str = "spring", communities_dict=None):
    """Renderiza múltiplos grafos interativamente com dropdown para seleção."""
    if not graphs_dict:
        print("Nenhum grafo para renderizar.")
        return

    first_name = next(iter(graphs_dict))
    first_graph = graphs_dict[first_name]

    # lista base de nós (união de todos os grafos)
    all_nodes = set()
    for g in graphs_dict.values():
        all_nodes.update(g.nodes())
    all_nodes = list(all_nodes)

    def create_figure(graph, highlight_node=None, communities=None):
        pos = get_layout(graph, layout)

        # ===== EDGES =====
        edge_x, edge_y = [], []
        for u, v in graph.edges():
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

        # ===== NODES =====
        node_x, node_y = [], []
        node_colors, node_sizes, texts = [], [], []

        # Preparar cores por comunidade se disponível
        if communities:
            num_communities = len(set(communities.values()))
            color_palette = px.colors.qualitative.Set3 if num_communities <= 12 else px.colors.qualitative.Light24
            colors = color_palette * ((num_communities // len(color_palette)) + 1)
        else:
            colors = None

        for node in all_nodes:
            if node in graph.nodes():
                x, y = pos[node]
                node_x.append(x)
                node_y.append(y)
                texts.append(str(node))

                # Determinar cor baseada em comunidade ou highlight
                if highlight_node and highlight_node in graph.neighbors(node):
                    node_colors.append("orange")
                    node_sizes.append(16)
                elif highlight_node == node:
                    node_colors.append("red")
                    node_sizes.append(22)
                elif communities and node in communities:
                    comm_id = communities[node]
                    node_colors.append(colors[comm_id % len(colors)])
                    node_sizes.append(12)
                else:
                    node_colors.append("lightblue")
                    node_sizes.append(10)
            else:
                # nó ausente nesse grafo
                node_x.append(0)
                node_y.append(0)
                texts.append("")
                node_colors.append("gray")
                node_sizes.append(5)

        node_trace = go.Scatter(
            x=node_x,
            y=node_y,
            mode="markers",
            text=texts,
            hovertemplate="%{text}<extra></extra>",
            marker=dict(
                size=node_sizes,
                color=node_colors,
                line=dict(width=1, color="black"),
            ),
        )

        return go.Figure(
            data=[edge_trace, node_trace],
            layout=go.Layout(
                title="Visualização do Grafo",
                showlegend=False,
                hovermode="closest",
                xaxis=dict(visible=False),
                yaxis=dict(visible=False),
                margin=dict(l=20, r=20, t=40, b=20),
            ),
        )

    # ===== DASH APP =====
    app = Dash(__name__)

    app.layout = html.Div([
        html.H1("Visualização Interativa de Grafos"),
        dcc.Dropdown(
            id="graph-selector",
            options=[{"label": name, "value": name} for name in graphs_dict.keys()],
            value=first_name,
            clearable=False,
        ),
        dcc.Graph(id="graph", figure=create_figure(first_graph, communities=communities_dict.get(first_name) if communities_dict else None)),
    ])

    @app.callback(
        Output("graph", "figure"),
        [Input("graph-selector", "value"), Input("graph", "clickData")],
    )
    def update_graph(selected_graph, clickData):
        graph = graphs_dict[selected_graph]
        highlight_node = None

        if clickData:
            point_index = clickData["points"][0]["pointIndex"]
            highlight_node = all_nodes[point_index]

        communities = communities_dict.get(selected_graph) if communities_dict else None
        return create_figure(graph, highlight_node, communities)

    # 🔥 abre automaticamente no navegador
    Timer(1, lambda: webbrowser.open("http://127.0.0.1:8050")).start()

    app.run(debug=True)