# Guia de Contribuição - Vestibulares ETL 🤝

Obrigado por seu interesse em contribuir para a estruturação aberta de questões de vestibulares brasileiros!

## 📌 Convenções de Commit (Conventional Commits)

Nossos commits seguem a especificação [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` Nova funcionalidade (ex: `feat: add scraper for comvest 2024`).
- `fix:` Correção de bug no parser ou validador.
- `docs:` Alterações na documentação (README, schemas ou comentários).
- `chore:` Atualizações em arquivos de build, DevEx ou dependências.
- `test:` Adição ou modificação de testes unitários.
- `refactor:` Refatoração de código sem mudança de funcionalidade externa.

Exemplo de mensagem de commit:
```bash
git commit -m "feat(scrapers): add fuvest first phase pdf downloader"
```

---

## 🛠️ Fluxo de Desenvolvimento

1. Certifique-se de ter instalado as dependências de desenvolvimento:
   ```bash
   pip install -r requirements-dev.txt
   ```
2. Crie uma branch para sua funcionalidade ou correção:
   ```bash
   git checkout -b feat/minha-nova-feature
   ```
3. Antes de submeter ou fazer commit, execute nosso fluxo obrigatório de verificação de qualidade:
   ```bash
   ruff check .
   mypy src/ tests/
   pytest
   ```
4. Se todos os testes passarem sem erros ou avisos, crie o seu commit seguindo a convenção e abra um Pull Request!

---

## 📐 Adicionando Novos Parsers de Vestibular
Ao implementar suporte a um novo vestibular ou ano, siga as seguintes diretrizes:
- Salve os arquivos em `src/parsers/<nome_do_vestibular>_parser.py`.
- Certifique-se de que todas as questões extraídas respeitam estritamente o schema definido em `schemas/questao_schema.json`.
- Adicione testes unitários em `tests/` cobrindo pelo menos uma amostra da prova.
