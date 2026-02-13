import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { usePageProgress } from '../context/PageProgressContext'
import NoInputMessage from '../components/NoInputMessage'
import './ElementsPage.css'

function ElementsPage() {
  const navigate = useNavigate()
  const { markPageComplete, completedPages, appData, updateAppData } = usePageProgress()
  
  // Frontend components state
  const [components, setComponents] = useState([])
  const [selectedComponents, setSelectedComponents] = useState(appData.selectedComponents || [])
  const [aiReasoning, setAiReasoning] = useState({})
  const [editedReasoning, setEditedReasoning] = useState(appData.componentReasoning || {})
  
  // Backend APIs state
  const [backendApis, setBackendApis] = useState([])
  const [selectedApis, setSelectedApis] = useState(appData.selectedApis || [])
  const [aiApiReasoning, setAiApiReasoning] = useState({})
  const [editedApiReasoning, setEditedApiReasoning] = useState(appData.apiReasoning || {})
  
  const [isLoading, setIsLoading] = useState(false)

  // Check if there's input from previous step (ChatPage)
  const hasInputFromPreviousStep = completedPages.chat && appData.devRequest && appData.devRequest.trim() !== ''

  useEffect(() => {
    // Initialize both frontend components and backend APIs from ChatPage
    const initializeData = async () => {
      if (!completedPages.chat) return

      setIsLoading(true)
      try {
        const componentsFromChat = appData.components || []
        const apisFromChat = appData.backendApis || []

        if (componentsFromChat.length === 0 && apisFromChat.length === 0) {
          console.warn('No components or APIs found in appData')
          setIsLoading(false)
          return
        }

        // Transform frontend components
        if (componentsFromChat.length > 0) {
          const transformedComponents = componentsFromChat.map(comp => {
            let displayName = comp.name
            if (displayName.startsWith('App')) displayName = displayName.substring(3)
            if (displayName.endsWith('Component')) displayName = displayName.substring(0, displayName.length - 9)
            displayName = displayName.replace(/([A-Z])/g, ' $1').trim()
            return {
              id: comp.id_name || comp.name,
              name: displayName,
              originalName: comp.name,
              description: comp.description,
              import_path: comp.import_path,
              ...comp
            }
          })
          setComponents(transformedComponents)
          updateAppData({ components: transformedComponents })
        }

        // Transform backend APIs
        if (apisFromChat.length > 0) {
          const transformedApis = apisFromChat.map(api => {
            let displayName = api.name
            // Make display name more readable
            displayName = displayName.replace(/Controller|API|Api/gi, '').trim()
            displayName = displayName.replace(/([A-Z])/g, ' $1').trim()
            return {
              id: api.id || api.name,
              name: displayName,
              originalName: api.name,
              description: api.description,
              file_path: api.file_path,
              endpoints: api.endpoints || [],
              ...api
            }
          })
          setBackendApis(transformedApis)
          updateAppData({ backendApis: transformedApis })
        }

        // 1. Start Background Task for AI selection
        const response = await fetch('http://localhost:5000/api/select-components', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ pageRequest: appData.devRequest || '' })
        })

        if (!response.ok) throw new Error('Failed to start selection task')
        
        const initData = await response.json()
        const taskId = initData.task_id

        console.log(`Selection Task Started: ${taskId}. Polling for results...`)

        // 2. Poll for Results
        let finalData = null
        while (true) {
          const statusRes = await fetch(`http://localhost:5000/api/tasks/${taskId}`)
          if (!statusRes.ok) throw new Error('Failed to poll status')
          
          const taskStatus = await statusRes.json()
          
          if (taskStatus.status === 'completed') {
            finalData = taskStatus.result
            break
          } else if (taskStatus.status === 'failed') {
            throw new Error(taskStatus.error || 'Selection task failed')
          }
          
          // Wait 2 seconds
          await new Promise(resolve => setTimeout(resolve, 2000))
        }

        console.log('Selection Complete:', finalData)

        // 3. Process Frontend Component Selection
        const componentReasoning = finalData.component_reasoning || finalData.reasoning || {}
        setAiReasoning(componentReasoning)

        if (componentReasoning && Object.keys(componentReasoning).length > 0) {
          setEditedReasoning(componentReasoning)
          updateAppData({ componentReasoning })
        } else if (appData.componentReasoning) {
          setEditedReasoning(appData.componentReasoning)
        }

        const selectedComponentIds = finalData.selected_component_ids || []
        if (selectedComponentIds.length > 0) {
          setSelectedComponents(selectedComponentIds)
          updateAppData({ selectedComponents: selectedComponentIds })
        }

        // 4. Process Backend API Selection
        const apiReasoning = finalData.api_reasoning || {}
        setAiApiReasoning(apiReasoning)

        if (apiReasoning && Object.keys(apiReasoning).length > 0) {
          setEditedApiReasoning(apiReasoning)
          updateAppData({ apiReasoning })
        } else if (appData.apiReasoning) {
          setEditedApiReasoning(appData.apiReasoning)
        }

        const selectedApiIds = finalData.selected_api_ids || []
        if (selectedApiIds.length > 0) {
          setSelectedApis(selectedApiIds)
          updateAppData({ selectedApis: selectedApiIds })
        }
        
      } catch (error) {
        console.error('Error initializing data:', error)
        alert(`Error: ${error.message}`)
      } finally {
        setIsLoading(false)
      }
    }

    initializeData()
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

  // Backend API handlers
  const toggleApi = (apiId) => {
    setSelectedApis(prev => {
      const newSelection = prev.includes(apiId)
        ? prev.filter(id => id !== apiId)
        : [...prev, apiId]
      updateAppData({ selectedApis: newSelection })

      // If API is removed, also remove its reasoning
      if (prev.includes(apiId)) {
        setEditedApiReasoning(prevReasoning => {
          const newReasoning = { ...prevReasoning }
          delete newReasoning[apiId]
          updateAppData({ apiReasoning: newReasoning })
          return newReasoning
        })
      } else {
        // If API is added and has AI reasoning, initialize it
        if (aiApiReasoning[apiId] && !editedApiReasoning[apiId]) {
          setEditedApiReasoning(prevReasoning => {
            const newReasoning = { ...prevReasoning, [apiId]: aiApiReasoning[apiId] }
            updateAppData({ apiReasoning: newReasoning })
            return newReasoning
          })
        }
      }

      return newSelection
    })
  }

  const handleApiReasoningChange = (apiId, newReasoning) => {
    setEditedApiReasoning(prev => {
      const updated = { ...prev, [apiId]: newReasoning }
      updateAppData({ apiReasoning: updated })
      return updated
    })
  }

  const handleContinue = async () => {
    // Save final reasoning before continuing
    updateAppData({ 
      componentReasoning: editedReasoning,
      apiReasoning: editedApiReasoning
    })

    try {
      // === UPDATE FRONTEND COMPONENT METADATA ===
      if (components.length > 0) {
        const originalComponents = appData.components || components
        const updatedComponents = originalComponents.map(comp => {
          const compId = comp.id || comp.id_name || comp.name
          const isRequired = selectedComponents.includes(compId)
          const compReasoning = editedReasoning[compId] || ''
          const requiredValue = isRequired ? true : false

          console.log(`Component ${compId}: required=${requiredValue}`)

          return {
            ...comp,
            required: requiredValue,
            reasoning: compReasoning
          }
        })

        const requiredCount = updatedComponents.filter(c => c.required === true).length
        console.log(`Updating frontend metadata: ${requiredCount} required components`)

        const response = await fetch('http://localhost:5000/api/update-component-metadata', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ components: updatedComponents })
        })

        if (!response.ok) {
          const errorData = await response.json().catch(() => ({ detail: `Server error: ${response.status}` }))
          throw new Error(errorData.detail || `Server error: ${response.status}`)
        }

        const data = await response.json()
        if (data.status !== 'success') {
          throw new Error(data.message || 'Failed to update component metadata')
        }

        console.log('✓ Frontend component metadata updated successfully')
      }

      // === UPDATE BACKEND API METADATA ===
      if (backendApis.length > 0) {
        const originalApis = appData.backendApis || backendApis
        const updatedApis = originalApis.map(api => {
          const apiId = api.id || api.name
          const isRequired = selectedApis.includes(apiId)
          const apiReasoningText = editedApiReasoning[apiId] || ''
          const requiredValue = isRequired ? true : false

          console.log(`API ${apiId}: required=${requiredValue}`)

          return {
            ...api,
            required: requiredValue,
            reasoning: apiReasoningText
          }
        })

        const requiredApiCount = updatedApis.filter(a => a.required === true).length
        console.log(`Updating backend metadata: ${requiredApiCount} required APIs`)

        const apiResponse = await fetch('http://localhost:5000/api/update-api-metadata', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ apis: updatedApis })
        })

        if (!apiResponse.ok) {
          const errorData = await apiResponse.json().catch(() => ({ detail: `Server error: ${apiResponse.status}` }))
          throw new Error(errorData.detail || `Server error: ${apiResponse.status}`)
        }

        const apiData = await apiResponse.json()
        if (apiData.status !== 'success') {
          throw new Error(apiData.message || 'Failed to update API metadata')
        }

        console.log('✓ Backend API metadata updated successfully')
      }

      // Clear old generated files so DownloadPage will regenerate with updated metadata
      updateAppData({ generatedFiles: null })

      // Mark elements page as complete and navigate
      markPageComplete('elements')
      navigate('/download')
    } catch (error) {
      console.error('Error updating metadata:', error)
      alert(`Error updating metadata: ${error.message}\n\nMake sure the backend server is running on http://localhost:5000`)
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

  const selectedApisWithReasoning = selectedApis
    .map(id => {
      const api = backendApis.find(a => a.id === id)
      const currentReasoning = editedApiReasoning[id] || aiApiReasoning[id] || ''
      const isAiSelected = !!aiApiReasoning[id]
      return api ? {
        ...api,
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
          {/* Frontend Components Section */}
          {components.length > 0 && (
            <>
              <h2>Frontend Components 🎨</h2>
              <p className="sidebar-description">Select Angular components:</p>
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
            </>
          )}

          {/* Backend APIs Section */}
          {backendApis.length > 0 && (
            <>
              <h2 style={{ marginTop: components.length > 0 ? '2rem' : '0' }}>Backend APIs 🐘</h2>
              <p className="sidebar-description">Select PHP API endpoints:</p>
              <div className="elements-list">
                {backendApis.map((api) => (
                  <div
                    key={api.id}
                    className={`element-item ${selectedApis.includes(api.id) ? 'selected' : ''}`}
                    onClick={() => toggleApi(api.id)}
                  >
                    <input
                      type="checkbox"
                      checked={selectedApis.includes(api.id)}
                      onChange={() => toggleApi(api.id)}
                      className="element-checkbox"
                    />
                    <span className="element-name">{api.name}</span>
                  </div>
                ))}
              </div>
            </>
          )}

          <button
            className="generate-button"
            onClick={handleContinue}
            disabled={false}
            style={{ marginTop: '2rem' }}
          >
            Continue
          </button>
        </div>

        <div className="reasoning-section">
          <h2>Requirements & Context</h2>
          <p className="reasoning-section-description">
            Edit the requirements for each selected item. This context will be used when generating code.
          </p>
          
          {/* Frontend Components Reasoning */}
          {selectedComponentsWithReasoning.length > 0 && (
            <>
              <h3 style={{ marginTop: '1.5rem', marginBottom: '1rem', color: '#2c3e50' }}>Frontend Components</h3>
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
                    </div>
                  </div>
                ))}
              </div>
            </>
          )}

          {/* Backend APIs Reasoning */}
          {selectedApisWithReasoning.length > 0 && (
            <>
              <h3 style={{ marginTop: '2rem', marginBottom: '1rem', color: '#2c3e50' }}>Backend APIs</h3>
              <div className="reasoning-list">
                {selectedApisWithReasoning.map((api) => (
                  <div key={api.id} className="reasoning-item">
                    <div className="reasoning-header">
                      <h3 className="reasoning-component-name">{api.name}</h3>
                      {api.isAiSelected && (
                        <span className="reasoning-badge">AI Selected</span>
                      )}
                    </div>
                    <div className="reasoning-input-container">
                      <label className="reasoning-label">
                        Usage & Context:
                      </label>
                      <textarea
                        className="reasoning-textarea"
                        value={api.reasoning || ''}
                        onChange={(e) => handleApiReasoningChange(api.id, e.target.value)}
                        placeholder={
                          api.isAiSelected
                            ? "Edit the AI's reasoning or add your own context..."
                            : "Enter how this API will be used in the page..."
                        }
                        rows={4}
                      />
                      {api.endpoints && api.endpoints.length > 0 && (
                        <div style={{ marginTop: '0.5rem', fontSize: '0.85rem', color: '#666' }}>
                          <strong>Endpoints:</strong>
                          <ul style={{ marginTop: '0.25rem', paddingLeft: '1.5rem' }}>
                            {api.endpoints.slice(0, 3).map((endpoint, idx) => (
                              <li key={idx}>
                                <code>{endpoint.method} {endpoint.path}</code>
                              </li>
                            ))}
                            {api.endpoints.length > 3 && (
                              <li>... and {api.endpoints.length - 3} more</li>
                            )}
                          </ul>
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </>
          )}

          {selectedComponentsWithReasoning.length === 0 && selectedApisWithReasoning.length === 0 && (
            <div className="reasoning-placeholder">
              <p>Select frontend components or backend APIs to add requirements and context</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default ElementsPage
