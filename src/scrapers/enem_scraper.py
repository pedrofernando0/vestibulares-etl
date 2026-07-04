"""Scraper / Ingestor de dados da API pública do ENEM (enem.dev)."""

import json

import requests

from src import config
from src.config import ensure_directories_exist
from src.utils.logger import get_logger
from src.validators.models import Alternativa, EnunciadoImagem, Questao

logger = get_logger(__name__)


class EnemScraper:
    """Ingestor para baixar e converter dados do ENEM da API pública enem.dev."""

    BASE_URL = "https://api.enem.dev/v1"

    def __init__(self, year: int) -> None:
        self.year = year
        self.assets_subdir = config.ASSETS_DIR / "enem" / str(year)
        ensure_directories_exist()
        self.assets_subdir.mkdir(parents=True, exist_ok=True)

    def download_image(self, url: str, filename: str) -> str | None:
        """Faz download de imagem associada a uma questão e salva em data/assets."""
        try:
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            target_path = self.assets_subdir / filename
            with open(target_path, "wb") as f:
                f.write(response.content)
            # Caminho relativo a partir da raiz do projeto para o JSON referenciar
            return f"data/assets/enem/{self.year}/{filename}"
        except Exception as e:
            logger.error(f"Erro ao baixar imagem {url}: {e}")
            return None

    def map_discipline(self, api_discipline: str) -> str:
        """Mapeia a disciplina vinda da API para o nome padrão."""
        mapping = {
            "linguagens": "Linguagens e Códigos",
            "matematica": "Matemática",
            "ciencias-humanas": "Ciências Humanas",
            "ciencias-natureza": "Ciências da Natureza",
        }
        return mapping.get(api_discipline.lower(), api_discipline.capitalize())

    def fetch_and_save(self) -> list[Questao]:
        """Busca todas as questões do ano selecionado, processa e salva em JSON."""
        url = f"{self.BASE_URL}/exams/{self.year}/questions"
        logger.info(f"Buscando questões do ENEM {self.year} de: {url}")

        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            logger.error(f"Falha ao consultar a API do ENEM para o ano {self.year}: {e}")
            raise

        # Se a API retornar formato com dicionário ou direto lista
        raw_questions = data if isinstance(data, list) else data.get("questions", [])
        if not raw_questions:
            logger.warning(f"Nenhuma questão encontrada para o ENEM {self.year}.")
            return []

        logger.info(
            f"Encontradas {len(raw_questions)} questões. "
            "Iniciando extração e download de assets..."
        )
        questoes_processadas: list[Questao] = []

        for idx, q in enumerate(raw_questions):
            q_index = q.get("index", idx + 1)
            q_id = f"enem-{self.year}-{q_index}"

            # Processar imagens do enunciado
            enunciado_imagens = []
            for img_idx, img_url in enumerate(q.get("files", [])):
                if img_url:
                    filename = f"img_q{q_index}_{img_idx}.png"
                    local_path = self.download_image(img_url, filename)
                    if local_path:
                        enunciado_imagens.append(
                            EnunciadoImagem(
                                id=f"{q_id}-img-{img_idx}",
                                caminho=local_path,
                                legenda=f"Figura {img_idx + 1} da Questão {q_index}"
                            )
                        )

            # Processar alternativas
            alternativas = []
            for alt in q.get("alternatives", []):
                letra = alt.get("letter")
                texto = alt.get("text") or ""
                alt_img_url = alt.get("file")
                local_alt_img = None

                if alt_img_url:
                    filename = f"img_q{q_index}_alt_{letra.lower()}.png"
                    local_alt_img = self.download_image(alt_img_url, filename)

                alternativas.append(
                    Alternativa(
                        letra=letra,
                        texto=texto,
                        imagem=local_alt_img
                    )
                )

            # Monta o modelo Pydantic
            try:
                questao_obj = Questao(
                    id=q_id,
                    vestibular="ENEM",
                    ano=self.year,
                    fase=1,
                    variante_prova=q.get("color") or "Azul",
                    numero_questao=q_index,
                    disciplina=self.map_discipline(q.get("discipline", "")),
                    subtopico=None,
                    enunciado_texto=q.get("context") or "",
                    enunciado_imagens=enunciado_imagens,
                    alternativas=alternativas,
                    gabarito=q.get("correctAlternative") or "ANULADA",
                    anulada=q.get("correctAlternative") is None,
                    resolucao_comentada=None
                )
                questoes_processadas.append(questao_obj)
            except Exception as val_err:
                logger.error(f"Erro de validação na questão {q_index}: {val_err}")

        # Salva o arquivo final
        dataset_file = config.DATASET_DIR / f"enem_{self.year}.json"
        with open(dataset_file, "w", encoding="utf-8") as f:
            json_content = [q.model_dump() for q in questoes_processadas]
            json.dump(json_content, f, ensure_ascii=False, indent=2)

        logger.info(
            f"Processamento concluído. {len(questoes_processadas)} "
            f"questões salvas em: {dataset_file}"
        )
        return questoes_processadas
