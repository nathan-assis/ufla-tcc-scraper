from src.csv.save import save_csv
from src.csv.column import get_column
from src.csv.load import load_csv
from src.scraper.courses_links import get_courses_links
from src.scraper.projects_links import get_projects_links
from src.scraper.project_infos import get_project_infos
from src.graph.embedding import generate_embeddings, similarity_matrix
from src.graph.create import create_graph, create_knn_graph
from src.graph.render import render_graph
from src.graph.render_interactive import render_interactive_graph

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
    graph = create_knn_graph(titulos, matrix)
    render_graph(graph)
    render_interactive_graph(graph)
