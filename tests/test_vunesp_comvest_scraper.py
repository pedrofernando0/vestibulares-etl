"""Testes unitários para o scraper de Unicamp (Comvest) e Unesp (Vunesp)."""

from unittest.mock import MagicMock, patch

from src.scrapers.vunesp_comvest_scraper import VunespComvestScraper


@patch("src.scrapers.vunesp_comvest_scraper.requests.get")
def test_unicamp_scraper_success(mock_get: MagicMock, tmp_path: object) -> None:
    """Valida o download padrão da Unicamp usando templates de URL da Comvest."""
    import src.config
    src.config.RAW_DIR = tmp_path / "raw"

    mock_response = MagicMock()
    mock_response.content = b"fake-pdf-content"
    mock_response.raise_for_status = MagicMock()
    mock_get.return_value = mock_response

    scraper = VunespComvestScraper(institution="unicamp", year=2024)
    resultado = scraper.run()

    # Asserts
    assert resultado["prova"] is not None
    assert resultado["gabarito"] is not None
    assert "unicamp/2024/prova_fase1_2024.pdf" in resultado["prova"]
    assert "unicamp/2024/gabarito_fase1_2024.pdf" in resultado["gabarito"]

    # Verifica chamadas do mock
    expected_prova_url = "https://www.comvest.unicamp.br/vest2024/F1/f12024.pdf"
    mock_get.assert_any_call(expected_prova_url, timeout=30)


@patch("src.scrapers.vunesp_comvest_scraper.requests.get")
def test_unesp_scraper_custom_urls(mock_get: MagicMock, tmp_path: object) -> None:
    """Valida o download da Unesp com URLs customizadas."""
    import src.config
    src.config.RAW_DIR = tmp_path / "raw"

    mock_response = MagicMock()
    mock_response.content = b"fake-pdf-content"
    mock_response.raise_for_status = MagicMock()
    mock_get.return_value = mock_response

    scraper = VunespComvestScraper(institution="unesp", year=2024)

    # Sem URLs customizadas deve falhar para unesp
    falha_res = scraper.run()
    assert falha_res["prova"] is None

    # Com URLs customizadas deve ter sucesso
    custom_p = "https://vunesp.com.br/arquivos/prova_unesp.pdf"
    custom_g = "https://vunesp.com.br/arquivos/gabarito_unesp.pdf"
    resultado = scraper.run(custom_prova_url=custom_p, custom_gabarito_url=custom_g)

    assert resultado["prova"] is not None
    assert resultado["gabarito"] is not None
    assert "unesp/2024/prova_fase1_2024.pdf" in resultado["prova"]
    mock_get.assert_any_call(custom_p, timeout=30)
    mock_get.assert_any_call(custom_g, timeout=30)
