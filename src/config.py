"""Módulo de configuração do pipeline vestibulares-etl."""

import os
from pathlib import Path

from dotenv import load_dotenv

# Carrega variáveis de ambiente do arquivo .env (se existir)
load_dotenv()

# Diretório raiz do projeto (duas pastas acima deste arquivo: src/ -> raiz)
ROOT_DIR = Path(__file__).resolve().parent.parent

# Configurações de Paths
DATA_DIR = ROOT_DIR / os.getenv("DATA_DIR", "data")
RAW_DIR = ROOT_DIR / os.getenv("RAW_DIR", "data/raw")
ASSETS_DIR = ROOT_DIR / os.getenv("ASSETS_DIR", "data/assets")
DATASET_DIR = ROOT_DIR / os.getenv("DATASET_DIR", "data/dataset")
SCHEMAS_DIR = ROOT_DIR / "schemas"

# Configurações de API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Configurações de Log
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()


def ensure_directories_exist() -> None:
    """Garante que todas as pastas base de dados existem no sistema de arquivos."""
    for directory in [DATA_DIR, RAW_DIR, ASSETS_DIR, DATASET_DIR, SCHEMAS_DIR]:
        directory.mkdir(parents=True, exist_ok=True)
