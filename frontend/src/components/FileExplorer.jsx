import { useState, useMemo, useRef, useEffect } from 'react'
import { useLocation } from 'react-router-dom'
import { usePageProgress } from '../context/PageProgressContext'
import './FileExplorer.css'

function FileExplorer() {
  const location = useLocation()
  const { appData } = usePageProgress()
  const [expandedFolders, setExpandedFolders] = useState(new Set())
  const [sidebarWidth, setSidebarWidth] = useState(250)
  const [isResizing, setIsResizing] = useState(false)
  const sidebarRef = useRef(null)
  const resizeHandleRef = useRef(null)
  
  // Check if we're on the first page (ChatPage)
  const isFirstPage = location.pathname === '/'
  
  // Build folder tree structure from files
  const folderStructure = useMemo(() => {
    if (!appData.folder || appData.folder.length === 0) return null

    const tree = {}
    
    appData.folder.forEach((file) => {
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
  }, [appData.folder])
  
  // Initialize all folders as expanded by default
  useEffect(() => {
    if (folderStructure) {
      const allFolders = new Set()
      const collectFolders = (node, path = '') => {
        const dirKeys = Object.keys(node).filter(key => key !== '_files')
        dirKeys.forEach((dirName) => {
          const newPath = path ? `${path}/${dirName}` : dirName
          allFolders.add(newPath)
          collectFolders(node[dirName], newPath)
        })
      }
      collectFolders(folderStructure)
      setExpandedFolders(allFolders)
    }
  }, [folderStructure])
  
  // Handle sidebar resizing
  useEffect(() => {
    const handleMouseMove = (e) => {
      if (!isResizing) return
      const newWidth = e.clientX
      if (newWidth >= 200 && newWidth <= 600) {
        setSidebarWidth(newWidth)
      }
    }
    
    const handleMouseUp = () => {
      setIsResizing(false)
      document.body.classList.remove('resizing')
    }
    
    if (isResizing) {
      document.body.classList.add('resizing')
      document.addEventListener('mousemove', handleMouseMove)
      document.addEventListener('mouseup', handleMouseUp)
      return () => {
        document.body.classList.remove('resizing')
        document.removeEventListener('mousemove', handleMouseMove)
        document.removeEventListener('mouseup', handleMouseUp)
      }
    }
  }, [isResizing])
  
  const toggleFolder = (path) => {
    setExpandedFolders(prev => {
      const newSet = new Set(prev)
      if (newSet.has(path)) {
        newSet.delete(path)
      } else {
        newSet.add(path)
      }
      return newSet
    })
  }

  // Render folder tree recursively with VS Code-style expandable folders
  const renderFolderTree = (node, level = 0, path = '') => {
    const items = []
    const dirKeys = Object.keys(node).filter(key => key !== '_files').sort()
    const fileCount = node._files ? node._files.length : 0

    // Render directories first
    dirKeys.forEach((dirName) => {
      const newPath = path ? `${path}/${dirName}` : dirName
      const isExpanded = expandedFolders.has(newPath)
      const hasChildren = Object.keys(node[dirName]).length > 0 || (node[dirName]._files && node[dirName]._files.length > 0)
      
      items.push(
        <div 
          key={newPath} 
          className="file-explorer-item file-explorer-folder" 
          style={{ paddingLeft: `${level * 16 + 8}px` }}
          onClick={() => hasChildren && toggleFolder(newPath)}
        >
          <span className={`file-explorer-chevron ${isExpanded ? 'expanded' : ''}`}>
            {hasChildren ? (
              <svg width="12" height="12" viewBox="0 0 12 12" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M4 2 L8 6 L4 10" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
            ) : (
              <span style={{ width: '12px', display: 'inline-block' }}></span>
            )}
          </span>
          <span className="file-explorer-icon">📁</span>
          <span className="file-explorer-name">{dirName}</span>
        </div>
      )
      
      // Only render children if folder is expanded
      if (isExpanded) {
        items.push(...renderFolderTree(node[dirName], level + 1, newPath))
      }
    })

    // Render files (always show root files, or show files if parent folder is expanded)
    if (node._files) {
      const shouldShowFiles = path === '' || expandedFolders.has(path)
      if (shouldShowFiles) {
        node._files
          .sort((a, b) => a.name.localeCompare(b.name))
          .forEach((fileItem) => {
            const filePath = path ? `${path}/${fileItem.name}` : fileItem.name
            const fileExtension = fileItem.name.split('.').pop()?.toLowerCase() || ''
            const icon = getFileIcon(fileExtension)
            
            items.push(
              <div key={filePath} className="file-explorer-item file-explorer-file" style={{ paddingLeft: `${level * 16 + 8}px` }}>
                <span className="file-explorer-chevron">
                  <span style={{ width: '12px', display: 'inline-block' }}></span>
                </span>
                <span className="file-explorer-icon">{icon}</span>
                <span className="file-explorer-name">{fileItem.name}</span>
              </div>
            )
          })
      }
    }

    return items
  }

  const getFileIcon = (extension) => {
    const iconMap = {
      'js': '📄',
      'jsx': '⚛️',
      'ts': '📘',
      'tsx': '⚛️',
      'html': '🌐',
      'css': '🎨',
      'json': '📋',
      'md': '📝',
      'py': '🐍',
      'java': '☕',
      'cpp': '⚙️',
      'c': '⚙️',
      'go': '🐹',
      'rs': '🦀',
      'php': '🐘',
      'rb': '💎',
      'xml': '📄',
      'yaml': '📄',
      'yml': '📄',
      'txt': '📄',
      'png': '🖼️',
      'jpg': '🖼️',
      'jpeg': '🖼️',
      'gif': '🖼️',
      'svg': '🖼️',
    }
    return iconMap[extension] || '📄'
  }

  // On first page, always show empty state
  // On other pages, show folder structure if available
  if (isFirstPage || !folderStructure) {
    return (
      <>
        <aside 
          ref={sidebarRef}
          className="file-explorer file-explorer-empty" 
          style={{ width: `${sidebarWidth}px` }}
        >
          <div className="file-explorer-header">
            <span className="file-explorer-title">Explorer</span>
          </div>
          <div className="file-explorer-empty-state">
            <p>{isFirstPage ? 'No folder uploaded' : 'No folder uploaded'}</p>
          </div>
        </aside>
        <div 
          ref={resizeHandleRef}
          className="file-explorer-resize-handle"
          onMouseDown={(e) => {
            e.preventDefault()
            setIsResizing(true)
          }}
        />
      </>
    )
  }

  return (
    <>
      <aside 
        ref={sidebarRef}
        className="file-explorer" 
        style={{ width: `${sidebarWidth}px` }}
      >
        <div className="file-explorer-header">
          <span className="file-explorer-title">Explorer</span>
        </div>
        <div className="file-explorer-content">
          {renderFolderTree(folderStructure)}
        </div>
      </aside>
      <div 
        ref={resizeHandleRef}
        className="file-explorer-resize-handle"
        onMouseDown={(e) => {
          e.preventDefault()
          setIsResizing(true)
        }}
      />
    </>
  )
}

export default FileExplorer
