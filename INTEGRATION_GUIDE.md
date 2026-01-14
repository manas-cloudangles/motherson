# Frontend-Backend Integration Guide

## Overview

The frontend and backend are now fully integrated! The application follows a 3-screen workflow:

1. **ChatPage** - Upload components directory & enter page request
2. **ElementsPage** - View components with LLM-powered selection & reasoning
3. **DownloadPage** - View and download generated code

---

## Setup Instructions

### 1. Install Backend Dependencies

```bash
cd backend
pip install flask flask-cors
```

### 2. Start the Backend Server

```bash
cd backend
python api_server.py
```

The server will start on `http://localhost:5000`

You should see:
```
============================================================
ANGULAR PAGE GENERATOR API SERVER
============================================================

Endpoints:
  POST /api/upload-and-analyze  - Upload components & generate metadata
  POST /api/select-components   - Select components for page request
  POST /api/generate-page       - Generate page code
  POST /api/reset               - Reset session
  GET  /api/health              - Health check

Server starting on http://localhost:5000
============================================================
```

### 3. Start the Frontend

```bash
cd frontend
npm install  # if not already done
npm run dev
```

The frontend will start on `http://localhost:5173` (or similar)

---

## How It Works

### Screen 1: ChatPage (Upload & Request)

**User Actions:**
1. User enters a page generation request (e.g., "Create a user profile page")
2. User selects/uploads a folder containing Angular components
3. User clicks "Send" button

**What Happens:**
- Frontend uploads all files to backend
- Backend analyzes components and generates metadata using LLM
- Each component is analyzed for:
  - Name, description
  - Import paths
  - Selectors/IDs
  - Source code (HTML, SCSS, TS)
- Frontend stores component metadata
- Navigate to ElementsPage

**API Call:**
```javascript
POST http://localhost:5000/api/upload-and-analyze
Body: FormData with files + pageRequest
Response: { components: [...], message: "..." }
```

---

### Screen 2: ElementsPage (Component Selection)

**What Happens Automatically:**
1. Frontend displays all identified components
2. Backend uses LLM to determine which components are needed for the request
3. LLM provides reasoning for each selected component
4. Selected components are pre-checked with checkmarks
5. Reasoning is displayed in editable text boxes

**User Actions:**
- Review LLM-selected components (marked with "AI Selected" badge)
- Check/uncheck components as needed
- Edit reasoning for each component
- Click "Continue" to proceed

**API Call:**
```javascript
POST http://localhost:5000/api/select-components
Body: { pageRequest: "..." }
Response: {
  all_components: [...],
  selected_component_ids: [...],
  reasoning: { "component-id": "reason", ... }
}
```

**Display:**
- Left sidebar: All components with checkboxes
- Right panel: Selected components with editable reasoning
- AI-selected components have a badge

---

### Screen 3: DownloadPage (Code Generation & Preview)

**What Happens Automatically:**
1. Backend generates HTML, SCSS, and TypeScript code
2. Uses selected components and their reasoning
3. LLM creates a complete Angular component

**User Actions:**
- View generated code in tabs (HTML/CSS/TS)
- See live preview of HTML
- Edit code if needed
- Click "Save" to update preview
- Click "Download All Files" to download as ZIP

**API Call:**
```javascript
POST http://localhost:5000/api/generate-page
Body: {
  pageRequest: "...",
  selectedComponentIds: [...]
}
Response: {
  html_code: "...",
  scss_code: "...",
  ts_code: "...",
  component_name: "...",
  path_name: "...",
  selector: "..."
}
```

**Features:**
- Code tabs for HTML, CSS, TypeScript
- Live preview of rendered HTML
- Syntax-highlighted code editing
- Download as individual files or ZIP

---

## API Endpoints

### POST /api/upload-and-analyze

Upload components directory and generate metadata.

**Request:**
```javascript
FormData {
  files: [File, File, ...],  // All files from directory
  pageRequest: "Create a user profile page"
}
```

**Response:**
```json
{
  "status": "success",
  "components": [
    {
      "name": "AppButtonComponent",
      "id_name": "app-button",
      "description": "A reusable button component...",
      "import_path": "app/common/components/app-button/app-button.component",
      "html_code": "<button>...</button>",
      "scss_code": ".button {...}",
      "ts_code": "export class AppButtonComponent..."
    },
    ...
  ],
  "message": "Analyzed 5 components successfully"
}
```

---

### POST /api/select-components

Determine which components are needed using LLM.

**Request:**
```json
{
  "pageRequest": "Create a user profile page"
}
```

**Response:**
```json
{
  "status": "success",
  "all_components": [...],
  "selected_component_ids": ["app-button", "app-input", "app-form"],
  "reasoning": {
    "app-button": "Buttons are needed for save/cancel actions on the profile form",
    "app-input": "Input fields are required for entering user information",
    "app-form": "Form component provides structure for user data collection"
  }
}
```

