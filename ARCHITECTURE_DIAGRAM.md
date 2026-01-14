# System Architecture Diagram

## High-Level Architecture

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                              FRONTEND (React + Vite)                          │
│                            http://localhost:5173                              │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                                │
│  ┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐      │
│  │   ChatPage      │ ───▶ │ ElementsPage    │ ───▶ │ DownloadPage    │      │
│  │                 │      │                 │      │                 │      │
│  │ • Upload Folder │      │ • View Components│     │ • View Code     │      │
│  │ • Enter Request │      │ • Select/Deselect│     │ • Preview       │      │
│  │                 │      │ • Edit Reasoning │     │ • Download      │      │
│  └────────┬────────┘      └────────┬────────┘      └────────┬────────┘      │
│           │                        │                         │                │
│           │                        │                         │                │
└───────────┼────────────────────────┼─────────────────────────┼────────────────┘
            │                        │                         │
            │ API Calls              │ API Calls               │ API Call
            │ (HTTP/JSON)            │ (HTTP/JSON)             │ (HTTP/JSON)
            │                        │                         │
            ▼                        ▼                         ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                             BACKEND (FastAPI)                                 │
│                            http://localhost:5000                              │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                                │
│  ┌─────────────────────────────────────────────────────────────────────────┐ │
│  │                           API Endpoints                                  │ │
│  ├─────────────────────────────────────────────────────────────────────────┤ │
│  │                                                                           │ │
│  │  POST /api/upload-and-analyze                                            │ │
│  │  ├─ Input: { folderPath, pageRequest }                                   │ │
│  │  └─ Output: { status, components[], message }                            │ │
│  │                                                                           │ │
│  │  POST /api/select-components                                             │ │
│  │  ├─ Input: { pageRequest }                                               │ │
│  │  ├─ Uses: LLM (OpenAI) for intelligent selection                         │ │
│  │  └─ Output: { status, components[] with required flags }                 │ │
│  │                                                                           │ │
│  │  POST /api/update-component                                              │ │
│  │  ├─ Input: { componentId, required, reasoning }                          │ │
│  │  └─ Output: { status, message }                                          │ │
│  │                                                                           │ │
│  │  POST /api/generate-page                                                 │ │
│  │  ├─ Input: { pageRequest, selectedComponentIds[] }                       │ │
│  │  ├─ Uses: LLM (OpenAI) for code generation                               │ │
│  │  └─ Output: { status, html_code, scss_code, ts_code, ... }               │ │
│  │                                                                           │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
│                                     │                                          │
│                                     ▼                                          │
│  ┌─────────────────────────────────────────────────────────────────────────┐ │
│  │                      Data Persistence Layer                              │ │
│  ├─────────────────────────────────────────────────────────────────────────┤ │
│  │                                                                           │ │
│  │  component_metadata.json (File-based storage)                            │ │
│  │  ├─ Stores all component metadata                                        │ │
│  │  ├─ Tracks required flags for each component                             │ │
│  │  ├─ Saves user-provided reasoning                                        │ │
│  │  └─ Single source of truth for entire system                             │ │
│  │                                                                           │ │
│  │  current_page_request.txt                                                │ │
│  │  └─ Stores current user's page request                                   │ │
│  │                                                                           │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
│                                     │                                          │
│                                     ▼                                          │
│  ┌─────────────────────────────────────────────────────────────────────────┐ │
│  │                       Business Logic Modules                             │ │
│  ├─────────────────────────────────────────────────────────────────────────┤ │
│  │                                                                           │ │
│  │  component_metadata_pipeline.py                                          │ │
│  │  ├─ Analyzes Angular component files                                     │ │
│  │  ├─ Extracts HTML, SCSS, TypeScript content                              │ │
│  │  ├─ Identifies inputs, outputs, methods                                  │ │
│  │  └─ Generates comprehensive metadata                                     │ │
│  │                                                                           │ │
│  │  component_selector.py                                                   │ │
│  │  ├─ Uses LLM to analyze page request                                     │ │
│  │  ├─ Matches request with available components                            │ │
│  │  ├─ Generates reasoning for selections                                   │ │
│  │  └─ Returns selected components with reasoning                           │ │
│  │                                                                           │ │
│  │  page_generation_pipeline.py                                             │ │
│  │  ├─ Takes selected component metadata                                    │ │
│  │  ├─ Uses LLM to generate cohesive page code                              │ │
│  │  ├─ Generates HTML, SCSS, TypeScript                                     │ │
│  │  └─ Ensures proper component integration                                 │ │
│  │                                                                           │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
│                                                                                │
└──────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                          EXTERNAL SERVICES                                    │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                                │
│  OpenAI API (LLM)                                                             │
│  ├─ Component selection reasoning                                             │
│  ├─ Page code generation                                                      │
│  └─ Intelligent analysis and synthesis                                        │
│                                                                                │
└──────────────────────────────────────────────────────────────────────────────┘
```

## Data Flow Diagram

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                            DATA FLOW SEQUENCE                                 │
└──────────────────────────────────────────────────────────────────────────────┘

Step 1: UPLOAD & ANALYZE
═══════════════════════════════════════════════════════════════════════════════

User Input:
  • Folder Path: C:/projects/angular-app/components
  • Page Request: "Create a user dashboard with data tables"

  ┌─────────────┐
  │  ChatPage   │
  └──────┬──────┘
         │
         │ POST /api/upload-and-analyze
         │ { folderPath, pageRequest }
         │
         ▼
  ┌─────────────────────────────────┐
  │  component_metadata_pipeline.py │
  │  • Scans folder for .ts files   │
  │  • Extracts HTML, SCSS, TS      │
  │  • Analyzes component structure │
  └──────────┬──────────────────────┘
             │
             │ Saves
             │
             ▼
  ┌──────────────────────────┐
  │ component_metadata.json  │
  │ [                        │
  │   {                      │
  │     id_name: "button",   │
  │     name: "Button",      │
  │     description: "...",  │
  │     html_content: "...", │
  │     scss_content: "...", │
  │     ts_content: "..."    │
  │   },                     │
  │   ...                    │
  │ ]                        │
  └──────────┬───────────────┘
             │
             │ Returns
             │
             ▼
  ┌─────────────┐
  │  ChatPage   │
  │  Navigates  │────▶ ElementsPage
  └─────────────┘


Step 2: SELECT COMPONENTS (AI-POWERED)
═══════════════════════════════════════════════════════════════════════════════

  ┌─────────────────┐
  │  ElementsPage   │
  │  (On Load)      │
  └────────┬────────┘
           │
           │ POST /api/select-components
           │ { pageRequest }
           │
           ▼
  ┌──────────────────────────┐
  │  Loads metadata from:    │
  │  component_metadata.json │
  └────────┬─────────────────┘
           │
           │ Sends to
           │
           ▼
  ┌───────────────────────────┐
  │  component_selector.py    │
  │  • Calls OpenAI LLM       │
  │  • Analyzes page request  │
  │  • Matches with components│
  │  • Generates reasoning    │
  └────────┬──────────────────┘
           │
           │ Returns
           │ { selected_components: [...],
           │   reasoning: {...} }
           │
           ▼
  ┌──────────────────────────┐
  │  Saves back to:          │
  │  component_metadata.json │
  │  [                       │
  │    {                     │
  │      id_name: "button",  │
  │      required: true,     │◀─── ADDED
  │      reasoning: "..."    │◀─── ADDED
  │    },                    │
  │    {                     │
  │      id_name: "navbar",  │
  │      required: false,    │◀─── ADDED
  │      reasoning: ""       │◀─── ADDED
  │    }                     │
  │  ]                       │
  └────────┬─────────────────┘
           │
           │ Returns
           │
           ▼
  ┌─────────────────┐
  │  ElementsPage   │
  │  • Shows all    │
  │  • Pre-checks   │
  │    required     │
  │  • Displays     │
  │    reasoning    │
  └─────────────────┘


Step 3: UPDATE COMPONENT (REAL-TIME)
═══════════════════════════════════════════════════════════════════════════════

User Action: Checks/Unchecks Component OR Edits Reasoning

  ┌─────────────────┐
  │  ElementsPage   │
  │  • User clicks  │
  │    checkbox     │
  │  OR             │
  │  • User edits   │
  │    reasoning    │
  │    and blurs    │
  └────────┬────────┘
           │
           │ POST /api/update-component
           │ { componentId, required, reasoning }
           │
           ▼
  ┌──────────────────────────┐
  │  Loads metadata from:    │
  │  component_metadata.json │
  │  • Finds component by ID │
  │  • Updates required flag │
  │  • Updates reasoning     │
  │  • Saves immediately     │
  └────────┬─────────────────┘
           │
           │ Saves
           │
           ▼
  ┌──────────────────────────┐
  │  component_metadata.json │
  │  [                       │
  │    {                     │
  │      id_name: "button",  │
  │      required: false,    │◀─── UPDATED
  │      reasoning: ""       │◀─── CLEARED
  │    }                     │
  │  ]                       │
  └────────┬─────────────────┘
           │
           │ Returns success
           │
           ▼
  ┌─────────────────┐
  │  ElementsPage   │
  │  • Updates UI   │
  │  • Shows success│
  └─────────────────┘


Step 4: GENERATE PAGE
═══════════════════════════════════════════════════════════════════════════════

  ┌─────────────────┐
  │  DownloadPage   │
  │  (On Load)      │
  └────────┬────────┘
           │
           │ POST /api/generate-page
           │ { pageRequest, selectedComponentIds: [] }
           │
           ▼
  ┌──────────────────────────┐
  │  Loads metadata from:    │
  │  component_metadata.json │
  │  • Filters required=true │
  └────────┬─────────────────┘
           │
           │ Sends required components
           │
           ▼
  ┌─────────────────────────────────┐
  │  page_generation_pipeline.py    │
  │  • Calls OpenAI LLM             │
  │  • Sends component metadata     │
  │  • Generates cohesive page      │
  │  • Creates HTML, SCSS, TS code  │
  └────────┬────────────────────────┘
           │
           │ Returns
           │ { html_code, scss_code, ts_code,
           │   component_name, selector, ... }
           │
           ▼
  ┌─────────────────┐
  │  DownloadPage   │
  │  • Shows HTML   │
  │  • Shows SCSS   │
  │  • Shows TS     │
  │  • Preview pane │
  └─────────────────┘
```

