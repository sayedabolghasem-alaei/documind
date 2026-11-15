import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app.generation.answer_generator import AnswerGenerator


def main():

    generator = AnswerGenerator()

    query = "BuildX چیست و از چه فناوری‌هایی استفاده می‌کند؟"

    print("\nHybrid Graph RAG Answer Test")
    print("=" * 60)

    print("\nUser Query:")
    print(query)

    print("\nGenerating answer...\n")

    result = generator.generate(
        query=query,
        top_k=3
    )

    print("Generated Answer:")
    print("-" * 60)
    print(result["answer"])

    print("\nRetrieved Documents:")
    print("-" * 60)

    for document in result.get("retrieved_documents", []):

        metadata = document.get("metadata", {})

        print("Source:", metadata.get("source"))
        print("Pages:", metadata.get("pages"))
        print()

    print("Test Completed Successfully.")


if __name__ == "__main__":
    main()
