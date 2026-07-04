"""Scraper de vestibulares paulistas: COMVEST (Unicamp) e VUNESP (Unesp)."""

import requests

from src import config
from src.config import ensure_directories_exist
from src.utils.logger import get_logger

logger = get_logger(__name__)


class VunespComvestScraper:
    """Downloader de provas e gabaritos para a Unicamp (COMVEST) e Unesp (VUNESP)."""

    def __init__(self, institution: str, year: int) -> None:
        self.institution = institution.lower()
        self.year = year
        self.raw_subdir = config.RAW_DIR / self.institution / str(year)
        ensure_directories_exist()
        self.raw_subdir.mkdir(parents=True, exist_ok=True)

    def get_default_unicamp_urls(self) -> dict[str, str]:
        """Gera os links padrões para as provas da Unicamp de acordo com o padrão COMVEST."""
        # Ex: https://www.comvest.unicamp.br/vest2024/F1/f12024.pdf
        base_url = f"https://www.comvest.unicamp.br/vest{self.year}/F1"
        return {
            "prova": f"{base_url}/f1{self.year}.pdf",
            "gabarito": f"{base_url}/gabarito1.pdf",
        }

    def download_file(self, url: str, filename: str) -> str | None:
        """Efetua o download do arquivo PDF e o salva no subdiretório correspondente."""
        try:
            logger.info(f"Iniciando download ({self.institution.upper()} {self.year}): {url}")
            response = requests.get(url, timeout=30)
            response.raise_for_status()

            target_path = self.raw_subdir / filename
            with open(target_path, "wb") as f:
                f.write(response.content)

            logger.info(f"Salvo com sucesso em: {target_path}")
            return str(target_path)
        except Exception as e:
            logger.error(f"Falha ao baixar arquivo do link {url}: {e}")
            return None

    def run(
        self,
        custom_prova_url: str | None = None,
        custom_gabarito_url: str | None = None,
    ) -> dict[str, str | None]:
        """Executa o pipeline de download."""
        downloaded = {"prova": None, "gabarito": None}

        # Resolução dos links
        if self.institution == "unicamp":
            defaults = self.get_default_unicamp_urls()
            prova_url = custom_prova_url or defaults["prova"]
            gabarito_url = custom_gabarito_url or defaults["gabarito"]
        else:
            # Para UNESP (Vunesp), exige URLs customizadas devido a IDs variáveis no portal
            if not custom_prova_url or not custom_gabarito_url:
                logger.error(
                    f"Para {self.institution.upper()}, é necessário "
                    "fornecer urls de prova e gabarito personalizadas."
                )
                return downloaded
            prova_url = custom_prova_url
            gabarito_url = custom_gabarito_url

        # Executa downloads
        downloaded["prova"] = self.download_file(prova_url, f"prova_fase1_{self.year}.pdf")
        downloaded["gabarito"] = self.download_file(gabarito_url, f"gabarito_fase1_{self.year}.pdf")

        return downloaded
