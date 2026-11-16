class QueryRouter:

    GRAPH_ONLY_TERMS = (
        "همسایه",
        "همسایه‌های",
        "همسایه های",
        "گره‌های متصل",
        "گره های متصل",
        "neighbors",
        "graph nodes"
    )

    RELATIONSHIP_TERMS = (
        "ارتباط",
        "رابطه",
        "وابستگی",
        "متصل",
        "مرتبط",
        "رابطه‌ای",
        "چه چیزی باعث",
        "تأثیر",
        "تاثیر",
        "relationship",
        "connected",
        "related",
        "dependency",
        "depends on"
    )

    def route(self, query: str) -> str:

        if not query or not query.strip():
            raise ValueError("Query cannot be empty.")

        normalized_query = query.casefold()

        # Graph-only questions
        if any(
            term in normalized_query
            for term in self.GRAPH_ONLY_TERMS
        ):
            return "graph"

        # Relationship-based questions
        if any(
            term in normalized_query
            for term in self.RELATIONSHIP_TERMS
        ):
            return "hybrid"

        # General document questions
        return "documents"