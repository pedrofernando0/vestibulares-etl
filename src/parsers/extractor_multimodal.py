"""Módulo para extração de questões e detecção de figuras usando Gemini Multimodal API."""

from typing import Any

from google import genai
from google.genai import types
from PIL import Image
from pydantic import BaseModel, Field

from src.config import GEMINI_API_KEY
from src.utils.logger import get_logger

logger = get_logger(__name__)


class AlternativaSimplificada(BaseModel):
    """Representação simplificada de alternativa para o retorno do LLM."""

    letra: str = Field(..., description="Letra da alternativa (A, B, C, D ou E).")
    texto: str = Field(..., description="Texto da alternativa formatado em Markdown/LaTeX.")


class ImagemDetectada(BaseModel):
    """Informação sobre imagem detectada na página para posterior recorte."""

    numero_questao: int = Field(
        ..., description="Número da questão à qual esta imagem/gráfico pertence."
    )
    box_2d: list[float] = Field(
        ...,
        description="Coordenadas normalizadas [ymin, xmin, ymax, xmax] (valores de 0.0 a 1.0).",
    )
    legenda: str | None = Field(
        default=None, description="Breve descrição da imagem ou legenda se houver."
    )


class QuestaoExtraida(BaseModel):
    """Estrutura da questão extraída da página pelo Gemini."""

    numero_questao: int = Field(..., description="Número da questão na prova.")
    disciplina: str = Field(..., description="Matéria/Disciplina estimada para a questão.")
    enunciado_texto: str = Field(
        ...,
        description="Texto completo do enunciado em Markdown, convertendo fórmulas para LaTeX.",
    )
    alternativas: list[AlternativaSimplificada] = Field(
        ..., description="Lista de alternativas da questão."
    )


class PaginaExtraida(BaseModel):
    """Estrutura final contendo tudo o que foi extraído de uma página do PDF."""

    questoes: list[QuestaoExtraida] = Field(
        default_factory=list, description="Questões detectadas na página."
    )
    imagens: list[ImagemDetectada] = Field(
        default_factory=list,
        description="Bounding boxes de todas as figuras, gráficos ou tabelas na página.",
    )


class GeminiExtractor:
    """Wrapper para interagir com a API do Gemini e extrair as questões e imagens."""

    def __init__(self, model_name: str = "gemini-2.5-flash") -> None:
        if not GEMINI_API_KEY:
            raise ValueError(
                "A chave GEMINI_API_KEY não foi encontrada nas variáveis de ambiente."
            )
        self.client = genai.Client(api_key=GEMINI_API_KEY)
        self.model_name = model_name

    def extract_page(
        self, image_path: str, vestibular: str, ano: int, fase: int
    ) -> PaginaExtraida | None:
        """Envia a imagem da página do PDF para o Gemini extrair dados estruturados."""
        logger.info(f"Enviando página {image_path} para o Gemini ({self.model_name})...")

        try:
            # Carrega a imagem usando PIL
            image = Image.open(image_path)
        except Exception as e:
            logger.error(f"Falha ao abrir imagem da página {image_path}: {e}")
            return None

        prompt = (
            "Você é um assistente especialista em curadoria de "
            "conteúdo escolar para vestibulares.\n"
            "Analise a imagem da página da prova de vestibular "
            f"({vestibular} {ano}, Fase {fase}).\n\n"
            "Instruções:\n"
            "1. Identifique todas as questões presentes nesta página e seus enunciados.\n"
            "2. Formate o texto dos enunciados e alternativas usando Markdown. "
            "Transforme qualquer fórmula matemática ou física em código LaTeX usando "
            "delimitadores $ ou $$.\n"
            "3. Localize visualmente quaisquer figuras, tabelas, ilustrações ou gráficos que "
            "façam parte das questões. Retorne suas coordenadas em box_2d como "
            "[ymin, xmin, ymax, xmax] normalizadas de 0.0 a 1.0 (onde ymin=0.0 é o topo "
            "e xmax=1.0 é a extrema direita da imagem).\n"
            "Associe cada box ao respectivo numero_questao."
        )

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=[image, prompt],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=PaginaExtraida,
                    temperature=0.1,
                ),
            )

            # O SDK analisa automaticamente o JSON no response.parsed
            result: Any = response.parsed
            if isinstance(result, PaginaExtraida):
                return result

            # Fallback se não parseou para o tipo correto mas retornou texto JSON
            if hasattr(response, "text") and response.text:
                logger.info("Executando parse manual do JSON retornado pelo Gemini.")
                return PaginaExtraida.model_validate_json(response.text)

            logger.error("Resposta do Gemini não pôde ser parseada para o modelo PaginaExtraida.")
            return None

        except Exception as e:
            logger.error(f"Erro na chamada do Gemini API: {e}")
            return None
