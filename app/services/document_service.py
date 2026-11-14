
import json
import threading
import uuid

from datetime import datetime, timezone
from pathlib import Path

from app.ingestion.ingestion_pipeline import IngestionPipeline


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

        self._pipeline = None

        # Separate locks for initialization and ingestion.
        self._pipeline_init_lock = threading.Lock()
        self._ingestion_lock = threading.Lock()
        self._registry_lock = threading.Lock()

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
        content: bytes
    ) -> dict:

        if not filename:
            raise ValueError("Filename cannot be empty.")

        if not content:
            raise ValueError("Uploaded file is empty.")

        if len(content) > self.MAX_FILE_SIZE:
            raise ValueError(
                "File size exceeds the 20 MB limit."
            )

        original_name = Path(filename).name
        extension = Path(original_name).suffix.lower()

        if extension not in self.ALLOWED_EXTENSIONS:
            raise ValueError(
                "Unsupported file type. Allowed types: PDF, DOCX, TXT."
            )

        file_id = uuid.uuid4().hex
        saved_filename = f"{file_id}{extension}"
        file_path = self.upload_dir / saved_filename

        file_path.write_bytes(content)

        try:
            # Serialize ingestion requests.
            with self._ingestion_lock:
                ingestion_result = self.pipeline.ingest(
                    str(file_path)
                )

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

            documents = self._read_registry()
            documents.append(document_info)
            self._write_registry(documents)

            return {
                "filename": original_name,
                "file_type": extension.lstrip("."),
                "total_documents": ingestion_result["total_documents"],
                "total_chunks": ingestion_result["total_chunks"],
                "stored_chunks": ingestion_result["stored_chunks"],
                "message": "Document uploaded and processed successfully."
            }

        except Exception:
            if file_path.exists():
                file_path.unlink()

            raise

    def list_documents(self) -> list[dict]:
        """Return documents uploaded through the API."""

        return self._read_registry()
