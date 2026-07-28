"""Chat entrypoint usando ChatService para conversação com grafo.

Usage: python main.py chat -k 3 ou python main.py chat -t 0.75
"""
import logging
from typing import Optional

logger = logging.getLogger(__name__)

from src.config import (
    OUTPUT_DIR,
    EMBEDDING_MODEL,
    GR_RETRIEVER_LLM_MODEL,
    GR_RETRIEVER_MLP_OUT_CHANNELS,
    GR_RETRIEVER_USE_LORA,
    CHAT_MAX_OUT_TOKENS,
)
from src.data.csv_handler import CSVHandler
from src.services.chat import ChatService
from src.services.embeddings import EmbeddingService
from src.services.graph import GraphService


def main(max_tokens: Optional[int] = None, threshold: Optional[float] = None, k: Optional[int] = None):
    """Chat REPL: carregar dados, construir grafo, inicializar ChatService e entrar em loop de perguntas."""
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

    logger.info("=== Etapa 4: Construindo grafo ===")
    if threshold is not None:
        graph = GraphService.threshold(titles, sim_matrix, threshold)
    elif k is not None:
        graph = GraphService.knn(titles, sim_matrix, k)
    else:
        graph = GraphService.threshold(titles, sim_matrix)

    logger.info("=== Etapa 5: Inicializando ChatService ===")
    out_tokens = max_tokens or CHAT_MAX_OUT_TOKENS
    chat_service = ChatService(
        summaries=summaries,
        titles=titles,
        embedder=embedder,
        sim_matrix=sim_matrix,
        graph=graph,
        llm_model_name=GR_RETRIEVER_LLM_MODEL,
        use_lora=GR_RETRIEVER_USE_LORA,
        mlp_out_channels=GR_RETRIEVER_MLP_OUT_CHANNELS,
        max_out_tokens=out_tokens,
    )

    # Enter REPL loop
    print("Entrando em modo chat. Digite 'exit' ou 'quit' para sair.")
    try:
        while True:
            try:
                msg = input("Pergunta> ")
            except EOFError:
                print()  # newline
                break

            if not msg:
                continue
            if msg.strip().lower() in ("exit", "quit"):
                break

            result = chat_service.infer(msg)
            print("Resposta:")
            print(result)
            print()
    except KeyboardInterrupt:
        print()  # newline
        logger.info("Sessão de chat encerrada pelo usuário.")


if __name__ == "__main__":
    main()
