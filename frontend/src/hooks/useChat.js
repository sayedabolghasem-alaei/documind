
import { useState } from "react";
import { sendMessage } from "../services/api";

function useChat() {
  const [messages, setMessages] = useState([]);
  const [conversationId, setConversationId] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  // Send a message and receive the AI response
  async function handleSendMessage(query) {
    const trimmedQuery = query.trim();

    if (!trimmedQuery || isLoading) {
      return;
    }

    const userMessage = {
      id: crypto.randomUUID(),
      role: "user",
      content: trimmedQuery,
    };

    setMessages((previousMessages) => [
      ...previousMessages,
      userMessage,
    ]);

    setIsLoading(true);
    setError(null);

    try {
      const response = await sendMessage(
        trimmedQuery,
        conversationId
      );

      const assistantMessage = {
        id: crypto.randomUUID(),
        role: "assistant",
        content: response.answer,
        sources: response.sources || [],
      };

      setMessages((previousMessages) => [
        ...previousMessages,
        assistantMessage,
      ]);

      if (response.conversation_id) {
        setConversationId(response.conversation_id);
      }
    } catch (err) {
      setError(err.message || "Something went wrong.");

      setMessages((previousMessages) => [
        ...previousMessages,
        {
          id: crypto.randomUUID(),
          role: "assistant",
          content: "Sorry, I couldn't process your request.",
          sources: [],
          isError: true,
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  }

  // Start a new conversation
  function startNewChat() {
    setMessages([]);
    setConversationId(null);
    setError(null);
  }

  return {
    messages,
    conversationId,
    isLoading,
    error,
    handleSendMessage,
    startNewChat,
  };
}

export default useChat;
