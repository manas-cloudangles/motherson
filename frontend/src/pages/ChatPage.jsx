import { useState, useRef, useMemo, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { usePageProgress } from '../context/PageProgressContext'
import './ChatPage.css'

function ChatPage() {
  const navigate = useNavigate()
  const { markPageComplete, updateAppData, appData } = usePageProgress()
  const [folder, setFolder] = useState(null)
  const [devRequest, setDevRequest] = useState(appData.devRequest || '')
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
  }, [devRequest])

  // Build folder tree structure from files
  const folderStructure = useMemo(() => {
    if (!folder || folder.length === 0) return null

    const tree = {}
    
    folder.forEach((file) => {
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
  }, [folder])

  // Render folder tree recursively with text-based tree format
  const renderFolderTree = (node, level = 0, path = '', prefix = '', isLast = true) => {
    const items = []
    const dirKeys = Object.keys(node).filter(key => key !== '_files').sort()
    const fileCount = node._files ? node._files.length : 0
    const totalItems = dirKeys.length + fileCount

    let itemIndex = 0

    // Render directories first
    dirKeys.forEach((dirName, dirIndex) => {
      const newPath = path ? `${path}/${dirName}` : dirName
      const isLastDir = dirIndex === dirKeys.length - 1 && fileCount === 0
      const currentPrefix = isLastDir ? '└─' : '├─'
      const nextPrefix = isLastDir ? prefix + '   ' : prefix + '│  '

      items.push(
        <div key={newPath} className="folder-tree-line">
          {prefix}{currentPrefix} {dirName}/
        </div>
      )
      
      items.push(...renderFolderTree(node[dirName], level + 1, newPath, nextPrefix, isLastDir))
    })

    // Render files
    if (node._files) {
      node._files
        .sort((a, b) => a.name.localeCompare(b.name))
        .forEach((fileItem, fileIndex) => {
          const isLastFile = fileIndex === node._files.length - 1
          const currentPrefix = isLastFile ? '└─' : '├─'
          items.push(
            <div key={`${path}/${fileItem.name}`} className="folder-tree-line">
              {prefix}{currentPrefix} {fileItem.name}
            </div>
          )
        })
    }

    return items
  }

  const handleFolderChange = (e) => {
    const files = Array.from(e.target.files)
    setFolder(files)
    updateAppData({ folder: files })
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!folder || folder.length === 0 || !devRequest.trim() || isLoading) return

    setIsLoading(true)
    updateAppData({ devRequest: devRequest.trim() })

    try {
      // TODO: Replace with actual backend API endpoint
      const formData = new FormData()
      folder.forEach((file) => {
        formData.append('files', file)
      })
      formData.append('dev_request', devRequest.trim())

      // Simulate API call - replace with actual fetch
      // const response = await fetch('/api/analyze-folder', {
      //   method: 'POST',
      //   body: formData
      // })
      // const data = await response.json()

      // For now, simulate the API call
      await new Promise(resolve => setTimeout(resolve, 1000))

      // Mark chat as complete when submission is successful
      markPageComplete('chat')
      
      // Navigate to elements page after processing is complete
      navigate('/elements')
    } catch (error) {
      console.error('Error submitting folder and request:', error)
      // Handle error (show error message to user)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="chat-page">
      <div className="chat-container">
        <div 
          className={`folder-structure-container ${!folderStructure ? 'folder-upload-area' : ''}`}
          onClick={() => !folderStructure && fileInputRef.current?.click()}
        >
          {folderStructure ? (
            <>
              <h3 className="folder-structure-title">Folder Structure</h3>
              <div className="folder-structure-tree">
                {renderFolderTree(folderStructure)}
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
              {folder && folder.length > 0 ? `${folder.length} file(s) selected` : 'Select Folder'}
            </button>
            <textarea
              ref={textareaRef}
              value={devRequest}
              onChange={(e) => {
                setDevRequest(e.target.value)
                adjustTextareaHeight()
              }}
              onInput={adjustTextareaHeight}
              placeholder="Enter your development request..."
              className="chat-input chat-textarea"
              disabled={isLoading}
              rows={1}
            />
            <button
              type="submit"
              className="send-button"
              disabled={!folder || folder.length === 0 || !devRequest.trim() || isLoading}
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
