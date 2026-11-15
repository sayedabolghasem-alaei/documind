
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

from app.retrieval.hybrid_retriever import HybridRetriever


TOP_K = 3

TEST_QUERIES = [
    "برای تحویل محصول در مسابقه چه چیزهایی باید آماده کنیم؟",
    "مستندات فنی محصول شامل چه مواردی است؟",
    "ویدیوی معرفی محصول باید چه محتوایی داشته باشد؟",
    "برای ارائه محصول به سرمایه گذار چه مواردی لازم است؟",
    "سورس کد پروژه چگونه باید تحویل داده شود؟"
]


def display_results(method_name, results, elapsed_time):

    print(f"\n{method_name}")
    print("-" * 70)
    print(f"Execution Time: {elapsed_time:.4f} seconds")
    print(f"Results Count: {len(results)}")

    for rank, document in enumerate(results, start=1):

        metadata = document.get("metadata", {})

        print(f"\nRank: {rank}")
        print(f"Document ID: {document.get('id')}")
        print(f"Source: {metadata.get('source', 'Unknown')}")
        print(f"Pages: {metadata.get('pages', 'Unknown')}")

        if "distance" in document:
            print(f"Distance: {document['distance']:.4f}")

        if "score" in document:
            print(f"BM25 Score: {document['score']:.4f}")

        if "rrf_score" in document:
            print(f"RRF Score: {document['rrf_score']:.6f}")

        if "rerank_score" in document:
            print(f"Rerank Score: {document['rerank_score']:.4f}")

        if "retrieval_sources" in document:
            print(f"Sources: {document['retrieval_sources']}")

        print(f"Text: {document.get('text', '')[:220]}")


def main():

    print("Initializing Retrieval Components...")

    hybrid_retriever = HybridRetriever()

    # Reuse the components initialized inside HybridRetriever.
    vector_retriever = hybrid_retriever.vector_retriever
    keyword_retriever = hybrid_retriever.keyword_retriever

    print("\nInitialization Completed.")

    for index, query in enumerate(TEST_QUERIES, start=1):

        print("\n" + "=" * 80)
        print(f"TEST QUERY {index}")
        print("=" * 80)

        print(f"\nQuery: {query}")

        # 1. Vector Search
        start_time = time.perf_counter()

        vector_results = vector_retriever.retrieve(
            query=query,
            top_k=TOP_K
        )

        vector_time = time.perf_counter() - start_time

        # 2. Keyword Search
        start_time = time.perf_counter()

        keyword_results = keyword_retriever.retrieve(
            query=query,
            top_k=TOP_K
        )

        keyword_time = time.perf_counter() - start_time

        # 3. Hybrid Search
        start_time = time.perf_counter()

        hybrid_results = hybrid_retriever.retrieve(
            query=query,
            top_k=TOP_K
        )

        hybrid_time = time.perf_counter() - start_time

        # Display results
        display_results(
            "VECTOR SEARCH",
            vector_results,
            vector_time
        )

        display_results(
            "KEYWORD SEARCH",
            keyword_results,
            keyword_time
        )

        display_results(
            "HYBRID SEARCH",
            hybrid_results,
            hybrid_time
        )

        # Summary
        print("\n" + "-" * 70)
        print("COMPARISON SUMMARY")
        print("-" * 70)

        print(f"Vector Results: {len(vector_results)}")
        print(f"Keyword Results: {len(keyword_results)}")
        print(f"Hybrid Results: {len(hybrid_results)}")

        print(f"Vector Time: {vector_time:.4f}s")
        print(f"Keyword Time: {keyword_time:.4f}s")
        print(f"Hybrid Time: {hybrid_time:.4f}s")


if __name__ == "__main__":
    main()
