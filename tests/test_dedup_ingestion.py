
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app.ingestion.ingestion_pipeline import IngestionPipeline


def main():

    file_1 = (
        PROJECT_ROOT
        / "data"
        / "uploads"
        / "eeecacbba02b4446b747cc98dc637c89.pdf"
    )

    file_2 = (
        PROJECT_ROOT
        / "data"
        / "uploads"
        / "sample.pdf"
    )

    # Verify both files exist
    if not file_1.exists() or not file_2.exists():
        raise FileNotFoundError("One or both PDF files were not found.")

    pipeline = IngestionPipeline()

    print("\nIngesting first PDF...")
    result_1 = pipeline.ingest(str(file_1))
    print(result_1)

    print("\nIngesting second PDF...")
    result_2 = pipeline.ingest(str(file_2))
    print(result_2)

    # Inspect stored metadata
    print("\nChecking ChromaDB metadata...")

    collection = pipeline.vector_store.collection

    data = collection.get(
        include=["metadatas"]
    )

    for chunk_id, metadata in zip(
        data["ids"],
        data["metadatas"]
    ):

        sources = metadata.get("sources", "")
        source = metadata.get("source", "")

        if (
            "sample.pdf" in str(sources)
            or "sample.pdf" in str(source)
        ):

            print("\n" + "=" * 60)
            print("Chunk ID:", chunk_id)
            print("Sources:", sources)
            print("Source:", source)
            print("Pages:", metadata.get("pages"))
            print("Chunk Indices:", metadata.get("chunk_indices"))


if __name__ == "__main__":
    main()
