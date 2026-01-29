# Python Project Template
[![en](https://img.shields.io/badge/lang-en-blue.svg)](https://github.com/nathanassis/python-project-template/blob/main/README.md)
[![pt-br](https://img.shields.io/badge/lang-pt--br-green.svg)](https://github.com/nathanassis/python-project-template/blob/main/README.pt-br.md)

This is a template repository for Python projects with the following development tools:

* `ruff`: Linter and formatter
* `pre-commit`: Runs checks before each commit
* `pytest`: Unit tests
* `GitHub Actions`: Runs tests and checks on every pull request and push to `main`

## Development Instructions

### Setting Up the Environment

First, create a virtual environment and activate it:

```sh
python3 -m venv .venv
source .venv/bin/activate
```

Then install the development tools and pre-commit hooks:

```sh
python3 -m pip install --user -r requirements-dev.txt
pre-commit install
```

### Running Tests

To run tests, use:

```sh
pytest
```

### Running Linter and Formatter

To run linter, use:

```sh
ruff check .
```

To run formatter, use:
```sh
ruff format .
```

## Repository Structure

* `.github/workflows/main.yml`: GitHub Actions workflow to run tests and checks
* `.gitignore`: Ignored files by Git
* `.pre-commit-config.yaml`: Configs for `pre-commit` hooks
* `README.md`: Project description
* `README.pt-br.md`: Project description in portuguese
* `pyproject.toml`: Configuration for Python tools
* `requirements.txt`: Production dependencies
* `requirements-dev.txt`: Development dependencies

## 🔎 Found an Issue or Have an Idea for Improvement?

Help improve this template by opening an issue or submitting a pull request!
