
import sys
from pathlib import Path
import json

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app.retrieval.hybrid_graph_retriever import HybridGraphRetriever


def main():

    retriever = HybridGraphRetriever()

    query = "BuildX"

    print("\nHybrid Retrieval Test")
    print("=" * 60)

    results = retriever.retrieve(
        query=query,
        top_k=3
    )

    print("\nQuery:")
    print(results["query"])

    print("\nVector Retrieval Results")
    print("=" * 60)

    print(
        json.dumps(
            results["vector_results"],
            ensure_ascii=False,
            indent=4,
            default=str
        )
    )

    print("\nGraph Retrieval Results")
    print("=" * 60)

    print(
        json.dumps(
            results["graph_results"],
            ensure_ascii=False,
            indent=4,
            default=str
        )
    )

    print("\nHybrid Retrieval Summary")
    print("=" * 60)

    print(
        "Vector Results:",
        len(results["vector_results"])
    )

    print(
        "Graph Entities:",
        len(results["graph_results"]["entities"])
    )

    print(
        "Graph Relationships:",
        len(results["graph_results"]["relationships"])
    )


if __name__ == "__main__":
    main()
