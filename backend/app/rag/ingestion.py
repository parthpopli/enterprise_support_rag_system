from pathlib import Path
import re
import pymupdf
from docx import Document


SUPPORTED_EXTENSIONS = {
    ".pdf",
    ".docx",
    ".txt"
}


def clean_text(text: str) -> str:

    text = re.sub(
        r"[ \t]+",
        " ",
        text
    )

    text = re.sub(
        r"\n\s*\n+",
        "\n\n",
        text
    )

    text = "\n".join(
        line.strip()
        for line in text.splitlines()
    )

    return text.strip()


def extract_pdf(file_path: Path) -> list[dict]:

    documents = []

    pdf = pymupdf.open(file_path)

    for page_number, page in enumerate(
        pdf,
        start=1
    ):

        text = page.get_text()

        text = clean_text(text)

        if not text:
            continue

        documents.append({
            "text": text,
            "metadata": {
                "source": file_path.name,
                "file_path": str(file_path),
                "file_type": "pdf",
                "page": page_number
            }
        })

    pdf.close()

    return documents


def extract_docx(file_path: Path) -> list[dict]:

    document = Document(file_path)

    paragraphs = []

    for paragraph in document.paragraphs:

        text = paragraph.text.strip()

        if text:
            paragraphs.append(text)

    text = "\n".join(paragraphs)

    text = clean_text(text)

    if not text:
        return []

    return [{
        "text": text,
        "metadata": {
            "source": file_path.name,
            "file_path": str(file_path),
            "file_type": "docx"
        }
    }]


def extract_txt(file_path: Path) -> list[dict]:

    text = file_path.read_text(
        encoding="utf-8",
        errors="ignore"
    )

    text = clean_text(text)

    if not text:
        return []

    return [{
        "text": text,
        "metadata": {
            "source": file_path.name,
            "file_path": str(file_path),
            "file_type": "txt"
        }
    }]


def load_document(file_path: Path) -> list[dict]:

    extension = file_path.suffix.lower()

    if extension == ".pdf":

        return extract_pdf(file_path)

    elif extension == ".docx":

        return extract_docx(file_path)

    elif extension == ".txt":

        return extract_txt(file_path)

    else:

        raise ValueError(
            f"Unsupported file type: {extension}"
        )


def load_documents(directory: str) -> list[dict]:

    directory_path = Path(directory)

    if not directory_path.exists():

        raise FileNotFoundError(
            f"Directory not found: {directory}"
        )

    documents = []

    for file_path in directory_path.rglob("*"):

        if not file_path.is_file():
            continue

        if file_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            continue

        try:

            extracted_documents = load_document(
                file_path
            )

            documents.extend(
                extracted_documents
            )

            print(
                f"Loaded: {file_path.name} "
                f"({len(extracted_documents)} sections)"
            )

        except Exception as e:

            print(
                f"Failed to load {file_path}: {e}"
            )

    return documents