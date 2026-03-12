import csv


def load_csv(path: str) -> list[dict[str, str]]:
    """
    Carrega as informações dos projetos a partir de um arquivo CSV.

    :param path: Caminho do arquivo CSV.
    :type path: str
    :return: Lista com as informações de cada projeto.
    :rtype: list[dict[str, str]]
    """
    projects: list[dict[str, str]] = []

    with open(path, mode="r", newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            projects.append(dict(row))

    return projects