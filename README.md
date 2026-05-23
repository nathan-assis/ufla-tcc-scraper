# UFLA TCC Scraper

Ferramenta para scraping, análise e visualização de Trabalhos de Conclusão de Curso (TCCs) da Universidade Federal de Lavras (UFLA).

## Funcionalidades

- **Scraping**: Coleta automática de projetos TCC do portal SIP da UFLA
- **Análise**: Geração de embeddings e construção de grafos de similaridade
- **Visualização**: Renderização em múltiplos formatos (PNG, Plotly, Interativo, GEXF)

## Instalação

1. Crie um ambiente virtual:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

2. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

## Uso

### Comando `scrape`

Scrape projetos de cursos específicos e salva em CSV.

```bash
python main.py scrape --courses "Ciência da Computação" "Sistemas de Informação"
```

- `--courses`, `-c`: Lista de nomes de cursos para consultar projetos

### Comando `analyze`

Carrega CSV, gera embeddings, cria grafos e calcula estatísticas.

```bash
python main.py analyze --threshold 0.8 0.7 0.75 --k 3 4 5
```

- `--threshold`, `-t`: Lista de valores float para threshold dos grafos (opcional)
- `--k`, `-k`: Lista de valores int para k dos grafos KNN (opcional)
- `--detect-communities`: Detecta comunidades com o algoritmo Leiden

**Lógica de parâmetros opcionais:**
- Se apenas `-k` for passado: analisa apenas grafos KNN
- Se apenas `-t` for passado: analisa apenas grafos de threshold
- Se nenhum for passado: usa valores padrão de ambos
- Se ambos forem passados: analisa todos os tipos com valores especificados

Os resultados das estatísticas são salvos automaticamente em `assets/output/analysis_results.csv`.

### Comando `visualize`

Carrega CSV, gera embeddings, cria grafos e renderiza visualizações.

```bash
python main.py visualize --format gexf png plotly interactive --layout spring --threshold 0.8 0.7 --k 3 4
```

- `--format`, `-f`: Lista de formatos de saída (gexf, png, plotly, interactive)
- `--layout`, `-l`: Algoritmo de layout para renderizar o grafo:
  - `spring` (padrão): Spring layout
  - `circular`: Circular layout
  - `kawai`: Kamada-Kawai layout
  - `atlas`: ForceAtlas2 layout
- `--threshold`, `-t`: Lista de valores float para threshold dos grafos (opcional)
- `--k`, `-k`: Lista de valores int para k dos grafos KNN (opcional)
- `--detect-communities`: Detecta comunidades usando o algoritmo Leiden (apenas para visualização com cores)

**Lógica de parâmetros opcionais:**
- Se apenas `-k` for passado: cria apenas grafos KNN
- Se apenas `-t` for passado: cria apenas grafos de threshold
- Se nenhum for passado: usa valores padrão de ambos
- Se ambos forem passados: cria todos os tipos com valores especificados
## Exemplos de Uso

### Scraping
```bash
# Fazer scraping de dois cursos
python main.py scrape -c "Ciência da Computação" "Sistemas de Informação"
```

### Análise
```bash
# Analisar com thresholds customizados
python main.py analyze -t 0.8 0.75 0.7

# Analisar apenas KNN com k=3 e k=5
python main.py analyze -k 3 5

# Análise completa com defaults
python main.py analyze
```

### Visualização
```bash
# Gerar PNG com layout circular
python main.py visualize -f png -l circular

# Interativo com layout Kamada-Kawai, apenas KNN
python main.py visualize -f interactive -l kawai -k 4

# Múltiplos formatos com valores customizados
python main.py visualize -f gexf png plotly -l spring -t 0.8 0.75 -k 3 4

# Interativo para explorar diferentes topologias
python main.py visualize -f interactive -t 0.8 0.7 -k 3 4 5
```
## Estrutura do Projeto

```
ufla-tcc-scraper/
├── src/
│   ├── services/          # Lógica de negócio
│   ├── data/              # I/O de dados
│   ├── views/             # Visualizações
│   └── config.py          # Configurações
├── assets/                # Arquivos de entrada/saída
├── scripts/               # Scripts específicos
├── tests/                 # Testes
├── main.py                # Entry point
└── requirements.txt       # Dependências
```