## Component Communication Pattern

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                      COMPONENT INTERACTION FLOW                               │
└──────────────────────────────────────────────────────────────────────────────┘

FRONTEND COMPONENTS:
═══════════════════════════════════════════════════════════════════════════════

  ┌──────────────────────────────────────────────────────────────────────────┐
  │  PageProgressContext (React Context)                                      │
  │  • Tracks page completion status                                          │
  │  • Stores shared application data                                         │
  │  • Provides navigation logic                                              │
  └──────────────────┬───────────────────────┬──────────────────┬────────────┘
                     │                       │                  │
          ┌──────────▼────────┐   ┌─────────▼────────┐  ┌──────▼──────────┐
          │    ChatPage       │   │  ElementsPage    │  │  DownloadPage   │
          │                   │   │                  │  │                 │
          │ State:            │   │ State:           │  │ State:          │
          │ • folder          │   │ • components[]   │  │ • htmlContent   │
          │ • devRequest      │   │ • selectedIds[]  │  │ • cssContent    │
          │                   │   │ • reasoning{}    │  │ • tsContent     │
          └───────────────────┘   └──────────────────┘  └─────────────────┘


BACKEND MODULES:
═══════════════════════════════════════════════════════════════════════════════

  ┌──────────────────────────────────────────────────────────────────────────┐
  │  api_server.py (FastAPI Application)                                      │
  │  • Defines all REST endpoints                                             │
  │  • Handles request/response validation                                    │
  │  • Manages file I/O for persistence                                       │
  └──────┬────────────────┬────────────────────┬──────────────────────────────┘
         │                │                    │
         │                │                    │
    ┌────▼────┐    ┌──────▼──────┐    ┌───────▼────────┐
    │Component│    │  Component  │    │  Page          │
    │Metadata │    │  Selector   │    │  Generation    │
    │Pipeline │    │             │    │  Pipeline      │
    │         │    │             │    │                │
    │ Analyzes│    │ Uses LLM to │    │ Uses LLM to    │
    │ Angular │    │ select      │    │ generate       │
    │ files   │    │ components  │    │ page code      │
    └─────────┘    └─────────────┘    └────────────────┘
