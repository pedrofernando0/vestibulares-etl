"""Testes unitários para o matcher de gabarito."""

from pathlib import Path
from unittest.mock import MagicMock, patch

from src.validators.gabarito_matcher import GabaritoMatcher
from src.validators.models import Questao


def test_gabarito_parse_from_text() -> None:
    """Verifica se extrai gabaritos de texto usando expressões regulares."""
    raw_text = """
    Gabarito Oficial Vestibular
    01 - A | 02 - B | 03: C
    04. D | 05 E | 6 - A
    """

    matcher = GabaritoMatcher()
    mapping = matcher.parse_from_text(raw_text)

    assert len(mapping) == 6
    assert mapping[1] == "A"
    assert mapping[2] == "B"
    assert mapping[3] == "C"
    assert mapping[4] == "D"
    assert mapping[5] == "E"
    assert mapping[6] == "A"


@patch("src.validators.gabarito_matcher.fitz.open")
def test_gabarito_parse_from_pdf_success(mock_fitz_open: MagicMock, tmp_path: Path) -> None:
    """Valida a leitura e parsing a partir de arquivo PDF."""
    mock_doc = MagicMock()
    mock_page = MagicMock()
    mock_page.get_text.return_value = "01 - A\n02 - B\n03 - C"
    mock_doc.__iter__.return_value = [mock_page]
    mock_fitz_open.return_value = mock_doc

    pdf_path = tmp_path / "gabarito.pdf"
    pdf_path.touch()

    matcher = GabaritoMatcher(gabarito_path=pdf_path)
    mapping = matcher.parse_from_pdf()

    assert len(mapping) == 3
    assert mapping[1] == "A"
    assert mapping[2] == "B"
    assert mapping[3] == "C"
    mock_doc.close.assert_called_once()


def test_match_questions() -> None:
    """Verifica a correlação correta entre o gabarito extraído e a lista de questões."""
    questoes = [
        Questao(
            id="fuvest-2024-fase1-q1",
            vestibular="FUVEST",
            ano=2024,
            fase=1,
            numero_questao=1,
            disciplina="História",
            enunciado_texto="...",
            alternativas=[
                {"letra": "A", "texto": "A1"},
                {"letra": "B", "texto": "B1"},
                {"letra": "C", "texto": "C1"},
                {"letra": "D", "texto": "D1"},
            ],
            gabarito="D",  # Gabarito provisório
            anulada=False,
        )
    ]

    matcher = GabaritoMatcher()
    matcher.mapping = {1: "B"}

    questoes_atualizadas = matcher.match_questions(questoes)

    assert questoes_atualizadas[0].gabarito == "B"
