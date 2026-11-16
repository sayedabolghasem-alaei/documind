
from app.agent.workflow import agent


def test_agent_execution():

    query = "ویدیوی معرفی محصول باید چه محتوایی داشته باشد؟"

    result = agent.invoke({
        "query": query
    })

    print("\n" + "=" * 60)
    print("AGENT EXECUTION RESULT")
    print("=" * 60)

    print("\nAnswer:")
    print(result.get("answer", "No answer generated."))

    print("\n" + "=" * 60)
    print("RETRIEVED DOCUMENTS")
    print("=" * 60)

    for index, document in enumerate(
        result.get("vector_results", []), start=1
    ):
        print(f"\nDocument {index}")
        print("Source:", document.get("metadata", {}).get("source"))
        print("Text:", document.get("text", ""))

    print("\n" + "=" * 60)
    print("FINAL CONTEXT")
    print("=" * 60)

    print(result.get("context", ""))

    print("\nRetrieval Attempts:", result.get("retrieval_attempts", 0))

    if result.get("error"):
        print("\nError:", result["error"])


if __name__ == "__main__":
    test_agent_execution()
