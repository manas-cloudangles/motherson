# API Integration Documentation

## Overview

This document describes the complete integration between the frontend React application and the backend FastAPI server for the Angular Page Generator.

## Architecture Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER WORKFLOW                           │
└─────────────────────────────────────────────────────────────────┘

1. CHAT PAGE (Upload & Request)
   ↓
   [API: /api/upload-and-analyze]
   ↓
2. ELEMENTS PAGE (Component Selection)
   ↓
   [API: /api/select-components]
   ↓
   [API: /api/update-component] (on each change)
   ↓
3. DOWNLOAD PAGE (Generated Code)
   ↓
   [API: /api/generate-page]
```

## API Endpoints

### 1. Upload and Analyze Components

**Endpoint:** `POST /api/upload-and-analyze`

**Purpose:** Analyzes components from a local folder and generates metadata

**Request Body:**
```json
{
  "folderPath": "C:/path/to/components",
  "pageRequest": "Create a user dashboard with login functionality"
}
```

**Response:**
```json
{
  "status": "success",
  "components": [
    {
      "id_name": "button-component",
      "name": "ButtonComponent",
      "description": "A reusable button component",
      "import_path": "./button/button.component",
      "selector": "app-button",
      ...
    }
  ],
  "message": "Analyzed 15 components successfully"
}
```

**Frontend Usage:**
- Called from ChatPage when user submits folder and request
- Stores component metadata in backend for subsequent operations

---

### 2. Select Components (LLM-based)

**Endpoint:** `POST /api/select-components`

**Purpose:** Uses LLM to determine which components are needed based on page request

**Request Body:**
```json
{
  "pageRequest": "Create a user dashboard with login functionality"
}
```

**Response:**
```json
{
  "status": "success",
  "components": [
    {
      "id_name": "button-component",
      "name": "ButtonComponent",
      "required": true,
      "reasoning": "Button component is needed for login and action buttons",
      "description": "A reusable button component",
      ...
    },
    {
      "id_name": "input-component",
      "name": "InputComponent",
      "required": true,
      "reasoning": "Input fields are necessary for username and password entry",
      ...
    },
    {
      "id_name": "navbar-component",
      "name": "NavbarComponent",
      "required": false,
      "reasoning": "",
      ...
    }
  ]
}
```

**Frontend Usage:**
- Called from ElementsPage when it first loads
- Displays all components with checkboxes
- Pre-selects components where `required: true`
- Shows reasoning only for required components

---

### 3. Update Component Selection

**Endpoint:** `POST /api/update-component`

**Purpose:** Updates a component's required status and reasoning in real-time

**Request Body:**
```json
{
  "componentId": "button-component",
  "required": true,
  "reasoning": "Button component is needed for login and action buttons"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Component button-component updated successfully"
}
```

**Frontend Usage:**
- Called when user checks/unchecks a component checkbox
- Called when user finishes editing reasoning (onBlur event)
- Updates component-metadata.json on backend immediately

---

### 4. Generate Page

**Endpoint:** `POST /api/generate-page`

**Purpose:** Generates HTML, SCSS, and TypeScript code for the page using selected components

**Request Body:**
```json
{
  "pageRequest": "Create a user dashboard with login functionality",
  "selectedComponentIds": []
}
```

**Note:** If `selectedComponentIds` is empty, the API uses all components marked as `required: true`

**Response:**
```json
{
  "status": "success",
  "html_code": "<div class=\"dashboard\">...</div>",
  "scss_code": ".dashboard { ... }",
  "ts_code": "import { Component } from '@angular/core';\n...",
  "component_name": "UserDashboardComponent",
  "path_name": "user-dashboard",
  "selector": "app-user-dashboard"
}
```

**Frontend Usage:**
- Called from DownloadPage when it first loads
- Uses components marked as required in backend
- Displays generated code in tabs (HTML, CSS, TypeScript)

---

## Frontend State Management

### ChatPage State
```javascript
{
  folder: FileList,           // Selected folder files
  devRequest: string,          // User's page request
  folderPath: string           // Absolute folder path
}
```

### ElementsPage State
```javascript
{
  components: Array<{
    id: string,                // Component ID (id_name)
    name: string,              // Component name
    description: string,       // Component description
    required: boolean,         // Is this component required?
    reasoning: string          // Why is this component needed?
  }>,
  selectedComponents: string[], // Array of selected component IDs
  componentReasoning: {        // Map of component ID to reasoning
    [componentId]: string
  }
}
```

### DownloadPage State
```javascript
{
  generatedFiles: {
    html: string,              // Generated HTML code
    css: string,               // Generated SCSS code
    ts: string                 // Generated TypeScript code
  },
  componentInfo: {
    name: string,              // Component class name
    pathName: string,          // Component path name
    selector: string           // Component selector
  }
}
```

---

## User Interaction Flow

### Step 1: Upload Components (ChatPage)
1. User selects a folder containing Angular components
2. User enters a page request description
3. User clicks submit button
4. Frontend prompts for absolute folder path
5. Frontend calls `POST /api/upload-and-analyze`
6. Backend analyzes components and stores metadata
7. User navigates to ElementsPage

### Step 2: Select Components (ElementsPage)
1. Frontend calls `POST /api/select-components`
2. Backend uses LLM to determine required components
3. Frontend displays all components with checkboxes
4. Required components are pre-checked with reasoning shown
5. **User Interaction:**
   - User can check/uncheck any component
   - On toggle: Frontend calls `POST /api/update-component`
   - User can edit reasoning for any selected component
   - On blur: Frontend calls `POST /api/update-component` with new reasoning
6. Backend updates component-metadata.json in real-time
7. User clicks "Continue" to navigate to DownloadPage

### Step 3: Generate Code (DownloadPage)
1. Frontend calls `POST /api/generate-page`
2. Backend uses only components marked as required
3. Backend generates HTML, SCSS, and TypeScript code
4. Frontend displays generated code in tabs
5. User can preview and download the generated files

---

## Key Features

### Real-time Component Updates
- When user checks a component: `required` flag set to `true` immediately
- When user unchecks a component: `required` flag set to `false`, reasoning cleared
- When user edits reasoning: Updated on blur event
- All changes are saved to `component-metadata.json` on backend

### Optimistic UI Updates
- UI updates immediately when user interacts
- API calls happen in background
- If API call fails, UI reverts to previous state
- User receives error notification

### Component Reasoning Workflow
1. **AI-Selected Components:** Pre-populated with LLM-generated reasoning
2. **User-Selected Components:** User must add reasoning manually
3. **Reasoning Updates:** Saved automatically when user leaves textarea (blur event)

### Error Handling
- All API calls wrapped in try-catch blocks
- User-friendly error messages displayed
- Failed operations revert UI state
- Console logging for debugging

---

## Backend Data Persistence

### component-metadata.json Structure
```json
[
  {
    "id_name": "button-component",
    "name": "ButtonComponent",
    "description": "A reusable button component",
    "import_path": "./button/button.component",
    "selector": "app-button",
    "required": true,
    "reasoning": "Button component is needed for login and action buttons",
    "html_content": "...",
    "scss_content": "...",
    "ts_content": "...",
    "inputs": [...],
    "outputs": [...],
    "methods": [...]
  }
]
```

### Data Flow
1. `upload-and-analyze` → Creates initial metadata (no required/reasoning)
2. `select-components` → Adds required flag and reasoning to metadata
3. `update-component` → Updates individual component's required/reasoning
4. `generate-page` → Reads metadata, filters by required flag, generates code

---

## Configuration

### Backend Configuration
- **Port:** 5000 (default)
- **Host:** 0.0.0.0
- **CORS:** Enabled for all origins (configure for production)

### Frontend Configuration
- **API Base URL:** `http://localhost:5000` (configurable via environment variable)
- See `frontend/src/config/api.js` for centralized configuration

