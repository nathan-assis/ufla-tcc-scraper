from src.csv.save import save_csv
from src.csv.column import get_column
from src.csv.load import load_csv
from src.scraper.courses_links import get_courses_links
from src.scraper.projects_links import get_projects_links
from src.scraper.project_infos import get_project_infos
from src.graph.embedding import generate_embeddings
from src.graph.similarity_matrix import similarity_matrix
from src.graph.create import (
    create_threshold_graph,
    create_knn_graph,
    create_symmetric_knn_graph,
)
from src.graph.render import (
    render_graph,
    render_graph_test,
    render_graph_plotly,
    render_graph_interactive,
)
from src.graph.stats import graph_stats

if __name__ == "__main__":
    """
    courses_links = get_courses_links()
    dcc_courses = {'Ciência da Computação': courses_links['Ciência da Computação'],
                   'Sistemas de Informação': courses_links['Sistemas de Informação']}

    projects_links = get_projects_links(dcc_courses)
    project_infos = get_project_infos(projects_links)

    save_csv(project_infos)
    print("Arquivo salvo com sucesso!")
    """
    projects = load_csv("dados_sip.csv")
    resumos = get_column(projects, "Resumo:")
    titulos = get_column(projects, "Título:")
    embeddings = generate_embeddings(resumos)
    matrix = similarity_matrix(embeddings)

    threshold = create_threshold_graph(titulos, matrix)
    knn = create_knn_graph(titulos, matrix)
    symmetric_knn = create_symmetric_knn_graph(titulos, matrix)


    print("\n\n=== threshold ===")
    threshold_stats = graph_stats(threshold)
    for k, v in threshold_stats.items():
        print(f"{k}: {v}")

    print("\n\n=== knn ===")
    knn_stats = graph_stats(knn)
    for k, v in knn_stats.items():
        print(f"{k}: {v}")

    print("\n\n=== symmetric knn ===")
    symmetric_knn_stats = graph_stats(symmetric_knn)
    for k, v in symmetric_knn_stats.items():
        print(f"{k}: {v}")

    # render_graph_interactive(threshold)
    # render_graph_interactive(knn)
    # render_graph_interactive(symmetric_knn)
