
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    query: str = Field(
        min_length=1,
        max_length=5000,
        description="User question"
    )

    conversation_id: str | None = None


class SourceInfo(BaseModel):
    filename: str
    pages: list[int] = Field(default_factory=list)
    distance: float | None = None


class ChatResponse(BaseModel):
    answer: str
    sources: list[SourceInfo] = Field(default_factory=list)
    conversation_id: str | None = None
