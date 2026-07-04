"""Modelos de dados Pydantic para validação das questões de vestibulares."""

from typing import Literal

from pydantic import BaseModel, Field, field_validator


class EnunciadoImagem(BaseModel):
    """Representação de uma imagem ou gráfico acoplado ao enunciado."""

    id: str = Field(..., description="ID identificador único da imagem.")
    caminho: str = Field(..., description="Caminho relativo para a imagem em data/assets.")
    legenda: str | None = Field(default=None, description="Legenda ou descrição da imagem.")


class Alternativa(BaseModel):
    """Representação de uma alternativa de resposta."""

    letra: Literal["A", "B", "C", "D", "E"] = Field(
        ..., description="Letra identificadora da alternativa."
    )
    texto: str = Field(..., description="Enunciado textual da alternativa.")
    imagem: str | None = Field(
        default=None, description="Caminho relativo de imagem para a alternativa se aplicável."
    )


class Questao(BaseModel):
    """Representação estruturada de uma questão de vestibular."""

    id: str = Field(..., description="Identificador único da questão.")
    vestibular: Literal["ENEM", "FUVEST", "UNICAMP", "UNESP", "FATEC"] = Field(
        ..., description="Nome do vestibular correspondente."
    )
    ano: int = Field(..., ge=1900, description="Ano de realização da prova.")
    fase: Literal[1, 2] = Field(..., description="Fase correspondente da prova (1 ou 2).")
    variante_prova: str | None = Field(
        default=None, description="Cor ou identificação do caderno de provas."
    )
    numero_questao: int = Field(..., ge=1, description="Número da questão no caderno original.")
    disciplina: str = Field(..., description="Matéria/Disciplina da questão.")
    subtopico: str | None = Field(default=None, description="Tópico específico da disciplina.")
    enunciado_texto: str = Field(
        ..., description="Texto do enunciado formatado em Markdown com LaTeX."
    )
    enunciado_imagens: list[EnunciadoImagem] = Field(
        default_factory=list, description="Lista de imagens que compõem o enunciado."
    )
    alternativas: list[Alternativa] = Field(
        ..., description="Lista de alternativas estruturadas (geralmente de A a E)."
    )
    gabarito: Literal["A", "B", "C", "D", "E", "ANULADA"] = Field(
        ..., description="Gabarito correto oficial ou indicação de anulação."
    )
    anulada: bool = Field(default=False, description="Flag indicativa de questão anulada.")
    resolucao_comentada: str | None = Field(
        default=None, description="Explicação/resolução detalhada da questão."
    )

    @field_validator("alternativas")
    @classmethod
    def validar_alternativas(cls, v: list[Alternativa]) -> list[Alternativa]:
        """Garante que a quantidade de alternativas e letras sejam consistentes."""
        if len(v) < 4 or len(v) > 5:
            raise ValueError("Uma questão deve conter exatamente 4 ou 5 alternativas.")

        letras = [alt.letra for alt in v]
        if len(letras) != len(set(letras)):
            raise ValueError("Letras das alternativas duplicadas encontradas.")

        # Ordenar alternativas alfabeticamente para consistência
        return sorted(v, key=lambda x: x.letra)
