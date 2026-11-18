from app.services.chat_service import ChatService


def test_chat_persistence():

    service = ChatService()

    # Mock the RAG pipeline to avoid calling the real model.
    class MockRAGPipeline:

        def run(self, query, top_k=3):
            return {
                "answer": "This is a test answer.",
                "retrieved_documents": []
            }

    service._rag_pipeline = MockRAGPipeline()

    # Create a conversation and save messages.
    result = service.chat(
        query="What is RAG?"
    )

    conversation_id = result["conversation_id"]

    # Retrieve the saved conversation.
    conversation = service.conversation_repository.get_conversation(
        conversation_id
    )

    messages = service.conversation_repository.get_messages(
        conversation_id
    )

    print("\nConversation:")
    print(dict(conversation))

    print("\nMessages:")
    for message in messages:
        print(dict(message))

    assert conversation is not None
    assert len(messages) == 2
    assert messages[0]["role"] == "user"
    assert messages[0]["content"] == "What is RAG?"
    assert messages[1]["role"] == "assistant"
    assert messages[1]["content"] == "This is a test answer."

    # Cleanup test data.
    service.conversation_repository.delete_conversation(
        conversation_id
    )

    print("\nChat persistence test passed!")


if __name__ == "__main__":
    test_chat_persistence()