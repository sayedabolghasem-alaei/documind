
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app.retrieval.vector_store import VectorStore


OLD_IDS = [
    "51495cf86f787b8bc3dc4607d76f72f244a42d68b3e9ab6242047bfdf59381da",
    "b9eead3bc9abdf8e70568b0e0bfd60424b3cf862d3e8c3b4d6d2959f8212a971",

    "5eafd36dfc7c744d70b0b74e03bdb30d2e2bf6b22602cd12bf32abae0c9d8fec",
    "cbc5bedd2313d231dc4fbc46fe4ab0663025dffcc6fd2135c9b96bd05d19ea98",

    "4135870abe7eab2bc4aab43a43350cb515d18b0b96b051557d8fbd6897d9067b",
    "78e08d8a89a4590d66fd753106fe512ae135c1debb5f16fc21b4115523cbff79",

    "18dda94194ce6ef661024051c327871e77575a0cb39f6b7125dc5ad0e1bfc1dd",
    "14f596f84f0f10aa5cdb606f1bc31ee115f24d601a7ef2518783f273e567ffd2"
]


NEW_IDS = [
    "8e534838b83426bb5403e28ad0ca3e72d1bff6d38625d94dd7d9fa2fe83c61ce",
    "3967f45b7dc4489dac6fe8934be03d2cb455499f28fa3f0a4b2f75ab4d79d541",
    "b99907f2a772da8bd14c808102a8b511ca62a028868f82ba04ac8078326e51db",
    "2dbed5a77aaf9f8c2d173dfe0dc589a83b141027414510ef30211f09206c5ee9"
]


def main():

    collection = VectorStore().collection

    # Verify old records
    old_data = collection.get(
        ids=OLD_IDS,
        include=["documents"]
    )

    # Verify preserved records
    new_data = collection.get(
        ids=NEW_IDS,
        include=["documents"]
    )

    if set(old_data["ids"]) != set(OLD_IDS):
        raise RuntimeError(
            "Old record validation failed. Cleanup cancelled."
        )

    if set(new_data["ids"]) != set(NEW_IDS):
        raise RuntimeError(
            "New record validation failed. Cleanup cancelled."
        )

    new_documents = set(new_data["documents"])

    if not all(
        document in new_documents
        for document in old_data["documents"]
    ):
        raise RuntimeError(
            "Content validation failed. Cleanup cancelled."
        )

    print("Validation successful.")
    print("Deleting 8 old duplicate records...")

    collection.delete(
        ids=OLD_IDS
    )

    # Verify deletion
    remaining_old = collection.get(
        ids=OLD_IDS,
        include=[]
    )

    remaining_new = collection.get(
        ids=NEW_IDS,
        include=[]
    )

    print("\nCleanup verification:")
    print("Remaining old records:", len(remaining_old["ids"]))
    print("Preserved new records:", len(remaining_new["ids"]))
    print("Total collection records:", collection.count())

    if remaining_old["ids"]:
        raise RuntimeError("Some old records were not deleted.")

    if len(remaining_new["ids"]) != len(NEW_IDS):
        raise RuntimeError("Some preserved records are missing.")

    print("\nCleanup completed successfully.")


if __name__ == "__main__":
    main()
