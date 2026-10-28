"""
Avaliação do pipeline GraphRAG (etapa de COLETA).

Executar da raiz do projeto:
    python -m scripts.evaluation

Coleta, por pergunta: tempo por etapa, RAM (média/pico), tokens, Recall@k,
contexto e resposta. Faithfulness e Answer Correctness (LLM-juiz) devem ser
calculadas depois, lendo o JSON gerado, para que as chamadas ao juiz não
interfiram nas medições de tempo/memória.
"""
import json
import threading
import time
from bert_score import score as bert_score
from contextlib import contextmanager
from pathlib import Path

import numpy as np
import psutil

from src.generation import generation_with_stats
from src.indexing import index
from src.retrieval import get_tok_k
from src.utils.embedder import build_embeddings, get_embedding_model
from src.utils.graph_builder import build_subgraph

# ----------------------------------------------------------------- config
SEEDS_K = 5                   # mesmo k usado em retrieval.py
K_VALUES = [1, 3, 5, 10]      # valores de k para Recall@k
N_RUNS = 3                    # repetições (desempenho)
WARMUP = True                 # descarta a 1ª execução (carga do modelo no Ollama)
OUTPUT_DIR = Path("assets/output/evaluation")

RUN_BERTSCORE = True
BERT_LANG = "pt"            # modelo padrão para "pt": bert-base-multilingual-cased
BERT_MODEL_TYPE = "xlm-roberta-large"      # ou "xlm-roberta-large" (mais pesado, em geral melhor)
BERT_RESCALE = True        # True aplica o baseline; se der erro de baseline, deixe False


