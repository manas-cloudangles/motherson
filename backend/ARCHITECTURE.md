# Architecture Diagram

## New Modular Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     MODULAR BACKEND PIPELINES                   │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                   1. Component Metadata Pipeline                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Input: Angular Components Directory                            │
│    │                                                             │
│    ├─► Discover Components                                      │
│    │                                                             │
│    ├─► Read Component Files (.ts, .html, .scss)                 │
│    │                                                             │
│    ├─► Analyze with LLM                                         │
│    │                                                             │
│    └─► Generate Metadata                                        │
│                                                                  │
│  Output: List[ComponentMetadata]                                │
│    {                                                             │
│      "name": "AppButtonComponent",                              │
│      "description": "...",                                       │
│      "import_path": "...",                                       │
│      "id_name": "app-button",                                    │
│      "html_code": "...",                                         │
│      "scss_code": "...",                                         │
│      "ts_code": "..."                                            │
│    }                                                             │
│                                                                  │
│  Optional: Save to component_metadata.json                      │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘

                              │
                              │ metadata
                              ▼

┌─────────────────────────────────────────────────────────────────┐
│                    2. Page Generation Pipeline                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Input 1: Component Metadata (from above)                       │
│  Input 2: Page Description (user request)                       │
│    │                                                             │
│    ├─► Create System Prompt with Components                     │
│    │                                                             │
│    ├─► Generate with LLM                                        │
│    │     - HTML Template                                        │
│    │     - SCSS Styles                                          │
│    │     - TypeScript Component                                 │
│    │                                                             │
│    └─► Return Generated Code                                    │
│                                                                  │
│  Output: PageData                                               │
│    {                                                             │
│      "component_name": "DashboardComponent",                    │
│      "path_name": "dashboard",                                   │
│      "selector": "app-dashboard",                                │
│      "html_code": "<div>...</div>",                             │
│      "scss_code": ".container {...}",                           │
│      "ts_code": "import { Component }..."                       │
│    }                                                             │
│                                                                  │
│  ✅ Returns code (no file saving by default)                    │
│  ✅ No module.ts modifications                                  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘

                              │
                              │ page data
                              ▼

┌─────────────────────────────────────────────────────────────────┐
│                      Usage Patterns                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Pattern 1: API Endpoint                                        │
│  ┌────────────────────────────────────────┐                    │
│  │  @app.post("/generate")                │                    │
│  │  async def generate(desc):             │                    │
│  │      page = await generate_page(desc)  │                    │
│  │      return page  # JSON response      │                    │
│  └────────────────────────────────────────┘                    │
│                                                                  │
│  Pattern 2: Frontend Integration                                │
│  ┌────────────────────────────────────────┐                    │
│  │  // Frontend                           │                    │
│  │  const response = await fetch('/gen')  │                    │
│  │  const page = await response.json()    │                    │
│  │  // Display HTML, SCSS, TS in UI       │                    │
│  └────────────────────────────────────────┘                    │
│                                                                  │
│  Pattern 3: File Saving (Optional)                              │
│  ┌────────────────────────────────────────┐                    │
│  │  page = await generate_page(desc)      │                    │
│  │  save_page_files(page, "output/")      │                    │
│  └────────────────────────────────────────┘                    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Workflow Diagram

```
┌──────────────┐
│   User App   │
└──────┬───────┘
       │
       │ Step 1: Generate Metadata (once)
       ▼
┌─────────────────────────────────────────┐
│ generate_component_metadata()           │
│                                         │
│ Components Dir ──► LLM ──► Metadata    │
└─────────────┬───────────────────────────┘
              │
              │ metadata.json (cached)
              ▼
┌─────────────────────────────────────────┐
│  Step 2: Generate Pages (many times)    │
│                                         │
│  generate_page()                        │
│                                         │
│  Page Desc + Metadata ──► LLM ──► Code │
└─────────────┬───────────────────────────┘
              │
              │ Returns: {html, scss, ts}
              ▼
┌─────────────────────────────────────────┐
│  Step 3: Use the Code                   │
│                                         │
│  • Display in UI                        │
│  • Send to frontend                     │
│  • Save to files                        │
│  • Edit before saving                   │
│  • Version control                      │
└─────────────────────────────────────────┘
```

## File Structure

