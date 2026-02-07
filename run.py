from src.file.save_csv import save_csv
from src.scraper.courses_links import get_courses_links
from src.scraper.projects_links import get_projects_links
from src.scraper.project_infos import get_project_infos

if __name__ == "__main__":
    courses_links = get_courses_links()
    dcc_courses = {'Ciência da Computação': courses_links['Ciência da Computação'],
                   'Sistemas de Informação': courses_links['Sistemas de Informação']}
    
    projects_links = get_projects_links(dcc_courses)
    project_infos = get_project_infos(projects_links)
    
    save_csv(project_infos)
    print("Arquivo salvo com sucesso!")
