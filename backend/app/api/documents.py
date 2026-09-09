
from pathlib import Path
import json
import os
import shutil
import urllib.request
import urllib.error

from fastapi import APIRouter, UploadFile, File, HTTPException

from app.rag.ingestion import load_document
from app.rag.chunking import chunk_documents
from app.rag.embeddings import EmbeddingModel
from app.rag.vector_store import VectorStore


router = APIRouter(
    prefix="/documents",
    tags=["Documents"]
)


# ============================================================
# PROJECT PATHS
# ============================================================

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


# ============================================================
# CONFIGURATION
# ============================================================

ALLOWED_EXTENSIONS = {
    ".pdf",
    ".docx",
    ".txt"
}

# Maximum upload size: 10 MB
MAX_FILE_SIZE = 10 * 1024 * 1024


# ============================================================
# RENDER RESET
# ============================================================

def reset_render_service():
    """
    Delete all uploaded/processed RAG data and
    trigger a fresh Render deployment.

    This is used when document processing fails.
    """

    print("====================================")
    print("RESETTING RENDER SERVICE")
    print("====================================")

    # --------------------------------------------------------
    # 1. Delete uploaded documents
    # --------------------------------------------------------

    paths_to_delete = [
        DOCUMENT_PATH,
        PROCESSED_PATH,
        PROJECT_ROOT / "vector_store",
    ]

    for path in paths_to_delete:

        if path.exists():

            try:
                shutil.rmtree(path)

                print(
                    f"Deleted: {path}"
                )

            except Exception as error:

                print(
                    f"Failed to delete {path}: {error}"
                )

    # --------------------------------------------------------
    # 2. Recreate required directories
    # --------------------------------------------------------

    DOCUMENT_PATH.mkdir(
        parents=True,
        exist_ok=True
    )

    PROCESSED_PATH.mkdir(
        parents=True,
        exist_ok=True
    )

    (
        PROJECT_ROOT / "vector_store"
    ).mkdir(
        parents=True,
        exist_ok=True
    )

    print(
        "Required directories recreated."
    )

    # --------------------------------------------------------
    # 3. Get Render credentials
    # --------------------------------------------------------

    render_api_key = os.getenv(
        "RENDER_API_KEY"
    )

    render_service_id = os.getenv(
        "RENDER_SERVICE_ID"
    )

    if not render_api_key:

        print(
            "RENDER_API_KEY is missing."
        )

        return

    if not render_service_id:

        print(
            "RENDER_SERVICE_ID is missing."
        )

        return

    # --------------------------------------------------------
    # 4. Trigger Render deployment
    # --------------------------------------------------------

    url = (
        "https://api.render.com/v1/services/"
        f"{render_service_id}/deploys"
    )

    payload = json.dumps({
        "clearCache": "do_not_clear"
    }).encode("utf-8")

    request = urllib.request.Request(
        url,
        data=payload,
        method="POST",
        headers={
            "Authorization":
                f"Bearer {render_api_key}",

            "Accept":
                "application/json",

            "Content-Type":
                "application/json",
        }
    )

    try:

        with urllib.request.urlopen(
            request,
            timeout=10
        ) as response:

            response_body = (
                response.read()
                .decode("utf-8")
            )

            print(
                "Render deploy response:",
                response.status
            )

            print(
                response_body
            )

            if 200 <= response.status < 300:

                print(
                    "Render redeployment triggered."
                )

    except urllib.error.HTTPError as error:

        print(
            "Render deployment failed."
        )

        print(
            "Status:",
            error.code
        )

        try:

            print(
                error.read()
                .decode("utf-8")
            )

        except Exception:
            pass

    except Exception as error:

        print(
            "Failed to trigger Render deployment:"
        )

        print(error)


# ============================================================
# CHUNK HELPERS
# ============================================================

