import time
from typing import Dict, List
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

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


def _get_course_urls() -> Dict:
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


def _get_tcc(tcc_url: str, course: str) -> Dict:
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


def scrape() -> List[Dict]:
    tccs = []

    courses = _get_course_urls()
    for course_name, course_url in courses.items():
        try:
            tcc_urls = _get_tcc_urls(course_url)

            for tcc_url in tcc_urls:
                tcc = _get_tcc(tcc_url, course_name)
                tccs.append(tcc)
        except Exception as e:
            print(f"scraper.py (scrape): {e}")
            raise

    return tccs


if __name__ == "__main__":
    print(scrape())


"""
[
    {
        'curso': 'Zootecnia',
        'titulo': 'MACHINE LEARNING APLICADO À CLASSIFICAÇÃO MORFOFUNCIONAL DE EQUINOS MANGALARGA MARCHADOR',
        'autor': 'Beatriz Maria Nascimento',
        'orientador': 'Sarah Laguna Conceicao Meirelles',
        'resumo': 'Este estudo avaliou a possibilidade de antecipar a classificação da qualidade da marcha de equinos Mangalarga Marchador a partir de índices de aptidão funcional e de proporções corporais derivadas do Sistema Eclético de Lesbre, por meio de algoritmos de aprendizado de máquina. A base inicial continha 227.335 animais, com 12 medidas lineares e escores visuais de morfologia e marcha após a organização dos dados, a base analítica final utilizada na classificação foi composta por 224.804 animais. A variável resposta foi estruturada em seis classes, definidas por modelo de mistura gaussiana, selecionado com base nos critérios de informação de Akaike e Bayesiano. Foram avaliados três cenários de preditores índices de aptidão funcional descritores do Sistema Eclético de Lesbre e combinação dos dois conjuntos. Os algoritmos testados foram Random Forest, SVM linear implementada pelo e rede neural do tipo multilayer perceptron. A comparação entre modelos foi realizada por validação cruzada estratificada em cinco fo',
        'url': 'https://sip.prg.ufla.br/publico/trabalhos_conclusao_curso/acessar_tcc_por_curso/zootecnia/index.php?dados=20261202120766'
    }
]
"""