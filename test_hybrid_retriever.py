from app.retrieval.hybrid_retriever import HybridRetriever


retriever = HybridRetriever()

query = "ویدیوی معرفی محصول باید چه محتوایی داشته باشد؟"

results = retriever.retrieve(
    query=query,
    top_k=3
)

print("\nUser Query:")
print(query)

print("\nRetrieved Documents:")
print("=" * 60)

for rank, result in enumerate(results, start=1):

    print(f"\nRank: {rank}")

    print(f"Rerank Score: {result['rerank_score']:.4f}")

    print(f"RRF Score: {result['rrf_score']:.6f}")

    print(f"Sources: {result['retrieval_sources']}")

    print(f"Individual Ranks: {result['ranks']}")

    print(f"Metadata: {result['metadata']}")

    print(f"Text:\n{result['text']}")