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
    sessionStorage.removeItem('pageProgress')
    sessionStorage.removeItem('appData')
  }

  const updateAppData = (updates) => {
    setAppData(prev => ({ ...prev, ...updates }))
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
      updateAppData
    }}>
      {children}
    </PageProgressContext.Provider>
  )
}