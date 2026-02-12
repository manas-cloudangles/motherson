import { useState, useEffect } from 'react'
import { usePageProgress } from '../context/PageProgressContext'
import NoInputMessage from '../components/NoInputMessage'
import './DownloadPage.css'
import { processReusableComponents } from '../utils/angularParser'

function DownloadPage() {
  const { markPageComplete, completedPages, appData, updateAppData } = usePageProgress()
  const [htmlContent, setHtmlContent] = useState(appData.generatedFiles?.html || '')
  const [scssContent, setScssContent] = useState(appData.generatedFiles?.scss || '')
  const [tsContent, setTsContent] = useState(appData.generatedFiles?.ts || '')
  const [previewContent, setPreviewContent] = useState('')
  const [activeTab, setActiveTab] = useState('html')
  const [isLoading, setIsLoading] = useState(false)
  // State for integration snippets (must be before any early returns)
  const [snippets, setSnippets] = useState(null)
  const [snippetsError, setSnippetsError] = useState(false)
  // State for backend integration code
  const [serviceCode, setServiceCode] = useState('')
  const [controllerCode, setControllerCode] = useState('')
  const [routesConfig, setRoutesConfig] = useState('')
  const [isLoadingIntegration, setIsLoadingIntegration] = useState(false)
  const [integrationError, setIntegrationError] = useState('')
  // For API: Use raw component name (e.g., "User Profile") for correct PascalCase
  const rawComponentName = appData.generatedFiles?.component_name?.replace('Component', '') || 'MyComponent'
  // For file naming: lowercase kebab-case
  const componentNameForFiles = rawComponentName.toLowerCase().replace(/\s+/g, '-') || 'my-component'

  // Check if there's input from previous steps
  const hasInputFromPreviousSteps = completedPages.chat && completedPages.elements

  // Output content state


  // Generate preview content combining HTML, SCSS, and TS
  const generatePreviewContent = (html, scss, ts) => {
    // Extract component class name from TypeScript
    const classMatch = ts.match(/export\s+class\s+(\w+)/)
    const className = classMatch ? classMatch[1] : 'Component'

    // Get component metadata from appData
    const componentsMetadata = appData.components || []

    // Process reusable components first
    const { html: processedHtml, componentStyles, componentScripts } = processReusableComponents(html, componentsMetadata)

    // Convert TypeScript to JavaScript for preview (basic conversion)
    let jsContent = ts
      .replace(/import\s+.*?from\s+['"].*?['"];?\s*/g, '') // Remove imports
      .replace(/@Component\s*\(\s*\{[^}]*\}\s*\)/g, '') // Remove decorators
      .replace(/export\s+class\s+(\w+)/g, 'class $1') // Remove export
      .replace(/:\s*\w+(\[\])?(\s*\|\s*\w+)?/g, '') // Remove type annotations
      .replace(/:\s*void/g, '') // Remove void return types
      .replace(/@Input\(\)/g, '') // Remove @Input decorators
      .replace(/@Output\(\)/g, '') // Remove @Output decorators
      .replace(/EventEmitter/g, '') // Remove EventEmitter
      .replace(/implements\s+\w+/g, '') // Remove implements

    // Convert Angular template syntax to vanilla JS/HTML (for remaining non-component elements)
    let finalHtml = processedHtml
      // Handle *ngFor - remove directive, show item
      .replace(/\*ngFor="let\s+(\w+)\s+of\s+([^"]+)"/g, (match, item, array) => {
        return `data-ngfor="${array}" data-item="${item}"`
      })
      // Handle *ngIf - Hide loading/empty states for "Happy Path" review
      .replace(/\*ngIf="([^"]+)"/g, (match, condition) => {
        const cond = condition.trim().toLowerCase();
        if (cond.includes('loading') ||
          (cond.includes('!') && (cond.includes('data') || cond.includes('record') || cond.includes('item'))) ||
          cond.includes('length === 0') ||
          cond.includes('error')) {
          return 'style="display: none !important;"';
        }
        return '';
      })
      // Handle (click) events - remove for preview
      .replace(/\(click\)="([^"]+)"/g, (match, handler) => {
        return ''
      })
      // Handle [ngClass]
      .replace(/\[ngClass\]="([^"]+)"/g, '')
      // Handle interpolation - convert to readable format
      .replace(/\{\{([^}]+)\}\}/g, (match, expr) => {
        const trimmed = expr.trim();
        // Mock methods
        if (trimmed.includes('(') && trimmed.includes(')')) {
          if (trimmed.includes('Date')) return 'Oct 24, 2023';
          return 'Sample Value';
        }
        return `<span class="interpolation">${trimmed}</span>`;
      })
      // Handle property binding [property]
      .replace(/\[([^\]]+)\]="([^"]+)"/g, (match, prop, value) => {
        // Special case: remove disabled binding to show enabled state
        if (prop === 'disabled') return '';
        return `${prop}="${value}"`
      })

    return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Component Preview</title>
    <style>
        * {
            box-sizing: border-box;
        }
        body {
            margin: 0;
            padding: 20px;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
        }
        .interpolation {
            background: #e3f2fd;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: monospace;
            font-size: 0.9em;
        }
        /* Allow buttons to be clickable for visual feedback, but prevent functionality */
        /* Links should not navigate */
        a {
            pointer-events: none;
            cursor: default;
        }
        /* Buttons can be clicked but won't do anything - allow visual feedback */
        button {
            cursor: pointer;
        }
        /* Inputs, selects, textareas should not be functional */
        input, select, textarea {
            pointer-events: none;
            cursor: default;
        }
        /* Reusable component styles */
        ${componentStyles}
        /* Page component styles */
        ${scss}
    </style>
