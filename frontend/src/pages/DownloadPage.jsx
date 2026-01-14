import { useState, useEffect } from 'react'
import { usePageProgress } from '../context/PageProgressContext'
import NoInputMessage from '../components/NoInputMessage'
import './DownloadPage.css'

function DownloadPage() {
  const { markPageComplete, completedPages, appData, updateAppData } = usePageProgress()
  const [htmlContent, setHtmlContent] = useState(appData.generatedFiles?.html || '')
  const [cssContent, setCssContent] = useState(appData.generatedFiles?.css || '')
  const [tsContent, setTsContent] = useState(appData.generatedFiles?.ts || '')
  const [previewContent, setPreviewContent] = useState('')
  const [activeTab, setActiveTab] = useState('html')
  const [isLoading, setIsLoading] = useState(false)
  const componentName = 'my-component' // This could come from appData or user input

  // Check if there's input from previous steps
  const hasInputFromPreviousSteps = completedPages.chat && completedPages.elements

  // Generate preview content combining HTML, CSS, and TS
  const generatePreviewContent = (html, css, ts) => {
    // Convert TypeScript to JavaScript for preview (basic conversion)
    // In a real scenario, you might want to use a TypeScript compiler
    let jsContent = ts
      .replace(/import\s+.*?from\s+['"].*?['"];?\s*/g, '') // Remove imports
      .replace(/@Component\s*\(\s*\{[^}]*\}\s*\)/g, '') // Remove decorators
      .replace(/export\s+class\s+(\w+)/g, 'class $1') // Remove export
      .replace(/:\s*\w+(\[\])?/g, '') // Remove type annotations
      .replace(/:\s*void/g, '') // Remove void return types
    
    // Convert Angular template syntax to vanilla JS
    let processedHtml = html
      .replace(/\(click\)="([^"]+)"/g, 'onclick="$1"') // Convert (click) to onclick
      .replace(/\[ngClass\]="([^"]+)"/g, '') // Remove ngClass
      .replace(/\[ngIf\]="([^"]+)"/g, '') // Remove ngIf
      .replace(/\*ngFor="([^"]+)"/g, '') // Remove ngFor
      .replace(/\{\{([^}]+)\}\}/g, '<span>$1</span>') // Convert interpolation (basic)
    
    return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Component Preview</title>
    <style>
        ${css}
    </style>
</head>
<body>
    ${processedHtml}
    <script>
        ${jsContent}
        // Initialize component methods globally for onclick handlers
        if (typeof MyComponentComponent !== 'undefined') {
            window.component = new MyComponentComponent();
            // Make methods available globally
            if (window.component.handleClick) {
                window.handleClick = function() { window.component.handleClick(); };
            }
        }
    </script>
