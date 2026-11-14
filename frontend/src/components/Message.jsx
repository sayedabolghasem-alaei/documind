
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

function Message({ message }) {
  const isUser = message.role === "user";

  // Merge sources that belong to the same document
  const uniqueSources = Object.values(
    (message.sources || []).reduce((result, source) => {
      const filename = source.filename || "Unknown document";

      if (!result[filename]) {
        result[filename] = {
          filename,
          pages: new Set(),
        };
      }

      (source.pages || []).forEach((page) => {
        result[filename].pages.add(page);
      });

      return result;
    }, {})
  ).map((source) => ({
    filename: source.filename,
    pages: [...source.pages].sort((a, b) => a - b),
  }));

  return (
    <div
      className={`message-row ${
        isUser ? "user-message-row" : "assistant-message-row"
      }`}
    >
      {!isUser && (
        <div className="message-avatar assistant-avatar">
          AI
        </div>
      )}

      <div className="message-content">
        <div
          className={`message-bubble ${
            isUser ? "user-bubble" : "assistant-bubble"
          } ${message.isError ? "error-bubble" : ""}`}
        >
          {isUser ? (
            <p>{message.content}</p>
          ) : (
            <div className="markdown-content">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {message.content || ""}
              </ReactMarkdown>
            </div>
          )}
        </div>

        {!isUser && uniqueSources.length > 0 && (
          <div className="message-sources">
            <strong>Sources</strong>

            {uniqueSources.map((source) => (
              <div
                className="source-item"
                key={source.filename}
              >
                <span className="source-icon">📄</span>

                <div>
                  <p>{source.filename}</p>

                  <span>
                    Pages: {source.pages.length > 0
                      ? source.pages.join(", ")
                      : "N/A"}
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {isUser && (
        <div className="message-avatar user-message-avatar">
          U
        </div>
      )}
    </div>
  );
}

export default Message;
