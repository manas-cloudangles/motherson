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
    // Fetch components from backend when page loads
    const fetchComponents = async () => {
      if (!completedPages.chat || !appData.devRequest) {
        console.log('Skipping fetch - chat not complete or no dev request')
        return
      }

      setIsLoading(true)
      try {
        console.log('Fetching components with page request:', appData.devRequest)
        
        // Call backend API to select components based on page request
        // This API reads component-metadata.json and adds required/reasoning fields
        const response = await fetch('http://localhost:5000/api/select-components', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            pageRequest: appData.devRequest
          })
        })

        if (!response.ok) {
          const errorData = await response.json().catch(() => ({}))
          throw new Error(errorData.detail || `Failed to fetch components: ${response.statusText}`)
        }

        const data = await response.json()
        console.log('Components fetched from backend:', data)
        
        // Expected API response format:
        // {
        //   status: 'success',
        //   components: [
        //     { id_name: 'button-comp', name: 'Button', required: true, reasoning: '...', ... },
        //     { id_name: 'navbar-comp', name: 'Navbar', required: false, reasoning: '', ... },
        //     ...
        //   ]
        // }
        
        const componentsData = data.components || []
        
        if (componentsData.length === 0) {
          throw new Error('No components found. Please make sure components were analyzed in the previous step.')
        }
        
        // Transform components for UI (use id_name as id)
        const transformedComponents = componentsData.map(comp => ({
          id: comp.id_name,
          name: comp.name,
          description: comp.description || '',
          required: comp.required || false,
          reasoning: comp.reasoning || '',
          ...comp
        }))
        
        console.log('Transformed components:', transformedComponents)
        setComponents(transformedComponents)
        
        // Build reasoning map and selected IDs based on required field
        const reasoningMap = {}
        const selectedIds = []
        
        transformedComponents.forEach(comp => {
          if (comp.required === true) {
            selectedIds.push(comp.id)
            if (comp.reasoning) {
              reasoningMap[comp.id] = comp.reasoning
            }
          }
        })
        
        console.log('Selected components (required=true):', selectedIds)
        console.log('Reasoning map:', reasoningMap)
        
        setAiReasoning(reasoningMap)
        setEditedReasoning(reasoningMap)
        setSelectedComponents(selectedIds)
        
        // Update app data
        updateAppData({ 
          selectedComponents: selectedIds,
          componentReasoning: reasoningMap
        })
        
      } catch (error) {
        console.error('Error fetching components:', error)
        alert(`Error: ${error.message}. Please make sure the backend server is running and components were analyzed.`)
      } finally {
        setIsLoading(false)
      }
    }

    fetchComponents()
  }, [completedPages.chat, appData.devRequest])

  const toggleComponent = (componentId) => {
    const isCurrentlySelected = selectedComponents.includes(componentId)
    const newRequired = !isCurrentlySelected
    
    // Update UI state only - no API call
    setSelectedComponents(prev => {
      const newSelection = newRequired
        ? [...prev, componentId]
        : prev.filter(id => id !== componentId)
      updateAppData({ selectedComponents: newSelection })
      return newSelection
    })
    
    // If deselecting, remove reasoning
    if (!newRequired) {
      setEditedReasoning(prevReasoning => {
        const newReasoning = { ...prevReasoning }
        delete newReasoning[componentId]
        updateAppData({ componentReasoning: newReasoning })
        return newReasoning
      })
    }
  }

  const handleReasoningChange = (componentId, newReasoning) => {
    // Update local state only - no API call
    setEditedReasoning(prev => {
      const updated = { ...prev, [componentId]: newReasoning }
      updateAppData({ componentReasoning: updated })
      return updated
    })
  }

  const handleContinue = async () => {
    if (selectedComponents.length === 0) {
      alert('Please select at least one component before continuing.')
      return
    }

    // Save to appData first
    updateAppData({ 
      componentReasoning: editedReasoning,
      selectedComponents: selectedComponents
    })

    // Batch update all components in backend
    setIsLoading(true)
    try {
      // Build list of all components with their required status
      const updatePromises = components.map(component => {
        const isSelected = selectedComponents.includes(component.id)
        const reasoning = editedReasoning[component.id] || ''
        
        return fetch('http://localhost:5000/api/update-component', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            componentId: component.id,
            required: isSelected,
            reasoning: isSelected ? reasoning : null
          })
        })
      })

      // Wait for all updates to complete
      await Promise.all(updatePromises)
      console.log('All components updated successfully')

      // Now generate the page with the selected components
      console.log('Generating page with selected components...')
      const generateResponse = await fetch('http://localhost:5000/api/generate-page', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          pageRequest: appData.devRequest,
          selectedComponentIds: selectedComponents
        })
      })

      if (!generateResponse.ok) {
        const errorData = await generateResponse.json()
        throw new Error(errorData.detail || 'Failed to generate page')
      }

      const generatedData = await generateResponse.json()
      console.log('Page generated successfully:', generatedData)

      // Save generated files to appData
      updateAppData({
        componentReasoning: editedReasoning,
        selectedComponents: selectedComponents,
        generatedFiles: {
          html: generatedData.html_code || '',
          css: generatedData.scss_code || '',
          ts: generatedData.ts_code || ''
        },
        componentInfo: {
          name: generatedData.component_name,
          pathName: generatedData.path_name,
          selector: generatedData.selector
        }
      })

      // Mark elements page as complete and navigate
      markPageComplete('elements')
      navigate('/download')
      
    } catch (error) {
      console.error('Error updating components:', error)
      alert(`Error: ${error.message}. Please try again.`)
    } finally {
      setIsLoading(false)
    }
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
            disabled={selectedComponents.length === 0}
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