```

## State Management Flow

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                           STATE MANAGEMENT                                    │
└──────────────────────────────────────────────────────────────────────────────┘

FRONTEND STATE (React Context):
═══════════════════════════════════════════════════════════════════════════════

  PageProgressContext
  ├─ completedPages: { chat: bool, elements: bool, download: bool }
  └─ appData: {
        folder: FileList,
        devRequest: string,
        folderPath: string,
        selectedComponents: string[],
        componentReasoning: { [id]: string },
        generatedFiles: { html, css, ts },
        componentInfo: { name, pathName, selector }
     }


BACKEND STATE (File-based):
═══════════════════════════════════════════════════════════════════════════════

  component_metadata.json (Array of components)
  ├─ For each component:
  │   ├─ id_name: string (unique ID)
  │   ├─ name: string
  │   ├─ description: string
  │   ├─ import_path: string
  │   ├─ selector: string
  │   ├─ html_content: string
  │   ├─ scss_content: string
  │   ├─ ts_content: string
  │   ├─ inputs: array
  │   ├─ outputs: array
  │   ├─ methods: array
  │   ├─ required: boolean ◀─── Set by AI or user
  │   └─ reasoning: string  ◀─── Editable by user
  
  current_page_request.txt (Single string)
  └─ User's page generation request


STATE SYNCHRONIZATION:
═══════════════════════════════════════════════════════════════════════════════

  Frontend State                Backend State
  ────────────────────────────────────────────────────────────
  
  User checks component    ───▶  POST /api/update-component
                                  └─▶ Updates component_metadata.json
                                       └─▶ required: true
  
  User edits reasoning     ───▶  POST /api/update-component (on blur)
                                  └─▶ Updates component_metadata.json
                                       └─▶ reasoning: "new text"
  
  Page loads               ───▶  GET via /api/select-components
                           ◀───  Returns all components with flags
                                  └─▶ Reads from component_metadata.json
```

