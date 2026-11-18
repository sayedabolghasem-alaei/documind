from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import chat, documents, health

from app.api.routes import conversations

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Personal Document AI Assistant is starting...")

    yield

    print("Personal Document AI Assistant is shutting down...")


app = FastAPI(
    title="Personal Document AI Assistant",
    description=(
        "An AI-powered assistant for uploading documents "
        "and answering questions using RAG."
    ),
    version="1.0.0",
    lifespan=lifespan
)


# Frontend communication settings.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"]
)


# Register API routes.
app.include_router(
    health.router,
    prefix="/api/v1"
)

app.include_router(
    documents.router,
    prefix="/api/v1"
)

app.include_router(
    chat.router,
    prefix="/api/v1"
)

app.include_router(
    conversations.router,
    prefix="/api/v1/conversations",
    tags=["Conversations"]
)

@app.get("/")
def root():
    return {
        "message": "Personal Document AI Assistant API",
        "version": "1.0.0",
        "docs": "/docs"
    }