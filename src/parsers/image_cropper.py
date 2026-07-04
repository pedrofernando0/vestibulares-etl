"""Módulo para recortar e salvar figuras detectadas em páginas de prova usando PIL."""

from pathlib import Path

from PIL import Image

from src.utils.logger import get_logger

logger = get_logger(__name__)


def crop_image_from_box(
    image_path: str | Path,
    box_2d: list[float],
    output_path: str | Path,
    padding_pixels: int = 5,
) -> bool:
    """Recorta uma região retangular da imagem baseada em coordenadas normalizadas."""
    try:
        image_path = Path(image_path)
        output_path = Path(output_path)

        if not image_path.exists():
            logger.error(f"Imagem de origem não encontrada: {image_path}")
            return False

        if len(box_2d) != 4:
            logger.error(
                f"Formato de bounding box inválido: {box_2d}. "
                "Deve conter [ymin, xmin, ymax, xmax]."
            )
            return False

        # Abrir imagem
        with Image.open(image_path) as img:
            width, height = img.size
            ymin, xmin, ymax, xmax = box_2d

            # Converte coordenadas normalizadas (0.0 a 1.0) para pixel absoluto
            left = int(xmin * width) - padding_pixels
            top = int(ymin * height) - padding_pixels
            right = int(xmax * width) + padding_pixels
            bottom = int(ymax * height) + padding_pixels

            # Garante limites válidos dentro da imagem (clamping)
            left = max(0, left)
            top = max(0, top)
            right = min(width, right)
            bottom = min(height, bottom)

            # Verifica se o retângulo recortado é válido
            if right <= left or bottom <= top:
                logger.error(
                    f"Área de recorte inválida calculada para box {box_2d} "
                    f"em imagem de tamanho {width}x{height}"
                )
                return False

            # Recorta e salva
            cropped_img = img.crop((left, top, right, bottom))
            output_path.parent.mkdir(parents=True, exist_ok=True)
            cropped_img.save(output_path)

        logger.info(f"Figura recortada com sucesso e salva em: {output_path}")
        return True

    except Exception as e:
        logger.error(f"Erro ao processar recorte da imagem {image_path} com box {box_2d}: {e}")
        return False