</head>
<body>
    <div class="preview-wrapper">
        ${finalHtml}
    </div>
    <script>
        // Allow buttons to be clickable but prevent any functionality
        document.addEventListener('DOMContentLoaded', function() {
            // Prevent all click events from doing anything functional
            // Buttons can be clicked for visual feedback but won't execute any actions
            document.addEventListener('click', function(e) {
                const target = e.target;
                const isButton = target.tagName === 'BUTTON' || target.closest('button');
                const isLink = target.tagName === 'A' || target.closest('a');
                const isInput = target.tagName === 'INPUT' || target.tagName === 'SELECT' || target.tagName === 'TEXTAREA';
                const hasOnclick = target.hasAttribute('onclick') || target.closest('[onclick]');
                const isButtonRole = target.getAttribute('role') === 'button' || target.closest('[role="button"]');
                
                // Prevent navigation from links
                if (isLink) {
                    e.preventDefault();
                    e.stopPropagation();
                    e.stopImmediatePropagation();
                    return false;
                }
                
                // Prevent form inputs from working
                if (isInput) {
                    e.preventDefault();
                    e.stopPropagation();
                    return false;
                }
                
                // Allow buttons to be clicked but prevent any functionality
                // This allows hover/active states to work but prevents actual actions
                if (isButton || hasOnclick || isButtonRole) {
                    e.preventDefault();
                    e.stopPropagation();
                    e.stopImmediatePropagation();
                    // Don't return false here - allow the click to register for visual feedback
                    // but prevent any actual functionality
                }
            }, true); // Use capture phase to catch events early
            
            // Prevent form submissions
            document.addEventListener('submit', function(e) {
                e.preventDefault();
                e.stopPropagation();
                return false;
            }, true);
            
            // Prevent input changes (for preview purposes)
            document.addEventListener('change', function(e) {
                if (e.target.tagName === 'INPUT' || e.target.tagName === 'SELECT' || e.target.tagName === 'TEXTAREA') {
                    e.preventDefault();
                    e.stopPropagation();
                }
            }, true);
            
            // Remove all onclick handlers from elements to prevent functionality
            // But keep them clickable for visual feedback
            const elementsWithOnclick = document.querySelectorAll('[onclick]');
            elementsWithOnclick.forEach(function(el) {
                el.removeAttribute('onclick');
            });
            
            // Prevent any Angular event handlers from executing
            // Override handleAngularEvent to do nothing
            window.handleAngularEvent = function(handler) {
                // Do nothing - buttons are clickable but non-functional
                console.log('Button clicked (preview mode - no action):', handler);
            };
        });
        
        // Reusable component scripts
        ${componentScripts}
        
        // Page component script
        ${jsContent}
        
        // Initialize component if class exists
        if (typeof ${className} !== 'undefined') {
            try {
                window.component = new ${className}();
                console.log('Component initialized:', window.component);
            } catch(e) {
                console.log('Could not initialize component:', e);
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
      setScssContent('')
      setTsContent('')
      setPreviewContent('')
      return
    }

    // If we already have content in appData, use it and generate preview
    if (appData.generatedFiles?.html && appData.generatedFiles?.scss && appData.generatedFiles?.ts) {
      const { html, scss, ts } = appData.generatedFiles
      setHtmlContent(html)
      setScssContent(scss)
      setTsContent(ts)
      const preview = generatePreviewContent(html, scss, ts)
      setPreviewContent(preview)
      setIsLoading(false)
      return
    }

    // Don't regenerate if we're already loading (prevents duplicate calls)
    if (isLoading) {
      return
    }

    // Fetch or generate Angular component files from backend
    const generateFiles = async () => {
      setIsLoading(true)
      try {
        // 1. Start Generation Task (Background)
        const response = await fetch('http://localhost:5000/api/generate-page', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            pageRequest: appData.devRequest || ''
          })
        })

        if (!response.ok) {
          const errorData = await response.json().catch(() => ({ detail: `Server error: ${response.status}` }))
          throw new Error(errorData.detail || `Server error: ${response.status}`)
        }

        const initData = await response.json()
        const taskId = initData.task_id

        console.log(`Generation Task Started: ${taskId}. Polling...`)

        // 2. Poll for Results
        let data = null
        while (true) {
          const statusRes = await fetch(`http://localhost:5000/api/tasks/${taskId}`)
          if (!statusRes.ok) throw new Error('Failed to poll status')

          const taskStatus = await statusRes.json()

          if (taskStatus.status === 'completed') {
            data = taskStatus.result
            break
          } else if (taskStatus.status === 'failed') {
            throw new Error(taskStatus.error || 'Generation task failed')
          }

          // Wait 2 seconds
          await new Promise(resolve => setTimeout(resolve, 2000))
        }

        if (data.status !== 'success') {
          throw new Error(data.message || 'Failed to generate page')
        }

        // Backend returns: html_code, scss_code, ts_code
        const html = data.html_code || ''
        const scss = data.scss_code || ''
        const ts = data.ts_code || ''

        console.log('Received from backend:', {
          status: data.status,
          hasHtml: !!html,
          hasScss: !!scss,
          hasTs: !!ts
        })

        // Validate that we received actual code
        if (!html && !scss && !ts) {
          throw new Error('Backend returned empty code. Please check the backend logs.')
        }

        setHtmlContent(html)
        setScssContent(scss)
        setTsContent(ts)

        // Generate initial preview
        const initialPreview = generatePreviewContent(html, scss, ts)
        setPreviewContent(initialPreview)

        updateAppData({
          generatedFiles: {
            html: html,
            scss: scss,
            ts: ts,
            component_name: data.component_name,
            path_name: data.path_name,
            selector: data.selector
          }
        })

        // Mark download page as complete when files are generated
        markPageComplete('download')
      } catch (error) {
        console.error('Error generating files:', error)
        alert(`Error: ${error.message}\n\nMake sure the backend server is running on http://localhost:5000`)
      } finally {
        setIsLoading(false)
      }
    }

    generateFiles()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [completedPages.chat, completedPages.elements, appData.generatedFiles])

  const handleSave = () => {
    const newPreview = generatePreviewContent(htmlContent, scssContent, tsContent)
    setPreviewContent(newPreview)
    updateAppData({
      generatedFiles: {
        html: htmlContent,
        scss: scssContent,
        ts: tsContent,
        component_name: appData.generatedFiles?.component_name,
        path_name: appData.generatedFiles?.path_name,
        selector: appData.generatedFiles?.selector
      }
    })
  }

  // Update preview when code changes (only if we have at least HTML)
  useEffect(() => {
    if (htmlContent) {
      const newPreview = generatePreviewContent(htmlContent, scssContent || '', tsContent || '')
      setPreviewContent(newPreview)
    }
  }, [htmlContent, scssContent, tsContent])

  // Fetch integration snippets when component name changes
  useEffect(() => {
    if (rawComponentName) {
      setSnippetsError(false)
      fetch('http://localhost:5000/api/integration/generate-snippets', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ component_name: rawComponentName })
      })
        .then(res => res.json())
        .then(data => {
          if (data.status === 'success') {
            setSnippets(data.snippets)
          } else {
            setSnippetsError(true)
          }
        })
        .catch(err => {
          console.error("Failed to load integration snippets", err)
          setSnippetsError(true)
        })
    }
  }, [rawComponentName])

  // Fetch backend integration code (service + controller) when files are ready
  useEffect(() => {
    if (htmlContent && tsContent && rawComponentName && !isLoadingIntegration && !serviceCode) {
      setIsLoadingIntegration(true)
      setIntegrationError('')
      
      console.log('Starting backend integration generation for:', rawComponentName)
      
      fetch('http://localhost:5000/api/integration/generate-integration', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          component_name: rawComponentName,
          html_code: htmlContent,  // ✅ Send actual HTML code
          ts_code: tsContent,      // ✅ Send actual TS code
          use_workspace_files: false  // ✅ Don't rely on workspace
        })
      })
        .then(async res => {
          if (!res.ok) {
            const errorData = await res.json().catch(() => ({}))
            throw new Error(errorData.detail || `Server error: ${res.status}`)
          }
          return res.json()
        })
        .then(async (data) => {
          if (data.status === 'processing') {
            // Poll for results
            const taskId = data.task_id
            console.log('Backend integration generation started:', taskId)
            
            let pollCount = 0
            const maxPolls = 30 // Max 60 seconds (30 * 2s)
            
            while (pollCount < maxPolls) {
              const statusRes = await fetch(`http://localhost:5000/api/tasks/${taskId}`)
              const taskStatus = await statusRes.json()
              
              if (taskStatus.status === 'completed') {
                const result = taskStatus.result
                setServiceCode(result.service?.service_code || '')
                setControllerCode(result.controller?.controller_code || '')
                setRoutesConfig(result.routes || '')
                console.log('Backend integration generated successfully')
                setIsLoadingIntegration(false)
                return
              } else if (taskStatus.status === 'failed') {
                setIntegrationError(taskStatus.error || 'Failed to generate backend integration')
                console.error('Backend integration generation failed:', taskStatus.error)
                setIsLoadingIntegration(false)
                return
              }
              
              pollCount++
              // Wait 2 seconds before polling again
              await new Promise(resolve => setTimeout(resolve, 2000))
            }
            
            // Timeout
            setIntegrationError('Backend integration generation timed out')
            setIsLoadingIntegration(false)
          } else if (data.status === 'success') {
            setServiceCode(data.service?.service_code || '')
            setControllerCode(data.controller?.controller_code || '')
            setRoutesConfig(data.routes || '')
            setIsLoadingIntegration(false)
          } else {
            setIntegrationError(data.message || 'Failed to generate backend integration')
            setIsLoadingIntegration(false)
          }
        })
        .catch(err => {
          console.error("Failed to generate backend integration", err)
          setIntegrationError(err.message || 'Unknown error occurred')
          setIsLoadingIntegration(false)
        })
    }
  }, [htmlContent, tsContent, rawComponentName, isLoadingIntegration, serviceCode])

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
    downloadFile(htmlContent, `${componentNameForFiles}.component.html`, 'text/html')
  }

  const downloadSCSS = () => {
    downloadFile(scssContent, `${componentNameForFiles}.component.scss`, 'text/scss')
  }

  const downloadTS = () => {
    downloadFile(tsContent, `${componentNameForFiles}.component.ts`, 'text/typescript')
  }

  const downloadService = () => {
    if (serviceCode) {
      downloadFile(serviceCode, `${componentNameForFiles}.service.ts`, 'text/typescript')
    }
  }

  const downloadController = () => {
    if (controllerCode) {
      // Extract controller name from code or use component name
      const controllerMatch = controllerCode.match(/class\s+(\w+Controller)/)
      const controllerName = controllerMatch ? controllerMatch[1] : `${rawComponentName.replace(/\s+/g, '')}Controller`
      downloadFile(controllerCode, `${controllerName}.php`, 'text/plain')
    }
  }

  const downloadRoutes = () => {
    if (routesConfig) {
      downloadFile(routesConfig, `${componentNameForFiles}-routes.php`, 'text/plain')
    }
  }

  const downloadAll = () => {
    downloadHTML()
    setTimeout(() => downloadSCSS(), 200)
    setTimeout(() => downloadTS(), 400)
    if (serviceCode) setTimeout(() => downloadService(), 600)
    if (controllerCode) setTimeout(() => downloadController(), 800)
    if (routesConfig) setTimeout(() => downloadRoutes(), 1000)
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
                {isLoadingIntegration && (
                  <span style={{ marginRight: '10px', color: '#4CAF50', fontSize: '0.9em' }}>
                    ⚡ Generating backend...
                  </span>
                )}
                {serviceCode && !isLoadingIntegration && (
                  <span style={{ marginRight: '10px', color: '#4CAF50', fontSize: '0.9em' }}>
                    ✅ Backend ready
                  </span>
                )}
                <button className="save-btn" onClick={handleSave}>
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"></path>
                    <polyline points="17 21 17 13 7 13 7 21"></polyline>
                    <polyline points="7 3 7 8 15 8"></polyline>
                  </svg>
                  Update Preview
                </button>
                <button 
                  className="download-all-btn" 
                  onClick={downloadAll}
                  title={`Download ${serviceCode ? '6' : '3'} files: HTML, SCSS, TS${serviceCode ? ', Service, Controller, Routes' : ''}`}
                >
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                    <polyline points="7 10 12 15 17 10"></polyline>
                    <line x1="12" y1="15" x2="12" y2="3"></line>
                  </svg>
                  Download All {serviceCode ? '(6)' : '(3)'}
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
                className={`editor-tab ${activeTab === 'scss' ? 'active' : ''}`}
                onClick={() => setActiveTab('scss')}
              >
                SCSS
              </button>
              <button
                className={`editor-tab ${activeTab === 'ts' ? 'active' : ''}`}
                onClick={() => setActiveTab('ts')}
              >
                TypeScript
              </button>
              <button
                className={`editor-tab ${activeTab === 'service' ? 'active' : ''}`}
                onClick={() => setActiveTab('service')}
                title="Angular Service (HTTP calls)"
              >
                Service.ts 🔌
              </button>
              <button
                className={`editor-tab ${activeTab === 'controller' ? 'active' : ''}`}
                onClick={() => setActiveTab('controller')}
                title="PHP Backend Controller"
              >
                Controller.php 🐘
              </button>
              <button
                className={`editor-tab ${activeTab === 'routes' ? 'active' : ''}`}
                onClick={() => setActiveTab('routes')}
                title="PHP Routes Configuration"
              >
                Routes 🛣️
              </button>
              <button
                className={`editor-tab ${activeTab === 'integration' ? 'active' : ''}`}
                onClick={() => setActiveTab('integration')}
              >
                Integration 📋
              </button>
            </div>

            {/* Code Editor */}
            <div className="code-editor-container">
              {activeTab === 'html' && (
                <textarea
                  className="code-editor"
                  value={htmlContent}
                  onChange={(e) => setHtmlContent(e.target.value)}
                  placeholder={htmlContent ? "Enter HTML code..." : "Waiting for HTML code from backend..."}
                  spellCheck={false}
                />
              )}
              {activeTab === 'scss' && (
                <textarea
                  className="code-editor"
                  value={scssContent}
                  onChange={(e) => setScssContent(e.target.value)}
                  placeholder={scssContent ? "Enter SCSS code..." : "Waiting for SCSS code from backend..."}
                  spellCheck={false}
                />
              )}
              {activeTab === 'ts' && (
                <textarea
                  className="code-editor"
                  value={tsContent}
                  onChange={(e) => setTsContent(e.target.value)}
                  placeholder={tsContent ? "Enter TypeScript code..." : "Waiting for TypeScript code from backend..."}
                  spellCheck={false}
                />
              )}
              {activeTab === 'service' && (
                <div style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
                  {isLoadingIntegration ? (
                    <div style={{ padding: '20px', textAlign: 'center' }}>
                      <p>🔄 Generating Angular service...</p>
                    </div>
                  ) : integrationError ? (
                    <div style={{ padding: '20px', color: '#ff6b6b' }}>
                      <p>❌ Error: {integrationError}</p>
                    </div>
                  ) : serviceCode ? (
                    <textarea
                      className="code-editor"
                      value={serviceCode}
                      onChange={(e) => setServiceCode(e.target.value)}
                      placeholder="Angular Service code..."
                      spellCheck={false}
                      style={{ flex: 1 }}
                    />
                  ) : (
                    <div style={{ padding: '20px', textAlign: 'center', color: '#888' }}>
                      <p>⏳ Service will be generated after component is created...</p>
                    </div>
                  )}
                </div>
              )}
              {activeTab === 'controller' && (
                <div style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
                  {isLoadingIntegration ? (
                    <div style={{ padding: '20px', textAlign: 'center' }}>
                      <p>🔄 Generating PHP controller...</p>
                    </div>
                  ) : integrationError ? (
                    <div style={{ padding: '20px', color: '#ff6b6b' }}>
                      <p>❌ Error: {integrationError}</p>
                    </div>
                  ) : controllerCode ? (
                    <textarea
                      className="code-editor"
                      value={controllerCode}
                      onChange={(e) => setControllerCode(e.target.value)}
                      placeholder="PHP Controller code..."
                      spellCheck={false}
                      style={{ flex: 1 }}
                    />
                  ) : (
                    <div style={{ padding: '20px', textAlign: 'center', color: '#888' }}>
                      <p>⏳ Controller will be generated after component is created...</p>
                    </div>
                  )}
                </div>
              )}
              {activeTab === 'routes' && (
                <div style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
                  {isLoadingIntegration ? (
                    <div style={{ padding: '20px', textAlign: 'center' }}>
                      <p>🔄 Generating routes configuration...</p>
                    </div>
                  ) : integrationError ? (
                    <div style={{ padding: '20px', color: '#ff6b6b' }}>
                      <p>❌ Error: {integrationError}</p>
                    </div>
                  ) : routesConfig ? (
                    <textarea
                      className="code-editor"
                      value={routesConfig}
                      onChange={(e) => setRoutesConfig(e.target.value)}
                      placeholder="PHP Routes configuration..."
                      spellCheck={false}
                      style={{ flex: 1 }}
                    />
                  ) : (
                    <div style={{ padding: '20px', textAlign: 'center', color: '#888' }}>
                      <p>⏳ Routes will be generated after component is created...</p>
                    </div>
                  )}
                </div>
              )}
              {activeTab === 'integration' && (
                <div className="integration-view" style={{ padding: '20px', overflow: 'auto', height: '100%' }}>
                  <h3>1. Setup Routing (app-routing.module.ts)</h3>
                  <div style={{ background: '#1e1e1e', padding: '15px', borderRadius: '4px', marginBottom: '20px' }}>
                    <p style={{ color: '#888', fontSize: '0.9em', marginBottom: '8px', fontFamily: 'monospace' }}>
                      // 1. Add this import to the top of your file
                    </p>
                    <code style={{ display: 'block', marginBottom: '15px', fontFamily: 'monospace', color: snippetsError ? '#ff6b6b' : '#fff' }}>
                      {snippetsError ? 'Error loading snippets' : (snippets?.routing?.import || 'Loading...')}
                    </code>
                    <p style={{ color: '#888', fontSize: '0.9em', marginBottom: '8px', fontFamily: 'monospace' }}>
                      // 2. Add this object to your 'routes' array
                    </p>
                    <pre style={{ margin: 0, fontFamily: 'monospace', whiteSpace: 'pre-wrap', color: snippetsError ? '#ff6b6b' : '#fff' }}>
                      {snippetsError ? 'Error loading snippets' : (snippets?.routing?.route || 'Loading...')}
                    </pre>
                  </div>

                  <h3>2. Setup Sidebar (layout-sidebar.module.ts)</h3>
                  <div style={{ background: '#1e1e1e', padding: '15px', borderRadius: '4px' }}>
                    <p style={{ color: '#888', fontSize: '0.9em', marginBottom: '8px', fontFamily: 'monospace' }}>
                      // 1. Add this import
                    </p>
                    <code style={{ display: 'block', marginBottom: '15px', fontFamily: 'monospace', color: snippetsError ? '#ff6b6b' : '#fff' }}>
                      {snippetsError ? 'Error loading snippets' : (snippets?.sidebar?.import || 'Loading...')}
                    </code>
                    <p style={{ color: '#888', fontSize: '0.9em', marginBottom: '8px', fontFamily: 'monospace' }}>
                      // 2. Add this to the 'declarations' array
                    </p>
                    <code style={{ display: 'block', fontFamily: 'monospace', color: snippetsError ? '#ff6b6b' : '#fff' }}>
                      {snippetsError ? 'Error loading snippets' : (snippets?.sidebar?.declaration || 'Loading...')}
                    </code>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default DownloadPage
