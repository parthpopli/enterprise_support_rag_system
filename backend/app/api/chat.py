from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.rag.hybrid_search import HybridRetriever
from app.rag.reranker import Reranker
from app.rag.generator import Generator


router = APIRouter(
    prefix="/chat",
    tags=["Chat"]
)


# ---------------------------------------------------------
# REQUEST / RESPONSE SCHEMAS
# ---------------------------------------------------------

class ChatRequest(BaseModel):
    query: str = Field(
        ...,
        min_length=1,
        max_length=2000
    )


class Source(BaseModel):
    file: str
    page: int | str
    chunk: int | str


class ChatResponse(BaseModel):
    answer: str
    sources: list[Source]


# ---------------------------------------------------------
# CHAT ENDPOINT
# ---------------------------------------------------------

@router.post("", response_model=ChatResponse)
def chat(request: ChatRequest):

    # Clean the user's question
    query = request.query.strip()

    # Validate empty query
    if not query:
        raise HTTPException(
            status_code=400,
            detail="Query cannot be empty."
        )

    try:

        # -------------------------------------------------
        # 1. INITIALIZE RAG COMPONENTS
        # -------------------------------------------------

        hybrid_retriever = HybridRetriever()
        reranker = Reranker()
        generator = Generator()

        # -------------------------------------------------
        # 2. HYBRID RETRIEVAL
        # -------------------------------------------------

        hybrid_results = hybrid_retriever.retrieve(
            query=query,
            top_k=5,
            candidate_k=5
        )

        # -------------------------------------------------
        # 3. HANDLE NO RETRIEVED DOCUMENTS
        # -------------------------------------------------

        if not hybrid_results:
            return ChatResponse(
                answer=(
                    "I don't have enough information in the "
                    "available enterprise documentation to "
                    "answer that question. Please contact "
                    "IT Support for further assistance."
                ),
                sources=[]
            )

        # -------------------------------------------------
        # 4. RERANK RETRIEVED DOCUMENTS
        # -------------------------------------------------

        final_documents = reranker.rerank(
            query=query,
            documents=hybrid_results,
            top_k=3
        )

        # -------------------------------------------------
        # 5. GENERATE GROUNDED ANSWER
        # -------------------------------------------------

        answer = generator.generate(
            query=query,
            documents=final_documents
        )

        # -------------------------------------------------
        # 6. BUILD STRUCTURED SOURCES
        # -------------------------------------------------

        sources = []

        for document in final_documents:

            metadata = document.get(
                "metadata",
                {}
            )

            source = Source(
                file=metadata.get(
                    "source",
                    "Unknown document"
                ),
                page=metadata.get(
                    "page",
                    "Unknown"
                ),
                chunk=metadata.get(
                    "chunk_index",
                    "Unknown"
                )
            )

            sources.append(source)

        # -------------------------------------------------
        # 7. RETURN ANSWER + SOURCES
        # -------------------------------------------------

        return ChatResponse(
            answer=answer,
            sources=sources
        )

    except Exception as error:

        print(
            f"Chat request failed: {error}"
        )

        raise HTTPException(
            status_code=500,
            detail="Failed to process the support request."
        )