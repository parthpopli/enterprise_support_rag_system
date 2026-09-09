from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
import traceback

from app.rag.hybrid_search import HybridRetriever
from app.rag.generator import Generator


router = APIRouter(
    prefix="/chat",
    tags=["Chat"]
)


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


@router.post("", response_model=ChatResponse)
def chat(request: ChatRequest):

    query = request.query.strip()

    if not query:
        raise HTTPException(
            status_code=400,
            detail="Query cannot be empty."
        )

    try:
        print(f"CHAT REQUEST: {query}")

        # Initialize retriever and generator
        print("Initializing HybridRetriever...")
        hybrid_retriever = HybridRetriever()

        print("Initializing Generator...")
        generator = Generator()

        # Retrieve relevant documents
        print("Running hybrid retrieval...")
        hybrid_results = hybrid_retriever.retrieve(
            query=query,
            top_k=3,
            candidate_k=5
        )

        print(f"Retrieved {len(hybrid_results)} documents")

        # No relevant documents
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

        # Generate answer
        print("Generating answer with Groq...")
        answer = generator.generate(
            query=query,
            documents=hybrid_results
        )

        print("Answer generated successfully")

        # Build sources
        sources = []

        for document in hybrid_results:

            metadata = document.get(
                "metadata",
                {}
            )

            sources.append(
                Source(
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
            )

        return ChatResponse(
            answer=answer,
            sources=sources
        )

    except Exception as error:

        print("====================================")
        print("CHAT REQUEST FAILED")
        print(f"ERROR: {error}")
        traceback.print_exc()
        print("====================================")

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )