from typing import Optional


def get_column(
    projects: list[dict[str, str]], column_name: str, separator: Optional[str] = None
) -> list[str]:
    """
    Extrai os valores de uma coluna específica dos projetos.

    :param projects: Lista com as informações de cada projeto.
    :type projects: list[dict[str, str]]
    :param column_name: Nome da coluna a ser extraída.
    :type column_name: str
    :param separator: Separador utilizado para dividir os valores da coluna (opcional).
    :type separator: Optional[str]
    :return: Lista contendo os valores da coluna especificada.
    :rtype: list[str]
    """
    response = []
    for project in projects:
        if column_name in project:
            column = project[column_name]
            if separator:
                response.extend(column.split(separator))
            else:
                response.append(column)

    return response