</body>
</html>`
  }

  useEffect(() => {
    // Only show content if previous pages are completed
    if (!completedPages.chat || !completedPages.elements) {
      setHtmlContent('')
      setCssContent('')
      setTsContent('')
      setPreviewContent('')
      return
    }

    // Use pre-generated content from appData (generated in ElementsPage)
    if (appData.generatedFiles?.html && appData.generatedFiles?.css && appData.generatedFiles?.ts) {
      const { html, css, ts } = appData.generatedFiles
      setHtmlContent(html)
      setCssContent(css)
      setTsContent(ts)
      const preview = generatePreviewContent(html, css, ts)
      setPreviewContent(preview)
      setIsLoading(false)
    } else {
      // This should not happen if the flow is correct
      console.error('No generated files found in appData')
      setIsLoading(false)
    }
  }, [completedPages.chat, completedPages.elements, appData.generatedFiles])

  const handleSave = () => {
    const newPreview = generatePreviewContent(htmlContent, cssContent, tsContent)
    setPreviewContent(newPreview)
    updateAppData({
      generatedFiles: {
        html: htmlContent,
        css: cssContent,
        ts: tsContent
      }
    })
  }

  const downloadFile = (content, filename, mimeType) => {
    if (!content) return
    
    const blob = new Blob([content], { type: mimeType })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = filename
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
    
    // Mark download page as complete when user downloads a file
    if (!completedPages.download) {
      markPageComplete('download')
    }
  }

  const downloadHTML = () => {
    downloadFile(htmlContent, `${componentName}.html`, 'text/html')
  }

  const downloadCSS = () => {
    downloadFile(cssContent, `${componentName}.css`, 'text/css')
  }

  const downloadTS = () => {
    downloadFile(tsContent, `${componentName}.component.ts`, 'text/typescript')
  }

  const downloadAll = () => {
    downloadHTML()
    setTimeout(() => downloadCSS(), 200)
    setTimeout(() => downloadTS(), 400)
  }

  // Show empty state if previous pages not completed
  if (!hasInputFromPreviousSteps) {
    return (
      <div className="download-page">
        <div className="download-container">
          <NoInputMessage />
        </div>
      </div>
    )
  }

  if (isLoading) {
    return (
      <div className="download-page">
        <div className="download-container">
          <div className="empty-state">
            <h2>Generating Files...</h2>
            <p>Please wait while we generate your Angular component files.</p>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="download-page">
      <div className="download-container">
        <div className="download-layout">
          {/* Left Side - Preview */}
          <div className="preview-section">
            <div className="preview-header">
              <h2>Component Preview</h2>
            </div>
            <div className="preview-container">
              {previewContent ? (
                <iframe
                  title="Component Preview"
                  srcDoc={previewContent}
                  className="preview-iframe"
                  sandbox="allow-scripts allow-same-origin"
                />
              ) : (
                <div className="preview-placeholder">
                  <p>Click "Save" to preview your component</p>
                </div>
              )}
            </div>
          </div>

          {/* Right Side - Code Editor */}
          <div className="editor-section">
            <div className="editor-header">
              <h2>Code Editor</h2>
              <div className="editor-actions">
                <button className="save-btn" onClick={handleSave}>
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"></path>
                    <polyline points="17 21 17 13 7 13 7 21"></polyline>
                    <polyline points="7 3 7 8 15 8"></polyline>
                  </svg>
                  Save
                </button>
                <button className="download-all-btn" onClick={downloadAll}>
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                    <polyline points="7 10 12 15 17 10"></polyline>
                    <line x1="12" y1="15" x2="12" y2="3"></line>
                  </svg>
                  Download All
                </button>
              </div>
            </div>

            {/* Tabs */}
            <div className="editor-tabs">
              <button
                className={`editor-tab ${activeTab === 'html' ? 'active' : ''}`}
                onClick={() => setActiveTab('html')}
              >
                HTML
              </button>
              <button
                className={`editor-tab ${activeTab === 'css' ? 'active' : ''}`}
                onClick={() => setActiveTab('css')}
              >
                CSS
              </button>
              <button
                className={`editor-tab ${activeTab === 'ts' ? 'active' : ''}`}
                onClick={() => setActiveTab('ts')}
              >
                TypeScript
              </button>
            </div>

            {/* Code Editor */}
            <div className="code-editor-container">
              {activeTab === 'html' && (
                <textarea
                  className="code-editor"
                  value={htmlContent}
                  onChange={(e) => setHtmlContent(e.target.value)}
                  placeholder="Enter HTML code..."
                  spellCheck={false}
                />
              )}
              {activeTab === 'css' && (
                <textarea
                  className="code-editor"
                  value={cssContent}
                  onChange={(e) => setCssContent(e.target.value)}
                  placeholder="Enter CSS code..."
                  spellCheck={false}
                />
              )}
              {activeTab === 'ts' && (
                <textarea
                  className="code-editor"
                  value={tsContent}
                  onChange={(e) => setTsContent(e.target.value)}
                  placeholder="Enter TypeScript code..."
                  spellCheck={false}
                />
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default DownloadPage
