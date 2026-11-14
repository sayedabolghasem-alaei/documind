
import { useEffect, useRef } from "react";
import Message from "./Message";

function ChatWindow({ messages, isLoading }) {
  const bottomRef = useRef(null);

  // Scroll to the latest message
  useEffect(() => {
    bottomRef.current?.scrollIntoView({
      behavior: "smooth",
      block: "end",
    });
  }, [messages, isLoading]);

  return (
    <div className="chat-window">
      {messages.length === 0 ? (
        <div className="chat-empty-state">
          <div className="welcome-icon">✦</div>

          <h2>How can I help you?</h2>

          <p>
            Ask a question about your uploaded documents
            and I'll find the relevant information.
          </p>

          <span className="chat-hint">
            Example: What are the main points in my documents?
          </span>
        </div>
      ) : (
        <div className="messages-list">
          {messages.map((message) => (
            <Message
              key={message.id}
              message={message}
            />
          ))}
        </div>
      )}

      {isLoading && (
        <div
          className="typing-indicator"
          role="status"
          aria-live="polite"
        >
          <span></span>
          <span></span>
          <span></span>

          <p>AI is processing your question...</p>
        </div>
      )}

      <div ref={bottomRef} />
    </div>
  );
}

export default ChatWindow;
