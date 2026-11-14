
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

    def __init__(self):

        self.document_loader = DocumentLoader()

        self.chunker = SentenceChunker(
            chunk_size=5,
            chunk_overlap=1
        )

        self.embedding_model = EmbeddingModel()

        self.vector_store = VectorStore(
            collection_name="documents"
        )

        # Graph RAG components
        self.entity_extractor = EntityExtractor()
        self.relationship_extractor = RelationshipExtractor()
        self.knowledge_graph = KnowledgeGraph()
        self.graph_storage = GraphStorage()

    def _create_chunk_id(self, chunk: dict) -> str:

        metadata = chunk["metadata"]

        unique_content = (
            f'{metadata.get("source", "")}|'
            f'{metadata.get("file_type", "")}|'
            f'{metadata.get("chunk_index", "")}|'
            f'{chunk["text"]}'
        )

        return hashlib.sha256(
            unique_content.encode("utf-8")
        ).hexdigest()

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

    def ingest(self, file_path: str) -> dict:

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

        # Step 3: Extract chunk texts
        texts = [
            chunk["text"]
            for chunk in chunks
        ]

        # Step 4: Generate embeddings
        embeddings = self.embedding_model.encode(texts)

        # Step 5: Prepare IDs and metadata
        ids = [
            self._create_chunk_id(chunk)
            for chunk in chunks
        ]

        metadatas = [
            self._prepare_metadata(chunk["metadata"])
            for chunk in chunks
        ]

        # Step 6: Store chunks in ChromaDB
        self.vector_store.add_documents(
            ids=ids,
            texts=texts,
            embeddings=embeddings,
            metadatas=metadatas
        )

        # Step 7: Process Graph RAG
        graph_info = self._process_graph(chunks)

        # Step 8: Return ingestion information
        return {
            "source": file_path,
            "total_documents": len(documents),
            "total_chunks": len(chunks),
            "stored_chunks": len(ids),
            "graph": graph_info
        }