---

## Testing the Integration

### 1. Start Backend Server
```bash
cd backend
python api_server.py
```

Server starts on: http://localhost:5000
API Documentation: http://localhost:5000/docs

### 2. Start Frontend Development Server
```bash
cd frontend
npm install
npm run dev
```

Frontend starts on: http://localhost:5173 (Vite default)

### 3. Test Workflow
1. Open browser to frontend URL
2. Upload a folder and enter a request
3. Verify components are displayed with AI selections
4. Toggle components and edit reasoning
5. Check browser console for API call logs
6. Verify generated code appears on download page

### 4. Monitor Backend
- Check terminal for API call logs
- Verify `component_metadata.json` is updated
- Check for any error messages

---

## Production Considerations

### Security
- [ ] Configure CORS with specific frontend origin
- [ ] Add authentication/authorization if needed
- [ ] Validate all user inputs on backend
- [ ] Sanitize file paths to prevent directory traversal

### Performance
- [ ] Add request debouncing for reasoning updates
- [ ] Implement caching for component metadata
- [ ] Consider WebSocket for real-time updates
- [ ] Optimize LLM calls (batch requests if possible)

### Error Handling
- [ ] Implement retry logic for failed API calls
- [ ] Add comprehensive error logging
- [ ] Show user-friendly error messages
- [ ] Handle network timeouts gracefully

### Deployment
- [ ] Use environment variables for API URL
- [ ] Set up proper HTTPS certificates
- [ ] Configure reverse proxy (nginx)
- [ ] Set up process manager (PM2) for backend
- [ ] Build frontend for production (`npm run build`)

---

## Troubleshooting

### Common Issues

**Issue:** CORS errors in browser console
**Solution:** Ensure backend CORS middleware is configured correctly

**Issue:** "Failed to fetch" errors
**Solution:** Verify backend server is running on correct port

**Issue:** Component metadata not persisting
**Solution:** Check file permissions for `component_metadata.json`

**Issue:** LLM selection not working
**Solution:** Verify OpenAI API keys are configured in backend

**Issue:** Generated code is empty
**Solution:** Ensure components are marked as required before generating

---

## API Client Example (React Hook)

```javascript
// hooks/useApi.js
import { useState } from 'react';
import { apiCall } from '../config/api';

export const useApi = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const call = async (endpoint, options) => {
    setLoading(true);
    setError(null);
    
    try {
      const data = await apiCall(endpoint, options);
      return data;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return { call, loading, error };
};
```

---

## Next Steps

1. ✅ Backend API endpoints implemented
2. ✅ Frontend API integration completed
3. ✅ Real-time component updates working
4. ✅ Component reasoning editable by user
5. 🔄 Test complete workflow end-to-end
6. 🔄 Add proper error handling and user feedback
7. 🔄 Implement request debouncing for reasoning updates
8. 🔄 Add loading states and progress indicators
9. 🔄 Deploy to production environment

---

## Support

For issues or questions:
- Check backend logs: Terminal where `api_server.py` is running
- Check frontend console: Browser Developer Tools (F12)
- Review API documentation: http://localhost:5000/docs
- Check this documentation for API contracts and flows
