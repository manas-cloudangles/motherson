import { useState, useRef, useMemo, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { usePageProgress } from '../context/PageProgressContext'
import './ChatPage.css'

function ChatPage() {
  const navigate = useNavigate()
  const { markPageComplete, updateAppData, appData } = usePageProgress()
  
  // Frontend (Angular components) refs and state
  const frontendFolderRef = useRef(null)
  const [frontendFileCount, setFrontendFileCount] = useState(0)
  const [frontendFolderStructure, setFrontendFolderStructure] = useState(null)
  const frontendFileInputRef = useRef(null)
  
  // Backend (PHP APIs) refs and state
  const backendFolderRef = useRef(null)
  const [backendFileCount, setBackendFileCount] = useState(0)
  const [backendFolderStructure, setBackendFolderStructure] = useState(null)
  const backendFileInputRef = useRef(null)
  
  // Common state
  const initialDevRequest = appData.devRequest || ''
  const [isLoading, setIsLoading] = useState(false)
  const textareaRef = useRef(null)

  // Auto-resize textarea
  const adjustTextareaHeight = () => {
    const textarea = textareaRef.current
    if (textarea) {
      textarea.style.height = 'auto'
      textarea.style.height = `${Math.min(textarea.scrollHeight, 200)}px`
    }
  }

  useEffect(() => {
    adjustTextareaHeight()
  }, [])

  // Build folder tree structure from files
  // Helper to build folder tree structure from files
  const buildFolderTree = (files) => {
    if (!files || files.length === 0) return null

    const tree = {}

    files.forEach((file) => {
      const path = file.webkitRelativePath || file.name
      const parts = path.split('/')
      let current = tree

      parts.forEach((part, index) => {
        if (index === parts.length - 1) {
          // This is a file
          if (!current._files) current._files = []
          current._files.push({ name: part, file })
        } else {
          // This is a directory
          if (!current[part]) {
            current[part] = {}
          }
          current = current[part]
        }
      })
    })

    return tree
  }

  // Render folder tree recursively with text-based tree format
  // Limit rendering to prevent lag with large file counts
  const MAX_VISIBLE_ITEMS = 100
  let renderedCount = 0

  const renderFolderTree = (node, level = 0, path = '', prefix = '', isLast = true) => {
    const items = []

    // Check if we've already hit the limit
    if (renderedCount >= MAX_VISIBLE_ITEMS) {
      return items
    }

    const dirKeys = Object.keys(node).filter(key => key !== '_files').sort()
    const fileCount = node._files ? node._files.length : 0

    // Render directories first
    for (const dirName of dirKeys) {
      if (renderedCount >= MAX_VISIBLE_ITEMS) {
        items.push(
          <div key="ellipsis-dir" className="folder-tree-line folder-tree-ellipsis">
            {prefix}└─ ... and more
          </div>
        )
        renderedCount++ // Prevent duplicate ellipsis
        return items
      }

      const newPath = path ? `${path}/${dirName}` : dirName
      const isLastDir = dirKeys.indexOf(dirName) === dirKeys.length - 1 && fileCount === 0
      const currentPrefix = isLastDir ? '└─' : '├─'
      const nextPrefix = isLastDir ? prefix + '   ' : prefix + '│  '

      items.push(
        <div key={newPath} className="folder-tree-line">
          {prefix}{currentPrefix} {dirName}/
        </div>
      )
      renderedCount++

      items.push(...renderFolderTree(node[dirName], level + 1, newPath, nextPrefix, isLastDir))
    }

    // Render files
    if (node._files) {
      const sortedFiles = node._files.sort((a, b) => a.name.localeCompare(b.name))
      for (let i = 0; i < sortedFiles.length; i++) {
        if (renderedCount >= MAX_VISIBLE_ITEMS) {
          items.push(
            <div key="ellipsis-file" className="folder-tree-line folder-tree-ellipsis">
              {prefix}└─ ... and {sortedFiles.length - i} more files
            </div>
          )
          renderedCount++ // Prevent duplicate ellipsis
          break
        }

        const fileItem = sortedFiles[i]
        const isLastFile = i === sortedFiles.length - 1
        const currentPrefix = isLastFile ? '└─' : '├─'
        items.push(
          <div key={`${path}/${fileItem.name}`} className="folder-tree-line">
            {prefix}{currentPrefix} {fileItem.name}
          </div>
        )
        renderedCount++
      }
    }

    return items
  }

  // Wrapper to reset count before each render
  const renderFolderTreeWrapper = () => {
    renderedCount = 0
    return renderFolderTree(folderStructure)
  }

  const handleFrontendFolderChange = (e) => {
    const files = Array.from(e.target.files)
    frontendFolderRef.current = files
    setFrontendFileCount(files.length)
    setFrontendFolderStructure(buildFolderTree(files))
    updateAppData({ frontendFolder: files })
  }

  const handleBackendFolderChange = (e) => {
    const files = Array.from(e.target.files)
    backendFolderRef.current = files
    setBackendFileCount(files.length)
    setBackendFolderStructure(buildFolderTree(files))
    updateAppData({ backendFolder: files })
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    const devRequestValue = textareaRef.current?.value?.trim() || ''
    const frontendFiles = frontendFolderRef.current
    const backendFiles = backendFolderRef.current
    
    // Require at least dev request and one set of files
    if (!devRequestValue || isLoading) return
    if ((!frontendFiles || frontendFiles.length === 0) && (!backendFiles || backendFiles.length === 0)) {
      alert('Please upload at least frontend or backend files')
      return
    }

    setIsLoading(true)
    updateAppData({ devRequest: devRequestValue })

    try {
      // Prepare FormData with both frontend and backend files
      const formData = new FormData()
      
      // Add frontend files
      if (frontendFiles && frontendFiles.length > 0) {
        frontendFiles.forEach((file) => {
          const relativePath = file.webkitRelativePath || file.name
          const fileWithPath = new File([file], relativePath, { type: file.type })
          formData.append('frontendFiles', fileWithPath)
        })
      }
      
      // Add backend files
      if (backendFiles && backendFiles.length > 0) {
        backendFiles.forEach((file) => {
          const relativePath = file.webkitRelativePath || file.name
          const fileWithPath = new File([file], relativePath, { type: file.type })
          formData.append('backendFiles', fileWithPath)
        })
      }
      
      formData.append('pageRequest', devRequestValue)

      // Call backend API
      const response = await fetch('http://localhost:5000/api/upload-and-analyze', {
        method: 'POST',
        body: formData
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: `Server error: ${response.status}` }))
        throw new Error(errorData.detail || `Server error: ${response.status}`)
      }

      const data = await response.json()

      if (data.status !== 'success') {
        throw new Error(data.message || 'Failed to analyze components')
      }

      // Store both frontend and backend data in context for ElementsPage
      updateAppData({
        components: data.frontend_components || [],
        backendApis: data.backend_apis || [],
        devRequest: devRequestValue.trim()
      })

      // Mark chat as complete when submission is successful
      markPageComplete('chat')

      // Navigate to elements page after processing is complete
      navigate('/elements')
    } catch (error) {
      console.error('Error submitting folders and request:', error)
      alert(`Error: ${error.message}\n\nMake sure the backend server is running on http://localhost:5000`)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="chat-page">
      <div className="chat-container">
        {isLoading && (
          <div className="loading-overlay">
            <div className="loading-spinner"></div>
            <p>Analyzing components and APIs... This may take a moment.</p>
          </div>
        )}
        
        {/* Split view: Frontend on left, Backend on right */}
        <div style={{ display: 'flex', gap: '1rem', marginBottom: '1rem' }}>
          {/* Frontend Upload Area */}
          <div
            className={`folder-structure-container ${!frontendFolderStructure ? 'folder-upload-area' : ''}`}
            onClick={() => !frontendFolderStructure && !isLoading && frontendFileInputRef.current?.click()}
            style={{ flex: 1 }}
          >
            {frontendFolderStructure ? (
              <>
                <h3 className="folder-structure-title">Frontend Components 🎨</h3>
                <div className="folder-structure-tree">
                  {(() => {
                    renderedCount = 0
                    return renderFolderTree(frontendFolderStructure)
                  })()}
                </div>
              </>
            ) : (
              <div className="folder-upload-placeholder">
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                  <polyline points="17 8 12 3 7 8"></polyline>
                  <line x1="12" y1="3" x2="12" y2="15"></line>
                </svg>
                <p>Upload Frontend (Angular)</p>
                <small style={{ color: '#888', marginTop: '0.5rem' }}>Optional: HTML, SCSS, TS files</small>
              </div>
            )}
          </div>

          {/* Backend Upload Area */}
          <div
            className={`folder-structure-container ${!backendFolderStructure ? 'folder-upload-area' : ''}`}
            onClick={() => !backendFolderStructure && !isLoading && backendFileInputRef.current?.click()}
            style={{ flex: 1 }}
          >
            {backendFolderStructure ? (
              <>
                <h3 className="folder-structure-title">Backend APIs 🐘</h3>
                <div className="folder-structure-tree">
                  {(() => {
                    renderedCount = 0
                    return renderFolderTree(backendFolderStructure)
                  })()}
                </div>
              </>
            ) : (
              <div className="folder-upload-placeholder">
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                  <polyline points="17 8 12 3 7 8"></polyline>
                  <line x1="12" y1="3" x2="12" y2="15"></line>
                </svg>
                <p>Upload Backend (PHP)</p>
                <small style={{ color: '#888', marginTop: '0.5rem' }}>Optional: PHP API files</small>
              </div>
            )}
          </div>
        </div>

        <form className="chat-input-form" onSubmit={handleSubmit}>
          <div className="chat-input-container">
            {/* Hidden file inputs */}
            <input
              ref={frontendFileInputRef}
              type="file"
              webkitdirectory=""
              directory=""
              multiple
              onChange={handleFrontendFolderChange}
              className="chat-input file-input"
              disabled={isLoading}
              style={{ display: 'none' }}
            />
            <input
              ref={backendFileInputRef}
              type="file"
              webkitdirectory=""
              directory=""
              multiple
              onChange={handleBackendFolderChange}
              className="chat-input file-input"
              disabled={isLoading}
              style={{ display: 'none' }}
            />
            
            <button
              type="button"
              onClick={() => frontendFileInputRef.current?.click()}
              className="folder-button"
              disabled={isLoading}
              style={{ marginRight: '0.5rem' }}
            >
              {frontendFileCount > 0 ? `Frontend: ${frontendFileCount} files` : 'Select Frontend'}
            </button>
            
            <button
              type="button"
              onClick={() => backendFileInputRef.current?.click()}
              className="folder-button"
              disabled={isLoading}
            >
              {backendFileCount > 0 ? `Backend: ${backendFileCount} files` : 'Select Backend'}
            </button>
            
            <textarea
              ref={textareaRef}
              defaultValue={initialDevRequest}
              onInput={adjustTextareaHeight}
              placeholder="Enter your development request..."
              className="chat-input chat-textarea"
              disabled={isLoading}
              rows={1}
            />
            <button
              type="submit"
              className="send-button"
              disabled={isLoading}
            >
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <line x1="22" y1="2" x2="11" y2="13"></line>
                <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
              </svg>
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default ChatPage
