import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app.retrieval.hybrid_retriever import HybridRetriever


QUERY = "مستندات فنی محصول شامل چه مواردی است؟"


def main():

    hybrid = HybridRetriever()

    vector_results = hybrid.vector_retriever.retrieve(
        query=QUERY,
        top_k=15
    )

    keyword_results = hybrid.keyword_retriever.retrieve(
        query=QUERY,
        top_k=15
    )

    candidates = {}

    for source, results in [
        ("vector", vector_results),
        ("keyword", keyword_results)
    ]:

        for rank, document in enumerate(results, start=1):

            document_id = document["id"]

            if document_id not in candidates:
                candidates[document_id] = document

    documents = list(candidates.values())

    print("Candidate Documents:", len(documents))

    reranker = hybrid.reranker
    tokenizer = reranker.model.tokenizer
    model = reranker.model.model

    pairs = [
        [QUERY, document["text"]]
        for document in documents
    ]

    start = time.perf_counter()

    features = tokenizer(
        pairs,
        padding=True,
        truncation=True,
        max_length=512,
        return_tensors="pt"
    )

    print(
        "Tokenization:",
        round(time.perf_counter() - start, 4),
        "seconds"
    )

    features = {
        key: value.to(reranker.model.device)
        for key, value in features.items()
    }

    start = time.perf_counter()

    model.eval()

    import torch

    with torch.no_grad():
        outputs = model(**features)

    print(
        "Model Inference:",
        round(time.perf_counter() - start, 4),
        "seconds"
    )

    print("Input Tensor Shape:", features["input_ids"].shape)


if __name__ == "__main__":
    main()