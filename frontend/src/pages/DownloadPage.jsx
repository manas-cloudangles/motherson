import { useState, useEffect, useRef } from 'react'
import { usePageProgress } from '../context/PageProgressContext'
import NoInputMessage from '../components/NoInputMessage'
import './DownloadPage.css'

function DownloadPage() {
  const { markPageComplete, completedPages, appData, updateAppData } = usePageProgress()
  const [htmlContent, setHtmlContent] = useState(appData.generatedFiles?.html || '')
  const [scssContent, setScssContent] = useState(appData.generatedFiles?.scss || '')
  const [tsContent, setTsContent] = useState(appData.generatedFiles?.ts || '')
  const [previewContent, setPreviewContent] = useState('')
  const [activeTab, setActiveTab] = useState('html')
  const [isLoading, setIsLoading] = useState(false)
  const componentName = appData.generatedFiles?.component_name?.replace('Component', '').toLowerCase() || 'my-component'


  // Chat state
  const [chatMessage, setChatMessage] = useState('')
  const [chatHistory, setChatHistory] = useState([])
  const [isChatLoading, setIsChatLoading] = useState(false)
  const chatEndRef = useRef(null)

  // Scroll to bottom of chat
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [chatHistory])
  // Check if there's input from previous steps
  const hasInputFromPreviousSteps = completedPages.chat && completedPages.elements

  // Helper function to convert Angular component template to vanilla HTML
  const convertAngularTemplateToHTML = (template, componentData = {}) => {
    let converted = template

    // Handle interpolation {{ expression }}
    converted = converted.replace(/\{\{([^}]+)\}\}/g, (match, expr) => {
      const trimmed = expr.trim()

      // Try to get value from componentData (dynamic lookup)
      if (componentData[trimmed] !== undefined) {
        const value = componentData[trimmed]
        // Handle different value types
        if (typeof value === 'string' || typeof value === 'number') {
          return String(value)
        }
        if (typeof value === 'boolean') {
          return value ? 'true' : 'false'
        }
        return String(value)
      }

      // Handle common expressions that might not be in componentData
      // Check if it's a method call or property access
      if (trimmed.includes('.')) {
        // Try to evaluate nested properties (e.g., "obj.property")
        const parts = trimmed.split('.')
        let value = componentData
        for (const part of parts) {
          if (value && typeof value === 'object' && part in value) {
            value = value[part]
          } else {
            // Can't resolve, show as interpolation
            return `<span class="interpolation">${trimmed}</span>`
          }
        }
        return String(value !== undefined ? value : '')
      }

      // Special case: currentYear (common in footers)
      if (trimmed === 'currentYear' || trimmed === 'new Date().getFullYear()') {
        return String(new Date().getFullYear())
      }

      // Default: show as interpolation placeholder
      return `<span class="interpolation">${trimmed}</span>`
    })

    // Handle property binding [property]="value"
    converted = converted.replace(/\[([^\]]+)\]="([^"]+)"/g, (match, prop, value) => {
      // For class bindings like [class]="'btn btn-' + variant"
      if (prop === 'class') {
        // Try to evaluate the expression
        if (value.includes("'") || value.includes('"')) {
          // Handle string concatenation like 'btn btn-' + variant
          const parts = value.split('+').map(p => p.trim().replace(/['"]/g, ''))
          let classValue = parts.join(' ')
          // Replace variable references with actual values from componentData
          Object.keys(componentData).forEach(key => {
            const regex = new RegExp(`\\b${key}\\b`, 'g')
            classValue = classValue.replace(regex, componentData[key] || '')
          })
          return `class="${classValue.trim()}"`
        }
        // If it's a simple variable reference
        if (componentData[value.trim()] !== undefined) {
          return `class="${componentData[value.trim()]}"`
        }
        return `class="${value}"`
      }

      // For other property bindings like [type]="type" or [disabled]="disabled"
      // The value expression might be:
      // 1. A simple variable: "type" -> get from componentData
      // 2. A string literal: "'primary'" -> use the string
      // 3. A boolean literal: "true" or "false"

      let propValue
      const valueTrimmed = value.trim()

      // Check if it's a string literal
      if ((valueTrimmed.startsWith("'") && valueTrimmed.endsWith("'")) ||
        (valueTrimmed.startsWith('"') && valueTrimmed.endsWith('"'))) {
        propValue = valueTrimmed.slice(1, -1)
      }
      // Check if it's a boolean literal
      else if (valueTrimmed === 'true') {
        propValue = true
      }
      else if (valueTrimmed === 'false') {
        propValue = false
      }
      // Otherwise, treat as variable reference and get from componentData
      else {
        propValue = componentData[valueTrimmed]

        // If not found, try to infer from the property name
        // This is a fallback for common HTML attributes
        if (propValue === undefined) {
          // For boolean HTML attributes, default to false if not provided
          const booleanAttributes = ['disabled', 'readonly', 'required', 'checked', 'selected', 'hidden']
          if (booleanAttributes.includes(prop.toLowerCase())) {
            propValue = false
          }
          // For other attributes, use the expression as-is (might be evaluated later)
          else {
            propValue = valueTrimmed
          }
        }
      }

      // Convert to HTML attribute format
      if (propValue === true || propValue === 'true') {
        // Boolean attributes: just the attribute name for true
        const booleanAttributes = ['disabled', 'readonly', 'required', 'checked', 'selected', 'hidden']
        if (booleanAttributes.includes(prop.toLowerCase())) {
          return prop
        }
        return `${prop}="true"`
      }
      if (propValue === false || propValue === 'false') {
        // Boolean attributes: omit for false
        return ''
      }

      // String/number values
      return `${prop}="${String(propValue)}"`
    })

    // Handle event binding (click)="handler()" - remove for preview (buttons should be visible but non-functional)
    converted = converted.replace(/\(click\)="([^"]+)"/g, (match, handler) => {
      return '' // Remove click handlers - buttons should be visible but non-interactive
    })

    // Handle *ngIf
    converted = converted.replace(/\*ngIf="([^"]+)"/g, (match, condition) => {
      // For preview, we'll show the element (can be enhanced later)
      return ''
    })

    // Handle *ngFor
    converted = converted.replace(/\*ngFor="let\s+(\w+)\s+of\s+([^"]+)"/g, (match, item, array) => {
      // For preview, we'll show a single instance
      return ''
    })

    // Handle (mouseenter) and (mouseleave)
    converted = converted.replace(/\(mouseenter\)="([^"]+)"/g, '')
    converted = converted.replace(/\(mouseleave\)="([^"]+)"/g, '')

    // Handle routerLink (convert to regular links for preview)
    converted = converted.replace(/routerLink="([^"]+)"/g, 'href="$1"')
    // Handle [routerLink] binding syntax
    converted = converted.replace(/\[routerLink\]="([^"]+)"/g, (match, value) => {
      // Try to get the route value from componentData
      const routeValue = componentData[value.trim()] || value.trim()
      return `href="${routeValue}"`
    })
    converted = converted.replace(/routerLinkActive="([^"]+)"/g, '')

    return converted
  }

  // Helper function to process reusable components
  const processReusableComponents = (html, componentsMetadata = []) => {
    if (!componentsMetadata || componentsMetadata.length === 0) {
      return { html, componentStyles: '', componentScripts: '' }
    }

    // Create a map of component selectors to their metadata
    const componentMap = {}
    componentsMetadata.forEach(comp => {
      const selector = comp.id_name || comp.selector || comp.name?.toLowerCase().replace('component', '')
      if (selector) {
        componentMap[selector] = comp
      }
    })

    let processedHtml = html
    let allComponentStyles = ''
    let allComponentScripts = ''
    const processedComponents = new Set()

    // Helper function to process a single component instance
    const processComponent = (selector, attributes, innerContent) => {
      const component = componentMap[selector]
      if (!component) {
        return null // Component not found in metadata
      }

      // Only add styles/scripts once per component type
      if (!processedComponents.has(selector)) {
        processedComponents.add(selector)

        // Add component styles
        if (component.scss_code) {
          allComponentStyles += `\n/* Styles for ${selector} */\n${component.scss_code}\n`
        }

        // Add component scripts
        if (component.ts_code) {
          const tsCode = component.ts_code
          const classMatch = tsCode.match(/export\s+class\s+(\w+)/)
          if (classMatch) {
            let jsCode = tsCode
              .replace(/import\s+.*?from\s+['"].*?['"];?\s*/g, '')
              .replace(/@Component\s*\(\s*\{[^}]*\}\s*\)/g, '')
              .replace(/export\s+class\s+(\w+)/g, 'class $1')
              .replace(/:\s*\w+(\[\])?(\s*\|\s*\w+)?/g, '')
              .replace(/:\s*void/g, '')
              .replace(/@Input\(\)/g, '')
              .replace(/@Output\(\)/g, '')
              .replace(/EventEmitter/g, '')
              .replace(/implements\s+\w+/g, '')

            allComponentScripts += `\n/* Script for ${selector} */\n${jsCode}\n`
          }
        }
      }

      // Extract attributes
      const attrs = {}
      if (attributes) {
        // First, handle Angular property bindings: [property]="value"
        const propBindingRegex = /\[(\w+)\]="([^"]+)"/g
        let propMatch
        while ((propMatch = propBindingRegex.exec(attributes)) !== null) {
          const propName = propMatch[1]
          let propValue = propMatch[2]
          // Remove quotes if present
          propValue = propValue.replace(/^['"]|['"]$/g, '')
          attrs[propName] = propValue
        }

        // Then, handle regular attributes: name="value" or name='value' or name (boolean)
        const attrRegex = /(\w+)(?:=["']([^"']*)["'])?/g
        let attrMatch
        while ((attrMatch = attrRegex.exec(attributes)) !== null) {
          const attrName = attrMatch[1]
          // Skip if already processed as property binding
          if (!attrs.hasOwnProperty(attrName)) {
            const attrValue = attrMatch[2] !== undefined ? attrMatch[2] : true
            attrs[attrName] = attrValue
          }
        }
      }

      // For components with inner content (like <app-button>Text</app-button>)
      // We need to determine which @Input() property should receive this content
      if (innerContent && innerContent.trim() && !innerContent.match(/<[^>]+>/)) {
        const innerText = innerContent.trim()

        // Try to determine the correct input property name by analyzing the component
        let inputPropertyName = null

        if (component.ts_code) {
          // Extract @Input() properties from TypeScript code
          const inputRegex = /@Input\(\)\s+(\w+):/g
          const inputs = []
          let inputMatch
          while ((inputMatch = inputRegex.exec(component.ts_code)) !== null) {
            inputs.push(inputMatch[1])
          }

          // If we found inputs, check the HTML template to see which one is used for content
          if (inputs.length > 0 && component.html_code) {
            // Look for interpolation expressions in the template
            const interpolationRegex = /\{\{\s*(\w+)\s*\}\}/g
            const interpolations = []
            let interpMatch
            while ((interpMatch = interpolationRegex.exec(component.html_code)) !== null) {
              interpolations.push(interpMatch[1])
            }

            // Find the first input that's used in interpolation
            // Common content property names (in order of preference)
            const contentPropertyNames = ['label', 'text', 'content', 'title', 'value', 'name']

            // First, try common content property names
            for (const propName of contentPropertyNames) {
              if (inputs.includes(propName) && interpolations.includes(propName)) {
                inputPropertyName = propName
                break
              }
            }

            // If not found, use the first input that appears in interpolation
            if (!inputPropertyName) {
              for (const input of inputs) {
                if (interpolations.includes(input)) {
                  inputPropertyName = input
                  break
                }
              }
            }

            // Fallback: use the first input property
            if (!inputPropertyName && inputs.length > 0) {
              inputPropertyName = inputs[0]
            }
          }
        }

        // Use the determined property name, or fallback to common names
        const propertyName = inputPropertyName || 'label'
        attrs[propertyName] = innerText
      }

      // Get component template and convert it
      const componentHtml = component.html_code || ''
      return convertAngularTemplateToHTML(componentHtml, attrs)
    }

    // Find all Angular component selectors in the HTML
    // Pattern: <app-component-name>...</app-component-name> or <app-component-name />
    // Component names typically follow app-* pattern

    // First, process self-closing tags: <app-button />
    processedHtml = processedHtml.replace(/<(\w+(-\w+)+)([^>]*)\s*\/>/g, (match, selector, _, attributes) => {
      const converted = processComponent(selector, attributes, null)
      return converted !== null ? converted : match
    })

    // Then, process opening/closing tags: <app-button>content</app-button>
    // Process from innermost to outermost to handle nested components
    let lastProcessedHtml = ''
    let iterations = 0
    const maxIterations = 20 // Prevent infinite loops

    while (processedHtml !== lastProcessedHtml && iterations < maxIterations) {
      lastProcessedHtml = processedHtml
      iterations++

      // Match component tags with simple text content (no nested tags)
      // This handles cases like <app-button>Click Me</app-button>
      processedHtml = processedHtml.replace(/<(\w+(-\w+)+)([^>]*)>([^<]*)<\/\1>/g, (match, selector, _, attributes, innerContent) => {
        // Only process if innerContent doesn't contain HTML tags
        if (!innerContent.match(/<[^>]+>/)) {
          const converted = processComponent(selector, attributes, innerContent)
          return converted !== null ? converted : match
        }
        return match
      })

      // Also handle empty component tags: <app-header></app-header>
      processedHtml = processedHtml.replace(/<(\w+(-\w+)+)([^>]*)><\/\1>/g, (match, selector, _, attributes) => {
        const converted = processComponent(selector, attributes, null)
        return converted !== null ? converted : match
      })
    }

    return {
      html: processedHtml,
      componentStyles: allComponentStyles,
      componentScripts: allComponentScripts
    }
  }

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
      // Handle *ngFor
      .replace(/\*ngFor="let\s+(\w+)\s+of\s+([^"]+)"/g, (match, item, array) => {
        return `data-ngfor="${array}" data-item="${item}"`
      })
      // Handle *ngIf
      .replace(/\*ngIf="([^"]+)"/g, (match, condition) => {
        return `data-ngif="${condition}"`
      })
      // Handle (click) events - remove for preview (buttons should be visible but non-functional)
      .replace(/\(click\)="([^"]+)"/g, (match, handler) => {
        return '' // Remove click handlers - buttons should be visible but non-interactive
      })
      // Handle [ngClass]
      .replace(/\[ngClass\]="([^"]+)"/g, '')
      // Handle interpolation - convert to readable format
      .replace(/\{\{([^}]+)\}\}/g, (match, expr) => {
        // Try to evaluate simple expressions, otherwise show as text
        try {
          // For simple property access, show placeholder
          return `<span class="interpolation">${expr.trim()}</span>`
        } catch {
          return `<span class="interpolation">${expr}</span>`
        }
      })
      // Handle property binding [property]
      .replace(/\[([^\]]+)\]="([^"]+)"/g, (match, prop, value) => {
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
        const response = await fetch('http://localhost:5000/api/generate-page', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            pageRequest: appData.devRequest || ''
            // Note: selectedComponentIds is no longer needed - backend uses required:true from metadata file
          })
        })

        if (!response.ok) {
          const errorData = await response.json().catch(() => ({ detail: `Server error: ${response.status}` }))
          throw new Error(errorData.detail || `Server error: ${response.status}`)
        }

        const data = await response.json()

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
          hasTs: !!ts,
          htmlLength: html.length,
          scssLength: scss.length,
          tsLength: ts.length,
          htmlPreview: html.substring(0, 200),
          scssPreview: scss.substring(0, 200),
          tsPreview: ts.substring(0, 200),
          fullData: data
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
    downloadFile(htmlContent, `${componentName}.component.html`, 'text/html')
  }

  const downloadSCSS = () => {
    downloadFile(scssContent, `${componentName}.component.scss`, 'text/scss')
  }

  const downloadTS = () => {
    downloadFile(tsContent, `${componentName}.component.ts`, 'text/typescript')
  }

  const downloadAll = () => {
    downloadHTML()
    setTimeout(() => downloadSCSS(), 200)
    setTimeout(() => downloadTS(), 400)
  }


  const handleSendMessage = async () => {
    if (!chatMessage.trim() || isChatLoading) return

    const userMsg = chatMessage.trim()
    setChatMessage('')

    // Add user message to history
    setChatHistory(prev => [...prev, { role: 'user', content: userMsg }])
    setIsChatLoading(true)

    try {
      const response = await fetch('http://localhost:5000/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: userMsg })
      })

      if (!response.ok) {
        throw new Error(`Server error: ${response.status}`)
      }

      const data = await response.json()

      if (data.status !== 'success') {
        throw new Error(data.message || 'Failed to update code')
      }

      // Update code
      setHtmlContent(data.html_code)
      setScssContent(data.scss_code)
      setTsContent(data.ts_code)

      // Update preview
      const newPreview = generatePreviewContent(data.html_code, data.scss_code, data.ts_code)
      setPreviewContent(newPreview)

      // Update appData
      updateAppData({
        generatedFiles: {
          html: data.html_code,
          scss: data.scss_code,
          ts: data.ts_code,
          component_name: appData.generatedFiles?.component_name,
          path_name: appData.generatedFiles?.path_name,
          selector: appData.generatedFiles?.selector
        }
      })

      // Add assistant message
      setChatHistory(prev => [...prev, { role: 'assistant', content: 'I have updated the code based on your request.' }])

    } catch (error) {
      console.error('Chat error:', error)
      setChatHistory(prev => [...prev, { role: 'assistant', content: `Error: ${error.message}` }])
    } finally {
      setIsChatLoading(false)
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
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
        <div className={`download-layout ${'with-chat'}`}>
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
            </div>
          </div>

          {/* Chat Interface */}
          <div className="chat-container">
            <div className="chat-header">
              <h3>Chat with Page</h3>
            </div>
            <div className="chat-messages">
              {chatHistory.length === 0 && (
                <div className="message assistant">
                  Hi! I can help you edit this page. Just tell me what you want to change.
                </div>
              )}
              {chatHistory.map((msg, index) => (
                <div key={index} className={`message ${msg.role}`}>
                  {msg.content}
                </div>
              ))}
              {isChatLoading && (
                <div className="message assistant">
                  Thinking...
                </div>
              )}
              <div ref={chatEndRef} />
            </div>
            <div className="chat-input-area">
              <textarea
                className="chat-input"
                placeholder="Type your request here..."
                value={chatMessage}
                onChange={(e) => setChatMessage(e.target.value)}
                onKeyDown={handleKeyPress}
                disabled={isChatLoading}
              />
              <button
                className="send-btn"
                onClick={handleSendMessage}
                disabled={!chatMessage.trim() || isChatLoading}
              >
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <line x1="22" y1="2" x2="11" y2="13"></line>
                  <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
                </svg>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default DownloadPage