DATASET = [
    {
        "id": "q01",
        "pergunta": "Quanto de microplástico foi ingerido por animais aquáticos? Quais espécies mais consumiram?",
        "resposta_referencia": "Os peixes juvenis migradores do Rio das Velhas (Prochilodus costatus, Salminus franciscanus e Megaleporinus obtusidens) tiveram 304 partículas no trato digestório de 30 indivíduos (10 por espécie). Todos ingeriram microplásticos, principalmente fragmentos e fibras. Em P. costatus, peixes maiores ingeriram mais partículas; em M. obtusidens, ingeriram menos; em S. franciscanus, não houve relação com o tamanho. Em um riacho urbano da região de Lavras, o lambari (Psalidodon paranae) teve as maiores taxas de ingestão, provavelmente pela caça visual na coluna d'água; o barrigudinho (Poecilia reticulata) teve consumo intermediário; a tuvira (Gymnotus sylvius) teve os menores índices, talvez por sua eletrorrecepção. Predominaram fibras transparentes e azuis, compatíveis com efluentes domésticos. Também foram analisados estômagos de camarões Macrobrachium amazonicum da Represa do Funil, mas os valores não aparecem no resumo. Uma revisão confirma que animais e microrganismos ingerem microplásticos.",
        "vertices_relevantes": ["3691", "2288", "2198", "3930"],
    },
    {
        "id": "q02",
        "pergunta": "Como remover microplásticos do ambiente ou reduzir sua geração?",
        "resposta_referencia": "Remoção: microalgas, alternativa eficiente, de baixo custo e sustentável para tratar efluentes urbanos, principal via de entrada de microplásticos em ambientes aquáticos. Redução na origem: economia circular nas empresas, com menos uso e produção de plástico, reciclagem, reutilização e redesign de produtos. Substituição de materiais: nos nanofertilizantes, trocar o encapsulamento com polímeros sintéticos por bactérias promotoras de crescimento revestidas com nanopartículas de cobre. Políticas e tecnologias: criar políticas e tecnologias que minimizem os resíduos plásticos e permitam tratá-los de forma eficaz.",
        "vertices_relevantes": ["3707", "3784", "8207", "3930"],
    },
    {
        "id": "q03",
        "pergunta": "Para que finalidades o blockchain pode ser aplicado na gestão de recursos hídricos e em projetos ambientais?",
        "resposta_referencia": "Gestão de águas outorgadas: contratos inteligentes (Hyperledger Sawtooth) que integram as regras de negócio, dando segurança, transparência, imutabilidade e gestão mais eficiente e sustentável. Monitoramento do uso de água: sensores IoT registram a quantidade de água usada em uma blockchain permissionada, garantindo confiabilidade e rastreabilidade. Créditos de carbono: garante auditabilidade, transparência, confiabilidade e integridade dos dados em projetos do Mecanismo de Desenvolvimento Limpo.",
        "vertices_relevantes": ["1938", "1939", "8500"],
    },
    {
        "id": "q04",
        "pergunta": "Que lacunas ou indefinições existem na legislação de proteção de dados e de tecnologia no Brasil (LGPD e normas correlatas)?",
        "resposta_referencia": "A LGPD não define claramente o regime de responsabilidade civil em incidentes de segurança, e os estudiosos divergem; a análise conclui que a responsabilidade subjetiva é a mais adequada. A Resolução CFM nº 2.314/2022 sobre telemedicina não trata da responsabilização ético-profissional por vazamento de dados sensíveis, e a cadeia de agentes (médicos, clínicas e terceiros) dificulta definir responsabilidades. O art. 14, §1º da LGPD é insuficiente para proteger adolescentes, pois depende do consentimento deles; defende-se a Privacy by Design. A legislação sobre racismo algorítmico (Marco Civil da Internet, LGPD, CDC e AI Act) é incipiente, e as normas existentes encontram obstáculos para surtir efeito. Há necessidade de delimitar a diferença entre o direito à proteção de dados pessoais e o direito à privacidade.",
        "vertices_relevantes": ["2715", "2711", "2707", "2457", "2670"],
    },
    {
        "id": "q05",
        "pergunta": "Em quais tarefas as redes neurais convolucionais (CNNs) podem ser aplicadas?",
        "resposta_referencia": "Classificação de torra de café em dispositivo embarcado (NVIDIA Jetson Nano) com MobileNetV2: acurácia de 100% em testes estáticos, queda a 66% in-situ por domain shift e 95% a 12 FPS com fusão de dados e espaço de cor HSV. Análise de sentimentos em textos (reviews do IMDB), com precisão, recall, F1 e acurácia de 89%. Reconhecimento facial em vídeos para segurança de casas inteligentes, com identificação e verificação facial. Estimativa de profundidade em aplicativo Android com TensorFlow Lite, com 74,8% de acurácia e 21% de erro quadrático médio, útil para mobilidade assistida. Detecção de transtorno depressivo maior por sinais de EEG, com a EEGNet, que teve 86,58% de acurácia.",
        "vertices_relevantes": ["1855", "1918", "2067", "5052", "8360"],
    },
    {
        "id": "q06",
        "pergunta": "Como aplicar grandes modelos de linguagem e IA generativa no contexto educacional?",
        "resposta_referencia": "Plugins de Moodle com LLMs: criar conteúdos educacionais, personalizar a aprendizagem, dar recomendações automatizadas e detectar plágio. Feedback automatizado: corrigir exercícios de Programação Orientada a Objetos com LLMs e a biblioteca LangGraph, que permite escolher o modelo, reduzindo o esforço docente e melhorando a consistência e a clareza do retorno. Apoio ao trabalho pedagógico na educação básica: exige competências críticas dos professores para um uso ético e seguro, formação docente específica e atenção às barreiras de implementação.",
        "vertices_relevantes": ["1852", "1840", "1832"],
    },
    {
        "id": "q07",
        "pergunta": "Como prevenir, diagnosticar e controlar a mastite bovina? Qual antisséptico é mais eficiente in vitro?",
        "resposta_referencia": "Prevenção e controle: higiene do úbere e dos tetos, limpeza e desinfecção dos equipamentos de ordenha, antissepsia dos tetos com pré e pós-dipping e boas práticas de ordenha. Antissépticos tradicionais à base de iodo, cloro e peróxidos podem deixar resíduos no leite; alternativas naturais incluem óleo de alecrim-pimenta e extrato de própolis. Antisséptico mais eficiente in vitro: a clorexidina inibiu todas as bactérias testadas já na menor concentração, com amplo espectro; o glutaraldeído não teve ação e não é indicado; iodo, peróxido de hidrogênio, ácido lático e ácido peracético inibiram todas as espécies em concentrações intermediárias e altas; triclosano e amônia quaternária tiveram ação parcial. Diagnóstico e monitoramento: a cultura microbiológica convencional é o padrão-ouro, usada para validar métodos rápidos de campo; a contagem de células somáticas (CCS) monitora a mastite subclínica; a hiperqueratose do esfíncter do teto, causada por traumas de ordenha (sobreordenha, pressão inadequada das teteiras, vácuo incorreto), predispõe a infecções.",
        "vertices_relevantes": ["8899", "4612", "8604", "8599", "8607"],
    },
    {
        "id": "q08",
        "pergunta": "Quais herbicidas pré-emergentes são seletivos para a canola e como os bioestimulantes entram nesse contexto?",
        "resposta_referencia": "Seletivos: o híbrido Diamond foi seletivo, sem fitotoxicidade, a diuron (750 g i.a./ha), diuron + S-metolacloro, clomazona (375 g i.a./ha) e hexazinona + diuron (132 + 468 g i.a./ha); esta última teve as maiores massas fresca e seca, altura e SPAD. Sulfentrazona e clomazona a 500 g i.a./ha não estão entre os seletivos. Clomazona (Gamit): a fitotoxidez cresce com a dose; o solo arenoso causou menos fitotoxidez que o argiloso e o melhor resultado foi na menor dose (45 g i.a.). Ametrina: potencial em híbridos TT e CT, mas exige avaliação de seletividade; a fenotipagem multiespectral é alternativa às escalas visuais, subjetivas e destrutivas. Bioestimulantes: Roadster e Sergomil L60 foram testados para mitigar a fitointoxicação causada por quincloraque + dicamba na canola.",
        "vertices_relevantes": ["1313", "1294", "923", "1010"],
    },
    {
        "id": "q09",
        "pergunta": "De que formas IA e aprendizado de máquina podem ser aplicados à cadeia produtiva do café?",
        "resposta_referencia": "Colheita mecanizada: redes neurais artificiais predizem eficiência de derriça (R² 0,94), eficiência de colheita (R² 0,97) e perda de chão da máquina (R² 0,93), com 34 fatores como entrada; a ferramenta LIME ordena os fatores mais influentes e orienta recomendações para aumentar a eficiência e reduzir perdas. Pós-colheita: classificação da torra por CNN (MobileNetV2) em dispositivo embarcado de baixo custo, com 95% de acurácia a 12 FPS. Mercado: previsão de preços de contratos futuros de café arábica com Redes Neurais Líquidas (LTC) e variáveis climáticas; a LNN superou a rede recorrente em 59,24% no RMSE de um passo e reduziu o tempo de treino em 50%; as variáveis climáticas reduziram o RMSE da previsão de 90 dias em cerca de 6%.",
        "vertices_relevantes": ["3614", "1855", "5355"],
    },
    {
        "id": "q10",
        "pergunta": "Como aplicar aprendizado de máquina e deep learning ao diagnóstico e ao apoio à decisão clínica?",
        "resposta_referencia": "Tuberculose: classificação de radiografias de tórax com curvas principais e redes siamesas, sem CNN, usando a base TBX11K (1.600 imagens), com mais de 80 em todas as métricas, perto dos resultados com CNN; serve para triagem e detecção precoce. Depressão (MDD): detecção por sinais de EEG; a EEGNet foi a melhor, com 86,58% de acurácia, 94,85% de sensibilidade e 80,05% de especificidade, superando SVM, Random Forest e XGBoost; a validação por sujeitos é essencial para não superestimar resultados (99,31% contra 83,09% por épocas). Sepse em UTI: previsão de morte com SVM e Regressão Logística (80 em acurácia e F1), usando SHAP para explicar os fatores e dar transparência à equipe médica.",
        "vertices_relevantes": ["5082", "8360", "1980"],
    },
]


