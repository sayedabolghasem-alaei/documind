
from fastapi import APIRouter

router = APIRouter(
    prefix="/health",
    tags=["Health"]
)


@router.get("/")
def health_check():
    return {
        "status": "healthy",
        "service": "Personal Document AI Assistant",
        "version": "1.0.0"
    }
