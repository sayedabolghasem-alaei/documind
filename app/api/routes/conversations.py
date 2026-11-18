from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.database.conversation_repository import ConversationRepository


router = APIRouter()
repository = ConversationRepository()


class ConversationCreate(BaseModel):
    title: str = "New Chat"


class ConversationRename(BaseModel):
    title: str = Field(min_length=1, max_length=100)


@router.post("/")
def create_conversation(request: ConversationCreate):

    title = request.title.strip() or "New Chat"

    conversation_id = repository.create_conversation(title)

    return {
        "id": conversation_id,
        "title": title
    }


@router.get("/")
def get_conversations():

    return repository.get_conversations()


@router.get("/{conversation_id}")
def get_conversation(conversation_id: str):

    conversation = repository.get_conversation(conversation_id)

    if not conversation:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found."
        )

    messages = repository.get_messages(conversation_id)

    return {
        "conversation": conversation,
        "messages": messages
    }


@router.patch("/{conversation_id}")
def rename_conversation(
    conversation_id: str,
    request: ConversationRename
):

    title = request.title.strip()

    if not title:
        raise HTTPException(
            status_code=400,
            detail="Title cannot be empty."
        )

    updated = repository.rename_conversation(
        conversation_id,
        title
    )

    if not updated:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found."
        )

    return {
        "message": "Conversation renamed successfully.",
        "title": title
    }


@router.delete("/{conversation_id}")
def delete_conversation(conversation_id: str):

    deleted = repository.delete_conversation(conversation_id)

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found."
        )

    return {
        "message": "Conversation deleted successfully."
    }