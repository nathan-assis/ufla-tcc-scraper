import requests
from bs4 import BeautifulSoup

from .constants import LINK_SIP

def get_courses_links() -> dict[str, str]:
    """
    Extrai os links das páginas de Trabalho de Conclusão de Curso (TCC)
    de cada curso do site da SIP.

    :return: Dicionário no formato {nome_do_curso: link_relativo}.
    :rtype: dict[str, str]
    """
    response = requests.get(LINK_SIP)
    response.raise_for_status()
    response.encoding = 'utf-8'

    soup = BeautifulSoup(response.text, "html.parser")

    links: dict[str, str] = {}
    for a in soup.find_all("a", class_="botoes_de_menu"):
        links[a.get_text(strip=True)] = LINK_SIP+a.get("href")

    return links
