// API Configuration
// Centralized API configuration for the frontend

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

export const API_ENDPOINTS = {
  // Component Analysis
  UPLOAD_AND_ANALYZE: `${API_BASE_URL}/api/upload-and-analyze`,
  
  // Component Selection
  SELECT_COMPONENTS: `${API_BASE_URL}/api/select-components`,
  UPDATE_COMPONENT: `${API_BASE_URL}/api/update-component`,
  
  // Page Generation
  GENERATE_PAGE: `${API_BASE_URL}/api/generate-page`,
  
  // System
  HEALTH: `${API_BASE_URL}/api/health`,
  RESET: `${API_BASE_URL}/api/reset`,
};

// Helper function to make API calls
export const apiCall = async (endpoint, options = {}) => {
  const defaultOptions = {
    headers: {
      'Content-Type': 'application/json',
    },
  };

  const response = await fetch(endpoint, {
    ...defaultOptions,
    ...options,
    headers: {
      ...defaultOptions.headers,
      ...options.headers,
    },
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `API Error: ${response.statusText}`);
  }

  return response.json();
};

export default API_ENDPOINTS;
