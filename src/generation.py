import networkx as nx
import requests


OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3:8b"


def generation(
    message: str,
    subgraph: nx.Graph,
) -> str:
    print(".:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.")
    print("                  .:. Generation .:.                   ")
    print(".:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.")
    context = build_context(subgraph)

    prompt = f"""
    Você é um assistente especializado nos trabalhos de conclusão
    de curso da Universidade Federal de Lavras (UFLA).

    Responda à pergunta do usuário utilizando apenas as informações
    presentes no contexto recuperado.

    Se o contexto não possuir informações suficientes para responder,
    diga explicitamente que não foi possível encontrar informações
    suficientes nos trabalhos recuperados.

    Não invente informações.

    Pergunta:
    {message}

    Contexto dos trabalhos recuperados:
    {context}
    """

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
        },
        timeout=120,
    )

    response.raise_for_status()

    data = response.json()

    return data["response"]


def build_context(
    graph: nx.Graph,
) -> str:
    context = []
    for node_id, data in graph.nodes(data=True):
        context.append(
            f"""
            TCC {node_id}
            Curso: {data.get("curso", "")}
            Título: {data.get("titulo", "")}
            Autor: {data.get("autor", "")}
            Orientador: {data.get("orientador", "")}
            Resumo: {data.get("resumo", "")}
            """.strip()
        )

    return "\n\n---\n\n".join(context)