# Visual Flow Diagram - Component Selection to Page Generation

## Complete Data Flow with State Changes

```
┌────────────────────────────────────────────────────────────────────────────┐
│                    STEP 1: UPLOAD COMPONENTS                               │
└────────────────────────────────────────────────────────────────────────────┘

User Action: Uploads folder + enters request

   ChatPage                        Backend
      │                               │
      │ POST /upload-and-analyze      │
      │──────────────────────────────>│
      │ {folderPath, pageRequest}     │
      │                               │
      │                               │ Analyzes components
      │                               │ Creates metadata
      │                               │
      │                               │ ┌─────────────────────────┐
      │                               │─│ component_metadata.json │
      │                               │ │ [                       │
      │                               │ │   {id_name, name, ...}  │
      │                               │ │   // NO required field  │
      │                               │ │ ]                       │
      │                               │ └─────────────────────────┘
      │<──────────────────────────────│
      │ {status, components[]}        │
      │                               │
Navigate to ElementsPage


┌────────────────────────────────────────────────────────────────────────────┐
│              STEP 2: AI SELECTS COMPONENTS (AUTO)                          │
└────────────────────────────────────────────────────────────────────────────┘

Automatic on ElementsPage Load

   ElementsPage                     Backend
      │                               │
      │ POST /select-components       │
      │──────────────────────────────>│
      │ {pageRequest}                 │
      │                               │
      │                               │ Loads metadata
      │                               │ Calls LLM
      │                               │ LLM selects components
      │                               │
      │                               │ UPDATES metadata:
      │                               │ ┌─────────────────────────┐
      │                               │─│ component_metadata.json │
      │                               │ │ [                       │
      │                               │ │   {                     │
      │                               │ │     id_name: "button",  │
      │                               │ │     required: true,  ◄──│ ADDED
      │                               │ │     reasoning: "..." ◄──│ ADDED
      │                               │ │   },                    │
      │                               │ │   {                     │
      │                               │ │     id_name: "navbar",  │
      │                               │ │     required: false, ◄──│ ADDED
      │                               │ │     reasoning: ""    ◄──│ ADDED
      │                               │ │   }                     │
      │                               │ │ ]                       │
      │                               │ └─────────────────────────┘
      │<──────────────────────────────│
      │ {components[] with required}  │
      │                               │

Frontend State Update:
┌─────────────────────────────────┐
│ selectedComponents:             │
│   ["button"]                    │
│                                 │
│ Display:                        │
│ ✅ Button (pre-checked)         │
│ ❌ Navbar (not checked)         │
└─────────────────────────────────┘


┌────────────────────────────────────────────────────────────────────────────┐
│          STEP 3a: USER CHECKS A COMPONENT (REAL-TIME)                      │
└────────────────────────────────────────────────────────────────────────────┘

User Action: Checks "Navbar" checkbox

   ElementsPage                     Backend
      │                               │
      │ Optimistic UI Update          │
      │ selectedComponents +=         │
      │   ["button", "navbar"]        │
      │                               │
      │ POST /update-component        │
      │──────────────────────────────>│
      │ {                             │
      │   componentId: "navbar",      │
      │   required: true,             │
      │   reasoning: ""               │
      │ }                             │
      │                               │
      │                               │ UPDATES metadata:
      │                               │ ┌─────────────────────────┐
      │                               │─│ component_metadata.json │
      │                               │ │   {                     │
      │                               │ │     id_name: "navbar",  │
      │                               │ │     required: true,  ◄──│ UPDATED
      │                               │ │     reasoning: ""       │
      │                               │ │   }                     │
      │                               │ └─────────────────────────┘
      │<──────────────────────────────│
      │ {status: "success"}           │
      │                               │

Frontend State:
┌─────────────────────────────────┐
│ selectedComponents:             │
│   ["button", "navbar"]          │
│                                 │
│ Display:                        │
│ ✅ Button                       │
│ ✅ Navbar (now checked)         │
└─────────────────────────────────┘


┌────────────────────────────────────────────────────────────────────────────┐
│        STEP 3b: USER UNCHECKS A COMPONENT (REAL-TIME)                      │
└────────────────────────────────────────────────────────────────────────────┘

User Action: Unchecks "Button" checkbox

   ElementsPage                     Backend
      │                               │
      │ Optimistic UI Update          │
      │ selectedComponents =          │
      │   ["navbar"]                  │
      │                               │
      │ POST /update-component        │
      │──────────────────────────────>│
      │ {                             │
      │   componentId: "button",      │
      │   required: false,         ◄──│ Sets to FALSE
      │   reasoning: null          ◄──│ Clears reasoning
      │ }                             │
      │                               │
      │                               │ UPDATES metadata:
      │                               │ ┌─────────────────────────┐
      │                               │─│ component_metadata.json │
      │                               │ │   {                     │
      │                               │ │     id_name: "button",  │
      │                               │ │     required: false, ◄──│ UPDATED
      │                               │ │     reasoning: ""    ◄──│ CLEARED
      │                               │ │   }                     │
      │                               │ └─────────────────────────┘
      │<──────────────────────────────│
      │ {status: "success"}           │
      │                               │

Frontend State:
┌─────────────────────────────────┐
│ selectedComponents:             │
│   ["navbar"]                    │
│                                 │
│ Display:                        │
│ ❌ Button (now unchecked)       │
│ ✅ Navbar                       │
└─────────────────────────────────┘


┌────────────────────────────────────────────────────────────────────────────┐
│           STEP 3c: USER EDITS REASONING (ON BLUR)                          │
└────────────────────────────────────────────────────────────────────────────┘

User Action: Types reasoning and clicks outside textarea

   ElementsPage                     Backend
      │                               │
      │ onChange: Updates local state │
      │ (no API call yet)             │
      │                               │
      │ onBlur: Triggered             │
      │                               │
      │ POST /update-component        │
      │──────────────────────────────>│
      │ {                             │
      │   componentId: "navbar",      │
      │   required: true,             │
      │   reasoning: "User needs..."  │
      │ }                             │
      │                               │
      │                               │ UPDATES metadata:
      │                               │ ┌─────────────────────────┐
      │                               │─│ component_metadata.json │
      │                               │ │   {                     │
      │                               │ │     id_name: "navbar",  │
      │                               │ │     required: true,     │
      │                               │ │     reasoning: "User.."◄│ UPDATED
      │                               │ │   }                     │
      │                               │ └─────────────────────────┘
      │<──────────────────────────────│
      │ {status: "success"}           │
      │                               │


┌────────────────────────────────────────────────────────────────────────────┐
│              STEP 4: CLICK CONTINUE BUTTON                                 │
└────────────────────────────────────────────────────────────────────────────┘

User Action: Clicks "Continue" button

   ElementsPage
      │
      │ handleContinue() executed
      │
      │ Saves to appData:
      │ ┌──────────────────────────────┐
      │ │ appData.selectedComponents:  │
      │ │   ["navbar", "input"]        │ ◄─── SAVED for next page
      │ └──────────────────────────────┘
      │
      │ markPageComplete('elements')
      │
      │ navigate('/download')
      │
      ▼

Navigate to DownloadPage


┌────────────────────────────────────────────────────────────────────────────┐
│              STEP 5: GENERATE PAGE (AUTO)                                  │
└────────────────────────────────────────────────────────────────────────────┘

Automatic on DownloadPage Load

   DownloadPage                     Backend
      │                               │
      │ Read from appData:            │
      │ selectedIds = ["navbar",      │
      │                "input"]       │
      │                               │
      │ POST /generate-page           │
      │──────────────────────────────>│
      │ {                             │
      │   pageRequest: "...",         │
      │   selectedComponentIds:    ◄──│ Sent from appData
      │     ["navbar", "input"]       │
      │ }                             │
      │                               │
      │                               │ Loads metadata
      │                               │ Filters by IDs:
      │                               │   - navbar
      │                               │   - input
      │                               │
      │                               │ Calls PageGenerationPipeline
      │                               │ LLM generates code
      │                               │
      │<──────────────────────────────│
      │ {                             │
      │   html_code: "<div>...</div>",│
      │   scss_code: ".container{...}",│
      │   ts_code: "import {...}"    │
      │ }                             │
      │                               │


┌────────────────────────────────────────────────────────────────────────────┐
│              STEP 6: DISPLAY CODE AND PREVIEW                              │
└────────────────────────────────────────────────────────────────────────────┘

   DownloadPage
      │
      │ Receives API response
      │
      │ setHtmlContent(data.html_code)
      │ setCssContent(data.scss_code)
      │ setTsContent(data.ts_code)
      │
      │ Generate Preview:
      │ preview = generatePreviewContent(html, css, ts)
      │
      │ setPreviewContent(preview)
      │
      ▼

┌──────────────────────────────────────────────────────────────────────────┐
│                          DOWNLOAD PAGE                                   │
├────────────────────────────┬─────────────────────────────────────────────┤
│                            │                                             │
│  PREVIEW (Left 50%)        │   CODE EDITOR (Right 50%)                   │
│                            │                                             │
│  ┌──────────────────────┐  │   ┌─────────────────────────────────────┐  │
│  │ Component Preview    │  │   │ Tabs: [HTML] [CSS] [TypeScript]    │  │
│  │                      │  │   └─────────────────────────────────────┘  │
│  │ <iframe>             │  │                                             │
│  │  HTML + CSS          │  │   ┌─────────────────────────────────────┐  │
│  │  Rendered            │  │   │ <textarea>                          │  │
│  │  AUTOMATICALLY    ◄──│──│───│   {html_code}                       │  │
│  │ </iframe>            │  │   │   or {scss_code}                    │  │
│  │                      │  │   │   or {ts_code}                      │  │
│  └──────────────────────┘  │   │ </textarea>                         │  │
│                            │   └─────────────────────────────────────┘  │
│                            │                                             │
└────────────────────────────┴─────────────────────────────────────────────┘
```

