from typing import TypedDict

class Node(TypedDict):
    curso: str
    titulo: str
    autor: str
    orientador: str
    resumo: str
    url: str


class EdgeData(TypedDict):
    weight: float


type Edge = tuple[str, str, EdgeData]