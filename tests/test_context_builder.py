
from app.generation.hybrid_context_builder import HybridContextBuilder


def test_duplicate_documents():

    builder = HybridContextBuilder()

    vector_results = [
        {
            "text": "This is a sample document.",
            "metadata": {"source": "file1.pdf", "pages": [1]}
        },
        {
            "text": "  This   is a sample document.  ",
            "metadata": {"source": "file2.pdf", "pages": [2]}
        },
        {
            "text": "This is another document.",
            "metadata": {"source": "file3.pdf", "pages": [3]}
        }
    ]

    context = builder.build(
        vector_results=vector_results,
        graph_results={
            "entities": [],
            "relationships": []
        }
    )

    assert context.count("Content:") == 2

    assert "file1.pdf" in context
    assert "file3.pdf" in context
    assert "file2.pdf" not in context

    print("Context deduplication test passed.")


if __name__ == "__main__":
    test_duplicate_documents()
