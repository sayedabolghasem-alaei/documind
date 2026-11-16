
import re


class HybridContextBuilder:

    @staticmethod
    def normalize_text(text: str) -> str:
        """Normalize whitespace for duplicate detection."""
        return re.sub(r"\s+", " ", text).strip().casefold()

    def build(self, vector_results: list, graph_results: dict) -> str:

        context_parts = []
        seen_contents = set()

        # Step 1: Add unique vector retrieval results
        context_parts.append("DOCUMENT CONTEXT:")

        if vector_results:

            document_index = 0

            for document in vector_results:

                text = document.get("text", "").strip()

                if not text:
                    continue

                normalized_text = self.normalize_text(text)

                if normalized_text in seen_contents:
                    continue

                seen_contents.add(normalized_text)
                document_index += 1

                metadata = document.get("metadata", {})

                source = metadata.get("source", "Unknown")
                pages = metadata.get("pages", "Unknown")

                context_parts.append(
                    f"\nDocument {document_index}:\n"
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
