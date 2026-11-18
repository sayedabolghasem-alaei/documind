from app.database.conversation_repository import ConversationRepository


repository = ConversationRepository()

# Create conversation
conversation_id = repository.create_conversation("Test Conversation")
print("Created:", conversation_id)

# Save messages
repository.save_message(
    conversation_id,
    "user",
    "Hello, DocuMind!"
)

repository.save_message(
    conversation_id,
    "assistant",
    "Hello! How can I help you?"
)

# Retrieve conversations
print("\nConversations:")
print(repository.get_conversations())

# Retrieve messages
print("\nMessages:")
print(repository.get_messages(conversation_id))

# Rename conversation
repository.rename_conversation(
    conversation_id,
    "Updated Test Conversation"
)

print("\nRenamed:")
print(repository.get_conversation(conversation_id))

# Delete conversation
repository.delete_conversation(conversation_id)

print("\nDeleted:")
print(repository.get_conversation(conversation_id))