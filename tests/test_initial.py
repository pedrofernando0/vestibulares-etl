"""Testes iniciais de validação do Scaffolding e DevEx."""

from pathlib import Path

from src.config import ROOT_DIR, ensure_directories_exist
from src.utils.logger import get_logger


def test_root_dir_resolution() -> None:
    """Verifica se o diretório raiz foi resolvido corretamente."""
    assert ROOT_DIR.exists()
    assert (ROOT_DIR / "pyproject.toml").exists()


def test_ensure_directories_exist(tmp_path: Path, monkeypatch: object) -> None:
    """Verifica a criação de diretórios de dados."""
    test_data_dir = tmp_path / "test_data"
    import src.config
    src.config.DATA_DIR = test_data_dir
    src.config.RAW_DIR = test_data_dir / "raw"
    src.config.ASSETS_DIR = test_data_dir / "assets"
    src.config.DATASET_DIR = test_data_dir / "dataset"
    src.config.SCHEMAS_DIR = test_data_dir / "schemas"

    ensure_directories_exist()

    assert test_data_dir.exists()
    assert (test_data_dir / "raw").exists()
    assert (test_data_dir / "assets").exists()
    assert (test_data_dir / "dataset").exists()
    assert (test_data_dir / "schemas").exists()


def test_logger_initialization() -> None:
    """Verifica se o logger do projeto é inicializado sem erros."""
    logger = get_logger("test_logger")
    assert logger is not None
    assert logger.name == "test_logger"