## State Synchronization Summary

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      STATE AT EACH STEP                                 │
└─────────────────────────────────────────────────────────────────────────┘

STEP 1 - After Upload:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Backend (component_metadata.json):
  [{ id_name: "button", name: "Button", ... }]  // No required field

Frontend (appData):
  { devRequest: "...", folderPath: "..." }


STEP 2 - After AI Selection:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Backend (component_metadata.json):
  [
    { id_name: "button", required: true, reasoning: "AI reason" },
    { id_name: "navbar", required: false, reasoning: "" }
  ]

Frontend (appData):
  { selectedComponents: ["button"] }


STEP 3 - After User Modifications:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Backend (component_metadata.json):
  [
    { id_name: "button", required: false, reasoning: "" },  ← Unchecked
    { id_name: "navbar", required: true, reasoning: "User reason" } ← Checked
  ]

Frontend (appData):
  { selectedComponents: ["navbar", "input"] }


STEP 4 - After Continue:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Frontend (appData):
  { 
    selectedComponents: ["navbar", "input"],  ← SAVED
    componentReasoning: { "navbar": "...", "input": "..." }
  }

→ Navigate to DownloadPage with this data


STEP 5 - During Generation:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
API Request:
  {
    pageRequest: "Create dashboard",
    selectedComponentIds: ["navbar", "input"]  ← From appData
  }

