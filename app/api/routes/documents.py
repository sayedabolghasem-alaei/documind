from fastapi import (
    APIRouter,
    UploadFile,
    File,
    Form,
    HTTPException,
    Depends
)

from app.schemas.document import (
    DocumentUploadResponse,
    DocumentListResponse,
    DocumentInfo
)

from starlette.concurrency import run_in_threadpool

from app.api.dependencies import get_document_service
from app.services.document_service import DocumentService


router = APIRouter(
    prefix="/documents",
    tags=["Documents"]
)


@router.post(
    "/upload",
    response_model=DocumentUploadResponse
)
async def upload_document(
    file: UploadFile = File(...),
    conversation_id: str | None = Form(default=None),
    service: DocumentService = Depends(get_document_service)
):
    content = await file.read()

    try:
        result = await run_in_threadpool(
            service.upload_document,
            file.filename or "",
            content,
            conversation_id
        )

        return result

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Document upload failed: {str(error)}"
        )

    finally:
        await file.close()


@router.get(
    "/",
    response_model=DocumentListResponse
)
def list_documents(
    service: DocumentService = Depends(get_document_service)
):
    try:
        documents = service.list_documents()

        document_items = [
            DocumentInfo(
                filename=document["filename"],
                file_type=document["file_type"],
                uploaded_at=document["uploaded_at"],
                total_chunks=document["total_chunks"]
            )
            for document in documents
        ]

        return DocumentListResponse(
            documents=document_items,
            total=len(document_items)
        )

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="An error occurred while retrieving documents."
        )