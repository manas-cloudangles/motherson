import { useState, useRef, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, Link, useLocation, Navigate } from 'react-router-dom'
import ChatPage from './pages/ChatPage'
import ElementsPage from './pages/ElementsPage'
import DownloadPage from './pages/DownloadPage'
import { PageProgressProvider, usePageProgress } from './context/PageProgressContext'
import FileExplorer from './components/FileExplorer'
import './App.css'

function TopBar() {
  return (
    <nav className="topbar">
      <div className="topbar-container">
        <div className="codebenders-logo">
          <img src="/codebenders-logo.svg" alt="Codebenders Logo" className="codebenders-logo-img" />
        </div>
        <Link to="/" className="motherson-logo">
          <img src="/motherson-logo-png_seeklogo-544537.png" alt="Motherson Logo" className="motherson-logo-img" />
        </Link>
      </div>
    </nav>
  )
}

function RightSidebar() {
  const location = useLocation()
  const { isPageAccessible, completedPages, chatHistory, isChatLoading, sendChatMessage } = usePageProgress()
  const [isExpanded, setIsExpanded] = useState(false)
  const [chatInput, setChatInput] = useState('')
  const chatEndRef = useRef(null)

  // Scroll to bottom of chat
  useEffect(() => {
    if (isExpanded && chatEndRef.current) {
      chatEndRef.current.scrollIntoView({ behavior: 'smooth' })
    }
  }, [chatHistory, isExpanded])

  const getLinkClassName = (path, pageName) => {
    const baseClass = 'sidebar-link'
    const active = location.pathname === path ? ' active' : ''
    const locked = !isPageAccessible(pageName) ? ' locked' : ''
    return baseClass + active + locked
  }

  const handleLinkClick = (e, pageName) => {
    if (!isPageAccessible(pageName)) {
      e.preventDefault()
      e.stopPropagation()
    }
  }

  const toggleSidebar = () => {
    setIsExpanded(!isExpanded)
  }

  const handleSendMessage = () => {
    if (!chatInput.trim() || isChatLoading) return
    sendChatMessage(chatInput)
    setChatInput('')
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  return (
    <aside className={`sidebar sidebar-right ${isExpanded ? 'expanded' : ''}`}>
      <nav className="sidebar-nav">
        <Link
          to="/"
          className={getLinkClassName('/', 'chat')}
        >
          <span>Chat</span>
          {completedPages.chat && <span className="checkmark">✓</span>}
        </Link>
        {isPageAccessible('elements') ? (
          <Link
            to="/elements"
            className={getLinkClassName('/elements', 'elements')}
          >
            <span>Elements</span>
            {completedPages.elements && <span className="checkmark">✓</span>}
          </Link>
        ) : (
          <div className={getLinkClassName('/elements', 'elements')} onClick={(e) => handleLinkClick(e, 'elements')}>
            <span>Elements</span>
            <span className="lock-icon">🔒</span>
          </div>
        )}
        {isPageAccessible('download') ? (
          <Link
            to="/download"
            className={getLinkClassName('/download', 'download')}
          >
            <span>Download</span>
            {completedPages.download && <span className="checkmark">✓</span>}
          </Link>
        ) : (
          <div className={getLinkClassName('/download', 'download')} onClick={(e) => handleLinkClick(e, 'download')}>
            <span>Download</span>
            <span className="lock-icon">🔒</span>
          </div>
        )}
      </nav>

      {location.pathname === '/download' && (
        <button className="chat-toggle-btn" onClick={toggleSidebar}>
          {isExpanded ? (
            <>
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <polyline points="9 18 15 12 9 6"></polyline>
              </svg>
              Hide Chat
            </>
          ) : (
            <>
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
              </svg>
              Ask AI
            </>
          )}
        </button>
      )}

      {isExpanded && location.pathname === '/download' && (
        <div className="sidebar-chat-section">
          <div className="sidebar-chat-header">
            <h3>AI Assistant</h3>
          </div>

          <div className="sidebar-chat-messages">
            {chatHistory.length === 0 && (
              <div className="chat-message assistant">
                How can I help you today?
              </div>
            )}
            {chatHistory.map((msg, index) => (
              <div key={index} className={`chat-message ${msg.role}`}>
                {msg.content}
              </div>
            ))}
            {isChatLoading && (
              <div className="chat-message assistant">
                Thinking...
              </div>
            )}
            <div ref={chatEndRef} />
          </div>

          <div className="sidebar-chat-input-area">
            <textarea
              className="sidebar-chat-input"
              placeholder="Ask anything..."
              value={chatInput}
              onChange={(e) => setChatInput(e.target.value)}
              onKeyDown={handleKeyPress}
              disabled={isChatLoading}
            />
            <button
              className="sidebar-send-btn"
              onClick={handleSendMessage}
              disabled={!chatInput.trim() || isChatLoading}
            >
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <line x1="22" y1="2" x2="11" y2="13"></line>
                <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
              </svg>
            </button>
          </div>
        </div>
      )}
    </aside>
  )
}

function Footer() {
  return (
    <footer className="app-footer">
      <div className="footer-content">
        <div className="footer-logo">

          <img src="/codebenderslight.svg" alt="Codebenders Symbol" className="footer-symbol" />
        </div>
        <p className="footer-text">© 2026 Cloudangles. All rights reserved.</p>
      </div>
    </footer>
  )
}

function ProtectedRoute({ children, pageName }) {
  const { isPageAccessible } = usePageProgress()

  if (!isPageAccessible(pageName)) {
    return <Navigate to="/" replace />
  }

  return children
}

function AppContent() {
  const location = useLocation()
  const showFileExplorer = location.pathname === '/elements'

  return (
    <div className="app">
      <TopBar />
      <div className="app-body">
        {showFileExplorer && <FileExplorer />}
        <main className={`main-content ${!showFileExplorer ? 'main-content-full' : ''} ${location.pathname === '/' ? 'no-scroll' : ''}`}>
          <Routes>
            <Route path="/" element={<ChatPage />} />
            <Route
              path="/elements"
              element={
                <ProtectedRoute pageName="elements">
                  <ElementsPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/download"
              element={
                <ProtectedRoute pageName="download">
                  <DownloadPage />
                </ProtectedRoute>
              }
            />
          </Routes>
        </main>
        <RightSidebar />
      </div>
      <Footer />
    </div>
  )
}

function App() {
  return (
    <PageProgressProvider>
      <Router>
        <AppContent />
      </Router>
    </PageProgressProvider>
  )
}

export default App
