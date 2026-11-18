
import json
import threading

from pathlib import Path

from app.database.conversation_repository import ConversationRepository
from app.generation.rag_pipeline import RAGPipeline


class ChatService:

    def __init__(self):
        self._rag_pipeline = None
        self._pipeline_lock = threading.Lock()

        self.conversation_repository = ConversationRepository()

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

            pages = self._extract_pages(metadata)

            source_map[stored_name]["pages"].update(pages)

            if distance is not None:
                current_distance = source_map[stored_name]["distance"]

                if (
                    current_distance is None
                    or distance < current_distance
                ):
                    source_map[stored_name]["distance"] = distance

        return [
            {
                "filename": source["filename"],
                "pages": sorted(source["pages"]),
                "distance": source["distance"]
            }
            for source in source_map.values()
        ]

    def chat(
        self,
        query: str,
        conversation_id: str | None = None
    ) -> dict:

        query = query.strip()

        if not query:
            raise ValueError("Query cannot be empty.")

        # Step 1: Create or validate the conversation.
        if conversation_id is None:

            title = query[:60]

            if len(query) > 60:
                title += "..."

            conversation_id = (
                self.conversation_repository.create_conversation(title)
            )

        else:
            conversation = (
                self.conversation_repository.get_conversation(
                    conversation_id
                )
            )

            if conversation is None:
                raise ValueError("Conversation not found.")

            # Set the title from the first user message.
            messages = self.conversation_repository.get_messages(
                conversation_id
            )

            if not messages and conversation["title"] == "New Chat":

                title = query[:60]

                if len(query) > 60:
                    title += "..."

                self.conversation_repository.rename_conversation(
                    conversation_id,
                    title
                )

        # Step 2: Save the user message.
        self.conversation_repository.save_message(
            conversation_id,
            "user",
            query
        )

        # Step 3: Generate the RAG response.
        result = self.rag_pipeline.run(
            query=query,
            top_k=3
        )

        # Step 4: Extract retrieved documents.
        retrieved_documents = result.get(
            "retrieved_documents",
            []
        )

        # Step 5: Build source information.
        sources = self._build_sources(
            retrieved_documents
        )

        # Step 6: Save the assistant response.
        answer = result.get(
            "answer",
            "No answer was generated."
        )

        self.conversation_repository.save_message(
            conversation_id,
            "assistant",
            answer
        )

        # Step 7: Return the response.
        return {
            "answer": answer,
            "sources": sources,
            "conversation_id": conversation_id
        }
