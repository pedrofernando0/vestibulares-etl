"""Testes unitários para a ferramenta de recorte de imagens."""

from pathlib import Path

from PIL import Image

from src.parsers.image_cropper import crop_image_from_box


def test_crop_image_from_box_success(tmp_path: Path) -> None:
    """Valida se recorta uma imagem de origem baseada no box normalizado e salva o resultado."""
    # Cria imagem de teste (solid blue 100x100)
    source_img_path = tmp_path / "source.png"
    img = Image.new("RGB", (100, 100), color="blue")
    img.save(source_img_path)

    output_img_path = tmp_path / "crop.png"
    box = [0.2, 0.2, 0.8, 0.8]  # Bounding box centralizado

    success = crop_image_from_box(source_img_path, box, output_img_path, padding_pixels=0)

    assert success is True
    assert output_img_path.exists()

    # Verifica se a imagem recortada tem o tamanho esperado (80-20 = 60px de largura e altura)
    with Image.open(output_img_path) as cropped_img:
        assert cropped_img.size == (60, 60)
