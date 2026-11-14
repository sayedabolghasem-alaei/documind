function Header() {
  return (
    <header className="main-header">
      <div>
        <h1>AI Assistant</h1>
        <p>Ask questions about your documents</p>
      </div>

      <div className="header-status">
        <span className="status-dot"></span>
        AI Ready
      </div>
    </header>
  );
}

export default Header;