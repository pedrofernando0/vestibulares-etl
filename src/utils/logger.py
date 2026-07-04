"""Módulo de log estruturado para o pipeline."""

import logging

from rich.logging import RichHandler

from src.config import LOG_LEVEL


def get_logger(name: str) -> logging.Logger:
    """Configura e retorna um logger formatado com suporte ao Rich."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))
        handler = RichHandler(rich_tracebacks=True, show_time=True, show_path=False)
        formatter = logging.Formatter("%(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.propagate = False
    return logger