Backend Process:
  1. Filters metadata by IDs: ["navbar", "input"]
  2. Sends to LLM for code generation
  3. Returns: { html_code, scss_code, ts_code }


STEP 6 - After Generation:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Frontend (DownloadPage):
  {
    htmlContent: "<div>...</div>",
    cssContent: ".container { ... }",
    tsContent: "import { ... }",
    previewContent: "<html>...</html>"  ← Auto-generated
  }

Display:
  - Left: Preview in <iframe>
  - Right: Code in tabs (HTML/CSS/TS)
```

## Key Points

### 1. Real-Time Updates ✅
Every checkbox change and reasoning edit → Immediate API call → Backend updated

### 2. Selected Component IDs ✅
- Saved to appData when "Continue" clicked
- Passed to /generate-page API
- Backend filters by these IDs

### 3. Required Flag Handling ✅
- Check component → required: true
- Uncheck component → required: false ← **IMPORTANT**
- Always synchronized with backend

### 4. Preview Display ✅
- Left side of DownloadPage
- Auto-generated when code received
- Shows HTML with CSS applied
- Updates on "Save" button click

### 5. Code Display ✅
- Right side of DownloadPage
- 3 tabs: HTML, CSS, TypeScript
- Reads from API response: html_code, scss_code, ts_code
- Editable in textareas

---

**Status:** ✅ All 4 questions answered and flow clarified!