---

### POST /api/generate-page

Generate Angular page code.

**Request:**
```json
{
  "pageRequest": "Create a user profile page",
  "selectedComponentIds": ["app-button", "app-input", "app-form"]
}
```

**Response:**
```json
{
  "status": "success",
  "html_code": "<div class=\"profile-page\">...</div>",
  "scss_code": ".profile-page { display: flex; ... }",
  "ts_code": "import { Component } from '@angular/core'...",
  "component_name": "UserProfileComponent",
  "path_name": "user-profile",
  "selector": "app-user-profile"
}
```

---

## Data Flow

```
User Input
   │
   ├─ Page Request: "Create a dashboard"
   └─ Components Directory Upload
           │
           ▼
   Backend: Component Metadata Generation
   - Analyzes each component
   - Extracts metadata
   - Returns component list
           │
           ▼
   Frontend: Display Components
   - Shows all components
   - Calls backend for LLM selection
           │
           ▼
   Backend: Component Selection (LLM)
   - Analyzes page request
   - Selects relevant components
   - Provides reasoning
           │
           ▼
   Frontend: User Reviews Selection
   - Checks/unchecks components
   - Edits reasoning
   - Clicks Continue
           │
           ▼
   Backend: Page Generation (LLM)
   - Uses selected components
   - Generates HTML, SCSS, TS
   - Returns complete code
           │
           ▼
   Frontend: Display & Download
   - Shows code tabs
   - Renders preview
   - Allows download
```

---

## State Management

The application uses `PageProgressContext` to manage state across pages:

```javascript
{
  devRequest: "User's page request",
  components: [...],  // All component metadata
  selectedComponents: [...],  // Selected component IDs
  componentReasoning: {...},  // Reasoning for each component
  generatedFiles: {
    html: "...",
    css: "...",
    ts: "..."
  },
  componentName: "...",
  pathName: "...",
  selector: "..."
}
```

---

## Error Handling

All API calls include error handling:

```javascript
try {
  const response = await fetch('http://localhost:5000/api/...');
  if (!response.ok) throw new Error(`Server error: ${response.status}`);
  const data = await response.json();
  if (data.error) throw new Error(data.error);
  // Process data...
} catch (error) {
  console.error('Error:', error);
  alert(`Error: ${error.message}\n\nMake sure backend is running`);
}
```

---

## Testing the Integration

### 1. Test Component Upload
1. Start backend server
2. Open frontend
3. Enter a request: "Create a login page"
4. Upload a components directory
5. Click Send
6. Verify: You see components on ElementsPage

### 2. Test Component Selection
1. Check that some components are pre-selected (with badge)
2. Verify reasoning is displayed
3. Try checking/unchecking components
4. Edit reasoning text
5. Click Continue

### 3. Test Code Generation
1. Wait for code generation
2. Verify HTML, CSS, TS tabs show code
3. Try editing code
4. Click Save to update preview
5. Click Download All Files

---

## Configuration

### Backend Port
Default: `http://localhost:5000`

To change, edit `backend/api_server.py`:
```python
app.run(debug=True, port=5000, host='0.0.0.0')
```

### Frontend API URL
The frontend is configured to call `http://localhost:5000`

If you change the backend port, update the fetch URLs in:
- `frontend/src/pages/ChatPage.jsx`
- `frontend/src/pages/ElementsPage.jsx`
- `frontend/src/pages/DownloadPage.jsx`

Or create a config file:
```javascript
// frontend/src/config.js
export const API_URL = 'http://localhost:5000';
```

---

## Troubleshooting

### "Failed to fetch" error
**Problem**: Backend server not running
**Solution**: Start the backend server with `python api_server.py`

### "CORS error"
**Problem**: CORS not configured
**Solution**: Already handled with `flask-cors`. If issues persist, check browser console.

### "No components available"
**Problem**: Component metadata not generated
**Solution**: Make sure you uploaded a valid components directory

### "LLM error"
**Problem**: AWS credentials or LLM configuration issue
**Solution**: Check `get_secrets.py` and AWS credentials

---

## Next Steps

### Optional Improvements

1. **Add Loading Indicators**
   - Show progress bars during uploads
   - Display "Analyzing..." messages

2. **Add File Validation**
   - Check file types before upload
   - Validate directory structure

3. **Add Error Messages**
   - Better error UI instead of alerts
   - Retry buttons for failed operations

4. **Add Download Options**
   - Download as ZIP (already implemented)
   - Download individual files
   - Choose download location

5. **Add Save/Load Sessions**
   - Save current state
   - Load previous sessions
   - Session management

---

## Complete! 🎉

Your application is now fully integrated:
- ✅ Upload and analyze components
- ✅ LLM-powered component selection
- ✅ Automatic reasoning generation
- ✅ Code generation with preview
- ✅ Download functionality

Start the backend, start the frontend, and try it out!
