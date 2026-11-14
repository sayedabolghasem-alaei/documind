
import json
import threading
import uuid

from pathlib import Path

from app.generation.rag_pipeline import RAGPipeline


class ChatService:

    def __init__(self):
        self._rag_pipeline = None
        self._pipeline_lock = threading.Lock()

        self.project_root = Path(__file__).resolve().parents[2]

        self.registry_path = (
            self.project_root
            / "data"
            / "processed"
            / "documents.json"
        )

    @property
    def rag_pipeline(self):
        """Initialize the RAG pipeline only once."""

        if self._rag_pipeline is None:
            with self._pipeline_lock:
                if self._rag_pipeline is None:
                    self._rag_pipeline = RAGPipeline()

        return self._rag_pipeline

    def _get_filename_map(self) -> dict:
        """Map stored filenames to their original filenames."""

        if not self.registry_path.exists():
            return {}

        try:
            documents = json.loads(
                self.registry_path.read_text(encoding="utf-8")
            )

            return {
                document["stored_filename"]: document["filename"]
                for document in documents
                if "stored_filename" in document
                and "filename" in document
            }

        except (json.JSONDecodeError, OSError, TypeError):
            return {}

    @staticmethod
    def _extract_pages(metadata: dict) -> list[int]:
        """Extract unique page numbers from document metadata."""

        raw_pages = metadata.get("pages")

        if raw_pages is None:
            raw_pages = metadata.get("page")

        if raw_pages is None:
            return []

        if not isinstance(raw_pages, list):
            raw_pages = str(raw_pages).split(",")

        pages = set()

        for page in raw_pages:
            try:
                page_number = int(str(page).strip())

                if page_number > 0:
                    pages.add(page_number)

            except (ValueError, TypeError):
                continue

        return sorted(pages)

    def _build_sources(
        self,
        retrieved_documents: list[dict]
    ) -> list[dict]:
        """Build source information from retrieved documents."""

        filename_map = self._get_filename_map()

        source_map = {}

        for document in retrieved_documents:

            metadata = document.get("metadata", {})

            stored_name = Path(
                str(metadata.get("source", "Unknown"))
            ).name

            original_name = filename_map.get(
                stored_name,
                stored_name
            )

            distance = document.get("distance")

            if stored_name not in source_map:
                source_map[stored_name] = {
                    "filename": original_name,
                    "pages": set(),
                    "distance": distance
                }

            # Collect page numbers.
            pages = self._extract_pages(metadata)

            source_map[stored_name]["pages"].update(pages)

            # Keep the best retrieval distance.
            if distance is not None:
                current_distance = source_map[stored_name]["distance"]

                if (
                    current_distance is None
                    or distance < current_distance
                ):
                    source_map[stored_name]["distance"] = distance

        sources = []

        for source in source_map.values():
            sources.append({
                "filename": source["filename"],
                "pages": sorted(source["pages"]),
                "distance": source["distance"]
            })

        return sources

    def chat(
        self,
        query: str,
        conversation_id: str | None = None
    ) -> dict:

        query = query.strip()

        if not query:
            raise ValueError("Query cannot be empty.")

        if conversation_id is None:
            conversation_id = str(uuid.uuid4())

        # Step 1: Run the RAG pipeline.
        result = self.rag_pipeline.run(
            query=query,
            top_k=3
        )

        # Step 2: Get retrieved documents.
        retrieved_documents = result.get(
            "retrieved_documents",
            []
        )

        # Step 3: Build source information.
        sources = self._build_sources(
            retrieved_documents
        )

        # Step 4: Return the final response.
        return {
            "answer": result.get(
                "answer",
                "No answer was generated."
            ),
            "sources": sources,
            "conversation_id": conversation_id
        }
