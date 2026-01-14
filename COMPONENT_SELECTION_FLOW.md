# Component Selection and Page Generation Flow - Complete Guide

## Overview

This document explains exactly how component selection and page generation works, addressing all key questions about the data flow.

## Complete Data Flow

### Step 1: Upload Components (ChatPage)
```
User uploads folder → Backend analyzes → component_metadata.json created
```

**component_metadata.json (initial state):**
```json
[
  {
    "id_name": "button-component",
    "name": "ButtonComponent",
    "description": "...",
    "html_content": "...",
    "scss_content": "...",
    "ts_content": "..."
    // NO required or reasoning fields yet
  }
]
```

---

### Step 2: AI Selection (ElementsPage - On Load)

**API Call:**
```javascript
POST /api/select-components
Body: { pageRequest: "Create a dashboard..." }
```

**Backend Process:**
1. Loads component_metadata.json
2. Sends to LLM with page request
3. LLM returns selected component IDs + reasoning
4. Backend **updates component_metadata.json** with required flags

**component_metadata.json (after AI selection):**
```json
[
  {
    "id_name": "button-component",
    "name": "ButtonComponent",
    "required": true,          ← ADDED by AI
    "reasoning": "Needed for user interactions",  ← ADDED by AI
    ...
  },
  {
    "id_name": "navbar-component",
    "name": "NavbarComponent",
    "required": false,         ← ADDED by AI (not selected)
    "reasoning": "",           ← ADDED (empty)
    ...
  }
]
```

**Frontend Updates:**
- Displays all components with checkboxes
- Pre-checks components where `required: true`
- Shows reasoning in right panel for required components

---

### Step 3: User Modifications (ElementsPage - User Actions)

#### Action 3a: User Checks a Component

**What Happens:**
```javascript
// User clicks checkbox for "navbar-component"
toggleComponent("navbar-component") is called

// Immediate UI update (optimistic)
selectedComponents: [..., "navbar-component"]

// API call
POST /api/update-component
Body: {
  componentId: "navbar-component",
  required: true,
  reasoning: "" // Current reasoning (empty for new selection)
}

// Backend updates component_metadata.json
{
  "id_name": "navbar-component",
  "required": true,    ← Updated from false to true
  "reasoning": ""
}
```

**Answer to Question 1:** ✅ **YES, when user unselects, `required: false` is set**

#### Action 3b: User Unchecks a Component

```javascript
// User unchecks "button-component"
toggleComponent("button-component") is called

// API call
POST /api/update-component
Body: {
  componentId: "button-component",
  required: false,      ← Sets to false
  reasoning: null       ← Clears reasoning
}

// Backend updates component_metadata.json
{
  "id_name": "button-component",
  "required": false,   ← Updated to false
  "reasoning": ""      ← Cleared
}
```

**Answer to Question 1 Confirmed:** ✅ **YES, unselecting sets required to false and clears reasoning**

#### Action 3c: User Edits Reasoning

```javascript
// User types in reasoning textarea and clicks outside (blur)
handleReasoningBlur("button-component") is called

// API call
POST /api/update-component
Body: {
  componentId: "button-component",
  required: true,
  reasoning: "Updated reasoning text from user"
}

// Backend updates component_metadata.json
{
  "id_name": "button-component",
  "required": true,
  "reasoning": "Updated reasoning text from user"  ← Updated
}
```

---

### Step 4: Navigate to Generation (ElementsPage - Continue Button)

**What Happens When User Clicks "Continue":**

```javascript
const handleContinue = () => {
  // 1. Save selected component IDs to appData
  updateAppData({ 
    selectedComponents: selectedComponents  // e.g., ["button-component", "input-component"]
  })
  
  // 2. Mark elements page as complete
  markPageComplete('elements')
  
  // 3. Navigate to DownloadPage
  navigate('/download')
}
```

**Answer to Question 2:** ✅ **Selected component IDs are saved to appData when "Continue" is clicked**