## Technology Stack

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                           TECHNOLOGY STACK                                    │
└──────────────────────────────────────────────────────────────────────────────┘

FRONTEND:
═══════════════════════════════════════════════════════════════════════════════
  • React 18.x            - UI framework
  • Vite                  - Build tool and dev server
  • React Router DOM      - Client-side routing
  • React Context API     - State management
  • CSS3                  - Styling
  • Fetch API             - HTTP requests

BACKEND:
═══════════════════════════════════════════════════════════════════════════════
  • Python 3.8+           - Programming language
  • FastAPI               - Web framework
  • Pydantic              - Data validation
  • Uvicorn               - ASGI server
  • asyncio               - Async/await support

EXTERNAL SERVICES:
═══════════════════════════════════════════════════════════════════════════════
  • OpenAI API            - Large Language Model
    ├─ Component selection reasoning
    └─ Page code generation

DATA PERSISTENCE:
═══════════════════════════════════════════════════════════════════════════════
  • JSON files            - File-based storage
    ├─ component_metadata.json
    └─ current_page_request.txt

DEVELOPMENT TOOLS:
═══════════════════════════════════════════════════════════════════════════════
  • VS Code              - Code editor
  • Browser DevTools     - Frontend debugging
  • Swagger UI           - API documentation
  • Git                  - Version control
```

## Deployment Architecture (Production)

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                      PRODUCTION ARCHITECTURE                                  │
└──────────────────────────────────────────────────────────────────────────────┘

                                  ┌──────────────┐
                                  │   Internet   │
                                  └──────┬───────┘
                                         │
                                         │ HTTPS
                                         │
                                  ┌──────▼───────┐
                                  │  Load        │
                                  │  Balancer    │
                                  │  (nginx)     │
                                  └──────┬───────┘
                                         │
                        ┌────────────────┼────────────────┐
                        │                │                │
                  ┌─────▼──────┐  ┌──────▼─────┐  ┌──────▼─────┐
                  │  Frontend  │  │  Frontend  │  │  Frontend  │
                  │  (Static)  │  │  (Static)  │  │  (Static)  │
                  │  React App │  │  React App │  │  React App │
                  └────────────┘  └────────────┘  └────────────┘
                                         │
                                         │ API Calls
                                         │
                                  ┌──────▼───────┐
                                  │   Reverse    │
                                  │   Proxy      │
                                  │   (nginx)    │
                                  └──────┬───────┘
                                         │
                        ┌────────────────┼────────────────┐
                        │                │                │
                  ┌─────▼──────┐  ┌──────▼─────┐  ┌──────▼─────┐
                  │  Backend   │  │  Backend   │  │  Backend   │
                  │  (FastAPI) │  │  (FastAPI) │  │  (FastAPI) │
                  │  Process 1 │  │  Process 2 │  │  Process 3 │
                  └─────┬──────┘  └──────┬─────┘  └──────┬─────┘
                        │                │                │
                        └────────────────┼────────────────┘
                                         │
                                  ┌──────▼───────┐
                                  │   Shared     │
                                  │   Storage    │
                                  │   (Redis/DB) │
                                  └──────────────┘
                                         │
                                  ┌──────▼───────┐
                                  │   External   │
                                  │   Services   │
                                  │   (OpenAI)   │
                                  └──────────────┘
```

---

**Created:** January 14, 2026  
**Version:** 1.0  
**Status:** Complete and Ready for Testing
