# src/services/models.py
from dataclasses import dataclass
from typing import Dict

@dataclass
class Project:
    """Representa um trabalho de conclusão de curso."""
    title: str
    summary: str
    metadata: Dict[str, str]
    
    def to_dict(self) -> Dict[str, str]:
        return {
            "Título:": self.title,
            "Resumo:": self.summary,
            **self.metadata
        }
    
    @staticmethod
    def from_dict(data: Dict[str, str]) -> "Project":
        title = data.pop("Título:", "")
        summary = data.pop("Resumo:", "")
        return Project(title=title, summary=summary, metadata=data)