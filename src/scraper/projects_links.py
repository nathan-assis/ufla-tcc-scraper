import requests
from bs4 import BeautifulSoup

def get_projects_links(courses_links: dict[str, str]) -> list[str]:
    """
    Extrai o link de cada Trabalho de Conclusão de Curso (TCC)
    que esteja na página do curso correspondente.
    
    :param courses_links: Dicionário no formato {nome_do_curso: link_relativo}.
    :type courses_links: dict[str, str]
    :return: Lista com a url de cada projeto do curso.
    :rtype: list[str]
    """
    links: list[str] = []
    total, current = len(courses_links), 0
    for url in courses_links.values():
        print(f"=== Searching project links ({current}/{total}) ===")
        response = requests.get(url)
        response.raise_for_status()
        response.encoding = 'utf-8'

        soup = BeautifulSoup(response.text, "html.parser")
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if "index.php?dados=" in href:
                links.append(url+href)
        current += 1
    print(f"=== Searching project links ({current}/{total}) ===")
    return links