# ------------------------------------------------------------- utilitários
@contextmanager
def timer(store: dict, key: str):
    t0 = time.perf_counter()
    yield
    store[key] = time.perf_counter() - t0


class RamSampler(threading.Thread):
    """Amostra o RSS (MiB) do processo atual + processos do Ollama."""

    def __init__(self, interval: float = 0.05):
        super().__init__(daemon=True)
        self.interval = interval
        self.samples: list[float] = []
        self._halt = threading.Event()

    @staticmethod
    def snapshot() -> float:
        procs = [psutil.Process()]
        for p in psutil.process_iter(["name"]):
            if "ollama" in (p.info["name"] or "").lower():
                procs.append(p)
        total = 0
        for p in procs:
            try:
                total += p.memory_info().rss
            except psutil.NoSuchProcess:
                pass
        return total / 2**20

    def run(self):
        while not self._halt.is_set():
            self.samples.append(self.snapshot())
            time.sleep(self.interval)

    def stop(self) -> dict:
        self._halt.set()
        self.join()
        s = self.samples or [self.snapshot()]
        return {"ram_media_mib": float(np.mean(s)), "ram_pico_mib": float(max(s))}


def recall_at_k(retrieved, relevant, k) -> float:
    rel = set(map(str, relevant))
    return len(set(map(str, retrieved[:k])) & rel) / len(rel)


