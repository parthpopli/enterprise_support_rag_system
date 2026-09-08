from pydantic import BaseModel


class ChatRequest(BaseModel):
    query: str


class Source(BaseModel):
    file: str
    page: int | str
    chunk: int | str
    score: float | str


class ChatResponse(BaseModel):
    answer: str
    sources: list[Source]