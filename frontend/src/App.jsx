import { useEffect, useRef, useState } from "react";
import "./App.css";

const API_URL = "http://127.0.0.1:8000";

const starterHistory = [
  {
    id: 1,
    title: "Password reset procedure",
    time: "Just now",
  },
  {
    id: 2,
    title: "VPN connection troubleshooting",
    time: "Earlier today",
  },
  {
    id: 3,
    title: "CloudSync not working",
    time: "Yesterday",
  },
];

function App() {
  const [query, setQuery] = useState("");
  const [messages, setMessages] = useState([]);
  const [history, setHistory] = useState(starterHistory);
  const [activeHistory, setActiveHistory] = useState(null);

  const [documents, setDocuments] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [documentLoading, setDocumentLoading] = useState(false);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const fileInputRef = useRef(null);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    loadDocuments();
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({
      behavior: "smooth",
    });
  }, [messages, loading]);

  async function loadDocuments() {
    try {
      setDocumentLoading(true);

      const response = await fetch(`${API_URL}/documents`);

      if (!response.ok) {
        throw new Error("Could not load documents");
      }

      const data = await response.json();

      if (Array.isArray(data)) {
        setDocuments(data);
      } else if (Array.isArray(data.documents)) {
        setDocuments(data.documents);
      }
    } catch (err) {
      console.error("Document loading error:", err);

      // Keep UI usable even before backend document endpoint exists.
      setDocuments([]);
    } finally {
      setDocumentLoading(false);
    }
  }

  async function sendMessage(event) {
    event?.preventDefault();

    const question = query.trim();

    if (!question || loading) {
      return;
    }

    const historyItem = {
      id: Date.now(),
      title:
        question.length > 42
          ? `${question.substring(0, 42)}...`
          : question,
      time: "Just now",
    };

    setHistory((previous) => [
      historyItem,
      ...previous.filter((item) => item.title !== question),
    ]);

    setActiveHistory(historyItem.id);

    setMessages((previous) => [
      ...previous,
      {
        role: "user",
        content: question,
      },
    ]);

    setQuery("");
    setLoading(true);
    setError("");

    try {
      const response = await fetch(`${API_URL}/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          query: question,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));

        throw new Error(
          errorData.detail || `Server error: ${response.status}`
        );
      }

      const data = await response.json();

      setMessages((previous) => [
        ...previous,
        {
          role: "assistant",
          content: data.answer,
          sources: data.sources || [],
        },
      ]);
    } catch (err) {
      console.error(err);

      setError(
        "The support service could not be reached. Make sure the FastAPI backend is running."
      );

      setMessages((previous) => [
        ...previous,
        {
          role: "assistant",
          content:
            "I couldn't connect to the support service. Please make sure the backend is running and try again.",
          sources: [],
          error: true,
        },
      ]);
    } finally {
      setLoading(false);
    }
  }

  function startNewChat() {
    setMessages([]);
    setQuery("");
    setActiveHistory(null);
    setError("");
  }

  function handleSuggestion(text) {
    setQuery(text);
  }

  function handleKeyDown(event) {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();

      if (query.trim() && !loading) {
        sendMessage(event);
      }
    }
  }

  function openHistory(item) {
    setActiveHistory(item.id);

    /*
      For now history is UI-only.

      Later we can connect this to PostgreSQL and
      retrieve the complete conversation by ID.
    */
  }

  function openFilePicker() {
    fileInputRef.current?.click();
  }

  async function handleFileUpload(event) {
    const files = Array.from(event.target.files || []);

    if (!files.length) {
      return;
    }

    setUploading(true);
    setError("");

    try {
      for (const file of files) {
        const formData = new FormData();
        formData.append("file", file);

        const response = await fetch(
          `${API_URL}/documents/upload`,
          {
            method: "POST",
            body: formData,
          }
        );

        if (!response.ok) {
          const errorData = await response
            .json()
            .catch(() => ({}));

          throw new Error(
            errorData.detail ||
              `Failed to upload ${file.name}`
          );
        }
      }

      await loadDocuments();
    } catch (err) {
      console.error(err);

      setError(
        err.message ||
          "Document upload failed."
      );
    } finally {
      setUploading(false);

      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
    }
  }

  async function removeDocument(document) {
    const filename =
      document.filename ||
      document.file ||
      document.name;

    if (!filename) {
      return;
    }

    const confirmed = window.confirm(
      `Remove "${filename}" from the knowledge base?`
    );

    if (!confirmed) {
      return;
    }

    try {
      const response = await fetch(
        `${API_URL}/documents/${encodeURIComponent(filename)}`,
        {
          method: "DELETE",
        }
      );

      if (!response.ok) {
        const errorData = await response
          .json()
          .catch(() => ({}));

        throw new Error(
          errorData.detail ||
            "Could not remove document"
        );
      }

      setDocuments((previous) =>
        previous.filter(
          (item) =>
            (item.filename ||
              item.file ||
              item.name) !== filename
        )
      );
    } catch (err) {
      console.error(err);

      setError(
        err.message ||
          "Document removal failed."
      );
    }
  }

  function getDocumentName(document) {
    return (
      document.filename ||
      document.file ||
      document.name ||
      "Unnamed document"
    );
  }

  function getDocumentType(document) {
    const name = getDocumentName(document);

    const extension = name
      .split(".")
      .pop()
      ?.toUpperCase();

    return extension || "FILE";
  }

  return (
    <div className="app-shell">

      {/* Ambient glass background */}
      <div className="ambient ambient-one"></div>
      <div className="ambient ambient-two"></div>
      <div className="ambient ambient-three"></div>

      {/* ========================================================= */}
      {/* LEFT 30% */}
      {/* ========================================================= */}

      <aside className="left-panel">

        {/* Brand */}
        <div className="brand-section">
          <div className="brand-logo">
            <span>✦</span>
          </div>

          <div>
            <h1>Support AI</h1>
            <p>Enterprise Assistant</p>
          </div>
        </div>

        {/* New chat */}
        <button
          className="new-chat-button"
          onClick={startNewChat}
        >
          <span className="new-chat-icon">＋</span>
          <span>New conversation</span>
        </button>

        {/* ===================================================== */}
        {/* HISTORY */}
        {/* ===================================================== */}

        <section className="history-section">

          <div className="section-heading">
            <div>
              <span className="section-eyebrow">
                WORKSPACE
              </span>

              <h2>Chat history</h2>
            </div>

            <span className="history-count">
              {history.length}
            </span>
          </div>

          <div className="history-list">

            {history.length === 0 ? (
              <div className="empty-history">
                <div className="empty-history-icon">
                  ◌
                </div>

                <p>No conversations yet</p>

                <span>
                  Your previous conversations
                  will appear here.
                </span>
              </div>
            ) : (
              history.map((item) => (
                <button
                  key={item.id}
                  className={`history-item ${
                    activeHistory === item.id
                      ? "active"
                      : ""
                  }`}
                  onClick={() =>
                    openHistory(item)
                  }
                >
                  <div className="history-icon">
                    ◌
                  </div>

                  <div className="history-content">
                    <strong>
                      {item.title}
                    </strong>

                    <span>
                      {item.time}
                    </span>
                  </div>

                  <span className="history-arrow">
                    →
                  </span>
                </button>
              ))
            )}

          </div>

        </section>

        {/* ===================================================== */}
        {/* ADMIN DOCUMENT MANAGEMENT */}
        {/* ===================================================== */}

        <section className="admin-section">

          <div className="admin-header">

            <div>
              <span className="section-eyebrow">
                ADMIN ACCESS
              </span>

              <h2>Knowledge base</h2>
            </div>

            <div className="admin-badge">
              ADMIN
            </div>

          </div>

          <p className="admin-description">
            Add or remove internal documents used
            by the AI assistant.
          </p>

          {/* Upload button */}

          <input
            ref={fileInputRef}
            type="file"
            multiple
            accept=".pdf,.docx,.txt"
            className="hidden-file-input"
            onChange={handleFileUpload}
          />

          <button
            className="upload-button"
            onClick={openFilePicker}
            disabled={uploading}
          >
            <div className="upload-icon">
              {uploading ? "…" : "↑"}
            </div>

            <div className="upload-text">
              <strong>
                {uploading
                  ? "Uploading..."
                  : "Add documents"}
              </strong>

              <span>
                PDF, DOCX or TXT
              </span>
            </div>

            <span className="upload-arrow">
              →
            </span>
          </button>

          {/* Documents */}

          <div className="documents-header">
            <span>
              DOCUMENTS
            </span>

            <span>
              {documentLoading
                ? "..."
                : documents.length}
            </span>
          </div>

          <div className="document-list">

            {documents.length === 0 ? (
              <div className="empty-documents">

                <div className="empty-document-icon">
                  ◫
                </div>

                <div>
                  <strong>
                    No documents
                  </strong>

                  <span>
                    Add your first knowledge
                    base document.
                  </span>
                </div>

              </div>
            ) : (
              documents.map((document, index) => (
                <div
                  className="document-item"
                  key={
                    document.id ||
                    document.filename ||
                    document.file ||
                    index
                  }
                >

                  <div className="document-type">
                    {getDocumentType(document)}
                  </div>

                  <div className="document-info">
                    <strong>
                      {getDocumentName(document)}
                    </strong>

                    <span>
                      Knowledge base document
                    </span>
                  </div>

                  <button
                    className="remove-document"
                    title="Remove document"
                    onClick={() =>
                      removeDocument(document)
                    }
                  >
                    ×
                  </button>

                </div>
              ))
            )}

          </div>

        </section>

        {/* Footer */}

        <div className="left-footer">

          <div className="system-status">
            <span className="status-dot"></span>

            <div>
              <strong>
                Knowledge base online
              </strong>

              <span>
                RAG system operational
              </span>
            </div>
          </div>

          <span className="version">
            v1.0 · Enterprise Support AI
          </span>

        </div>

      </aside>

      {/* ========================================================= */}
      {/* RIGHT 70% CHAT */}
      {/* ========================================================= */}

      <main className="chat-panel">

        {/* Chat header */}

        <header className="chat-header">

          <div className="chat-header-left">

            <div className="chat-ai-icon">
              ✦
            </div>

            <div>
              <span className="chat-header-label">
                AI SUPPORT
              </span>

              <h2>
                Enterprise Support
              </h2>
            </div>

          </div>

          <div className="ai-status">
            <span></span>
            AI Online
          </div>

        </header>

        {/* Chat body */}

        <section className="chat-body">

          {messages.length === 0 ? (

            <div className="welcome-screen">

              <div className="welcome-orb">
                <div className="orb-ring ring-one"></div>
                <div className="orb-ring ring-two"></div>

                <div className="orb-core">
                  ✦
                </div>
              </div>

              <span className="welcome-eyebrow">
                ENTERPRISE KNOWLEDGE ASSISTANT
              </span>

              <h1>
                How can I help
                <span> today?</span>
              </h1>

              <p>
                Ask questions about internal IT
                procedures, troubleshooting guides,
                products and company documentation.
              </p>

              <div className="suggestions">

                <button
                  onClick={() =>
                    handleSuggestion(
                      "I forgot my password. How can I reset it?"
                    )
                  }
                >
                  <span className="suggestion-symbol">
                    ⌘
                  </span>

                  <div>
                    <strong>
                      Reset password
                    </strong>

                    <span>
                      Recover account access
                    </span>
                  </div>

                  <span>→</span>
                </button>

                <button
                  onClick={() =>
                    handleSuggestion(
                      "I cannot connect to the company VPN."
                    )
                  }
                >
                  <span className="suggestion-symbol">
                    ◉
                  </span>

                  <div>
                    <strong>
                      VPN troubleshooting
                    </strong>

                    <span>
                      Resolve connection problems
                    </span>
                  </div>

                  <span>→</span>
                </button>

                <button
                  onClick={() =>
                    handleSuggestion(
                      "I am having trouble logging into my account."
                    )
                  }
                >
                  <span className="suggestion-symbol">
                    ◌
                  </span>

                  <div>
                    <strong>
                      Login issues
                    </strong>

                    <span>
                      Troubleshoot account access
                    </span>
                  </div>

                  <span>→</span>
                </button>

                <button
                  onClick={() =>
                    handleSuggestion(
                      "What should I do if CloudSync is not working?"
                    )
                  }
                >
                  <span className="suggestion-symbol">
                    ◇
                  </span>

                  <div>
                    <strong>
                      CloudSync
                    </strong>

                    <span>
                      Get product support
                    </span>
                  </div>

                  <span>→</span>
                </button>

              </div>

            </div>

          ) : (

            <div className="messages-container">

              {messages.map((message, index) => (

                <div
                  className={`message-row ${message.role}`}
                  key={index}
                >

                  <div
                    className={`message-avatar ${
                      message.role === "user"
                        ? "user-avatar"
                        : "ai-avatar"
                    }`}
                  >
                    {message.role === "user"
                      ? "P"
                      : "✦"}
                  </div>

                  <div className="message-content">

                    <div className="message-meta">

                      <strong>
                        {message.role === "user"
                          ? "You"
                          : "Support AI"}
                      </strong>

                      {message.role ===
                        "assistant" &&
                        !message.error && (
                          <span className="grounded">
                            ● GROUNDED
                          </span>
                        )}

                    </div>

                    <div
                      className={`message-bubble ${
                        message.error
                          ? "error-message"
                          : ""
                      }`}
                    >
                      {message.content}
                    </div>

                    {/* Sources */}

                    {message.sources &&
                      message.sources.length >
                        0 && (

                        <div className="sources">

                          <div className="sources-title">
                            <span></span>
                            REFERENCED DOCUMENTS
                          </div>

                          <div className="source-grid">

                            {message.sources.map(
                              (
                                source,
                                sourceIndex
                              ) => (

                                <div
                                  className="source-card"
                                  key={sourceIndex}
                                >

                                  <div className="source-file-icon">
                                    ◫
                                  </div>

                                  <div>
                                    <strong>
                                      {source.file ||
                                        source.source ||
                                        "Document"}
                                    </strong>

                                    <span>
                                      {source.page &&
                                        source.page !==
                                          "Unknown" &&
                                        `Page ${source.page}`}

                                      {source.chunk !==
                                        undefined &&
                                        ` · Chunk ${source.chunk}`}
                                    </span>
                                  </div>

                                </div>

                              )
                            )}

                          </div>

                        </div>

                      )}

                  </div>

                </div>

              ))}

              {loading && (

                <div className="message-row assistant">

                  <div className="message-avatar ai-avatar">
                    ✦
                  </div>

                  <div className="message-content">

                    <div className="message-meta">
                      <strong>
                        Support AI
                      </strong>
                    </div>

                    <div className="thinking-card">

                      <div className="thinking-icon">
                        ✦
                      </div>

                      <div>
                        <strong>
                          Searching knowledge base
                        </strong>

                        <span>
                          Finding relevant internal
                          documentation...
                        </span>
                      </div>

                      <div className="thinking-dots">
                        <i></i>
                        <i></i>
                        <i></i>
                      </div>

                    </div>

                  </div>

                </div>

              )}

              <div ref={messagesEndRef}></div>

            </div>

          )}

        </section>

        {/* Error */}

        {error && (
          <div className="error-banner">
            <span>!</span>
            {error}
          </div>
        )}

        {/* Input */}

        <footer className="chat-input-area">

          <form
            className="chat-input"
            onSubmit={sendMessage}
          >

            <div className="input-ai-icon">
              ✦
            </div>

            <textarea
              value={query}
              onChange={(event) =>
                setQuery(event.target.value)
              }
              onKeyDown={handleKeyDown}
              placeholder="Ask anything about your enterprise support documentation..."
              rows="1"
              disabled={loading}
            />

            <button
              type="submit"
              disabled={
                loading ||
                !query.trim()
              }
              className="send-button"
            >
              {loading ? (
                <span className="button-spinner"></span>
              ) : (
                "↑"
              )}
            </button>

          </form>

          <div className="input-footer">
            <span>
              ↵ Enter to send · Shift + Enter for new line
            </span>

            <span>
              Answers are grounded in internal documentation
            </span>
          </div>

        </footer>

      </main>

    </div>
  );
}

export default App;