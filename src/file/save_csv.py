import csv


def save_csv(projects: list[dict[str, str]]) -> None:
    """
    Salva as informações dos projetos em um arquivo CSV.
    
    :param projects: Lista com as informações de cada projeto.
    :type projects: list[dict[str, str]]
    """
    fieldnames: set[str] = set()
    for project in projects:
        fieldnames.update(project.keys())

    with open("dados_sip.csv", mode="w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for project in projects:
            writer.writerow(project)
