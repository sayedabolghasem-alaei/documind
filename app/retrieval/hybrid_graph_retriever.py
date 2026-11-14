
from app.retrieval.retriever import Retriever
from app.graph.graph_retriever import GraphRetriever


class HybridGraphRetriever:

    def __init__(self):

        self.vector_retriever = Retriever()
        self.graph_retriever = GraphRetriever()

    def _find_query_entities(self, query: str) -> list:

        matched_entities = []

        # Search for every known entity inside the query.
        for entity in self.graph_retriever.graph.nodes:

            entity_name = str(entity)

            if entity_name.casefold() in query.casefold():
                matched_entities.append(entity_name)

        return matched_entities

    def _retrieve_graph_results(self, query: str) -> dict:

        # Step 1: Find entities mentioned in the query
        matched_entities = self._find_query_entities(query)

        all_entities = []
        all_relationships = []

        # Step 2: Retrieve graph information for each entity
        for entity_name in matched_entities:

            result = self.graph_retriever.search(
                entity_name=entity_name,
                direction="both"
            )

            all_entities.extend(result["entities"])
            all_relationships.extend(result["relationships"])

        # Step 3: Remove duplicate entities
        unique_entities = {
            entity["name"]: entity
            for entity in all_entities
        }

        # Step 4: Remove duplicate relationships
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

        query = query.strip()

        # Step 1: Vector Retrieval
        vector_results = self.vector_retriever.retrieve(
            query=query,
            top_k=top_k
        )

        # Step 2: Graph Retrieval using matched entities
        graph_results = self._retrieve_graph_results(query)

        # Step 3: Return combined results
        return {
            "query": query,
            "vector_results": vector_results,
            "graph_results": graph_results
        }
