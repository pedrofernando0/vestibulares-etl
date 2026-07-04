"""Scraper de provas e gabaritos oficiais da FUVEST."""

import urllib.parse

import requests
from bs4 import BeautifulSoup

from src import config
from src.config import ensure_directories_exist
from src.utils.logger import get_logger

logger = get_logger(__name__)


class FuvestScraper:
    """Downloader automático para provas e gabaritos do portal da FUVEST."""

    BASE_INDEX_URL = "https://www.fuvest.br/acervo/"

    def __init__(self, year: int) -> None:
        self.year = year
        self.raw_subdir = config.RAW_DIR / "fuvest" / str(year)
        ensure_directories_exist()
        self.raw_subdir.mkdir(parents=True, exist_ok=True)

    def fetch_pdf_links(self) -> dict[str, list[str]]:
        """Acessa o acervo da FUVEST para o ano informado e extrai os links de PDFs."""
        params = {"anoprova": self.year}
        logger.info(f"Acessando o acervo FUVEST em: {self.BASE_INDEX_URL} com params {params}")

        try:
            response = requests.get(self.BASE_INDEX_URL, params=params, timeout=30)
            response.raise_for_status()
        except Exception as e:
            logger.error(f"Erro ao acessar acervo FUVEST: {e}")
            return {"provas": [], "gabaritos": []}

        soup = BeautifulSoup(response.text, "html.parser")
        links = {"provas": [], "gabaritos": []}

        for a_tag in soup.find_all("a", href=True):
            href = a_tag["href"]
            if not href.lower().endswith(".pdf"):
                continue

            absolute_url = urllib.parse.urljoin(self.BASE_INDEX_URL, href)
            lower_href = href.lower()

            is_gabarito = "gabarito" in lower_href or "respostas" in lower_href
            is_prova = "prova" in lower_href or "caderno" in lower_href

            if is_gabarito and absolute_url not in links["gabaritos"]:
                links["gabaritos"].append(absolute_url)
            elif is_prova and absolute_url not in links["provas"]:
                links["provas"].append(absolute_url)

        logger.info(
            f"Extraídos {len(links['provas'])} links de provas e "
            f"{len(links['gabaritos'])} links de gabaritos."
        )
        return links

    def download_pdf(self, url: str, filename: str) -> str | None:
        """Efetua o download do arquivo PDF e o salva em data/raw."""
        try:
            logger.info(f"Baixando PDF de: {url}")
            response = requests.get(url, timeout=30)
            response.raise_for_status()

            target_path = self.raw_subdir / filename
            with open(target_path, "wb") as f:
                f.write(response.content)

            logger.info(f"Salvo em: {target_path}")
            return str(target_path)
        except Exception as e:
            logger.error(f"Falha ao baixar PDF {url}: {e}")
            return None

    def run(self) -> dict[str, list[str]]:
        """Executa a busca e download de todos os PDFs encontrados para o ano correspondente."""
        links = self.fetch_pdf_links()
        downloaded = {"provas": [], "gabaritos": []}

        # Baixar provas
        for idx, url in enumerate(links["provas"]):
            # Gera nome amigável do arquivo
            filename = f"prova_fase1_caderno_{idx + 1}.pdf"
            if "fase2" in url.lower() or "fase_2" in url.lower() or "2fase" in url.lower():
                filename = f"prova_fase2_dia_{idx + 1}.pdf"

            path = self.download_pdf(url, filename)
            if path:
                downloaded["provas"].append(path)

        # Baixar gabaritos
        for idx, url in enumerate(links["gabaritos"]):
            filename = f"gabarito_fase1_{idx + 1}.pdf"
            if "fase2" in url.lower() or "fase_2" in url.lower() or "2fase" in url.lower():
                filename = f"gabarito_fase2_dia_{idx + 1}.pdf"

            path = self.download_pdf(url, filename)
            if path:
                downloaded["gabaritos"].append(path)

        return downloaded
