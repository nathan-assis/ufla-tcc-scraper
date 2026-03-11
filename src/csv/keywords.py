def extract_keywords(projects: list[dict[str, str]]) -> list[str]:
    """
    Extrai as palavras-chave dos projetos.
    
    :param projects: Lista com as informações de cada projeto.
    :type projects: list[dict[str, str]]
    :return: Lista contendo todas as palavras-chave dos projetos.
    :rtype: list[str]
    """
    keywords = []
    for project in projects:
        if "Palavras-chaves:" in project:
            project_keywords = project["Palavras-chaves:"].split(', ')
            keywords.extend(project_keywords)

    return keywords