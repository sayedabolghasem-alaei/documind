
class HybridContextBuilder:

    def build(self, vector_results: list, graph_results: dict) -> str:

        context_parts = []

        # Step 1: Add vector retrieval context
        context_parts.append("DOCUMENT CONTEXT:")

        if vector_results:

            for index, document in enumerate(vector_results, start=1):

                text = document.get("text", "")
                metadata = document.get("metadata", {})

                source = metadata.get("source", "Unknown")
                pages = metadata.get("pages", "Unknown")

                context_parts.append(
                    f"\nDocument {index}:\n"
                    f"Source: {source}\n"
                    f"Pages: {pages}\n"
                    f"Content: {text}"
                )

        else:
            context_parts.append("No relevant documents found.")

        # Step 2: Add graph entities
        context_parts.append("\n\nKNOWLEDGE GRAPH ENTITIES:")

        entities = graph_results.get("entities", [])

        if entities:

            for entity in entities:

                context_parts.append(
                    f"\nEntity: {entity['name']}\n"
                    f"Type: {entity['type']}\n"
                    f"Description: {entity['description']}"
                )

        else:
            context_parts.append("No related entities found.")

        # Step 3: Add graph relationships
        context_parts.append("\n\nKNOWLEDGE GRAPH RELATIONSHIPS:")

        relationships = graph_results.get("relationships", [])

        if relationships:

            for relationship in relationships:

                context_parts.append(
                    f"\n{relationship['source']} "
                    f"--[{relationship['relation']}]--> "
                    f"{relationship['target']}\n"
                    f"Description: {relationship['description']}"
                )

        else:
            context_parts.append("No related relationships found.")

        # Step 4: Return combined context
        return "\n".join(context_parts)
