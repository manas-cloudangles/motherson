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
  const { isPageAccessible, completedPages } = usePageProgress()
  
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
  
  return (
    <aside className="sidebar sidebar-right">
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
    </aside>
  )
}

function Footer() {
  return (
    <footer className="app-footer">
      <div className="footer-content">
        <div className="footer-logo">
          <img src="/motherson-logo-png_seeklogo-544537.png" alt="Motherson Logo" className="footer-logo-img" />
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
        <main className={`main-content ${!showFileExplorer ? 'main-content-full' : ''}`}>
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
