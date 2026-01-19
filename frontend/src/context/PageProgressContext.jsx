import { createContext, useContext, useState, useEffect } from 'react'

const PageProgressContext = createContext()

export const usePageProgress = () => {
  const context = useContext(PageProgressContext)
  if (!context) {
    throw new Error('usePageProgress must be used within PageProgressProvider')
  }
  return context
}

export const PageProgressProvider = ({ children }) => {
  // Check if app session is active (exists during navigation, cleared on reload)
  const hasActiveSession = () => {
    return sessionStorage.getItem('appSessionActive') === 'true'
  }

  const [completedPages, setCompletedPages] = useState(() => {
    // Only restore from sessionStorage if we have an active session (navigation within app)
    // On page reload, the flag is cleared, so we start fresh
    if (hasActiveSession()) {
      const saved = sessionStorage.getItem('pageProgress')
      return saved ? JSON.parse(saved) : { chat: false, elements: false, download: false }
    }
    // Page reload or first visit - start fresh
    return { chat: false, elements: false, download: false }
  })

  const [appData, setAppData] = useState(() => {
    // Only restore from sessionStorage if we have an active session
    if (hasActiveSession()) {
      const saved = sessionStorage.getItem('appData')
      return saved ? JSON.parse(saved) : {
        folder: null,
        devRequest: '',
        components: [],
        selectedComponents: [],
        componentReasoning: {},
        generatedFiles: {
          html: '',
          css: '',
          ts: ''
        }
      }
    }
    // Page reload or first visit - start fresh
    return {
      folder: null,
      devRequest: '',
      components: [],
      selectedComponents: [],
      componentReasoning: {},
      generatedFiles: {
        html: '',
        css: '',
        ts: ''
      }
    }
  })

  // Chat state
  const [chatHistory, setChatHistory] = useState(() => {
    if (hasActiveSession()) {
      const saved = sessionStorage.getItem('chatHistory')
      return saved ? JSON.parse(saved) : []
    }
    return []
  })
  const [isChatLoading, setIsChatLoading] = useState(false)

  // Handle page reload detection and session management
  useEffect(() => {
    // If no active session flag exists, this is a reload or first visit
    // Clear any stale data from sessionStorage
    if (!hasActiveSession()) {
      sessionStorage.removeItem('pageProgress')
      sessionStorage.removeItem('appData')
    }

    // Set app session flag to track active session (for navigation within app)
    sessionStorage.setItem('appSessionActive', 'true')

    // Clear flag on page unload (reload/close) so next load starts fresh
    const handleBeforeUnload = () => {
      sessionStorage.removeItem('appSessionActive')
    }

    window.addEventListener('beforeunload', handleBeforeUnload)

    return () => {
      window.removeEventListener('beforeunload', handleBeforeUnload)
    }
  }, [])

  // Save to sessionStorage whenever completedPages changes
  useEffect(() => {
    sessionStorage.setItem('pageProgress', JSON.stringify(completedPages))
  }, [completedPages])

  // Save app data to sessionStorage whenever it changes (excluding folder)
  useEffect(() => {
    const dataToSave = {
      devRequest: appData.devRequest,
      components: appData.components,
      selectedComponents: appData.selectedComponents,
      componentReasoning: appData.componentReasoning || {},
      generatedFiles: appData.generatedFiles
      // Don't save folder to sessionStorage (File objects aren't serializable)
    }
    sessionStorage.setItem('appData', JSON.stringify(dataToSave))
  }, [appData.devRequest, appData.components, appData.selectedComponents, appData.componentReasoning, appData.generatedFiles])

  // Save chat history to sessionStorage
  useEffect(() => {
    sessionStorage.setItem('chatHistory', JSON.stringify(chatHistory))
  }, [chatHistory])

  const markPageComplete = (page) => {
    setCompletedPages(prev => ({ ...prev, [page]: true }))
  }

  const resetProgress = () => {
    setCompletedPages({ chat: false, elements: false, download: false })
    setAppData({
      folder: null,
      devRequest: '',
      components: [],
      selectedComponents: [],
      componentReasoning: {},
      generatedFiles: {
        html: '',
        css: '',
        ts: ''
      }
    })
    setChatHistory([])
    sessionStorage.removeItem('pageProgress')
    sessionStorage.removeItem('appData')
    sessionStorage.removeItem('chatHistory')
  }

  const updateAppData = (updates) => {
    setAppData(prev => ({ ...prev, ...updates }))
  }

  const sendChatMessage = async (message) => {
    if (!message.trim() || isChatLoading) return

    const userMsg = message.trim()

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

      // Update appData with new code
      updateAppData({
        generatedFiles: {
          html: data.html_code,
          scss: data.scss_code,
          ts: data.ts_code,
          // Preserve existing metadata if not returned
          component_name: appData.generatedFiles?.component_name,
          path_name: appData.generatedFiles?.path_name,
          selector: appData.generatedFiles?.selector
        }
      })

      // Add assistant message
      setChatHistory(prev => [...prev, { role: 'assistant', content: 'I have updated the code based on your request.' }])

      return data
    } catch (error) {
      console.error('Chat error:', error)
      setChatHistory(prev => [...prev, { role: 'assistant', content: `Error: ${error.message}` }])
      throw error
    } finally {
      setIsChatLoading(false)
    }
  }

  const isPageAccessible = (page) => {
    if (page === 'chat') return true
    if (page === 'elements') return completedPages.chat
    if (page === 'download') return completedPages.chat && completedPages.elements
    return false
  }

  return (
    <PageProgressContext.Provider value={{
      completedPages,
      markPageComplete,
      resetProgress,
      isPageAccessible,
      appData,
      updateAppData,
      chatHistory,
      isChatLoading,
      sendChatMessage
    }}>
      {children}
    </PageProgressContext.Provider>
  )
}