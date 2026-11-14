
from app.retrieval.retriever import Retriever


def main():

    retriever = Retriever()

    test_queries = [
        "برای تحویل محصول در مسابقه چه چیزهایی باید آماده کنیم؟",
        "مستندات فنی محصول شامل چه مواردی است؟",
        "ویدیوی معرفی محصول باید چه محتوایی داشته باشد؟",
        "برای ارائه محصول به سرمایه گذار چه مواردی لازم است؟",
        "سورس کد پروژه چگونه باید تحویل داده شود؟"
    ]

    for index, query in enumerate(test_queries, start=1):

        print(f"\nTest Query {index}:")
        print(query)

        results = retriever.retrieve(
            query=query,
            top_k=3
        )

        print("\nRetrieved Documents:")
        print("=" * 60)

        for rank, document in enumerate(results, start=1):

            print(f"\nRank: {rank}")
            print(f"Distance: {document['distance']:.4f}")
            print(f"Source: {document['metadata']['source']}")
            print(f"Page: {document['metadata'].get('pages', document['metadata'].get('page'))}")
            print(f"Text: {document['text'][:300]}")


if __name__ == "__main__":
    main()
