
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app.retrieval.hybrid_graph_retriever import HybridGraphRetriever
from app.generation.hybrid_context_builder import HybridContextBuilder


def main():

    query = "BuildX"

    # Step 1: Retrieve vector and graph results
    retriever = HybridGraphRetriever()

    results = retriever.retrieve(
        query=query,
        top_k=3
    )

    vector_results = results["vector_results"]
    graph_results = results["graph_results"]

    # Step 2: Build combined context
    context_builder = HybridContextBuilder()

    context = context_builder.build(
        vector_results=vector_results,
        graph_results=graph_results
    )

    # Step 3: Display context
    print("\nHybrid Context Builder Test")
    print("=" * 60)

    print(context)

    # Step 4: Display statistics
    print("\nContext Statistics")
    print("=" * 60)

    print("Vector Documents:", len(vector_results))
    print("Graph Entities:", len(graph_results["entities"]))
    print("Graph Relationships:", len(graph_results["relationships"]))
    print("Context Characters:", len(context))


if __name__ == "__main__":
    main()
