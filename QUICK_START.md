# Quick Start Guide

## Backend Setup & Start

### Step 1: Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### Step 2: Start the API Server
```bash
python api_server.py
```

You should see:
```
============================================================
ANGULAR PAGE GENERATOR API SERVER (FastAPI)
============================================================
Server starting on http://localhost:5000

📖 Swagger UI:  http://localhost:5000/docs
📖 ReDoc:       http://localhost:5000/redoc
============================================================
```

**New with FastAPI:**
- **Interactive API Documentation** at http://localhost:5000/docs
- **Alternative Documentation** at http://localhost:5000/redoc
- **Native async/await** for better performance
- **Automatic request/response validation**

## Frontend Setup & Start

### Step 1: Install Dependencies (if not done)
```bash
cd frontend
npm install
```

### Step 2: Start the Development Server
```bash
npm run dev
```

The app will open at `http://localhost:5173`

## Using the Application

### Screen 1: Upload & Request
1. Enter your page request (e.g., "Create a user profile page")
2. Click "Select Folder" and choose your Angular components directory
3. Click Send (arrow button)
4. Wait for components to be analyzed

### Screen 2: Component Selection
1. Review the components that were automatically selected by AI (marked with "AI Selected" badge)
2. Check/uncheck additional components as needed
3. Edit the reasoning for each component if desired
4. Click "Continue"

### Screen 3: Code Generation
1. View the generated HTML, SCSS, and TypeScript code
2. See the live preview
3. Edit the code if needed and click "Save" to update preview
4. Click "Download All Files" to get a ZIP file

## Troubleshooting

### Backend won't start
- Make sure you have Python 3.8+ installed
- Install dependencies: `pip install -r requirements.txt`
- Check if port 5000 is available

### Frontend can't connect to backend
- Make sure backend is running on http://localhost:5000
- Check browser console for errors
- Ensure CORS is not being blocked

### "No components available" error
- Make sure you uploaded a valid Angular components directory
- Components should be in separate folders with .ts, .html, and .scss files

## Architecture

```
┌─────────────────┐
│   Frontend      │
│  (React/Vite)   │
└────────┬────────┘
         │ HTTP
         ▼
┌─────────────────┐
│  API Server     │
│  (Flask)        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Modular        │
│  Pipelines      │
│  - Metadata Gen │
│  - Component    │
│    Selection    │
│  - Page Gen     │
└─────────────────┘
```

## What's Integrated

✅ **Upload & Analysis**: Upload components, generate metadata with LLM
✅ **Component Selection**: LLM automatically selects relevant components
✅ **Reasoning Generation**: LLM explains why each component is needed
✅ **Code Generation**: Generate HTML, SCSS, TypeScript based on request
✅ **Preview & Download**: View code, see preview, download files

## Need Help?

See [INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md) for detailed documentation.
