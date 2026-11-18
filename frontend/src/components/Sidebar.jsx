
function Sidebar({
  activeView,
  onChangeView,
  onNewChat,

  conversations = [],
  activeConversationId,

  onSelectConversation,
  onRenameConversation,
  onDeleteConversation,
}) {

  async function handleRename(conversation) {

    const newTitle = window.prompt(
      "Enter the new conversation title:",
      conversation.title
    );

    if (newTitle === null) return;

    const trimmedTitle = newTitle.trim();

    if (!trimmedTitle) {
      window.alert("Conversation title cannot be empty.");
      return;
    }

    await onRenameConversation(
      conversation.id,
      trimmedTitle
    );
  }


  async function handleDelete(conversation) {

    const confirmed = window.confirm(
      `Delete "${conversation.title}"?`
    );

    if (!confirmed) return;

    await onDeleteConversation(conversation.id);
  }


  return (
    <aside className="sidebar">

      <div className="sidebar-brand">
        <div className="brand-icon">✦</div>

        <div>
          <h2>DocuMind</h2>
          <span>AI Assistant</span>
        </div>
      </div>


      <button
        className="new-chat-button"
        onClick={onNewChat}
      >
        <span>＋</span>
        New Chat
      </button>


      <div className="sidebar-section">

        <p className="section-label">WORKSPACE</p>

        <button
          className={`sidebar-item ${
            activeView === "chat" ? "active" : ""
          }`}
          onClick={() => onChangeView("chat")}
        >
          <span>▤</span>
          Chat
        </button>

        <button
          className={`sidebar-item ${
            activeView === "documents" ? "active" : ""
          }`}
          onClick={() => onChangeView("documents")}
        >
          <span>▧</span>
          My Documents
        </button>

      </div>


      <div className="sidebar-section recent-section">

        <p className="section-label">RECENT CHATS</p>


        {conversations.length === 0 ? (

          <div className="empty-sidebar-message">
            No conversations yet.
          </div>

        ) : (

          <div className="conversation-list">

            {conversations.map((conversation) => (

              <div
                key={conversation.id}
                className={`conversation-item ${
                  activeConversationId === conversation.id
                    ? "active"
                    : ""
                }`}
              >

                <button
                  className="conversation-title"
                  onClick={() => {
                    onSelectConversation(conversation.id);
                  }}
                  title={conversation.title}
                >
                  {conversation.title}
                </button>


                <div className="conversation-actions">

                  <button
                    className="conversation-action"
                    title="Rename conversation"
                    onClick={() => handleRename(conversation)}
                  >
                    ✎
                  </button>

                  <button
                    className="conversation-action delete"
                    title="Delete conversation"
                    onClick={() => handleDelete(conversation)}
                  >
                    ×
                  </button>

                </div>

              </div>

            ))}

          </div>

        )}

      </div>


      <div className="sidebar-bottom">

        <div className="user-avatar">U</div>

        <div className="user-info">
          <strong>My Workspace</strong>
          <span>Personal Account</span>
        </div>

      </div>

    </aside>
  );
}


export default Sidebar;
