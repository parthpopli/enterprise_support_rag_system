def build_prompt(
    query: str,
    documents: list[dict]
) -> str:
    """
    Build a grounded prompt using the retrieved documents.
    """

    context_parts = []

    for index, document in enumerate(documents, start=1):

        source = document["metadata"].get(
            "source",
            "Unknown source"
        )

        page = document["metadata"].get(
            "page",
            "Unknown"
        )

        text = document["text"]

        context_parts.append(
            f"""
SOURCE {index}
File: {source}
Page: {page}

{text}
"""
        )

    context = "\n".join(context_parts)

    prompt = f"""
You are an Enterprise IT Support Assistant.

Answer the user's question using ONLY the information
provided in the context below.

If the answer cannot be found in the provided context,
say that you do not have enough information and
recommend contacting IT Support.

Do not invent procedures, policies, URLs, credentials,
or technical details.

Keep the answer clear and concise.

User Question:
{query}

Context:
{context}

Instructions:
1. Answer directly.
2. Use only the provided context.
3. Do not make unsupported assumptions.
4. Mention the relevant source file when appropriate.
"""

    return prompt