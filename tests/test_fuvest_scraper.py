"""Testes unitários para o scraper da FUVEST."""

from unittest.mock import MagicMock, patch

from src.scrapers.fuvest_scraper import FuvestScraper


@patch("src.scrapers.fuvest_scraper.requests.get")
def test_fuvest_scraper_success(mock_get: MagicMock, tmp_path: object) -> None:
    """Verifica se o scraper da FUVEST analisa o HTML e baixa as provas/gabaritos corretamente."""
    # Configura o diretório temporário para os PDFs em raw
    import src.config
    src.config.RAW_DIR = tmp_path / "raw"

    # HTML simulado da página de acervo da FUVEST
    mock_html = """
    <html>
        <body>
            <h1>Acervo Fuvest 2024</h1>
            <a href="/uploads/2024_prova_V.pdf">Prova V</a>
            <a href="/uploads/2024_gabarito.pdf">Gabarito</a>
            <a href="outro.html">Outros</a>
        </body>
    </html>
    """

    mock_html_response = MagicMock()
    mock_html_response.text = mock_html
    mock_html_response.raise_for_status = MagicMock()

    mock_pdf_response = MagicMock()
    mock_pdf_response.content = b"%PDF-1.4 dummy-pdf-content"
    mock_pdf_response.raise_for_status = MagicMock()

    # Define os retornos das requisições sucessivas (HTML, PDF Prova, PDF Gabarito)
    mock_get.side_effect = [mock_html_response, mock_pdf_response, mock_pdf_response]

    scraper = FuvestScraper(year=2024)
    resultado = scraper.run()

    # Asserts
    assert len(resultado["provas"]) == 1
    assert len(resultado["gabaritos"]) == 1

    # Confirma se salvou no diretório correto com os nomes tratados
    assert "prova_fase1_caderno_1.pdf" in resultado["provas"][0]
    assert "gabarito_fase1_1.pdf" in resultado["gabaritos"][0]
