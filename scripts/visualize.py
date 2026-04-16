# scripts/visualize.py
"""Script para gerar visualizações."""
import logging
from pathlib import Path

from src.config import OUTPUT_DIR, EMBEDDING_MODEL, DEFAULT_SIMILARITY_THRESHOLD, DEFAULT_KNN_K, DEFAULT_KNN_SYMMETRIC_K
from src.data.csv_handler import CSVHandler
from src.services.embeddings import EmbeddingService
from src.services.graph import GraphService

logger = logging.getLogger(__name__)


def main(formats: list[str], layout: str, thresholds: list[float] | None, ks: list[int] | None, detect_communities: bool = False):
    """Visualize: carregar CSV → embeddings → grafos → render."""
    logger.info("=== Etapa 1: Carregando dados ===")
    csv_path = OUTPUT_DIR / "dados_sip.csv"
    projects = CSVHandler.load(csv_path)
    
    logger.info("=== Etapa 2: Extraindo campos ===")
    summaries = CSVHandler.get_column(projects, "Resumo:")
    titles = CSVHandler.get_column(projects, "Título:")
    
    logger.info("=== Etapa 3: Gerando embeddings ===")
    embedder = EmbeddingService(EMBEDDING_MODEL)
    embeddings = embedder.encode(summaries)
    sim_matrix = embedder.similarity_matrix(embeddings)
    
    logger.info("=== Etapa 4: Criando grafos ===")
    
    # Lógica condicional
    if thresholds is None and ks is None:
        thresholds = [DEFAULT_SIMILARITY_THRESHOLD]
        ks = [DEFAULT_KNN_K, DEFAULT_KNN_SYMMETRIC_K]
    elif thresholds is None:
        thresholds = []  # só knn e symmetric_knn
    elif ks is None:
        ks = []  # só threshold
    # else: ambos passados
    
    graphs = {}
    for thresh in thresholds:
        graphs[f"threshold_{thresh}"] = GraphService.threshold(titles, sim_matrix, thresh)
    
    for k in ks:
        graphs[f"knn_{k}"] = GraphService.knn(titles, sim_matrix, k)
        graphs[f"symmetric_knn_{k}"] = GraphService.symmetric_knn(titles, sim_matrix, k)
    
    logger.info("=== Etapa 5: Detectando comunidades (se solicitado) ===")
    communities_map = {}
    if detect_communities:
        for name, graph in graphs.items():
            logger.info(f"Detectando comunidades para {name}...")
            communities_map[name] = GraphService.detect_communities(graph)
    
    logger.info("=== Etapa 6: Renderizando ===")
    # Nome do arquivo: junção dos parâmetros
    thresh_str = '_'.join(map(str, thresholds)) if thresholds else ''
    k_str = '_'.join(map(str, ks)) if ks else ''
    param_str = f"layout_{layout}_thresholds_{thresh_str}_ks_{k_str}".rstrip('_')
    if detect_communities:
        param_str += "_communities"
    
    # Para interactive, coletar todos os graphs e renderizar juntos
    if "interactive" in formats:
        from src.views.interactive import render_graph_interactive
        render_graph_interactive(graphs, layout=layout, communities_dict=communities_map)
        # Não processar outros formatos se interactive estiver presente, pois bloqueia
        return
    
    for name, graph in graphs.items():
        filename_base = f"{name}_{param_str}"
        communities = communities_map.get(name) if detect_communities else None
        
        if "gexf" in formats:
            from src.data.graph_io import GraphIO
            GraphIO.save_gexf(graph, OUTPUT_DIR / f"{filename_base}.gexf")
        
        if "png" in formats:
            from src.views.renderers import render_graph_png
            render_graph_png(graph, str(OUTPUT_DIR / f"{filename_base}.png"), layout=layout, communities=communities)
        
        if "plotly" in formats:
            from src.views.renderers import render_graph_plotly
            render_graph_plotly(graph, name, layout=layout, communities=communities)
    
    return


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 5:
        print("Uso: python scripts/visualize.py formats layout thresholds ks")
        print("Ex: python scripts/visualize.py gexf,png spring 0.8,0.7 3,4")
        sys.exit(1)
    
    formats = sys.argv[1].split(',')
    layout = sys.argv[2]
    thresholds = [float(x) for x in sys.argv[3].split(',')]
    ks = [int(x) for x in sys.argv[4].split(',')]
    main(formats, layout, thresholds, ks)