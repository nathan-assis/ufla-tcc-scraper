from csv.save import save_csv
from src.scraper.courses_links import get_courses_links
from src.scraper.projects_links import get_projects_links
from src.scraper.project_infos import get_project_infos
from src.constants import KEY_WORDS

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

    x = KEY_WORDS.replace(".", "")
    y = x.replace("\n", ", ").split(", ")

    counter = {}
    for word in y:
        word2 = word.lower()
        if word2 in counter.keys():
            counter[word2] += 1
        else:
            counter[word2] = 1
        """
        if word in counter.keys():
            counter[word] += 1
        else:
            counter[word] = 1
        """

    dict_ordenado = dict(
        sorted(counter.items(), key=lambda item: item[1], reverse=False)
    )
    print(dict_ordenado)
