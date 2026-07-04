"""Módulo para renderizar páginas de arquivos PDF para imagens de alta resolução."""

from pathlib import Path

import fitz  # PyMuPDF

from src.utils.logger import get_logger

logger = get_logger(__name__)


def render_pdf_page_to_image(
    pdf_path: str | Path,
    page_number: int,
    output_path: str | Path,
    dpi: int = 300,
) -> bool:
    """Renderiza uma página específica do PDF em uma imagem PNG de alta resolução."""
    try:
        pdf_path = Path(pdf_path)
        output_path = Path(output_path)

        if not pdf_path.exists():
            logger.error(f"Arquivo PDF não encontrado: {pdf_path}")
            return False

        # Abrir documento
        doc = fitz.open(pdf_path)
        if page_number < 0 or page_number >= len(doc):
            logger.error(
                f"Número de página inválido ({page_number}) para "
                f"PDF com {len(doc)} páginas."
            )
            doc.close()
            return False

        # Configura a matriz de escala com base no DPI (72 DPI é o padrão do PDF)
        zoom = dpi / 72
        mat = fitz.Matrix(zoom, zoom)

        # Carrega a página e renderiza para pixmap (raster image)
        page = doc[page_number]
        pix = page.get_pixmap(matrix=mat, alpha=False)

        # Salva o arquivo final
        output_path.parent.mkdir(parents=True, exist_ok=True)
        pix.save(str(output_path))
        doc.close()

        logger.info(f"Página {page_number} renderizada com sucesso em: {output_path}")
        return True

    except Exception as e:
        logger.error(f"Erro ao renderizar página {page_number} do PDF {pdf_path}: {e}")
        return False


def render_all_pdf_pages(
    pdf_path: str | Path,
    output_dir: str | Path,
    dpi: int = 300,
) -> list[Path]:
    """Renderiza todas as páginas de um PDF em uma pasta específica e retorna os caminhos."""
    rendered_paths: list[Path] = []
    try:
        pdf_path = Path(pdf_path)
        output_dir = Path(output_dir)

        if not pdf_path.exists():
            logger.error(f"Arquivo PDF não encontrado: {pdf_path}")
            return []

        doc = fitz.open(pdf_path)
        logger.info(f"Iniciando renderização de {len(doc)} páginas de: {pdf_path}")

        for page_num in range(len(doc)):
            filename = f"page_{page_num + 1:03d}.png"
            output_file = output_dir / filename
            success = render_pdf_page_to_image(pdf_path, page_num, output_file, dpi)
            if success:
                rendered_paths.append(output_file)

        doc.close()
        logger.info(f"Renderização concluída. {len(rendered_paths)} páginas salvas.")
        return rendered_paths

    except Exception as e:
        logger.error(f"Erro ao processar renderização do PDF {pdf_path}: {e}")
        return []
