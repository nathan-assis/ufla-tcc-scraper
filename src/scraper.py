import requests
from bs4 import BeautifulSoup
from typing import Dict, List
from urllib.parse import urljoin

from .types import Node

BASE_URL = "https://sip.prg.ufla.br/publico/trabalhos_conclusao_curso/acessar_tcc_por_curso/"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/138.0 Safari/537.36"
    )
}

TIMEOUT = 2

session = requests.Session()
session.headers.update(HEADERS)


def _get_soup(url: str) -> BeautifulSoup:
    try:
        response = session.get(url, timeout=TIMEOUT)
        response.raise_for_status()
        response.encoding = "utf-8"
    except requests.RequestException as e:
        print(f'scraper.py (_get_soup): {e}')
        raise

    return BeautifulSoup(response.text, "html.parser")


def _get_course_urls() -> Dict[str, str]:
    soup = _get_soup(BASE_URL)

    courses = {}
    for link in soup.find_all("a", class_="botoes_de_menu"):
        course_name = link.get_text(strip=True)
        course_url = urljoin(BASE_URL, link.get("href", ""))
        courses[course_name] = course_url

    return courses


def _get_tcc_urls(course_url: str) -> List[str]:
    soup = _get_soup(course_url)

    tcc_urls = []
    for link in soup.find_all("a", href=True):
        href = link.get("href", "")
        if "index.php?dados=" not in href:
            continue

        url = urljoin(course_url, href)
        tcc_urls.append(url)

    return tcc_urls


def _get_tcc(tcc_url: str, course: str) -> Node:
    soup = _get_soup(tcc_url)

    fields = {}
    for paragraph in soup.find_all("p", class_="paragrafo_padrao_com_borda_inferior"):
        label = paragraph.find("span")
        if not label:
            continue

        key = label.get_text(strip=True).replace(":", "")
        label.extract()
        value = " ".join(paragraph.stripped_strings)

        fields[key] = value

    return {
        "titulo": fields.get("Título", ""),
        "autor": fields.get("Autoria de", ""),
        "orientador": fields.get("Orientação de", ""),
        "resumo": fields.get("Resumo", ""),
        "curso": course,
        "url": tcc_url,
    }


def scrape() -> Dict[str, Node]:
    tccs, id = {}, 0

    courses = _get_course_urls()
    # courses = {'Ciência da Computação': 'https://sip.prg.ufla.br/publico/trabalhos_conclusao_curso/acessar_tcc_por_curso/ciencia_da_computacao/'}
    for course_name, course_url in courses.items():
        try:
            tcc_urls = _get_tcc_urls(course_url)

            for tcc_url in tcc_urls:
                tcc = _get_tcc(tcc_url, course_name)
                tccs[str(id)] = tcc
                id += 1
        except Exception as e:
            print(f"scraper.py (scrape): {e}")
            raise

    return tccs
