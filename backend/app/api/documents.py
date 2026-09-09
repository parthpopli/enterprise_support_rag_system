from pathlib import Path
import json
import shutil

from fastapi import APIRouter, UploadFile, File, HTTPException

from app.rag.ingestion import load_document
from app.rag.chunking import chunk_documents
from app.rag.embeddings import EmbeddingModel
from app.rag.vector_store import VectorStore



router = APIRouter(
    prefix="/documents",
    tags=["Documents"]
)


PROJECT_ROOT = Path(__file__).resolve().parents[3]

DOCUMENT_PATH = (
    PROJECT_ROOT
    / "data"
    / "documents"
    / "enterprise_support_sample_docs"
)

PROCESSED_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
)

CHUNKS_FILE = (
    PROCESSED_PATH
    / "chunks.json"
)

ALLOWED_EXTENSIONS = {
    ".pdf",
    ".docx",
    ".txt"
}


def read_chunks() -> list[dict]:
    if not CHUNKS_FILE.exists():
        return []

    with open(
        CHUNKS_FILE,
        "r",
        encoding="utf-8"
    ) as file:
        return json.load(file)


def save_chunks(chunks: list[dict]):
    PROCESSED_PATH.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        CHUNKS_FILE,
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            chunks,
            file,
            ensure_ascii=False,
            indent=2
        )


@router.get("")
def list_documents():
    """
    Return all documents currently present
    in the enterprise knowledge-base folder.
    """

    DOCUMENT_PATH.mkdir(
        parents=True,
        exist_ok=True
    )

    documents = []

    for file_path in DOCUMENT_PATH.iterdir():

        if not file_path.is_file():
            continue

        if file_path.suffix.lower() not in ALLOWED_EXTENSIONS:
            continue

        documents.append({
            "filename": file_path.name,
            "file_type": file_path.suffix.lower().replace(".", ""),
            "size": file_path.stat().st_size
        })

    documents.sort(
        key=lambda item: item["filename"].lower()
    )

    return {
        "documents": documents
    }


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...)
):
    """
    Upload a document and immediately add it
    to the RAG knowledge base.
    """

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Filename is required."
        )

    extension = Path(
        file.filename
    ).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=(
                "Unsupported file type. "
                "Only PDF, DOCX and TXT files "
                "are allowed."
            )
        )

    DOCUMENT_PATH.mkdir(
        parents=True,
        exist_ok=True
    )

    file_path = (
        DOCUMENT_PATH
        / Path(file.filename).name
    )

    try:

        # Save uploaded file
        with open(
            file_path,
            "wb"
        ) as buffer:

            shutil.copyfileobj(
                file.file,
                buffer
            )

        # --------------------------------------------------
        # Extract
        # --------------------------------------------------

        extracted_documents = load_document(
            file_path
        )

        if not extracted_documents:
            raise HTTPException(
                status_code=400,
                detail="The uploaded document contains no readable text."
            )

        # --------------------------------------------------
        # Chunk
        # --------------------------------------------------

        new_chunks = chunk_documents(
            extracted_documents,
            chunk_size=500,
            chunk_overlap=100
        )

        # --------------------------------------------------
        # Embeddings
        # --------------------------------------------------

        embedding_model = EmbeddingModel()

        embedded_documents = (
            embedding_model.embed_documents(
                new_chunks
            )
        )

        # --------------------------------------------------
        # Remove previous version from ChromaDB
        # --------------------------------------------------

        vector_store = VectorStore()

        vector_store.delete_by_source(
            file.filename
        )

        # --------------------------------------------------
        # Store new embeddings
        # --------------------------------------------------

        vector_store.add_documents(
            embedded_documents
        )

        # --------------------------------------------------
        # Update chunks.json
        # --------------------------------------------------

        existing_chunks = read_chunks()

        existing_chunks = [
            chunk
            for chunk in existing_chunks
            if chunk["metadata"].get("source")
            != file.filename
        ]

        existing_chunks.extend(
            new_chunks
        )

        save_chunks(
            existing_chunks
        )

        return {
            "message": "Document uploaded successfully.",
            "filename": file.filename,
            "chunks": len(new_chunks)
        }

    except HTTPException:
        if file_path.exists():
            file_path.unlink()

        raise

    except Exception as error:

        print(
            f"Document upload failed: {error}"
        )

        if file_path.exists():
            file_path.unlink()

        raise HTTPException(
            status_code=500,
            detail="Document processing failed."
        )


@router.delete("/{filename}")
def delete_document(
    filename: str
):
    """
    Remove a document from both the filesystem
    and the RAG index.
    """

    safe_filename = Path(
        filename
    ).name

    file_path = (
        DOCUMENT_PATH
        / safe_filename
    )

    if not file_path.exists():
        raise HTTPException(
            status_code=404,
            detail="Document not found."
        )

    try:

        # --------------------------------------------------
        # Remove from ChromaDB
        # --------------------------------------------------

        vector_store = VectorStore()

        vector_store.delete_by_source(
            safe_filename
        )

        # --------------------------------------------------
        # Remove from chunks.json
        # --------------------------------------------------

        existing_chunks = read_chunks()

        remaining_chunks = [
            chunk
            for chunk in existing_chunks
            if chunk["metadata"].get("source")
            != safe_filename
        ]

        save_chunks(
            remaining_chunks
        )

        # --------------------------------------------------
        # Remove actual file
        # --------------------------------------------------

        file_path.unlink()

        return {
            "message": "Document removed successfully.",
            "filename": safe_filename
        }

    except Exception as error:

        print(
            f"Document deletion failed: {error}"
        )

        raise HTTPException(
            status_code=500,
            detail="Document removal failed."
        )