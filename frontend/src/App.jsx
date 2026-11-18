
import { useState } from "react";

import Sidebar from "./components/Sidebar";
import Header from "./components/Header";
import ChatWindow from "./components/ChatWindow";
import ChatInput from "./components/ChatInput";
import DocumentUpload from "./components/DocumentUpload";
import DocumentList from "./components/DocumentList";

import useChat from "./hooks/useChat";

import "./App.css";


function App() {

  const {
    messages,
    conversations,
    conversationId,
    isLoading,

    handleSendMessage,
    startNewChat,
    selectConversation,
    renameChat,
    removeConversation,

  } = useChat();


  const [refreshDocuments, setRefreshDocuments] = useState(0);
  const [activeView, setActiveView] = useState("chat");


  function handleUploadSuccess() {
    setRefreshDocuments((previous) => previous + 1);
  }


  function handleNewChat() {
    startNewChat();
    setActiveView("chat");
  }


  async function handleSelectConversation(id) {
    await selectConversation(id);
    setActiveView("chat");
  }


  return (
    <div className="app-container">

      <Sidebar
        activeView={activeView}
        onChangeView={setActiveView}
        onNewChat={handleNewChat}

        conversations={conversations}
        activeConversationId={conversationId}

        onSelectConversation={handleSelectConversation}
        onRenameConversation={renameChat}
        onDeleteConversation={removeConversation}
      />


      <main className="main-content">

        <Header />

        <div className="workspace">

          <section className="chat-section">

            {activeView === "chat" ? (

              <>

                <ChatWindow
                  messages={messages}
                  isLoading={isLoading}
                />


                <div className="chat-footer">

                  <DocumentUpload
                    conversationId={conversationId}
                    onUploadSuccess={handleUploadSuccess}
                  />

                  <ChatInput
                    onSendMessage={handleSendMessage}
                    isLoading={isLoading}
                  />

                  <p className="footer-note">
                    AI responses are based on your uploaded documents.
                  </p>

                </div>

              </>

            ) : (

              <div className="documents-view">

                <DocumentUpload
                  conversationId={null}
                  onUploadSuccess={handleUploadSuccess}
                />

                <DocumentList
                  refreshKey={refreshDocuments}
                />

              </div>

            )}

          </section>


          <aside className="documents-sidebar">

            <DocumentList
              refreshKey={refreshDocuments}
            />

          </aside>

        </div>

      </main>

    </div>
  );
}


export default App;
