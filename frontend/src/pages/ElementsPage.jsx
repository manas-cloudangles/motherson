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
      if (!completedPages.chat) return

      setIsLoading(true)
      try {
        // TODO: Replace with actual backend API endpoint
        // const response = await fetch('/api/get-components', {
        //   method: 'POST',
        //   headers: {
        //     'Content-Type': 'application/json',
        //   },
        //   body: JSON.stringify({
        //     dev_request: appData.devRequest
        //   })
        // })
        // const data = await response.json()
        
        // For now, use mock data - replace with actual API response
        // Expected API response format:
        // {
        //   components: [
        //     { id: 'button', name: 'Button', ... },
        //     ...
        //   ],
        //   recommended: ['button', 'input', ...], // IDs of recommended components
        //   reasoning: {
        //     'button': 'Reason why button was selected...',
        //     ...
        //   }
        // }
        
        const mockData = {
          components: [
            { id: 'button', name: 'Button' },
            { id: 'input', name: 'Input Field' },
            { id: 'card', name: 'Card' },
            { id: 'navbar', name: 'Navigation Bar' },
            { id: 'form', name: 'Form' },
            { id: 'modal', name: 'Modal' },
            { id: 'table', name: 'Table' },
            { id: 'list', name: 'List' },
          ],
          recommended: ['button', 'input', 'card'],
          reasoning: {
            'button': 'Based on your requirement, buttons are essential for user interactions and call-to-action elements. The uploaded folder structure suggests a need for interactive elements.',
            'input': 'Input fields are necessary for collecting user data. Your project structure indicates form-based interactions, making input components a core requirement.',
            'card': 'Card components provide a clean way to display content in organized sections. The folder structure shows content-heavy pages that would benefit from card layouts.'
          }
        }

        setComponents(mockData.components)
        setAiReasoning(mockData.reasoning || {})
        
        // Initialize edited reasoning from appData or use AI reasoning as default
        if (!appData.componentReasoning && mockData.reasoning) {
          setEditedReasoning(mockData.reasoning)
          updateAppData({ componentReasoning: mockData.reasoning })
        }
        
        // Pre-select recommended components if not already selected
        if (selectedComponents.length === 0 && mockData.recommended) {
          const recommendedComponents = mockData.components.filter(comp => 
            mockData.recommended.includes(comp.id)
          )
          setSelectedComponents(recommendedComponents.map(comp => comp.id))
          updateAppData({ selectedComponents: recommendedComponents.map(comp => comp.id) })
        }
      } catch (error) {
        console.error('Error fetching components:', error)
      } finally {
        setIsLoading(false)
      }
    }

    fetchComponents()
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

  const handleContinue = () => {
    // Save final component reasoning before continuing
    updateAppData({ componentReasoning: editedReasoning })
    
    // Mark elements page as complete when user continues
    if (selectedComponents.length > 0) {
      markPageComplete('elements')
      // Navigate to download page
      navigate('/download')
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
