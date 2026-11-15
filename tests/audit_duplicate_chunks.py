
import sys
import hashlib
from pathlib import Path
from collections import defaultdict

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app.retrieval.vector_store import VectorStore


def normalize_text(text: str) -> str:
    return " ".join(text.split())


def main():

    vector_store = VectorStore()

    collection = vector_store.collection

    data = collection.get(
        include=["documents", "metadatas"]
    )

    duplicate_groups = defaultdict(list)

    for index, text in enumerate(data["documents"]):

        normalized_text = normalize_text(text)

        content_hash = hashlib.sha256(
            normalized_text.encode("utf-8")
        ).hexdigest()

        duplicate_groups[content_hash].append({
            "id": data["ids"][index],
            "source": data["metadatas"][index].get(
                "source", "Unknown"
            ),
            "pages": data["metadatas"][index].get(
                "pages", "Unknown"
            ),
            "text": text[:150]
        })

    duplicates = {
        key: documents
        for key, documents in duplicate_groups.items()
        if len(documents) > 1
    }

    print("=" * 70)
    print("CHROMADB DUPLICATE AUDIT")
    print("=" * 70)

    print(f"\nTotal Chunks: {len(data['ids'])}")
    print(f"Unique Content Groups: {len(duplicate_groups)}")
    print(f"Duplicate Groups: {len(duplicates)}")

    duplicate_documents = sum(
        len(documents) - 1
        for documents in duplicates.values()
    )

    print(f"Extra Duplicate Chunks: {duplicate_documents}")

    for index, documents in enumerate(
        duplicates.values(), start=1
    ):

        print("\n" + "-" * 70)
        print(f"Duplicate Group {index}")

        for document in documents:

            print(f"\nID: {document['id']}")
            print(f"Source: {document['source']}")
            print(f"Pages: {document['pages']}")
            print(f"Text: {document['text']}")


if __name__ == "__main__":
    main()
