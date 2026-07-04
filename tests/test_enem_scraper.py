"""Testes para o scraper do ENEM."""

import json
from unittest.mock import MagicMock, patch

from src.scrapers.enem_scraper import EnemScraper
from src.validators.models import Questao


@patch("src.scrapers.enem_scraper.requests.get")
def test_enem_scraper_success(mock_get: MagicMock, tmp_path: object) -> None:
    """Valida o fluxo do scraper do ENEM simulando a API externa."""
    # Configura o diretório temporário para assets/dataset no config
    import src.config
    src.config.ASSETS_DIR = tmp_path / "assets"
    src.config.DATASET_DIR = tmp_path / "dataset"

    # Mock da resposta JSON da API do ENEM
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "questions": [
            {
                "index": 1,
                "discipline": "matematica",
                "context": "Quanto é 2+2?",
                "files": ["https://dummyimage.com/600x400/000/fff.png"],
                "correctAlternative": "A",
                "alternatives": [
                    {"letter": "A", "text": "4", "file": None},
                    {"letter": "B", "text": "5", "file": None},
                    {"letter": "C", "text": "6", "file": None},
                    {"letter": "D", "text": "7", "file": None},
                ],
            }
        ]
    }
    mock_response.raise_for_status = MagicMock()

    # Mock para o download de imagem retornar dados dummy
    mock_image_response = MagicMock()
    mock_image_response.content = b"fake-png-binary-content"
    mock_image_response.raise_for_status = MagicMock()

    # Define os retornos de requests.get consecutivas
    mock_get.side_effect = [mock_response, mock_image_response]

    scraper = EnemScraper(year=2024)
    questoes = scraper.fetch_and_save()

    # Verificações
    assert len(questoes) == 1
    q = questoes[0]
    assert isinstance(q, Questao)
    assert q.id == "enem-2024-1"
    assert q.disciplina == "Matemática"
    assert q.enunciado_texto == "Quanto é 2+2?"
    assert len(q.enunciado_imagens) == 1
    assert "img_q1_0.png" in q.enunciado_imagens[0].caminho
    assert q.gabarito == "A"
    assert q.anulada is False

    # Verifica se o arquivo JSON final foi criado
    json_output_path = src.config.DATASET_DIR / "enem_2024.json"
    assert json_output_path.exists()

    with open(json_output_path, encoding="utf-8") as f:
        saved_data = json.load(f)
    assert len(saved_data) == 1
    assert saved_data[0]["id"] == "enem-2024-1"
