"""Testes unitários para o extrator multimodal com Gemini API."""

from unittest.mock import MagicMock, patch

from src.parsers.extractor_multimodal import (
    GeminiExtractor,
    ImagemDetectada,
    PaginaExtraida,
    QuestaoExtraida,
)


@patch("src.parsers.extractor_multimodal.genai.Client")
@patch("src.parsers.extractor_multimodal.Image.open")
def test_gemini_extractor_success(
    mock_image_open: MagicMock, mock_genai_client: MagicMock
) -> None:
    """Valida se o pipeline do extrator envia a imagem e processa a resposta do Gemini."""
    # Configura chaves fictícias no config
    import src.config
    src.config.GEMINI_API_KEY = "dummy-api-key"

    # Mocks da API do Gemini
    mock_client_instance = MagicMock()
    mock_genai_client.return_value = mock_client_instance

    mock_response = MagicMock()

    # Cria os objetos esperados no retorno parsed
    mock_questao = QuestaoExtraida(
        numero_questao=1,
        disciplina="Matemática",
        enunciado_texto="Resolva a equação $x^2 = 4$.",
        alternativas=[
            {"letra": "A", "texto": "$x = 2$"},
            {"letra": "B", "texto": "$x = 4$"},
            {"letra": "C", "texto": "$x = 0$"},
            {"letra": "D", "texto": "$x = -1$"}
        ]
    )
    mock_imagem = ImagemDetectada(
        numero_questao=1,
        box_2d=[0.1, 0.2, 0.4, 0.5],
        legenda="Figura geométrica"
    )

    mock_response.parsed = PaginaExtraida(
        questoes=[mock_questao],
        imagens=[mock_imagem]
    )
    mock_client_instance.models.generate_content.return_value = mock_response

    # Instancia o extractor e executa
    extractor = GeminiExtractor()
    resultado = extractor.extract_page("dummy_page.png", "FUVEST", 2024, 1)

    assert resultado is not None
    assert len(resultado.questoes) == 1
    assert len(resultado.imagens) == 1
    assert resultado.questoes[0].numero_questao == 1
    assert resultado.imagens[0].box_2d == [0.1, 0.2, 0.4, 0.5]
    mock_client_instance.models.generate_content.assert_called_once()
