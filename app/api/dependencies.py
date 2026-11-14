from functools import lru_cache

from app.services.document_service import DocumentService
from app.services.chat_service import ChatService


@lru_cache
def get_document_service() -> DocumentService:
    return DocumentService()


@lru_cache
def get_chat_service() -> ChatService:
    return ChatService()