"""Testes unitários para exportação em JSON e SQLite."""

import json
import sqlite3
from pathlib import Path

from src.exporters.export_json import export_to_json, export_to_sqlite
from src.validators.models import Questao


def test_export_to_json_success(tmp_path: Path) -> None:
    """Verifica a exportação correta de uma lista de questões para arquivo JSON."""
    questoes = [
        Questao(
            id="fuvest-2024-fase1-q1",
            vestibular="FUVEST",
            ano=2024,
            fase=1,
            numero_questao=1,
            disciplina="História",
            enunciado_texto="Enunciado de teste.",
            alternativas=[
                {"letra": "A", "texto": "A1"},
                {"letra": "B", "texto": "B1"},
                {"letra": "C", "texto": "C1"},
                {"letra": "D", "texto": "D1"},
            ],
            gabarito="A",
            anulada=False,
        )
    ]

    output_file = tmp_path / "fuvest_2024.json"
    success = export_to_json(questoes, output_file)

    assert success is True
    assert output_file.exists()

    with open(output_file, encoding="utf-8") as f:
        data = json.load(f)

    assert len(data) == 1
    assert data[0]["id"] == "fuvest-2024-fase1-q1"
    assert data[0]["gabarito"] == "A"


def test_export_to_sqlite_success(tmp_path: Path) -> None:
    """Valida a criação e inserção de dados de questões em banco SQLite."""
    questoes = [
        Questao(
            id="fuvest-2024-fase1-q1",
            vestibular="FUVEST",
            ano=2024,
            fase=1,
            numero_questao=1,
            disciplina="Geografia",
            enunciado_texto="Enunciado geo.",
            alternativas=[
                {"letra": "A", "texto": "A1"},
                {"letra": "B", "texto": "B1"},
                {"letra": "C", "texto": "C1"},
                {"letra": "D", "texto": "D1"},
            ],
            gabarito="D",
            anulada=False,
        )
    ]

    db_file = tmp_path / "questoes.db"
    success = export_to_sqlite(questoes, db_file)

    assert success is True
    assert db_file.exists()

    # Consulta ao banco de dados SQLite criado
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute("SELECT id, disciplina, gabarito, alternativas FROM questoes")
    row = cursor.fetchone()
    conn.close()

    assert row is not None
    assert row[0] == "fuvest-2024-fase1-q1"
    assert row[1] == "Geografia"
    assert row[2] == "D"

    # Valida o JSON das alternativas guardado
    alts = json.loads(row[3])
    assert len(alts) == 4
    assert alts[0]["letra"] == "A"
