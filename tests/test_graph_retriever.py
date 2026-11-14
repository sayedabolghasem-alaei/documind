
import sys
from pathlib import Path
import json

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app.graph.graph_retriever import GraphRetriever


def main():

    retriever = GraphRetriever()

    # Test 1: Find an entity
    print("\nTest 1: Find Entity")
    print("=" * 50)

    entities = retriever.find_entity("DocuMind")

    print(
        json.dumps(
            entities,
            ensure_ascii=False,
            indent=4
        )
    )

    # Test 2: Get outgoing relationships
    print("\nTest 2: Outgoing Relationships")
    print("=" * 50)

    relationships = retriever.get_relationships(
        entity_name="DocuMind",
        direction="out"
    )

    print(
        json.dumps(
            relationships,
            ensure_ascii=False,
            indent=4
        )
    )

    # Test 3: Search entity and relationships
    print("\nTest 3: Graph Search")
    print("=" * 50)

    results = retriever.search("DocuMind")

    print(
        json.dumps(
            results,
            ensure_ascii=False,
            indent=4
        )
    )

    # Test 4: Get neighbors
    print("\nTest 4: Entity Neighbors")
    print("=" * 50)

    neighbors = retriever.get_neighbors("DocuMind")

    print(
        json.dumps(
            neighbors,
            ensure_ascii=False,
            indent=4
        )
    )


if __name__ == "__main__":
    main()
