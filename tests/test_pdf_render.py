"""Testes unitários para o renderizador de PDFs."""

from pathlib import Path
from unittest.mock import MagicMock, patch

from src.parsers.pdf_render import render_all_pdf_pages, render_pdf_page_to_image


@patch("src.parsers.pdf_render.fitz.open")
def test_render_pdf_page_to_image_success(mock_fitz_open: MagicMock, tmp_path: Path) -> None:
    """Verifica se renderiza uma página do PDF salvando a imagem em disco."""
    # Configura documento fictício
    mock_doc = MagicMock()
    mock_page = MagicMock()
    mock_pix = MagicMock()

    mock_doc.__len__.return_value = 1
    mock_doc.__getitem__.return_value = mock_page
    mock_page.get_pixmap.return_value = mock_pix
    mock_fitz_open.return_value = mock_doc

    pdf_path = tmp_path / "teste.pdf"
    pdf_path.touch()  # Cria arquivo vazio para passar no teste de existência

    output_path = tmp_path / "page_1.png"

    success = render_pdf_page_to_image(pdf_path, 0, output_path)

    assert success is True
    mock_pix.save.assert_called_once_with(str(output_path))
    mock_doc.close.assert_called_once()


@patch("src.parsers.pdf_render.fitz.open")
def test_render_all_pdf_pages(mock_fitz_open: MagicMock, tmp_path: Path) -> None:
    """Valida se itera e renderiza todas as páginas do PDF."""
    mock_doc = MagicMock()
    mock_page = MagicMock()
    mock_pix = MagicMock()

    mock_doc.__len__.return_value = 3
    mock_doc.__getitem__.return_value = mock_page
    mock_page.get_pixmap.return_value = mock_pix
    mock_fitz_open.return_value = mock_doc

    pdf_path = tmp_path / "teste.pdf"
    pdf_path.touch()

    output_dir = tmp_path / "output_images"

    rendered_files = render_all_pdf_pages(pdf_path, output_dir)

    assert len(rendered_files) == 3
    assert rendered_files[0] == output_dir / "page_001.png"
    assert rendered_files[1] == output_dir / "page_002.png"
    assert rendered_files[2] == output_dir / "page_003.png"
    assert mock_page.get_pixmap.call_count == 3
