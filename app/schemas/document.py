
from datetime import datetime

from pydantic import BaseModel, Field


class DocumentUploadResponse(BaseModel):
    filename: str
    file_type: str
    total_documents: int
    total_chunks: int
    stored_chunks: int
    message: str


class DocumentInfo(BaseModel):
    filename: str
    file_type: str
    uploaded_at: datetime | None = None
    total_chunks: int = 0


class DocumentListResponse(BaseModel):
    documents: list[DocumentInfo] = Field(default_factory=list)
    total: int
