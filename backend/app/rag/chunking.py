from typing import List, Dict


def chunk_text(
    text: str,
    chunk_size: int = 500,
    chunk_overlap: int = 100
) -> List[str]:
    """
    Split text into overlapping chunks.

    Args:
        text: Clean document text.
        chunk_size: Maximum number of characters per chunk.
        chunk_overlap: Number of characters shared between chunks.

    Returns:
        List of text chunks.
    """

    if not text:
        return []

    if chunk_overlap >= chunk_size:
        raise ValueError(
            "chunk_overlap must be smaller than chunk_size"
        )

    chunks = []

    start = 0
    text_length = len(text)

    while start < text_length:

        end = start + chunk_size

        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        start = end - chunk_overlap

    return chunks


def chunk_documents(
    documents: List[Dict],
    chunk_size: int = 500,
    chunk_overlap: int = 100
) -> List[Dict]:
    """
    Chunk all extracted documents while preserving metadata.
    """

    chunked_documents = []

    for document in documents:

        text = document["text"]
        metadata = document["metadata"]

        chunks = chunk_text(
            text,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )

        for chunk_index, chunk in enumerate(chunks):

            chunked_documents.append(
                {
                    "text": chunk,
                    "metadata": {
                        **metadata,
                        "chunk_index": chunk_index
                    }
                }
            )

    return chunked_documents