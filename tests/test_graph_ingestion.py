
import sys
from pathlib import Path
import json

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app.ingestion.ingestion_pipeline import IngestionPipeline
from app.graph.graph_storage import GraphStorage


def main():

    # Locate sample PDF
    sample_file = PROJECT_ROOT / "data" / "uploads" / "sample.pdf"

    if not sample_file.exists():
        print("Error: sample.pdf was not found.")
        return

    # Initialize pipeline
    pipeline = IngestionPipeline()

    print("\nStarting Graph RAG Ingestion Test")
    print("=" * 50)

    # Run ingestion
    result = pipeline.ingest(str(sample_file))

    print("\nIngestion Result")
    print("=" * 50)

    print(
        json.dumps(
            result,
            ensure_ascii=False,
            indent=4
        )
    )

    # Load stored knowledge graph
    storage = GraphStorage()
    graph = storage.load()

    print("\nStored Knowledge Graph")
    print("=" * 50)

    print(f"Total Entities: {graph.number_of_nodes()}")
    print(f"Total Relationships: {graph.number_of_edges()}")

    print("\nEntities:")

    for node, attributes in graph.nodes(data=True):
        print({
            "name": node,
            "type": attributes.get("entity_type")
        })

    print("\nRelationships:")

    for source, target, attributes in graph.edges(data=True):
        print({
            "source": source,
            "target": target,
            "relation": attributes.get("relation")
        })


if __name__ == "__main__":
    main()
