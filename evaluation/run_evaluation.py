
import json
import sys
import time

from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app.retrieval.hybrid_retriever import HybridRetriever


CONFIG_PATH = Path(__file__).parent / "queries.json"
OUTPUT_DIR = Path(__file__).parent / "results"


def load_queries():

    with open(CONFIG_PATH, "r", encoding="utf-8") as file:
        config = json.load(file)

    return config["queries"], config["top_k"]


def fuse_candidates(
    vector_results,
    keyword_results
):

    rrf_k = 60
    fused_results = {}

    result_lists = [
        ("vector", vector_results),
        ("keyword", keyword_results)
    ]

    for source, results in result_lists:

        for rank, document in enumerate(results, start=1):

            content_key = HybridRetriever._content_key(
                document["text"]
            )

            if content_key not in fused_results:

                fused_results[content_key] = {
                    "id": document["id"],
                    "duplicate_ids": [],
                    "text": document["text"],
                    "metadata": dict(document["metadata"]),
                    "rrf_score": 0.0,
                    "retrieval_sources": [],
                    "ranks": {}
                }

            fused_document = fused_results[content_key]

            if (
                document["id"] != fused_document["id"]
                and document["id"] not in fused_document["duplicate_ids"]
            ):
                fused_document["duplicate_ids"].append(
                    document["id"]
                )

            fused_document["metadata"] = (
                HybridRetriever._merge_metadata(
                    fused_document["metadata"],
                    document["metadata"]
                )
            )

            if source not in fused_document["retrieval_sources"]:

                fused_document["rrf_score"] += (
                    1 / (rrf_k + rank)
                )

                fused_document["retrieval_sources"].append(source)
                fused_document["ranks"][source] = rank

    return sorted(
        fused_results.values(),
        key=lambda document: document["rrf_score"],
        reverse=True
    )


def run_evaluation():

    queries, top_k = load_queries()

    candidate_k = top_k * 5

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    print("Initializing Retrieval Components...")

    hybrid_retriever = HybridRetriever()

    vector_retriever = hybrid_retriever.vector_retriever
    keyword_retriever = hybrid_retriever.keyword_retriever
    reranker = hybrid_retriever.reranker

    print("Initialization Completed.")

    evaluation_results = []

    for index, item in enumerate(queries, start=1):

        query_id = item["id"]
        query = item["query"]

        print("\n" + "=" * 80)
        print(f"QUERY {index}: {query_id}")
        print("=" * 80)

        print(f"Question: {query}")

        # 1. Vector Search

        start = time.perf_counter()

        vector_results = vector_retriever.retrieve(
            query=query,
            top_k=candidate_k
        )

        vector_time = time.perf_counter() - start

        # 2. Keyword Search

        start = time.perf_counter()

        keyword_results = keyword_retriever.retrieve(
            query=query,
            top_k=candidate_k
        )

        keyword_time = time.perf_counter() - start

        # 3. RRF Fusion

        start = time.perf_counter()

        fused_results = fuse_candidates(
            vector_results,
            keyword_results
        )

        rrf_time = time.perf_counter() - start

        # 4. Reranking

        start = time.perf_counter()

        reranked_results = reranker.rerank(
            query=query,
            documents=fused_results,
            top_k=top_k
        )

        reranker_time = time.perf_counter() - start

        result = {
            "query_id": query_id,
            "query": query,
            "relevance_criteria": item.get(
                "relevance_criteria", ""
            ),
            "timings": {
                "vector": round(vector_time, 4),
                "keyword": round(keyword_time, 4),
                "rrf": round(rrf_time, 4),
                "reranker": round(reranker_time, 4)
            },
            "vector_results": vector_results,
            "keyword_results": keyword_results,
            "rrf_results": fused_results,
            "reranked_results": reranked_results
        }

        evaluation_results.append(result)

        print(f"\nVector Results: {len(vector_results)}")
        print(f"Keyword Results: {len(keyword_results)}")
        print(f"RRF Candidates: {len(fused_results)}")
        print(f"Reranked Results: {len(reranked_results)}")

        print("\nExecution Times:")
        print(f"Vector: {vector_time:.4f}s")
        print(f"Keyword: {keyword_time:.4f}s")
        print(f"RRF: {rrf_time:.4f}s")
        print(f"Reranker: {reranker_time:.4f}s")

        print("\nTop Reranked Results:")

        for rank, document in enumerate(
            reranked_results,
            start=1
        ):

            print(f"\nRank: {rank}")
            print(f"ID: {document['id']}")
            print(
                f"RRF Score: {document['rrf_score']:.6f}"
            )
            print(
                f"Rerank Score: {document['rerank_score']:.4f}"
            )
            print(f"Text: {document['text'][:180]}")

    # Save evaluation results

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    output_path = OUTPUT_DIR / (
        f"retrieval_evaluation_{timestamp}.json"
    )

    with open(output_path, "w", encoding="utf-8") as file:

        json.dump(
            evaluation_results,
            file,
            ensure_ascii=False,
            indent=4
        )

    print("\n" + "=" * 80)
    print("EVALUATION COMPLETED")
    print("=" * 80)

    print(f"Results saved to: {output_path}")


if __name__ == "__main__":
    run_evaluation()
