/**
 * Helper function to convert Angular component template to vanilla HTML
 * @param {string} template - The Angular HTML template
 * @param {Object} componentData - Data object for interpolation
 * @returns {string} - Converted HTML
 */
export const convertAngularTemplateToHTML = (template, componentData = {}) => {
    let converted = template

    // Handle interpolation {{ expression }}
    converted = converted.replace(/\{\{([^}]+)\}\}/g, (match, expr) => {
        const trimmed = expr.trim()

        // Handle method calls - show sample data instead of code
        if (trimmed.includes('(') && trimmed.includes(')')) {
            if (trimmed.includes('Date')) return 'Oct 24, 2023';
            if (trimmed.includes('currency')) return '$1,234.56';
            if (trimmed.includes('status')) return 'Active';
            return 'Sample Value';
        }

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

        // Handle commonexpressions that might not be in componentData
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
                    // For preview beauty, show the last part as a placeholder
                    return parts[parts.length - 1]; // e.g. "name" from "user.name"
                }
            }
            return String(value !== undefined ? value : '')
        }

        // Special case: currentYear (common in footers)
        if (trimmed === 'currentYear' || trimmed === 'new Date().getFullYear()') {
            return String(new Date().getFullYear())
        }

        // Default: show as interpolation placeholder but cleaner
        return trimmed;
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

        // FORCE ENABLE: specific fix for [disabled]
        // If it's a disabled binding, remove it so the element appears enabled in preview
        if (prop === 'disabled') {
            return '';
        }

        // For other property bindings like [type]="type"
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
            if (propValue === undefined) {
                // For boolean HTML attributes, default to false if not provided
                const booleanAttributes = ['readonly', 'required', 'checked', 'selected', 'hidden']
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
            const booleanAttributes = ['disabled', 'readonly', 'required', 'checked', 'selected', 'hidden']
            if (booleanAttributes.includes(prop.toLowerCase())) {
                return prop
            }
            return `${prop}="true"`
        }
        if (propValue === false || propValue === 'false') {
            return ''
        }

        // String/number values
        return `${prop}="${String(propValue)}"`
    })

    // Handle event binding (click)="handler()" - remove for preview
    converted = converted.replace(/\(click\)="([^"]+)"/g, (match, handler) => {
        return ''
    })

    // Handle *ngIf - IMPROVED for Happy Path
    // We want to hide "loading" and "empty" states, and show "data" states
    converted = converted.replace(/\*ngIf="([^"]+)"/g, (match, condition) => {
        const cond = condition.trim().toLowerCase();
        // Heuristics to HIDE elements (loading, no records, error)
        if (cond.includes('loading') ||
            (cond.includes('!') && (cond.includes('data') || cond.includes('record') || cond.includes('item'))) ||
            cond.includes('length === 0') ||
            cond.includes('error')) {
            // Hide this element
            return 'style="display: none !important;"';
        }

        // Ensure "Happy Path" elements are shown (no attribute needed)

        return ''
    })

    // Handle *ngFor - simplify for preview
    converted = converted.replace(/\*ngFor="let\s+(\w+)\s+of\s+([^"]+)"/g, (match, item, array) => {
        // Just remove the directive, letting the SINGLE item render as a sample
        return ''
    })

    // Handle (mouseenter) and (mouseleave)
    converted = converted.replace(/\(mouseenter\)="([^"]+)"/g, '')
    converted = converted.replace(/\(mouseleave\)="([^"]+)"/g, '')

    // Handle routerLink
    converted = converted.replace(/routerLink="([^"]+)"/g, 'href="$1"')
    converted = converted.replace(/\[routerLink\]="([^"]+)"/g, (match, value) => {
        const routeValue = componentData[value.trim()] || value.trim()
        return `href="${routeValue}"`
    })
    converted = converted.replace(/routerLinkActive="([^"]+)"/g, '')

    return converted
}

/**
 * Helper function to process reusable components
 * @param {string} html - The HTML content containing component tags
 * @param {Array} componentsMetadata - Metadata of available components
 * @returns {Object} - { html, componentStyles, componentScripts }
 */
export const processReusableComponents = (html, componentsMetadata = []) => {
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
        if (innerContent && innerContent.trim() && !innerContent.match(/<[^>]+>/)) {
            const innerText = innerContent.trim()
            let inputPropertyName = null

            if (component.ts_code) {
                // Extract @Input() properties from TypeScript code
                const inputRegex = /@Input\(\)\s+(\w+):/g
                const inputs = []
                let inputMatch
                while ((inputMatch = inputRegex.exec(component.ts_code)) !== null) {
                    inputs.push(inputMatch[1])
                }

                // If we found inputs, check the HTML template
                if (inputs.length > 0 && component.html_code) {
                    const interpolationRegex = /\{\{\s*(\w+)\s*\}\}/g
                    const interpolations = []
                    let interpMatch
                    while ((interpMatch = interpolationRegex.exec(component.html_code)) !== null) {
                        interpolations.push(interpMatch[1])
                    }

                    const contentPropertyNames = ['label', 'text', 'content', 'title', 'value', 'name']
                    for (const propName of contentPropertyNames) {
                        if (inputs.includes(propName) && interpolations.includes(propName)) {
                            inputPropertyName = propName
                            break
                        }
                    }

                    if (!inputPropertyName) {
                        for (const input of inputs) {
                            if (interpolations.includes(input)) {
                                inputPropertyName = input
                                break
                            }
                        }
                    }

                    if (!inputPropertyName && inputs.length > 0) {
                        inputPropertyName = inputs[0]
                    }
                }
            }

            const propertyName = inputPropertyName || 'label'
            attrs[propertyName] = innerText
        }

        // Get component template and convert it
        const componentHtml = component.html_code || ''
        return convertAngularTemplateToHTML(componentHtml, attrs)
    }

    // Find all Angular component selectors in the HTML
    // First, process self-closing tags: <app-button />
    processedHtml = processedHtml.replace(/<(\w+(-\w+)+)([^>]*)\s*\/>/g, (match, selector, _, attributes) => {
        const converted = processComponent(selector, attributes, null)
        return converted !== null ? converted : match
    })

    // Then, process opening/closing tags: <app-button>content</app-button>
    let lastProcessedHtml = ''
    let iterations = 0
    const maxIterations = 20

    while (processedHtml !== lastProcessedHtml && iterations < maxIterations) {
        lastProcessedHtml = processedHtml
        iterations++

        // Match component tags with simple text content (no nested tags)
        processedHtml = processedHtml.replace(/<(\w+(-\w+)+)([^>]*)>([^<]*)<\/\1>/g, (match, selector, _, attributes, innerContent) => {
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