```
backend/
│
├── 📁 Core Pipelines (NEW)
│   ├── component_metadata_pipeline.py    ⭐ Metadata generation
│   ├── page_generation_pipeline.py       ⭐ Page generation
│   └── modular_pipeline.py               ⭐ Unified interface
│
├── 📁 Configuration & Utilities
│   ├── config.py                         Configuration
│   └── utils.py                          Helper functions
│
├── 📁 Documentation (NEW)
│   ├── README_MODULAR_PIPELINES.md       📖 Main documentation
│   ├── IMPLEMENTATION_SUMMARY.md         📖 What was done
│   ├── MIGRATION_GUIDE.md                📖 Migration guide
│   └── ARCHITECTURE.md                   📖 This file
│
├── 📁 Examples (NEW)
│   ├── quick_start.py                    🚀 Quick demonstration
│   ├── example_metadata_generation.py    Example: Metadata
│   ├── example_page_generation.py        Example: Pages
│   └── example_complete_workflow.py      Example: Full workflow
│
├── 📁 Legacy Code (for reference)
│   ├── component_metadata_generator.py   ⚠️ Old version
│   ├── page_generator.py                 ⚠️ Old version
│   └── pipeline.py                       ⚠️ Old version
│
└── 📁 Notebooks (unchanged)
    ├── component_metadata_generator.ipynb
    └── page_generator_agent.ipynb
```

## Data Flow

```
Components Directory
        │
        ├─► [Component 1]
        │       ├── component.ts
        │       ├── component.html
        │       └── component.scss
        │
        ├─► [Component 2]
        │       └── ...
        │
        └─► [Component N]
                └── ...
                
        ▼ (analyze with LLM)
        
Component Metadata JSON
[
  {
    "name": "AppButtonComponent",
    "description": "A reusable button...",
    "import_path": "app/common/components/app-button/app-button.component",
    "id_name": "app-button",
    "html_code": "<button>...</button>",
    "scss_code": ".button {...}",
    "ts_code": "export class AppButtonComponent..."
  },
  ...
]

        ▼ (use as context)
        
Page Generation Request
{
  "description": "Create a dashboard page with stats"
}

        ▼ (generate with LLM)
        
Generated Page
{
  "component_name": "DashboardComponent",
  "path_name": "dashboard",
  "selector": "app-dashboard",
  "html_code": "<div class='dashboard'>...</div>",
  "scss_code": ".dashboard { display: grid; ... }",
  "ts_code": "import { Component } from '@angular/core'..."
}

        ▼ (return to caller)
        
Application Uses Code:
• API response
• Frontend display
• File saving
• Version control
• etc.
```

## API Interface

```
ModularPipeline
├── generate_component_metadata()
│   ├─ Input: components_dir, save_to_file
│   └─ Output: List[ComponentMetadata]
│
├── generate_page()
│   ├─ Input: page_description, component_metadata
│   └─ Output: PageData {html, scss, ts}
│
├── generate_multiple_pages()
│   ├─ Input: List[page_descriptions], component_metadata
│   └─ Output: List[PageData]
│
└── run_complete_pipeline()
    ├─ Input: page_descriptions, regenerate_metadata
    └─ Output: {metadata, pages, counts}
```

## Comparison: Old vs New

```
OLD ARCHITECTURE                 NEW ARCHITECTURE
─────────────────               ─────────────────

Generate Metadata               Generate Metadata
     │                               │
     ├─► Save to file                ├─► Return data
     │                               │   (optional save)
     ▼                               ▼
     
Generate Page                   Generate Page
     │                               │
     ├─► Save files                  ├─► Return code
     │   (forced)                    │   (you decide)
     │                               │
     ├─► Update module.ts            └─► Done!
     │   (forced)                        (no side effects)
     │
     └─► Done!
         (files changed)
```

## Integration Patterns

### Pattern 1: Standalone Script
```python
# Generate once, use many times
metadata = await generate_component_metadata(save_to_file=True)

# Generate pages as needed
page1 = await generate_page("Dashboard", metadata)
page2 = await generate_page("Settings", metadata)
```

### Pattern 2: API Service
```python
# Load metadata at startup
metadata = load_metadata("component_metadata.json")

# API endpoint
@app.post("/generate")
async def generate(request):
    page = await generate_page(request.description, metadata)
    return page  # Returns JSON
```

### Pattern 3: Batch Processing
```python
# Process multiple requests
descriptions = ["Dashboard", "Settings", "Profile", "Admin"]
pages = await generate_multiple_pages(descriptions, metadata)

# Export all
export_to_json(pages, "generated_pages.json")
```

### Pattern 4: Interactive Tool
```python
# User interface
while True:
    desc = input("Describe page: ")
    page = await generate_page(desc, metadata)
    
    # Show preview
    print(page['html_code'][:200])
    
    # Ask to save
    if input("Save? (y/n) ") == 'y':
        save_page_files(page, "output/")
```

## Key Takeaways

✅ **Two Independent Pipelines**
   - Component metadata generation
   - Page generation

✅ **Returns Data**
   - No forced file saving
   - No module.ts modifications
   - You control what happens

✅ **Clean API**
   - Simple functions
   - Clear inputs/outputs
   - Easy to use

✅ **Flexible**
   - Use together or separately
   - Cache metadata
   - Optional file saving

✅ **Production Ready**
   - Error handling
   - Type hints
   - Documentation
   - Examples

---

This architecture provides maximum flexibility while maintaining clean, modular code! 🚀
