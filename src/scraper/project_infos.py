import requests
from bs4 import BeautifulSoup


def get_project_infos(urls: list[str]) -> list[dict[str, str]]:
    """
    Extrai as informações de cada projeto contido na lista de urls.
    
    :param urls: Lista com a url de cada projeto do curso.
    :type urls: list[str]
    :return: Lista com as informações de cada projeto na lista de urls.
    :rtype: list[dict[str, str]]
    """
    infos: list[dict[str, str]] = []
    total, current = len(urls), 0
    for url in urls:
        print(f"=== Searching project infos ({current}/{total}) ===")
        response = requests.get(url)
        response.raise_for_status()
        response.encoding = "utf-8"

        soup = BeautifulSoup(response.text, "html.parser")
        paragraphs = soup.find_all("p", class_="paragrafo_padrao_com_borda_inferior")
        project_info: dict[str, str] = {}
        for p in paragraphs:
            span = p.find("span")
            if not span:
                continue

            key = span.get_text(strip=True)
            value = p.get_text(strip=True).replace(key, "", 1)

            project_info[key] = value
        infos.append(project_info)
        current += 1

    print(f"=== Searching project infos ({current}/{total}) ===")
    return infos
