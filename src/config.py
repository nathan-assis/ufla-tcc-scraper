# src/config.py
import os
from pathlib import Path

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
ASSETS_DIR = PROJECT_ROOT / "assets"
OUTPUT_DIR = ASSETS_DIR / "output"
INPUT_DIR = ASSETS_DIR / "input"

# Ensure directories exist
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
INPUT_DIR.mkdir(parents=True, exist_ok=True)

# Load from .env if exists
def load_env(key: str, default: str) -> str:
    return os.getenv(key, default)

# URLs
SIP_BASE_URL = load_env("SIP_BASE_URL", "https://sip.prg.ufla.br/publico/trabalhos_conclusao_curso/acessar_tcc_por_curso/")

# Graph parameters
DEFAULT_SIMILARITY_THRESHOLD = float(load_env("DEFAULT_SIMILARITY_THRESHOLD", "0.75"))
DEFAULT_KNN_K = int(load_env("DEFAULT_KNN_K", "3"))
DEFAULT_KNN_SYMMETRIC_K = int(load_env("DEFAULT_KNN_SYMMETRIC_K", "4"))

# Embeddings
EMBEDDING_MODEL = load_env("EMBEDDING_MODEL", "all-MiniLM-L6-v2")

# Logging
LOG_LEVEL = load_env("LOG_LEVEL", "INFO")