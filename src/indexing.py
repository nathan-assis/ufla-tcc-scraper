import networkx as nx
from sentence_transformers import SentenceTransformer
from pathlib import Path
from .utils.scraper import scrape
from .utils.graph_builder import build_graph, load_graph, save_graph


BASE_DIR = Path(__file__).resolve().parent
PATH = BASE_DIR / "files" / "graph.graphml"


def index(model: SentenceTransformer) -> nx.Graph:
    print(".:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.")
    print("                   .:. Indexing .:.                    ")
    print(".:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.")

    if PATH.exists():
        print(".:. Carregando dados .:.")
        return load_graph(PATH)

    print(".:. Extraindo dados .:.")
    tccs_data = scrape()

    print(".:. Construindo grafo .:.")
    graph, embeddings = build_graph(tccs_data, model)
    
    print(".:. Salvando grafo .:.")
    save_graph(graph, embeddings, PATH)

    return load_graph(PATH)
