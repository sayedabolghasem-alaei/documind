
function Sidebar({ activeView, onChangeView, onNewChat }) {
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

        <div className="empty-sidebar-message">
          Your conversations will appear here.
        </div>
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
