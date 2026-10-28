import time

import networkx as nx
import requests
import textwrap

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "qwen3:8b"
PROMPT_TEMPLATE = textwrap.dedent("""\
    Você é um assistente que responde perguntas sobre Trabalhos de
    Conclusão de Curso (TCCs) da Universidade Federal de Lavras (UFLA).

    Abaixo estão os TCCs recuperados para a pergunta. Cada trabalho tem
    um ID, curso, título, autor, orientador e resumo. Também são listadas
    as conexões entre os trabalhos (pares src,dst): uma conexão indica
    apenas que os dois trabalhos são semanticamente próximos, e não é
    evidência de nada além disso.

    Regras:
    1. Use APENAS as informações do contexto. Não use conhecimento externo.
    2. Alguns trabalhos recuperados podem não ser relevantes para a
       pergunta. Ignore-os e não os mencione.
    3. Ao afirmar algo, cite o ID do trabalho que o sustenta, no formato
       [TCC 123].
    4. Se o contexto não tiver informação suficiente, diga exatamente:
       "Não encontrei informações suficientes nos trabalhos recuperados."
       Se houver informação apenas parcial, responda o que for possível
       e diga o que está faltando.
    5. Não invente títulos, autores, orientadores, cursos ou conclusões
       que não estejam no contexto.
    6. Responda em português do Brasil, de forma direta e objetiva.

    Contexto dos trabalhos recuperados:
    {context}

    Pergunta: {message}

    Resposta:
""")


def generation(
    message: str,
    subgraph: nx.Graph,
) -> str:
    """Mantém a assinatura original, usada pelo server.py."""
    return generation_with_stats(message, subgraph)["response"]


def generation_with_stats(
    message: str,
    subgraph: nx.Graph,
) -> dict:
    """
    Executa a geração e devolve, além da resposta, o contexto enviado ao LLM,
    os tempos de cada sub-etapa e as contagens de tokens reportadas pelo Ollama.
    """
    print(".:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.")
    print("                  .:. Generation .:.                   ")
    print(".:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.:.")

    t0 = time.perf_counter()
    context = build_context(subgraph)
    t_contexto = time.perf_counter() - t0

    prompt = build_prompt(message, context)

    t0 = time.perf_counter()
    response = requests.post(
        OLLAMA_URL,
        json={
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
            "think": False,
            "options": {
                "temperature": 0,
                "seed": 42,
                "num_ctx": 16384,
            },
        },
        timeout=120,
    )

    response.raise_for_status()

    data = response.json()
    t_llm = time.perf_counter() - t0

    return {
        "response": data["response"],
        "context": context,
        "t_contexto": t_contexto,
        "t_llm": t_llm,
        "prompt_eval_count": data.get("prompt_eval_count"),
        "eval_count": data.get("eval_count"),
    }


def build_prompt(message: str, context: str) -> str:
    return PROMPT_TEMPLATE.format(message=message, context=context)


def build_context(graph: nx.Graph, ranked_ids: list[str] | None = None) -> str:
    node_ids = list(graph.nodes)
    if ranked_ids:  # relevantes primeiro, nós-ponte (Steiner) por último
        pos = {n: i for i, n in enumerate(ranked_ids)}
        node_ids.sort(key=lambda n: pos.get(n, len(pos)))

    nodes_txt = []
    for node_id in node_ids:
        d = graph.nodes[node_id]
        nodes_txt.append(
            "\n".join(
                [
                    f"TCC {node_id}",
                    f"Curso: {d.get('curso', '')}",
                    f"Título: {d.get('titulo', '')}",
                    f"Autor: {d.get('autor', '')}",
                    f"Orientador: {d.get('orientador', '')}",
                    f"Resumo: {d.get('resumo', '')}",
                ]
            )
        )

    edges_txt = ["src,dst"]
    edges_txt += [f"{u},{v}" for u, v in graph.edges()]

    return (
        "## Trabalhos\n\n"
        + "\n\n---\n\n".join(nodes_txt)
        + "\n\n## Conexões entre os trabalhos (src,dst)\n\n"
        + "\n".join(edges_txt)
    )
