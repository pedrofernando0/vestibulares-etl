"""Módulo para exportação consolidada de dados para JSON e SQLite."""

import json
import sqlite3
from pathlib import Path

from src.utils.logger import get_logger
from src.validators.models import Questao

logger = get_logger(__name__)


def export_to_json(questoes: list[Questao], output_path: str | Path) -> bool:
    """Exporta a lista de questões validadas para um arquivo JSON estruturado."""
    try:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        data = [q.model_dump() for q in questoes]
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        logger.info(f"Dataset exportado com sucesso para JSON em: {output_path}")
        return True
    except Exception as e:
        logger.error(f"Erro ao exportar dataset para JSON {output_path}: {e}")
        return False


def export_to_sqlite(questoes: list[Questao], db_path: str | Path) -> bool:
    """Exporta a lista de questões para um banco de dados SQLite."""
    try:
        db_path = Path(db_path)
        db_path.parent.mkdir(parents=True, exist_ok=True)

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Criação da tabela de questões
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS questoes (
                id TEXT PRIMARY KEY,
                vestibular TEXT,
                ano INTEGER,
                fase INTEGER,
                variante_prova TEXT,
                numero_questao INTEGER,
                disciplina TEXT,
                subtopico TEXT,
                enunciado_texto TEXT,
                enunciado_imagens TEXT,
                alternativas TEXT,
                gabarito TEXT,
                anulada INTEGER,
                resolucao_comentada TEXT
            )
            """
        )

        # Inserção das questões
        for q in questoes:
            cursor.execute(
                """
                INSERT OR REPLACE INTO questoes (
                    id, vestibular, ano, fase, variante_prova, numero_questao,
                    disciplina, subtopico, enunciado_texto, enunciado_imagens,
                    alternativas, gabarito, anulada, resolucao_comentada
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    q.id,
                    q.vestibular,
                    q.ano,
                    q.fase,
                    q.variante_prova,
                    q.numero_questao,
                    q.disciplina,
                    q.subtopico,
                    q.enunciado_texto,
                    json.dumps([img.model_dump() for img in q.enunciado_imagens]),
                    json.dumps([alt.model_dump() for alt in q.alternativas]),
                    q.gabarito,
                    1 if q.anulada else 0,
                    q.resolucao_comentada,
                ),
            )

        conn.commit()
        conn.close()

        logger.info(f"Dataset exportado com sucesso para SQLite em: {db_path}")
        return True
    except Exception as e:
        logger.error(f"Erro ao exportar para SQLite {db_path}: {e}")
        return False
