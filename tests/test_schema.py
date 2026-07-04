"""Testes unitários para validação de schemas de dados (JSON Schema & Pydantic)."""

import json

import pytest
from pydantic import ValidationError

from src.config import SCHEMAS_DIR
from src.validators.models import Questao


def test_json_schema_file_exists_and_is_valid() -> None:
    """Valida se o arquivo questao_schema.json existe e é um JSON válido."""
    schema_path = SCHEMAS_DIR / "questao_schema.json"
    assert schema_path.exists()

    with open(schema_path, encoding="utf-8") as f:
        schema_data = json.load(f)

    assert schema_data["title"] == "Questao"
    assert "required" in schema_data


def test_valida_questao_pydantic_sucesso() -> None:
    """Testa a validação bem-sucedida de um objeto Questao estruturado."""
    questao_dict = {
        "id": "fuvest-2024-fase1-q01",
        "vestibular": "FUVEST",
        "ano": 2024,
        "fase": 1,
        "variante_prova": "V",
        "numero_questao": 1,
        "disciplina": "Física",
        "subtopico": "Cinemática",
        "enunciado_texto": "Um carro se move com velocidade constante de $20 m/s$.",
        "enunciado_imagens": [
            {
                "id": "img_q01",
                "caminho": "data/assets/fuvest/2024/fase1/img_q01.png",
                "legenda": "Gráfico S x t",
            }
        ],
        "alternativas": [
            {"letra": "A", "texto": "10 m/s"},
            {"letra": "B", "texto": "20 m/s"},
            {"letra": "C", "texto": "30 m/s"},
            {"letra": "D", "texto": "40 m/s"},
            {"letra": "E", "texto": "50 m/s"},
        ],
        "gabarito": "B",
        "anulada": False,
    }

    questao = Questao(**questao_dict)
    assert questao.id == "fuvest-2024-fase1-q01"
    assert len(questao.alternativas) == 5
    assert questao.alternativas[0].letra == "A"


def test_valida_questao_pydantic_falha_valores_invalidos() -> None:
    """Testa a rejeição de valores inválidos (regras do Pydantic)."""
    # Ano inválido (< 1900)
    with pytest.raises(ValidationError):
        Questao(
            id="fuvest-2024-fase1-q01",
            vestibular="FUVEST",
            ano=1899,
            fase=1,
            numero_questao=1,
            disciplina="Física",
            enunciado_texto="...",
            alternativas=[{"letra": "A", "texto": "1"}],
            gabarito="A",
            anulada=False,
        )

    # Menos de 4 alternativas
    with pytest.raises(ValidationError):
        Questao(
            id="fuvest-2024-fase1-q01",
            vestibular="FUVEST",
            ano=2024,
            fase=1,
            numero_questao=1,
            disciplina="Física",
            enunciado_texto="...",
            alternativas=[
                {"letra": "A", "texto": "1"},
                {"letra": "B", "texto": "2"},
                {"letra": "C", "texto": "3"},
            ],
            gabarito="A",
            anulada=False,
        )


def test_valida_questao_alternativas_duplicadas() -> None:
    """Garante que a validação barre alternativas com letras duplicadas."""
    with pytest.raises(ValidationError, match="Letras das alternativas duplicadas"):
        Questao(
            id="fuvest-2024-fase1-q01",
            vestibular="FUVEST",
            ano=2024,
            fase=1,
            numero_questao=1,
            disciplina="Física",
            enunciado_texto="...",
            alternativas=[
                {"letra": "A", "texto": "1"},
                {"letra": "A", "texto": "2"},
                {"letra": "C", "texto": "3"},
                {"letra": "D", "texto": "4"},
            ],
            gabarito="A",
            anulada=False,
        )