def read_chunks() -> list[dict]:

    if not CHUNKS_FILE.exists():
        return []

    with open(
        CHUNKS_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


def save_chunks(
    chunks: list[dict]
):

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


# ============================================================
# LIST DOCUMENTS
# ============================================================

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

        if (
            file_path.suffix.lower()
            not in ALLOWED_EXTENSIONS
        ):
            continue

        documents.append({
            "filename": file_path.name,
            "file_type": (
                file_path.suffix
                .lower()
                .replace(".", "")
            ),
            "size": file_path.stat().st_size
        })

    documents.sort(
        key=lambda item:
        item["filename"].lower()
    )

    return {
        "documents": documents
    }


# ============================================================
# UPLOAD DOCUMENT
# ============================================================

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...)
):

    """
    Upload a document and immediately add it
    to the RAG knowledge base.

    If document processing fails:

    1. Delete uploaded documents.
    2. Delete processed chunks.
    3. Delete ChromaDB vector data.
    4. Trigger a fresh Render deployment.
    """

    # --------------------------------------------------------
    # Validate filename
    # --------------------------------------------------------

    if not file.filename:

        raise HTTPException(
            status_code=400,
            detail="Filename is required."
        )

    # --------------------------------------------------------
    # Validate extension
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Create directories
    # --------------------------------------------------------

    DOCUMENT_PATH.mkdir(
        parents=True,
        exist_ok=True
    )

    PROCESSED_PATH.mkdir(
        parents=True,
        exist_ok=True
    )

    # --------------------------------------------------------
    # Secure filename
    # --------------------------------------------------------

    safe_filename = Path(
        file.filename
    ).name

    file_path = (
        DOCUMENT_PATH
        / safe_filename
    )

    try:

        # ====================================================
        # 1. SAVE UPLOADED FILE
        # ====================================================

        total_size = 0

        with open(
            file_path,
            "wb"
        ) as buffer:

            while True:

                chunk = await file.read(
                    1024 * 1024
                )

                if not chunk:
                    break

                total_size += len(chunk)

                # Prevent huge uploads from
                # consuming the Render instance.

                if total_size > MAX_FILE_SIZE:

                    raise HTTPException(
                        status_code=413,
                        detail=(
                            "File is too large. "
                            "Maximum allowed size is 10 MB."
                        )
                    )

                buffer.write(chunk)

        print(
            f"Uploaded {safe_filename} "
            f"({total_size / (1024 * 1024):.2f} MB)"
        )

        # ====================================================
        # 2. EXTRACT TEXT
        # ====================================================

        print(
            "Extracting document text..."
        )

        extracted_documents = load_document(
            file_path
        )

        if not extracted_documents:

            raise HTTPException(
                status_code=400,
                detail=(
                    "The uploaded document "
                    "contains no readable text."
                )
            )

        # ====================================================
        # 3. CHUNK DOCUMENT
        # ====================================================

        print(
            "Creating document chunks..."
        )

        new_chunks = chunk_documents(
            extracted_documents,
            chunk_size=500,
            chunk_overlap=100
        )

        if not new_chunks:

            raise HTTPException(
                status_code=400,
                detail=(
                    "No usable chunks were created "
                    "from the document."
                )
            )

        print(
            f"Created {len(new_chunks)} chunks."
        )

        # ====================================================
        # 4. CREATE EMBEDDINGS
        # ====================================================

        print(
            "Creating embeddings..."
        )

        embedding_model = EmbeddingModel()

        embedded_documents = (
            embedding_model.embed_documents(
                new_chunks
            )
        )

        print(
            "Embeddings created."
        )

        # ====================================================
        # 5. UPDATE CHROMADB
        # ====================================================

        print(
            "Updating vector store..."
        )

        vector_store = VectorStore()

        vector_store.delete_by_source(
            safe_filename
        )

        vector_store.add_documents(
            embedded_documents
        )

        print(
            "Vector store updated."
        )

        # ====================================================
        # 6. UPDATE chunks.json
        # ====================================================

        print(
            "Updating chunks.json..."
        )

        existing_chunks = read_chunks()

        existing_chunks = [
            chunk
            for chunk in existing_chunks
            if chunk.get(
                "metadata",
                {}
            ).get("source")
            != safe_filename
        ]

        existing_chunks.extend(
            new_chunks
        )

        save_chunks(
            existing_chunks
        )

        print(
            "chunks.json updated."
        )

        # ====================================================
        # 7. SUCCESS
        # ====================================================

        return {
            "message":
                "Document uploaded successfully.",

            "filename":
                safe_filename,

            "chunks":
                len(new_chunks)
        }

    # ========================================================
    # EXPECTED HTTP ERROR
    # ========================================================

    except HTTPException as error:

        print(
            "Document upload rejected:"
        )

        print(
            error.detail
        )

        # Delete only the uploaded file
        # for normal validation errors.

        if file_path.exists():

            try:
                file_path.unlink()

            except Exception as cleanup_error:

                print(
                    "Failed to remove uploaded file:",
                    cleanup_error
                )

        raise

    # ========================================================
    # UNEXPECTED PROCESSING ERROR
    # ========================================================

    except MemoryError as error:

        print(
            "===================================="
        )

        print(
            "MEMORY ERROR DURING DOCUMENT UPLOAD"
        )

        print(
            error
        )

        print(
            "===================================="
        )

        # Delete everything and trigger
        # a fresh Render deployment.

        reset_render_service()

        raise HTTPException(
            status_code=500,
            detail=(
                "Document processing exceeded "
                "available memory. The RAG data "
                "was cleared and the service is "
                "being restarted."
            )
        )

    except Exception as error:

        print(
            "===================================="
        )

        print(
            "DOCUMENT PROCESSING FAILED"
        )

        print(
            f"ERROR: {error}"
        )

        print(
            "===================================="
        )

        # Delete everything and trigger
        # a fresh Render deployment.

        reset_render_service()

        raise HTTPException(
            status_code=500,
            detail=(
                "Document processing failed. "
                "The RAG data was cleared and "
                "the service is being restarted."
            )
        )


# ============================================================
# DELETE DOCUMENT
# ============================================================

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

        # ----------------------------------------------------
        # Remove from ChromaDB
        # ----------------------------------------------------

        vector_store = VectorStore()

        vector_store.delete_by_source(
            safe_filename
        )

        # ----------------------------------------------------
        # Remove from chunks.json
        # ----------------------------------------------------

        existing_chunks = read_chunks()

        remaining_chunks = [
            chunk
            for chunk in existing_chunks
            if chunk.get(
                "metadata",
                {}
            ).get("source")
            != safe_filename
        ]

        save_chunks(
            remaining_chunks
        )

        # ----------------------------------------------------
        # Remove actual file
        # ----------------------------------------------------

        file_path.unlink()

        return {
            "message":
                "Document removed successfully.",

            "filename":
                safe_filename
        }

    except Exception as error:

        print(
            f"Document deletion failed: {error}"
        )

        raise HTTPException(
            status_code=500,
            detail="Document removal failed."
        )

