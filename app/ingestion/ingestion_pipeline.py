
import hashlib
import networkx as nx

from app.ingestion.document_loader import DocumentLoader
from app.ingestion.sentence_chunker import SentenceChunker
from app.embedding.embedding_model import EmbeddingModel
from app.retrieval.vector_store import VectorStore

from app.graph.entity_extractor import EntityExtractor
from app.graph.relationship_extractor import RelationshipExtractor
from app.graph.knowledge_graph import KnowledgeGraph
from app.graph.graph_storage import GraphStorage


class IngestionPipeline:


    def __init__(
        self,
        collection_name: str = "documents",
        enable_graph: bool = True
    ):

        self.document_loader = DocumentLoader()

        self.chunker = SentenceChunker(
            chunk_size=5,
            chunk_overlap=1
        )

        self.embedding_model = EmbeddingModel()

        self.vector_store = VectorStore(
            collection_name=collection_name
        )

        self.enable_graph = enable_graph

        # Graph RAG components
        self.entity_extractor = EntityExtractor()
        self.relationship_extractor = RelationshipExtractor()
        self.knowledge_graph = KnowledgeGraph()
        self.graph_storage = GraphStorage()


    # --------------------------------------------------
    # Chunk ID
    # --------------------------------------------------

    def _create_chunk_id(self, chunk: dict) -> str:

        normalized_text = " ".join(
            chunk["text"].split()
        )

        return hashlib.sha256(
            normalized_text.encode("utf-8")
        ).hexdigest()

    # --------------------------------------------------
    # Metadata Helpers
    # --------------------------------------------------

    def _get_metadata_values(self, value) -> list[str]:

        if value is None:
            return []

        if isinstance(value, list):
            values = value
        else:
            values = str(value).split(",")

        return list(dict.fromkeys(
            str(item).strip()
            for item in values
            if str(item).strip()
        ))

    def _merge_metadata(
        self,
        existing: dict,
        incoming: dict
    ) -> dict:

        merged = dict(existing)

        # Merge source filenames
        sources = list(dict.fromkeys(
            self._get_metadata_values(existing.get("sources"))
            + self._get_metadata_values(existing.get("source"))
            + self._get_metadata_values(incoming.get("sources"))
            + self._get_metadata_values(incoming.get("source"))
        ))

        merged["sources"] = sources
        merged["source"] = ", ".join(sources)

        # Merge file types
        file_types = list(dict.fromkeys(
            self._get_metadata_values(existing.get("file_types"))
            + self._get_metadata_values(existing.get("file_type"))
            + self._get_metadata_values(incoming.get("file_types"))
            + self._get_metadata_values(incoming.get("file_type"))
        ))

        merged["file_types"] = file_types
        merged["file_type"] = ", ".join(file_types)

        # Merge page numbers
        pages = list(dict.fromkeys(
            self._get_metadata_values(existing.get("pages"))
            + self._get_metadata_values(existing.get("page"))
            + self._get_metadata_values(incoming.get("pages"))
            + self._get_metadata_values(incoming.get("page"))
        ))

        merged["pages"] = pages

        # Merge chunk indexes
        chunk_indices = list(dict.fromkeys(
            self._get_metadata_values(existing.get("chunk_indices"))
            + self._get_metadata_values(existing.get("chunk_index"))
            + self._get_metadata_values(incoming.get("chunk_indices"))
            + self._get_metadata_values(incoming.get("chunk_index"))
        ))

        merged["chunk_indices"] = chunk_indices

        return merged

    def _merge_duplicate_chunks(self, chunks: list) -> list:

        unique_chunks = {}

        for chunk in chunks:

            chunk_id = self._create_chunk_id(chunk)

            if chunk_id not in unique_chunks:

                unique_chunks[chunk_id] = {
                    "text": chunk["text"],
                    "metadata": dict(chunk["metadata"])
                }

            else:

                existing_metadata = unique_chunks[
                    chunk_id
                ]["metadata"]

                unique_chunks[chunk_id]["metadata"] = (
                    self._merge_metadata(
                        existing_metadata,
                        chunk["metadata"]
                    )
                )

        return list(unique_chunks.values())

    def _prepare_metadata(self, metadata: dict) -> dict:

        prepared_metadata = {}

        for key, value in metadata.items():

            if value is None:
                continue

            if isinstance(value, list):
                value = ",".join(
                    str(item) for item in value
                )

            prepared_metadata[key] = value

        return prepared_metadata

    # --------------------------------------------------
    # Graph RAG Processing
    # --------------------------------------------------

    def _process_graph(self, chunks: list) -> dict:

        # Step 1: Combine chunk texts
        document_text = "\n".join(
            chunk["text"]
            for chunk in chunks
        )

        # Step 2: Extract entities
        entities = self.entity_extractor.extract(
            document_text
        )

        # Step 3: Extract relationships
        relationships = self.relationship_extractor.extract(
            text=document_text,
            entities=entities
        )

        # Step 4: Build the new knowledge graph
        new_graph = self.knowledge_graph.build(
            entities=entities,
            relationships=relationships
        )

        # Step 5: Load the existing graph
        if self.graph_storage.exists():
            existing_graph = self.graph_storage.load()
        else:
            existing_graph = nx.DiGraph()

        # Step 6: Merge old and new graphs
        combined_graph = nx.compose(
            existing_graph,
            new_graph
        )

        # Step 7: Save the combined graph
        self.graph_storage.save(combined_graph)

        return {
            "total_entities": combined_graph.number_of_nodes(),
            "total_relationships": combined_graph.number_of_edges(),
            "new_entities": len(entities),
            "new_relationships": len(relationships)
        }

    # --------------------------------------------------
    # Main Ingestion Pipeline
    # --------------------------------------------------

    def ingest(
        self,
        file_path: str,
        conversation_id: str | None = None
    ) -> dict:

        # Step 1: Load document
        documents = self.document_loader.load(file_path)

        # Step 2: Create chunks
        chunks = self.chunker.chunk_documents(documents)

        if not chunks:
            return {
                "source": file_path,
                "total_documents": len(documents),
                "total_chunks": 0,
                "stored_chunks": 0
            }

        # Step 3: Remove duplicate chunks
        unique_chunks = self._merge_duplicate_chunks(chunks)

        # Attach conversation scope to every chunk.
        if conversation_id is not None:

            for chunk in unique_chunks:
                chunk["metadata"]["conversation_id"] = conversation_id

        # Step 4: Extract unique chunk texts
        texts = [
            chunk["text"]
            for chunk in unique_chunks
        ]

        # Step 5: Generate embeddings
        embeddings = self.embedding_model.encode(texts)

        # Step 6: Prepare IDs and metadata
        ids = [
            self._create_chunk_id(chunk)
            for chunk in unique_chunks
        ]

        metadatas = [
            self._prepare_metadata(chunk["metadata"])
            for chunk in unique_chunks
        ]

        # Step 7: Merge metadata with existing ChromaDB records
        existing_data = self.vector_store.collection.get(
            ids=ids,
            include=["metadatas"]
        )

        existing_metadata = dict(zip(
            existing_data["ids"],
            existing_data["metadatas"]
        ))

        for index, chunk_id in enumerate(ids):

            if chunk_id in existing_metadata:

                metadatas[index] = self._prepare_metadata(
                    self._merge_metadata(
                        existing_metadata[chunk_id],
                        metadatas[index]
                    )
                )

        # Step 8: Store unique chunks
        self.vector_store.add_documents(
            ids=ids,
            texts=texts,
            embeddings=embeddings,
            metadatas=metadatas
        )

        # Step 9: Process Graph RAG
        graph_info = None

        if self.enable_graph:
            graph_info = self._process_graph(unique_chunks)

        # Step 10: Return ingestion information
        return {
            "source": file_path,
            "total_documents": len(documents),
            "total_chunks": len(chunks),
            "stored_chunks": len(unique_chunks),
            "graph": graph_info
        }
