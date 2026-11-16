
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app.retrieval.hybrid_retriever import HybridRetriever


TEST_QUERIES = [
    "برای تحویل محصول در مسابقه چه چیزهایی باید آماده کنیم؟",
    "مستندات فنی محصول شامل چه مواردی است؟",
    "ویدیوی معرفی محصول باید چه محتوایی داشته باشد؟",
    "برای ارائه محصول به سرمایه گذار چه مواردی لازم است؟",
    "سورس کد پروژه چگونه باید تحویل داده شود؟"
]


def add_timing_wrapper(instance, method_name, label):

    original_method = getattr(instance, method_name)

    def wrapper(*args, **kwargs):

        start_time = time.perf_counter()

        results = original_method(*args, **kwargs)

        elapsed_time = time.perf_counter() - start_time

        print(f"{label}: {elapsed_time:.4f} seconds")

        if method_name == "rerank":

            documents = (
                args[1]
                if len(args) > 1
                else kwargs.get("documents", [])
            )

            query = (
                args[0]
                if args
                else kwargs.get("query", "")
            )

            print("Reranker Input Documents:", len(documents))

            print(
                "Document Text Lengths:",
                [len(document["text"]) for document in documents]
            )

            print(
                "Total Document Characters:",
                sum(len(document["text"]) for document in documents)
            )

            tokenizer = instance.model.tokenizer

            token_lengths = []

            for document in documents:

                encoded = tokenizer(
                    query,
                    document["text"],
                    truncation=False,
                    add_special_tokens=True
                )

                token_lengths.append(
                    len(encoded["input_ids"])
                )

            print("Document Pair Token Lengths:", token_lengths)

            print("Maximum Token Length:", max(token_lengths))

            print(
                "Average Token Length:",
                sum(token_lengths) / len(token_lengths)
            )

        return results

    setattr(instance, method_name, wrapper)
def main():

    print("Initializing Hybrid Retriever...")

    initialization_start = time.perf_counter()

    hybrid_retriever = HybridRetriever()

    initialization_time = (
        time.perf_counter() - initialization_start
    )

    print(
        f"Initialization Time: {initialization_time:.4f} seconds"
    )

    # Measure individual retrieval components.
    add_timing_wrapper(
        hybrid_retriever.vector_retriever,
        "retrieve",
        "Vector Retrieval"
    )

    add_timing_wrapper(
        hybrid_retriever.keyword_retriever,
        "retrieve",
        "Keyword Retrieval"
    )

    add_timing_wrapper(
        hybrid_retriever.reranker,
        "rerank",
        "Reranker"
    )

    for index, query in enumerate(TEST_QUERIES, start=1):

        print("\n" + "=" * 70)
        print(f"QUERY {index}")
        print("=" * 70)

        print(f"Query: {query}")

        start_time = time.perf_counter()

        results = hybrid_retriever.retrieve(
            query=query,
            top_k=3
        )

        total_time = time.perf_counter() - start_time

        print(f"Final Results: {len(results)}")
        print(f"Total Hybrid Time: {total_time:.4f} seconds")


if __name__ == "__main__":
    main()