# ---------------------------------------------------------------- pipeline
def run_once(item, graph, embeddings, model) -> dict:
    times: dict[str, float] = {}
    sampler = RamSampler()
    sampler.start()
    t_total = time.perf_counter()
    try:
        with timer(times, "embedding"):
            msg_emb = build_embeddings(model, item["pergunta"], True)
        with timer(times, "busca_semantica"):
            seeds = get_tok_k(msg_emb, embeddings, SEEDS_K)
        with timer(times, "subgrafo"):
            subgraph = build_subgraph(graph, seeds)
        gen = generation_with_stats(item["pergunta"], subgraph)
        times["contexto"] = gen["t_contexto"]
        times["llm"] = gen["t_llm"]
    finally:
        times["total"] = time.perf_counter() - t_total
        ram = sampler.stop()

    # abaixo: fora da janela de medição de tempo/RAM
    return {
        "tempo_s": times,
        "ram": ram,
        "tokens_entrada": gen["prompt_eval_count"],
        "tokens_saida": gen["eval_count"],
        "seeds": [str(s) for s in seeds],
        "seeds_similaridade": [float(embeddings[s] @ msg_emb) for s in seeds],
        "nos_subgrafo": [str(n) for n in subgraph.nodes],
        "n_arestas_subgrafo": subgraph.number_of_edges(),
        "contexto": gen["context"],
        "resposta": gen["response"],
    }


def mean_nested(dicts: list[dict]) -> dict:
    return {k: float(np.mean([d[k] for d in dicts])) for k in dicts[0]}


def comparar_seeds_subgrafo(seeds, nos_subgrafo, relevantes) -> dict:
    """Compara os top-k (get_tok_k) com os nós da Steiner tree (build_subgraph)."""
    seeds = [str(s) for s in seeds]
    nos = [str(n) for n in nos_subgrafo]
    rel = set(map(str, relevantes))
    s_set, n_set = set(seeds), set(nos)
    extras = [n for n in nos if n not in s_set]
    return {
        "nos_extras_steiner": extras,
        "seeds_ausentes_no_subgrafo": [s for s in seeds if s not in n_set],
        "relevantes_nos_seeds": sorted(rel & s_set),
        "relevantes_no_subgrafo": sorted(rel & n_set),
        "relevantes_ganhos_steiner": sorted((rel & n_set) - s_set),
        "relevantes_perdidos_steiner": sorted((rel & s_set) - n_set),
        "recall_seeds": len(rel & s_set) / len(rel),
        "recall_subgrafo": len(rel & n_set) / len(rel),
        "precisao_seeds": len(rel & s_set) / max(len(s_set), 1),
        "precisao_subgrafo": len(rel & n_set) / max(len(n_set), 1),
        "n_seeds": len(seeds),
        "n_nos_subgrafo": len(nos),
        "n_nos_extras": len(extras),
        "n_relevantes_entre_extras": len(rel & set(extras)),
    }


