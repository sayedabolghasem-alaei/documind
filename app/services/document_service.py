
import json
import threading
import uuid

from datetime import datetime, timezone
from pathlib import Path

from app.ingestion.ingestion_pipeline import IngestionPipeline
from app.database.conversation_repository import ConversationRepository

class DocumentService:

    ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt"}
    MAX_FILE_SIZE = 20 * 1024 * 1024  # 20 MB

    def __init__(self):
        self.project_root = Path(__file__).resolve().parents[2]

        self.upload_dir = (
            self.project_root / "data" / "uploads"
        )

        self.registry_path = (
            self.project_root
            / "data"
            / "processed"
            / "documents.json"
        )

        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)

        # Global ingestion pipeline.
        self._pipeline = None

        # Separate locks for thread safety.
        self._pipeline_init_lock = threading.Lock()
        self._ingestion_lock = threading.Lock()
        self._registry_lock = threading.Lock()
        self._conversation_pipeline_lock = threading.Lock()

        # Conversation database repository.
        self.conversation_repository = ConversationRepository()

        # Cache for conversation-specific ingestion pipelines.
        self._conversation_pipelines = {}

        # Initialize document registry.
        if not self.registry_path.exists():
            self.registry_path.write_text(
                "[]",
                encoding="utf-8"
            )

    @property
    def pipeline(self):
        """Initialize the ingestion pipeline only once."""

        if self._pipeline is None:
            with self._pipeline_init_lock:
                if self._pipeline is None:
                    self._pipeline = IngestionPipeline()

        return self._pipeline

    def get_conversation_pipeline(
        self,
        conversation_id: str
    ) -> IngestionPipeline:

        with self._conversation_pipeline_lock:

            if conversation_id not in self._conversation_pipelines:

                collection_name = (
                    f"conversation_{conversation_id.replace('-', '_')}"
                )

                self._conversation_pipelines[conversation_id] = (
                    IngestionPipeline(
                        collection_name=collection_name,
                        enable_graph=False
                    )
                )

            return self._conversation_pipelines[conversation_id]

    def get_conversation_pipeline(
        self,
        conversation_id: str
    ) -> IngestionPipeline:

        with self._conversation_pipeline_lock:

            if conversation_id not in self._conversation_pipelines:

                collection_name = f"conversation_{conversation_id.replace('-', '_')}"

                self._conversation_pipelines[conversation_id] = (
                    IngestionPipeline(
                        collection_name=collection_name,
                        enable_graph=False
                    )
                )

            return self._conversation_pipelines[conversation_id]

    def _read_registry(self) -> list[dict]:

        with self._registry_lock:
            try:
                data = json.loads(
                    self.registry_path.read_text(
                        encoding="utf-8"
                    )
                )

                return data if isinstance(data, list) else []

            except (json.JSONDecodeError, OSError):
                return []

    def _write_registry(self, documents: list[dict]) -> None:

        with self._registry_lock:
            self.registry_path.write_text(
                json.dumps(
                    documents,
                    ensure_ascii=False,
                    indent=4
                ),
                encoding="utf-8"
            )

    def upload_document(
        self,
        filename: str,
        content: bytes,
        conversation_id: str | None = None
    ) -> dict:

        # Validate filename.
        if not filename:
            raise ValueError("Filename is required.")

        original_name = Path(filename).name

        if not original_name:
            raise ValueError("Invalid filename.")

        # Validate file content.
        if not content:
            raise ValueError("File is empty.")

        if len(content) > self.MAX_FILE_SIZE:
            raise ValueError("File size exceeds the 20 MB limit.")

        # Validate file extension.
        extension = Path(original_name).suffix.lower()

        if extension not in self.ALLOWED_EXTENSIONS:
            raise ValueError(
                "Unsupported file type. Allowed formats: PDF, DOCX, TXT."
            )

        # Validate conversation and select ingestion pipeline.
        if conversation_id is not None:

            conversation = self.conversation_repository.get_conversation(
                conversation_id
            )

            if conversation is None:
                raise ValueError("Conversation not found.")

            ingestion_pipeline = self.get_conversation_pipeline(
                conversation_id
            )

        else:
            ingestion_pipeline = self.pipeline

        # Generate unique file ID.
        file_id = uuid.uuid4().hex

        saved_filename = f"{file_id}{extension}"

        file_path = self.upload_dir / saved_filename

        # Save uploaded file.
        file_path.write_bytes(content)

        try:

            # Process document.
            with self._ingestion_lock:

                ingestion_result = ingestion_pipeline.ingest(
                    str(file_path),
                    conversation_id=conversation_id
                )

            # Create document information.
            uploaded_at = datetime.now(
                timezone.utc
            ).isoformat()

            document_info = {
                "id": file_id,
                "filename": original_name,
                "stored_filename": saved_filename,
                "file_type": extension.lstrip("."),
                "uploaded_at": uploaded_at,
                "total_chunks": ingestion_result["total_chunks"],
                "stored_chunks": ingestion_result["stored_chunks"]
            }

            # Register document under its conversation.
            if conversation_id is not None:

                self.conversation_repository.add_document(
                    conversation_id=conversation_id,
                    document_id=file_id,
                    filename=original_name,
                    stored_filename=saved_filename
                )

            # Update global document registry.
            with self._registry_lock:

                docs = self._read_registry()
                docs.append(document_info)
                self._write_registry(docs)

            # Return upload result.
            return {
                "filename": original_name,
                "file_type": extension.lstrip("."),
                "total_documents": len(docs),
                "total_chunks": ingestion_result["total_chunks"],
                "stored_chunks": ingestion_result["stored_chunks"],
                "message": "Document uploaded and processed successfully."
            }

        except Exception:

            # Remove uploaded file if processing fails.
            if file_path.exists():
                file_path.unlink()

            raise

    def list_documents(self) -> list[dict]:
        """Return documents uploaded through the API."""

        return self._read_registry()
