#!/usr/bin/env python3
"""Entry point do projeto UFLA TCC Scraper."""
import argparse
import logging.config
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from config import LOG_LEVEL

# Setup logging
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": LOG_LEVEL,
            "formatter": "standard",
        }
    },
    "root": {
        "handlers": ["console"],
        "level": LOG_LEVEL,
    }
}
logging.config.dictConfig(LOGGING_CONFIG)


def main():
    parser = argparse.ArgumentParser(description="UFLA TCC Scraper")
    subparsers = parser.add_subparsers(dest="command", help="Comandos disponíveis")
    
    # Scrape
    scrape_parser = subparsers.add_parser("scrape", help="Scrape projetos de cursos")
    scrape_parser.add_argument(
        "-c", "--courses",
        nargs="+",
        required=False,
        help="Lista de nomes de cursos (ex: 'Ciência da Computação' 'Sistemas de Informação')"
    )
    
    # Analyze
    analyze_parser = subparsers.add_parser("analyze", help="Análise de grafos")
    analyze_parser.add_argument(
        "-t", "--threshold",
        nargs="+",
        type=float,
        required=False,
        default=None,
        help="Lista de thresholds para create_threshold_graph"
    )
    analyze_parser.add_argument(
        "-k", "--k",
        nargs="+",
        type=int,
        required=False,
        default=None,
        help="Lista de valores k para KNN graphs"
    )
    analyze_parser.add_argument(
        "--detect-communities",
        action="store_true",
        help="Detectar comunidades usando algoritmo de Leiden"
    )
    
    # Visualize
    visualize_parser = subparsers.add_parser("visualize", help="Gerar visualizações")
    visualize_parser.add_argument(
        "-f", "--format",
        nargs="+",
        required=True,
        choices=["gexf", "png", "plotly", "interactive"],
        help="Formatos de saída"
    )
    visualize_parser.add_argument(
        "-l", "--layout",
        choices=["spring", "circular", "kawai", "atlas"],
        default="spring",
        help="Algoritmo de layout"
    )
    visualize_parser.add_argument(
        "-t", "--threshold",
        nargs="+",
        type=float,
        required=False,
        default=None,
        help="Lista de thresholds para create_threshold_graph"
    )
    visualize_parser.add_argument(
        "-k", "--k",
        nargs="+",
        type=int,
        required=False,
        default=None,
        help="Lista de valores k para KNN graphs"
    )
    visualize_parser.add_argument(
        "--detect-communities",
        action="store_true",
        help="Detectar comunidades usando algoritmo de Leiden"
    )

    # Chat (GRetriever)
    chat_parser = subparsers.add_parser("chat", help="Entrar em modo chat usando GRetriever/embeddings")
    chat_parser.add_argument("--max-tokens", "-m", type=int, required=False, default=None, help="Máximo de tokens de saída do LLM")
    chat_parser.add_argument("--threshold", "-t", type=float, required=False, default=None, help="Threshold para criar grafo de similaridade")
    chat_parser.add_argument("--k", "-k", type=int, required=False, default=None, help="k para KNN ao criar grafo se desejado")
    
    args = parser.parse_args()
    
    if args.command == "scrape":
        from scripts.scrape import main as scrape_main
        scrape_main(args.courses)
    elif args.command == "analyze":
        from scripts.analyze import main as analyze_main
        analyze_main(args.threshold, args.k, args.detect_communities)
    elif args.command == "visualize":
        from scripts.visualize import main as visualize_main
        visualize_main(args.format, args.layout, args.threshold, args.k, args.detect_communities)
    elif args.command == "chat":
        from scripts.chat import main as chat_main
        chat_main(max_tokens=args.max_tokens, threshold=args.threshold, k=args.k)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()