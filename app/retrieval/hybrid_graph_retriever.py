
from app.retrieval.hybrid_retriever import HybridRetriever
from app.graph.graph_retriever import GraphRetriever


class HybridGraphRetriever:

    def __init__(self, collection_name: str = "documents"):

        self.document_retriever = HybridRetriever(
            collection_name=collection_name
        )

        self.graph_retriever = GraphRetriever()

    def _find_query_entities(self, query: str) -> list:

        matched_entities = []

        for entity in self.graph_retriever.graph.nodes:

            entity_name = str(entity)

            if entity_name.casefold() in query.casefold():
                matched_entities.append(entity_name)

        return matched_entities

    def _retrieve_graph_results(self, query: str) -> dict:

        matched_entities = self._find_query_entities(query)

        all_entities = []
        all_relationships = []

        for entity_name in matched_entities:

            result = self.graph_retriever.search(
                entity_name=entity_name,
                direction="both"
            )

            all_entities.extend(result["entities"])
            all_relationships.extend(result["relationships"])

        unique_entities = {
            entity["name"]: entity
            for entity in all_entities
        }

        unique_relationships = {}

        for relationship in all_relationships:

            key = (
                relationship["source"],
                relationship["target"],
                relationship["relation"]
            )

            unique_relationships[key] = relationship

        return {
            "query": query,
            "matched_entities": matched_entities,
            "entities": list(unique_entities.values()),
            "relationships": list(unique_relationships.values())
        }

    def retrieve(
        self,
        query: str,
        top_k: int = 3
    ) -> dict:

        if not query or not query.strip():
            raise ValueError("Query cannot be empty.")

        if top_k <= 0:
            raise ValueError("top_k must be greater than zero.")

        query = query.strip()

        # Step 1: Hybrid Document Retrieval
        vector_results = self.document_retriever.retrieve(
            query=query,
            top_k=top_k
        )

        # Step 2: Knowledge Graph Retrieval
        graph_results = self._retrieve_graph_results(query)

        # Step 3: Return combined results
        return {
            "query": query,
            "vector_results": vector_results,
            "graph_results": graph_results
        }
