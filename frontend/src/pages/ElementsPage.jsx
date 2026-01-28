import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { usePageProgress } from '../context/PageProgressContext'
import NoInputMessage from '../components/NoInputMessage'
import './ElementsPage.css'

function ElementsPage() {
  const navigate = useNavigate()
  const { markPageComplete, completedPages, appData, updateAppData } = usePageProgress()
  const [components, setComponents] = useState([])
  const [selectedComponents, setSelectedComponents] = useState(appData.selectedComponents || [])
  const [isLoading, setIsLoading] = useState(false)
  const [aiReasoning, setAiReasoning] = useState({})
  const [editedReasoning, setEditedReasoning] = useState(appData.componentReasoning || {})

  // Check if there's input from previous step (ChatPage)
  const hasInputFromPreviousStep = completedPages.chat && appData.devRequest && appData.devRequest.trim() !== ''

  useEffect(() => {
    // Use components from ChatPage and fetch component selection from backend
    const initializeComponents = async () => {
      if (!completedPages.chat) return

      setIsLoading(true)
      try {
        // First, use components from appData (set by ChatPage)
        const componentsFromChat = appData.components || []

        if (componentsFromChat.length === 0) {
          console.warn('No components found in appData')
          setIsLoading(false)
          return
        }

        // Transform backend component format to frontend format
        // Backend format: { name, id_name, description, ... }
        // Frontend format: { id, name, ... }
        const transformedComponents = componentsFromChat.map(comp => {
          // Format name: remove "App" prefix, "Component" suffix, and add spaces
          let displayName = comp.name
          if (displayName.startsWith('App')) displayName = displayName.substring(3)
          if (displayName.endsWith('Component')) displayName = displayName.substring(0, displayName.length - 9)

          // Add spaces before capital letters (e.g. "DateRange" -> "Date Range")
          displayName = displayName.replace(/([A-Z])/g, ' $1').trim()

          return {
            id: comp.id_name || comp.name,
            name: displayName,
            originalName: comp.name, // Keep original name just in case
            description: comp.description,
            import_path: comp.import_path,
            ...comp // Include all other properties
          }
        })

        setComponents(transformedComponents)
        updateAppData({ components: transformedComponents })

        // Now call backend API to get component selection and reasoning
        const response = await fetch('http://localhost:5000/api/select-components', {
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

        const data = await response.json()

        if (data.status !== 'success') {
          throw new Error(data.message || 'Failed to select components')
        }

        // Set AI reasoning from backend response
        const reasoning = data.reasoning || {}
        setAiReasoning(reasoning)

        // Always use AI reasoning from backend (it's based on the page request)
        if (reasoning && Object.keys(reasoning).length > 0) {
          setEditedReasoning(reasoning)
          updateAppData({ componentReasoning: reasoning })
        } else if (appData.componentReasoning) {
          // Fallback to existing reasoning if backend didn't provide any
          setEditedReasoning(appData.componentReasoning)
        }

        // Always auto-select components based on backend's AI selection
        // This ensures components are selected based on the user's page request from page 1
        const selectedIds = data.selected_component_ids || []
        if (selectedIds.length > 0) {
          setSelectedComponents(selectedIds)
          updateAppData({ selectedComponents: selectedIds })
          console.log(`✓ Auto-selected ${selectedIds.length} components based on page request`)
        } else {
          console.log('⚠ No components were auto-selected by the backend')
        }
      } catch (error) {
        console.error('Error initializing components:', error)
        alert(`Error: ${error.message}\n\nMake sure the backend server is running on http://localhost:5000`)
      } finally {
        setIsLoading(false)
      }
    }

    initializeComponents()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [completedPages.chat])

  const toggleComponent = (componentId) => {
    setSelectedComponents(prev => {
      const newSelection = prev.includes(componentId)
        ? prev.filter(id => id !== componentId)
        : [...prev, componentId]
      updateAppData({ selectedComponents: newSelection })

      // If component is removed, also remove its reasoning
      if (prev.includes(componentId)) {
        setEditedReasoning(prevReasoning => {
          const newReasoning = { ...prevReasoning }
          delete newReasoning[componentId]
          updateAppData({ componentReasoning: newReasoning })
          return newReasoning
        })
      } else {
        // If component is added and has AI reasoning, initialize it
        if (aiReasoning[componentId] && !editedReasoning[componentId]) {
          setEditedReasoning(prevReasoning => {
            const newReasoning = { ...prevReasoning, [componentId]: aiReasoning[componentId] }
            updateAppData({ componentReasoning: newReasoning })
            return newReasoning
          })
        }
      }

      return newSelection
    })
  }

  const handleReasoningChange = (componentId, newReasoning) => {
    setEditedReasoning(prev => {
      const updated = { ...prev, [componentId]: newReasoning }
      updateAppData({ componentReasoning: updated })
      return updated
    })
  }

  const handleContinue = async () => {
    // Save final component reasoning before continuing
    updateAppData({ componentReasoning: editedReasoning })

    // Mark elements page as complete when user continues
    // if (selectedComponents.length > 0) {
    try {
      // Update component metadata on backend with user's manual changes
      // Use original components from appData to ensure we have all fields (html_code, scss_code, ts_code, etc.)
      const originalComponents = appData.components || components

      // Build updated components list with required and reasoning fields
      const updatedComponents = originalComponents.map(comp => {
        const compId = comp.id || comp.id_name || comp.name
        const isRequired = selectedComponents.includes(compId)
        const compReasoning = editedReasoning[compId] || ''

        // Explicitly set required to false if not in selectedComponents
        // This ensures user's manual deselection is respected
        const requiredValue = isRequired ? true : false

        console.log(`Component ${compId}: required=${requiredValue}, in selectedComponents=${isRequired}`)

        // Preserve all original fields and update required/reasoning
        return {
          ...comp,
          required: requiredValue, // Explicitly set to boolean
          reasoning: compReasoning
        }
      })

      // Log summary of required components
      const requiredCount = updatedComponents.filter(c => c.required === true).length
      const notRequiredCount = updatedComponents.filter(c => c.required === false).length
      console.log(`Updating metadata: ${requiredCount} required, ${notRequiredCount} not required`)
      console.log('Required components:', updatedComponents.filter(c => c.required).map(c => c.id || c.id_name || c.name))
      console.log('Not required components:', updatedComponents.filter(c => !c.required).map(c => c.id || c.id_name || c.name))

      // Call API to update metadata
      const response = await fetch('http://localhost:5000/api/update-component-metadata', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          components: updatedComponents
        })
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: `Server error: ${response.status}` }))
        throw new Error(errorData.detail || `Server error: ${response.status}`)
      }

      const data = await response.json()
      if (data.status !== 'success') {
        throw new Error(data.message || 'Failed to update component metadata')
      }

      console.log('✓ Component metadata updated successfully')

      // Clear old generated files so DownloadPage will regenerate with updated metadata
      updateAppData({ generatedFiles: null })

      // Mark elements page as complete and navigate
      markPageComplete('elements')
      navigate('/download')
    } catch (error) {
      console.error('Error updating component metadata:', error)
      alert(`Error updating component metadata: ${error.message}\n\nMake sure the backend server is running on http://localhost:5000`)
    }
    // }
  }

  if (!hasInputFromPreviousStep) {
    return (
      <div className="elements-page">
        <div className="elements-container elements-container-empty">
          <NoInputMessage />
        </div>
      </div>
    )
  }

  if (isLoading) {
    return (
      <div className="elements-page">
        <div className="elements-container">
          <div className="reasoning-placeholder">
            <p>Loading components...</p>
          </div>
        </div>
      </div>
    )
  }

  const selectedComponentsWithReasoning = selectedComponents
    .map(id => {
      const component = components.find(c => c.id === id)
      const currentReasoning = editedReasoning[id] || aiReasoning[id] || ''
      const isAiSelected = !!aiReasoning[id]
      return component ? {
        ...component,
        reasoning: currentReasoning,
        isAiSelected,
        hasReasoning: !!currentReasoning
      } : null
    })
    .filter(Boolean)

  return (
    <div className="elements-page">
      <div className="elements-container">
        <div className="elements-sidebar">
          <h2>Common Components</h2>
          <p className="sidebar-description">Select components you want to include in your app:</p>
          <div className="elements-list">
            {components.map((component) => (
              <div
                key={component.id}
                className={`element-item ${selectedComponents.includes(component.id) ? 'selected' : ''}`}
                onClick={() => toggleComponent(component.id)}
              >
                <input
                  type="checkbox"
                  checked={selectedComponents.includes(component.id)}
                  onChange={() => toggleComponent(component.id)}
                  className="element-checkbox"
                />
                <span className="element-name">{component.name}</span>
              </div>
            ))}
          </div>
          <button
            className="generate-button"
            onClick={handleContinue}
            disabled={false}
          >
            Continue
          </button>
        </div>
        <div className="reasoning-section">
          <h2>Component Requirements</h2>
          <p className="reasoning-section-description">
            Edit the requirements for each selected component. This will be used to generate HTML, CSS, and TypeScript code.
          </p>
          {selectedComponentsWithReasoning.length > 0 ? (
            <div className="reasoning-list">
              {selectedComponentsWithReasoning.map((component) => (
                <div key={component.id} className="reasoning-item">
                  <div className="reasoning-header">
                    <h3 className="reasoning-component-name">{component.name}</h3>
                    {component.isAiSelected && (
                      <span className="reasoning-badge">AI Selected</span>
                    )}
                  </div>
                  <div className="reasoning-input-container">
                    <label className="reasoning-label">
                      Requirements & Reasoning:
                    </label>
                    <textarea
                      className="reasoning-textarea"
                      value={component.reasoning || ''}
                      onChange={(e) => handleReasoningChange(component.id, e.target.value)}
                      placeholder={
                        component.isAiSelected
                          ? "Edit the AI's reasoning or add your own requirements..."
                          : "Enter requirements and reasoning for this component..."
                      }
                      rows={4}
                    />
                    {component.isAiSelected && !component.reasoning && (
                      <p className="reasoning-hint">
                        This component was AI-selected but has no reasoning. Please add requirements.
                      </p>
                    )}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="reasoning-placeholder">
              <p>Select components to add requirements and reasoning for each selection</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default ElementsPage
