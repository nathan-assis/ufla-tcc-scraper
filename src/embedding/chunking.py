def fixed_size_chunking_with_overlap(
    text: str, chunk_size: int = 100, overlap: int = 20
) -> list[str]:
    """
    Divide um texto em chunks de tamanho fixo com sobreposição.
    COnsidera as palavras para realizar o chunking.
    
    :param text: O texto que será dividido
    :type text: str
    :param chunk_size: Número de palavras por chunk
    :type chunk_size: int
    :param overlap: Número de palavras na sobreposição
    :type overlap: int
    :return: Uma lista de strings, onde cada string representa um chunk.
    :rtype: list[str]
    """
    if not text:
        return []

    words = text.split()
    chunks = [" ".join(words[: chunk_size + overlap])]

    for i in range(chunk_size, len(words), chunk_size):
        chunks.append(" ".join(words[i - overlap : i + chunk_size + overlap]))

    return chunks
