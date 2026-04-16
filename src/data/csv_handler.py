# src/data/csv_handler.py
import csv
import logging
from pathlib import Path
from typing import Optional

from ..services.models import Project

logger = logging.getLogger(__name__)


class CSVHandler:
    """Handler para leitura/escrita de CSV com projetos."""
    
    @staticmethod
    def load(filepath: Path | str) -> list[Project]:
        """Carrega projetos de um arquivo CSV."""
        filepath = Path(filepath)
        
        if not filepath.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {filepath}")
        
        projects = []
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    project = Project.from_dict(dict(row))
                    projects.append(project)
            logger.info(f"Carregados {len(projects)} projetos de {filepath}")
        except Exception as e:
            logger.error(f"Erro ao carregar CSV: {e}")
            raise
        
        return projects
    
    @staticmethod
    def save(projects: list[Project], filepath: Path | str) -> None:
        """Salva projetos em um arquivo CSV."""
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        if not projects:
            logger.warning("Lista de projetos vazia, não salvando")
            return
        
        try:
            # Coletam todas as colunas
            fieldnames = set()
            for project in projects:
                fieldnames.update(project.to_dict().keys())
            fieldnames = sorted(list(fieldnames))
            
            with open(filepath, "w", encoding="utf-8", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                for project in projects:
                    writer.writerow(project.to_dict())
            
            logger.info(f"Salvos {len(projects)} projetos em {filepath}")
        except Exception as e:
            logger.error(f"Erro ao salvar CSV: {e}")
            raise
    
    @staticmethod
    def get_column(projects: list[Project], column_name: str, separator: Optional[str] = None) -> list[str]:
        """Extrai valores de uma coluna."""
        result = []
        for project in projects:
            data = project.to_dict()
            if column_name in data:
                value = data[column_name]
                if separator:
                    result.extend(value.split(separator))
                else:
                    result.append(value)
        return result