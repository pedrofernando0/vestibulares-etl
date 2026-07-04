# Vestibulares ETL 🎓📐

Pipeline automatizado para extração, processamento multimodal e catalogação em JSON de questões de provas de vestibulares paulistas (**FUVEST**, **UNICAMP**, **UNESP**) e **ENEM**.

---

## 🎯 Objetivo
Preencher a lacuna no ecossistema open-source brasileiro criando uma base de dados padronizada, limpa e estruturada em **JSON** contendo questões de vestibulares com suporte integral a:
- Enunciados complexos com formatação Markdown e equações matemáticas em LaTeX.
- Recortes automáticos e mapeamento de figuras, gráficos e tabelas (assets) associadas aos enunciados e alternativas.
- Alinhamento automático com gabaritos oficiais por variante de prova.
- Compatibilidade direta com planilhas de simulados, aplicativos de estudo e engines de IA/RAG.

---

## 🏗️ Arquitetura do Projeto

```
vestibulares-etl/
├── data/
│   ├── raw/                  # PDFs originais de provas e gabaritos
│   ├── assets/               # Imagens, figuras e recortes das questões
│   └── dataset/              # Arquivos JSON finais estruturados
├── schemas/
│   └── questao_schema.json   # Schema de validação JSON/Pydantic
├── src/
│   ├── scrapers/             # Downloaders de portais (ENEM, FUVEST, COMVEST, VUNESP)
│   ├── parsers/              # Motores de extração multimodal (Layout-aware / Marker / Gemini)
│   ├── validators/           # Matchers de gabarito e validadores de schema
│   ├── exporters/            # Utilitários de exportação (JSON, SQLite, Excel)
│   ├── utils/                # Logger e funções de suporte
│   └── config.py             # Gerenciamento de paths e variáveis de ambiente
├── tests/                    # Testes unitários e de integração
├── pyproject.toml            # Configuração de DevEx e dependências
└── requirements.txt          # Dependências de produção
```

---

## 🚀 Guia de DevEx (Desenvolvimento local)

### 1. Requisitos
- **Python >= 3.10**
- Git

### 2. Configuração do Ambiente Virtual
Clone o repositório e crie um ambiente virtual:
```bash
git clone https://github.com/[seu-usuario]/vestibulares-etl.git
cd vestibulares-etl

# Criar e ativar virtualenv
python3 -m venv .venv
source .venv/bin/activate  # No Windows: .venv\Scripts\activate

# Instalar dependências de desenvolvimento e teste
pip install -r requirements-dev.txt
```

### 3. Variáveis de Ambiente
Copie o arquivo de exemplo e configure suas chaves (se utilizar API Multimodal):
```bash
cp .env.example .env
```

### 4. Ferramentas de Qualidade (Lint & Testes)
O projeto utiliza ferramentas modernas para garantir código limpo e seguro:

- **Linting e Formatação (`ruff`)**:
  ```bash
  ruff check .
  ruff format .
  ```
- **Verificação de Tipos (`mypy`)**:
  ```bash
  mypy src/ tests/
  ```
- **Execução de Testes (`pytest`)**:
  ```bash
  pytest
  ```

---

## 🗺️ Roadmap e Status das Fases
- [x] **L1: Scaffolding, Estrutura, DevEx e Git + GH**
- [x] **L2: Schema de Dados e Modelos de Validação (Pydantic / JSON Schema)**
- [x] **L3: Aquisição e Downloaders (Scrapers para ENEM, FUVEST, UNICAMP e UNESP)**
- [x] **L4: Motor de Extração Multimodal (Layout-Aware Parser / Imagens / LaTeX)**
- [x] **L5: Conciliação de Gabaritos e Exportação Consolidada**

---

## 📄 Licença
Distribuído sob a licença **MIT**. Veja o arquivo `LICENSE` para mais detalhes.
