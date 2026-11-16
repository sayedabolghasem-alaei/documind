import sys
import time
import torch

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app.retrieval.reranker import Reranker


def main():

    print("Initializing Reranker...")

    start = time.perf_counter()

    reranker = Reranker()

    print(
        f"Initialization: {time.perf_counter() - start:.2f}s"
    )

    query = "مستندات فنی محصول شامل چه مواردی است؟"

    documents = [
        {
            "id": str(i),
            "text": (
                "مستندات فنی محصول شامل معماری سیستم، "
                "ساختار پایگاه داده، API و راهنمای نصب است."
            )
        }
        for i in range(8)
    ]

    print("\nRunning benchmark...")

    for i in range(3):

        start = time.perf_counter()

        results = reranker.rerank(
            query=query,
            documents=documents,
            top_k=3
        )

        elapsed = time.perf_counter() - start

        print(
            f"Run {i + 1}: {elapsed:.4f} seconds"
        )

    print("\nDevice:", reranker.model.device)
    print("Threads:", torch.get_num_threads())


if __name__ == "__main__":
    main()