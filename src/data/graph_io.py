# src/data/graph_io.py
import logging
from pathlib import Path

import networkx as nx

logger = logging.getLogger(__name__)


class GraphIO:
    """Handler para salvar/carregar grafos."""
    
    @staticmethod
    def save_gexf(G: nx.Graph, filepath: Path | str) -> None:
        """Salva grafo em formato GEXF."""
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            nx.write_gexf(G, filepath)
            logger.info(f"Grafo salvo em {filepath}")
        except Exception as e:
            logger.error(f"Erro ao salvar GEXF: {e}")
            raise
    
    @staticmethod
    def load_gexf(filepath: Path | str) -> nx.Graph:
        """Carrega grafo de arquivo GEXF."""
        filepath = Path(filepath)
        
        if not filepath.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {filepath}")
        
        try:
            G = nx.read_gexf(filepath)
            logger.info(f"Grafo carregado de {filepath}")
            return G
        except Exception as e:
            logger.error(f"Erro ao carregar GEXF: {e}")
            raise