def compute_bertscore(results: list[dict]) -> None:
    """Calcula BERTScore (P/R/F1) resposta x referência, em lote, ao final."""
    cands = [r["resposta"] for r in results]
    refs = [r["resposta_referencia"] for r in results]
    P, R, F1 = bert_score(
        cands, refs,
        lang=BERT_LANG,
        model_type=BERT_MODEL_TYPE,
        rescale_with_baseline=BERT_RESCALE,
        verbose=False,
    )
    for r, p, rc, f in zip(results, P, R, F1):
        r["bertscore"] = {"precision": float(p), "recall": float(rc), "f1": float(f)}


def summarize(results: list[dict]) -> dict:
    def m(fn):
        return float(np.mean([fn(r) for r in results]))

    cmp = lambda key: m(lambda r: r["comparacao_seeds_subgrafo"][key])
    resumo = {
        "recall_at_k": {k: m(lambda r: r["recall_at_k"][k]) for k in K_VALUES},
        "seeds_vs_subgrafo": {
            key: cmp(key) for key in [
                "recall_seeds", "recall_subgrafo", "precisao_seeds",
                "precisao_subgrafo", "n_nos_subgrafo", "n_nos_extras",
                "n_relevantes_entre_extras",
            ]
        },
        "tempo_s": mean_nested([r["tempo_s"] for r in results]),
        "ram": mean_nested([r["ram"] for r in results]),
        "ram_pico_max_mib": max(r["ram_pico_max_mib"] for r in results),
        "tokens_entrada": m(lambda r: r["tokens_entrada"]),
        "tokens_saida": m(lambda r: r["tokens_saida"]),
    }
    if all("bertscore" in r for r in results):
        resumo["bertscore"] = mean_nested([r["bertscore"] for r in results])
    return resumo


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    model = get_embedding_model()
    graph, embeddings = index(model)
    ram_baseline = RamSampler.snapshot()

    if WARMUP:
        print("warm-up...")
        run_once(DATASET[0], graph, embeddings, model)

    results = []
    for item in DATASET:
        print(f"[{item['id']}] {item['pergunta'][:60]}")
        runs = [run_once(item, graph, embeddings, model) for _ in range(N_RUNS)]

        # ranking completo (fora das medições) para Recall@k
        ranking = get_tok_k(
            build_embeddings(model, item["pergunta"], True), embeddings, max(K_VALUES)
        )
        rel = item["vertices_relevantes"]
        first = runs[0]

        results.append({
            "id": item["id"],
            "pergunta": item["pergunta"],
            "resposta_referencia": item["resposta_referencia"],
            "vertices_relevantes": rel,
            "resposta": first["resposta"],
            "contexto": first["contexto"],
            "recall_at_k": {k: recall_at_k(ranking, rel, k) for k in K_VALUES},
            "comparacao_seeds_subgrafo": {
                "seeds": first["seeds"],
                "seeds_similaridade": first["seeds_similaridade"],
                "nos_subgrafo": first["nos_subgrafo"],
                "n_arestas_subgrafo": first["n_arestas_subgrafo"],
                **comparar_seeds_subgrafo(first["seeds"], first["nos_subgrafo"], rel),
            },
            "tokens_entrada": first["tokens_entrada"],
            "tokens_saida": first["tokens_saida"],
            "tempo_s": mean_nested([r["tempo_s"] for r in runs]),
            "ram": mean_nested([r["ram"] for r in runs]),
            "ram_pico_max_mib": max(r["ram"]["ram_pico_mib"] for r in runs),
        })

    # BERTScore roda só no fim, para o modelo BERT não entrar nas medições de RAM/tempo
    if RUN_BERTSCORE:
        try:
            compute_bertscore(results)
        except Exception as e:
            print(f"BERTScore falhou: {e}")

    out = {
        "ram_baseline_mib": ram_baseline,
        "n_runs": N_RUNS,
        "resumo": summarize(results),
        "resultados": results,
    }
    path = OUTPUT_DIR / "raw_results.json"
    path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"salvo em {path}")


if __name__ == "__main__":
    main()