
import { useState } from "react";

function ChatInput({ onSendMessage, isLoading }) {
  const [input, setInput] = useState("");

  function handleSubmit(event) {
    event.preventDefault();

    const message = input.trim();

    if (!message || isLoading) {
      return;
    }

    onSendMessage(message);
    setInput("");
  }

  function handleKeyDown(event) {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      handleSubmit(event);
    }
  }

  return (
    <form className="chat-input-container" onSubmit={handleSubmit}>
      <textarea
        className="chat-textarea"
        value={input}
        onChange={(event) => setInput(event.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="Ask anything about your documents..."
        rows={1}
        disabled={isLoading}
      />

      <button
        type="submit"
        className="send-button"
        disabled={!input.trim() || isLoading}
      >
        {isLoading ? "..." : "↑"}
      </button>
    </form>
  );
}

export default ChatInput;
