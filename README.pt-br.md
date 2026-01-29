# Template de Projeto Python
[![en](https://img.shields.io/badge/lang-en-blue.svg)](https://github.com/nathanassis/python-project-template/blob/main/README.md)
[![pt-br](https://img.shields.io/badge/lang-pt--br-green.svg)](https://github.com/nathanassis/python-project-template/blob/main/README.pt-br.md)

Este é um repositório de template para projetos Python com as seguintes ferramentas de desenvolvimento:

* `ruff`: Linter e formatador
* `pre-commit`: Executa verificações antes de cada commit
* `pytest`: Testes unitários
* `GitHub Actions`: Executa testes e verificações em cada pull request e push para o `main`

## Instruções de Desenvolvimento

### Configurando o Ambiente

Primeiro, crie um ambiente virtual e ative-o:

```sh
python3 -m venv .venv
source .venv/bin/activate
```

Em seguida, instale as ferramentas de desenvolvimento e os hooks do pre-commit:

```sh
python3 -m pip install --user -r requirements-dev.txt
pre-commit install
```

### Executando Testes

Para rodar os testes, use:

```sh
pytest
```

### Executando Linter and Formatter

Para rodar o linter, use:

```sh
ruff check .
```

Para rodar o formatador, use:
```sh
ruff format .
```

## Estrutura do Repositório

* `.github/workflows/main.yml`: GitHub Actions para rodar testes e verificações
* `.gitignore`: Arquivos ignorados pelo Git
* `.pre-commit-config.yaml`: Configurações dos hooks do `pre-commit`
* `README.md`: Descrição do projeto em inglês
* `README.pt-br.md`: Descrição do projeto em português
* `pyproject.toml`: Configuração das ferramentas usadas
* `requirements.txt`: Dependências de produção
* `requirements-dev.txt`: Dependências de desenvolvimento

## 🔎 Encontrou um Problema ou Tem uma Sugestão?

Ajude a melhorar este template abrindo um issue ou criando um pull request!