**Selected IDs:** The IDs in `selectedComponents` state are exactly the ones that have been checked by the user (which also means they have `required: true` in backend)

---

### Step 5: Generate Page (DownloadPage - On Load)

**What Happens When DownloadPage Loads:**

```javascript
useEffect(() => {
  const generateFiles = async () => {
    // 1. Get selected component IDs from appData
    const selectedIds = appData.selectedComponents || []
    // e.g., ["button-component", "input-component"]
    
    // 2. Call generate-page API
    const response = await fetch('http://localhost:5000/api/generate-page', {
      method: 'POST',
      body: JSON.stringify({
        pageRequest: appData.devRequest,
        selectedComponentIds: selectedIds  ← Sent to backend
      })
    })
    
    // 3. Receive generated code
    const data = await response.json()
    // {
    //   html_code: "<div>...</div>",
    //   scss_code: ".container { ... }",
    //   ts_code: "import { Component } from ..."
    // }
    
    // 4. Display in tabs
    setHtmlContent(data.html_code)
    setCssContent(data.scss_code)
    setTsContent(data.ts_code)
    
    // 5. Generate preview
    const preview = generatePreviewContent(data.html_code, data.scss_code, data.ts_code)
    setPreviewContent(preview)
  }
  
  generateFiles()
}, [])
```

**Answer to Question 2:** ✅ **YES, selected component IDs are sent directly to the API from appData**

**Backend Process:**

```python
@app.post('/api/generate-page')
async def generate_page(request_data: GeneratePageRequest):
    selected_ids = request_data.selectedComponentIds or []
    component_metadata = load_metadata()
    
    if selected_ids:
        # Use explicitly provided IDs from frontend
        metadata_to_use = [
            comp for comp in component_metadata
            if comp.get('id_name') in selected_ids
        ]
    else:
        # Fallback: Use components marked as required in metadata
        metadata_to_use = [
            comp for comp in component_metadata
            if comp.get('required', False)
        ]
    
    # Generate page with selected components
    pipeline = PageGenerationPipeline(component_metadata=metadata_to_use)
    page_data = await pipeline.generate_page(page_request)
    
    return {
        "html_code": page_data['html_code'],
        "scss_code": page_data['scss_code'],
        "ts_code": page_data['ts_code']
    }
```

**Answer to Question 2 Clarification:** ✅ **The frontend sends the selected IDs that were saved when "Continue" was clicked. These IDs correspond to components with `required: true` in the backend.**

---

### Step 6: Display Generated Code (DownloadPage)

**Answer to Question 3:** ✅ **YES, frontend reads html_code, scss_code, and ts_code from JSON response**

**Layout (Grid Display):**

```
┌──────────────────────────────────────────────────────────┐
│                    DownloadPage                          │
├─────────────────────────┬────────────────────────────────┤
│                         │                                │
│  PREVIEW SECTION        │   CODE EDITOR SECTION          │
│  (Left 50%)             │   (Right 50%)                  │
│                         │                                │
│  ┌───────────────────┐  │   ┌─ Tabs ──────────────────┐ │
│  │  Component Preview│  │   │ [HTML] [CSS] [TypeScript]│ │
│  │                   │  │   └──────────────────────────┘ │
│  │  <iframe>         │  │                                │
│  │   Shows rendered  │  │   ┌──────────────────────────┐ │
│  │   HTML with CSS   │  │   │                          │ │
│  │  </iframe>        │  │   │  <textarea>              │ │
│  │                   │  │   │    Editable code         │ │
│  │                   │  │   │  </textarea>             │ │
│  │                   │  │   │                          │ │
│  └───────────────────┘  │   └──────────────────────────┘ │
│                         │                                │
└─────────────────────────┴────────────────────────────────┘
```

**Answer to Question 4:** ✅ **YES, HTML preview is shown on the LEFT side automatically**

**Preview Process:**

