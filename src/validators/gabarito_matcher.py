"""Módulo para processar gabaritos oficiais e conciliá-los com as questões extraídas."""

import re
from pathlib import Path

import fitz  # PyMuPDF

from src.utils.logger import get_logger
from src.validators.models import Questao

logger = get_logger(__name__)


class GabaritoMatcher:
    """Classe para extrair gabaritos de texto/PDF e associar às questões."""

    def __init__(self, gabarito_path: str | Path | None = None) -> None:
        self.gabarito_path = Path(gabarito_path) if gabarito_path else None
        self.mapping: dict[int, str] = {}

    def parse_from_text(self, text: str) -> dict[int, str]:
        """Extrai mapeamentos 'Número -> Resposta' de um texto bruto usando regex."""
        # Procura padrões como "01 - A", "1. B", "12 C", "35: D"
        pattern = re.compile(r"\b(\d{1,3})\b\s*[-–—.:\s]\s*\b([A-Ea-e])\b")
        matches = pattern.findall(text)

        extracted: dict[int, str] = {}
        for num_str, letter in matches:
            num = int(num_str)
            extracted[num] = letter.upper()

        self.mapping.update(extracted)
        logger.info(f"Extraídas {len(extracted)} entradas de gabarito do texto.")
        return extracted

    def parse_from_pdf(self) -> dict[int, str]:
        """Extrai o texto de um PDF de gabarito e realiza o mapeamento regex."""
        if not self.gabarito_path or not self.gabarito_path.exists():
            logger.error("Arquivo de gabarito PDF não especificado ou inexistente.")
            return {}

        try:
            doc = fitz.open(self.gabarito_path)
            full_text = ""
            for page in doc:
                full_text += page.get_text()
            doc.close()

            return self.parse_from_text(full_text)
        except Exception as e:
            logger.error(f"Erro ao ler gabarito em PDF {self.gabarito_path}: {e}")
            return {}

    def match_questions(self, questoes: list[Questao]) -> list[Questao]:
        """Associa as respostas corretas do gabarito extraído às respectivas questões."""
        if not self.mapping:
            logger.warning("Nenhum gabarito foi carregado. Nenhuma questão foi atualizada.")
            return questoes

        updated_count = 0
        for q in questoes:
            if q.numero_questao in self.mapping:
                # Atualiza o gabarito
                q.gabarito = self.mapping[q.numero_questao]
                updated_count += 1
            else:
                logger.warning(f"Questão {q.numero_questao} não encontrada no gabarito carregado.")

        logger.info(f"Conciliação concluída: {updated_count}/{len(questoes)} questões atualizadas.")
        return questoes
