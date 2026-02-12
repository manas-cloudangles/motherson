import { useState, useRef, useMemo, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { usePageProgress } from '../context/PageProgressContext'
import './ChatPage.css'

function ChatPage() {
  const navigate = useNavigate()
  const { markPageComplete, updateAppData, appData } = usePageProgress()
  const folderRef = useRef(null) // Use ref for heavy file data
  const [fileCount, setFileCount] = useState(0) // Track count for UI
  const [folderStructure, setFolderStructure] = useState(null) // Track tree for UI
  // Using uncontrolled textarea to avoid re-renders on every keystroke
  const initialDevRequest = appData.devRequest || ''
  const [isLoading, setIsLoading] = useState(false)
  const fileInputRef = useRef(null)
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

  const handleFolderChange = (e) => {
    const files = Array.from(e.target.files)
    folderRef.current = files
    setFileCount(files.length)
    setFolderStructure(buildFolderTree(files))
    updateAppData({ folder: files })
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    const devRequestValue = textareaRef.current?.value?.trim() || ''
    const currentFolder = folderRef.current
    if (!currentFolder || currentFolder.length === 0 || !devRequestValue || isLoading) return

    setIsLoading(true)
    updateAppData({ devRequest: devRequestValue })

    try {
      // Prepare FormData with files and page request
      const formData = new FormData()
      currentFolder.forEach((file) => {
        // Create a new File object with webkitRelativePath in the name if available
        // This preserves the directory structure
        const relativePath = file.webkitRelativePath || file.name
        const fileWithPath = new File([file], relativePath, { type: file.type })
        formData.append('files', fileWithPath)
      })
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

      // Store components in context for ElementsPage
      updateAppData({
        components: data.components || [],
        devRequest: devRequestValue.trim()
      })

      // Mark chat as complete when submission is successful
      markPageComplete('chat')

      // Navigate to elements page after processing is complete
      navigate('/elements')
    } catch (error) {
      console.error('Error submitting folder and request:', error)
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
            <p>Analyzing components... This may take a moment.</p>
          </div>
        )}
        <div
          className={`folder-structure-container ${!folderStructure ? 'folder-upload-area' : ''}`}
          onClick={() => !folderStructure && !isLoading && fileInputRef.current?.click()}
        >
          {folderStructure ? (
            <>
              <h3 className="folder-structure-title">Folder Structure</h3>
              <div className="folder-structure-tree">
                {renderFolderTreeWrapper()}
              </div>
            </>
          ) : (
            <div className="folder-upload-placeholder">
              <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                <polyline points="17 8 12 3 7 8"></polyline>
                <line x1="12" y1="3" x2="12" y2="15"></line>
              </svg>
              <p>Please upload reference folder</p>
            </div>
          )}
        </div>
        <form className="chat-input-form" onSubmit={handleSubmit}>
          <div className="chat-input-container">
            <input
              ref={fileInputRef}
              type="file"
              webkitdirectory=""
              directory=""
              multiple
              onChange={handleFolderChange}
              className="chat-input file-input"
              disabled={isLoading}
              style={{ display: 'none' }}
            />
            <button
              type="button"
              onClick={() => fileInputRef.current?.click()}
              className="folder-button"
              disabled={isLoading}
            >
              {fileCount > 0 ? `${fileCount} file(s) selected` : 'Select Folder'}
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
              disabled={!fileCount || fileCount === 0 || isLoading}
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