```javascript
// 1. When files are generated, preview is created automatically
const generatePreviewContent = (html, css, ts) => {
  return `
    <!DOCTYPE html>
    <html>
      <head>
        <style>${css}</style>
      </head>
      <body>
        ${html}
        <script>${ts}</script>
      </body>
    </html>
  `
}

// 2. Preview is set immediately after receiving data
const preview = generatePreviewContent(data.html_code, data.scss_code, data.ts_code)
setPreviewContent(preview)

// 3. Preview is rendered in iframe
<iframe
  srcDoc={previewContent}
  className="preview-iframe"
/>
```

**Preview Updates:**
- ✅ **Automatic on load:** Preview generated when page data is received
- ✅ **Manual update:** User can click "Save" button to refresh preview after editing code
- ✅ **Live rendering:** iframe shows HTML with CSS styling applied

---

## Summary of Answers

### Question 1: Does unselecting set required to false?
**Answer:** ✅ **YES**
- When user unchecks a component, `toggleComponent` calls API with `required: false`
- Backend updates `component_metadata.json` with `required: false`
- Reasoning is also cleared (`reasoning: ""`)

### Question 2: How are selected component IDs sent?
**Answer:** ✅ **Sent from appData when "Continue" is clicked**
1. ElementsPage saves `selectedComponents` to appData on Continue
2. DownloadPage reads `appData.selectedComponents`
3. DownloadPage sends these IDs to `/api/generate-page`
4. Backend filters components by these IDs
5. Only selected components are used for generation

**Alternative (Fallback):** If `selectedComponentIds` is empty, backend uses all components with `required: true`

### Question 3: How is generated code displayed?
**Answer:** ✅ **Read from JSON response and displayed in tabs**
- API returns: `{ html_code, scss_code, ts_code }`
- Frontend stores in state: `setHtmlContent(data.html_code)`, etc.
- Displayed in 3 tabs: HTML, CSS, TypeScript
- User can switch tabs to view different code files
- Code is editable in textareas

### Question 4: Where is HTML preview shown?
**Answer:** ✅ **LEFT side of DownloadPage, automatically rendered**
- Preview section is on the left (50% width)
- Code editor is on the right (50% width)
- Preview is generated automatically when page loads
- Rendered in `<iframe>` with HTML + CSS combined
- Updates when user clicks "Save" button

---

## Complete Component State at Each Step

### After Upload (ChatPage)
```json
component_metadata.json:
[
  { "id_name": "button-component", "name": "ButtonComponent", ... }
  // NO required or reasoning fields
]
```

### After AI Selection (ElementsPage Load)
```json
component_metadata.json:
[
  { "id_name": "button-component", "required": true, "reasoning": "..." },
  { "id_name": "navbar-component", "required": false, "reasoning": "" }
]

appData.selectedComponents: ["button-component"]
```

### After User Modifications (ElementsPage)
```json
component_metadata.json:
[
  { "id_name": "button-component", "required": false, "reasoning": "" },
  { "id_name": "navbar-component", "required": true, "reasoning": "User added" }
]

appData.selectedComponents: ["navbar-component", "input-component"]
```

### After Continue (Navigate to DownloadPage)
```javascript
appData.selectedComponents: ["navbar-component", "input-component"]
// These are the IDs that will be sent to generate-page API
```

### After Generation (DownloadPage)
```javascript
// API sends
selectedComponentIds: ["navbar-component", "input-component"]

// API returns
{
  html_code: "<div class='dashboard'>...</div>",
  scss_code: ".dashboard { ... }",
  ts_code: "import { Component } from '@angular/core'..."
}

// Frontend displays
- Left: HTML preview in iframe
- Right: Code in tabs (HTML/CSS/TS)
```

---

## Key Takeaways

1. ✅ **Real-time sync:** Every checkbox change and reasoning edit is saved to backend immediately
2. ✅ **required flag:** Always reflects current selection state (true/false)
3. ✅ **Selected IDs:** Passed from ElementsPage → appData → DownloadPage → API
4. ✅ **Code display:** JSON response parsed and shown in 3 tabs
5. ✅ **Preview:** HTML rendered on left side, automatically generated on load

**The flow is optimal and working as intended!** 🚀
