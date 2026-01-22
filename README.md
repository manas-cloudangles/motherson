# Motherson: AI-Powered Angular Page Generator

A powerful, modular tool that leverages Large Language Models (LLMs) to automatically generate Angular components, pages, and styles from natural language descriptions.

---

## 🚀 Features

- **AI-Driven Generation**: Uses advanced LLMs (Bedrock/Claude, Groq) to understand requirements and generate code.
- **Smart Component Selection**: Automatically identifies and reuses existing Angular components to maintain consistency.
- **Interactive UI**: User-friendly React/Vite frontend for easy interaction with the generation pipelines.
- **Modular Architecture**: Separate pipelines for component metadata analysis and page generation.

---

## 📋 Prerequisites

- **Python**: 3.8 or higher
- **Node.js**: 16 or higher
- **AWS Credentials**: Configured for Bedrock access (if using AWS).
- **Groq API Key**: If using Groq models.

---

## 🔧 Environment Configuration (.env)

Since environment variables are not version-controlled, you must create a `.env` file in the `backend/` directory.

**File Path**: `backend/.env`

Copy the following content and update with your keys:

```ini
# LLM Provider Configuration
# Options: "groq" (faster, cheaper) or "bedrock" (AWS Claude Sonnet)
LLM_PROVIDER=groq

# ------------------------------------------------------------------
# GROQ CONFIGURATION
# Get your API key from: https://console.groq.com/
# ------------------------------------------------------------------
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=moonshotai/kimi-k2-instruct-0905

# ------------------------------------------------------------------
# AWS BEDROCK CONFIGURATION
# Required if LLM_PROVIDER=bedrock
# ------------------------------------------------------------------
AWS_PROFILE=your-aws-profile  # e.g., cloudangles-mlops
AWS_REGION=us-east-1

# ------------------------------------------------------------------
# LLM TUNING
# ------------------------------------------------------------------
LLM_MAX_TOKENS=16000
LLM_TEMPERATURE=0.3

# ------------------------------------------------------------------
# SYSTEM SETTINGS
# ------------------------------------------------------------------
LOG_LEVEL=INFO
```

> **Note**: You must restart the backend server after making changes to the `.env` file.

---

## ⚡ Quick Start

### 1. Backend Setup

Navigate to the backend directory and install dependencies:

```bash
cd backend
pip install -r requirements.txt
```

Start the FastAPI server:

```bash
python -m app.main
```
*The server will start at http://localhost:5000*

### 2. Frontend Setup

Navigate to the frontend directory and install dependencies:

```bash
cd frontend
npm install
```

Start the development server:

```bash
npm run dev
```
*The application will open at http://localhost:5173*

---

## 📖 Usage Guide

The application follows a simple 3-step workflow:

### Step 1: Upload & Request (ChatPage)
1.  **Enter Request**: Type what you want to build (e.g., "Create a user profile page").
2.  **Upload Components**: Click "Select Folder" and upload your existing Angular components directory.
    *   *The backend analyzes your components to understand your design system.*
3.  **Send**: Click the arrow button.

### Step 2: Component Selection (ElementsPage)
1.  **Review AI Selection**: The AI will automatically select relevant components for your page and provide reasoning.
2.  **Customize**: textual reasoning can be edited, and you can manually check/uncheck components.
3.  **Continue**: Proceed to generation.

### Step 3: Generation & Download (DownloadPage)
1.  **Preview**: View the generated HTML, SCSS, and TypeScript code in real-time.
2.  **Save/Edit**: Make manual adjustments if needed.
3.  **Download**: Click "Download All Files" to get a ZIP of your new Angular component.

---

## 🏗️ Architecture & Configuration

### Tech Stack
- **Backend**: Python, FastAPI, Boto3 (AWS Bedrock), Groq SDK.
- **Frontend**: React, Vite.
- **AI/ML**: AWS Bedrock (Claude 3), Groq.

### Key Endpoints
- `POST /api/upload-and-analyze`: Uploads components & generates metadata.
- `POST /api/select-components`: AI selects components based on request.
- `POST /api/generate-page`: Generates final code.

### Configuration
- **Backend Port**: Defaults to `5000`. To change, edit `backend/app/main.py`.
- **Frontend API URL**: Configured to `http://localhost:5000`. Update fetch calls in `frontend/src/pages/` if changed.
