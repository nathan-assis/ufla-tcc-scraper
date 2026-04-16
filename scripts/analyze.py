# scripts/analyze.py
"""Script para análise de grafos."""
import csv
import logging
from pathlib import Path

from src.config import OUTPUT_DIR, EMBEDDING_MODEL, DEFAULT_SIMILARITY_THRESHOLD, DEFAULT_KNN_K, DEFAULT_KNN_SYMMETRIC_K
from src.data.csv_handler import CSVHandler
from src.services.embeddings import EmbeddingService
from src.services.graph import GraphService, GraphStats

logger = logging.getLogger(__name__)


def main(thresholds: list[float] | None, ks: list[int] | None, detect_communities: bool = False):
    """Análise: carregar CSV → embeddings → grafos → stats."""
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
    
    logger.info("=== Etapa 5: Estatísticas ===")
    # Mapeamento para português
    stat_labels = {
        "num_vertices": "Número de vértices",
        "num_edges": "Número de arestas",
        "density": "Densidade",
        "avg_degree": "Grau médio",
        "max_degree": "Grau máximo",
        "min_degree": "Grau mínimo",
        "num_components": "Número de componentes",
        "largest_component": "Maior componente",
        "avg_clustering": "Coeficiente de clustering médio",
        "diameter": "Diâmetro",
        "avg_shortest_path": "Caminho médio",
        "modularity": "Modularidade",
        "num_communities": "Número de comunidades",
    }
    
    # Coletar estatísticas para CSV
    all_stats = {}
    for name, graph in graphs.items():
        stats = GraphStats.compute(graph)
        all_stats[name] = stats
        print(f"\n{name}:")
        for key, value in stats.items():
            label = stat_labels.get(key, key)
            if isinstance(value, float):
                print(f"  {label}({key}): {value:.4f}")
            else:
                print(f"  {label}({key}): {value}")
    
    # Salvar em CSV
    csv_path = OUTPUT_DIR / "analysis_results.csv"
    logger.info(f"Salvando resultados em {csv_path}")
    
    # Obter todas as métricas únicas
    all_keys = set()
    for stats in all_stats.values():
        all_keys.update(stats.keys())
    all_keys = sorted(all_keys)
    
    # Criar colunas: threshold_{thresh}, knn_{k}, symmetric_knn_{k}
    columns = []
    if thresholds:
        for thresh in thresholds:
            columns.append(f"threshold_{thresh}")
    if ks:
        for k in ks:
            columns.append(f"knn_{k}")
        for k in ks:
            columns.append(f"symmetric_knn_{k}")
    
    with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        # Cabeçalho
        writer.writerow(['Metric'] + columns)
        # Dados
        for key in all_keys:
            row = [key]
            for col in columns:
                if col in all_stats:
                    value = all_stats[col].get(key, '')
                    if isinstance(value, float):
                        row.append(f"{value:.4f}")
                    else:
                        row.append(str(value))
                else:
                    row.append('')
            writer.writerow(row)
    
    logger.info("Análise concluída!")