# Modular Backend Pipelines

This backend provides two independent, modular pipelines for Angular code generation:

1. **Component Metadata Generation Pipeline** - Analyzes existing Angular components and generates metadata
2. **Page Generation Pipeline** - Generates new Angular pages using LLM and component metadata

## Key Features

✅ **Modular Design** - Each pipeline works independently
✅ **Returns Code** - Generates and returns code without saving files (optional saving available)
✅ **No Module Modifications** - Page generation doesn't modify module.ts files
✅ **Flexible** - Can be used programmatically or via scripts
✅ **Clean API** - Simple, intuitive function interfaces

## Architecture

```
backend/
├── component_metadata_pipeline.py    # Component metadata generation
├── page_generation_pipeline.py       # Page generation  
├── modular_pipeline.py               # Unified interface for both pipelines
├── config.py                         # Configuration settings
├── utils.py                          # Utility functions
└── examples/                         # Example usage scripts
```

## Quick Start

### 1. Component Metadata Generation

Generate metadata for all Angular components in a directory:

```python
from backend.modular_pipeline import generate_component_metadata

# Generate metadata
metadata = await generate_component_metadata(
    components_dir="path/to/components",
    save_to_file=True  # Optional: save to component_metadata.json
)

# Use the metadata
for component in metadata:
    print(f"{component['name']}: {component['description']}")
```

### 2. Page Generation

Generate a new Angular page using component metadata:

```python
from backend.modular_pipeline import generate_page

# Generate a page
page = await generate_page(
    page_description="Create a user profile page with a form",
    component_metadata=metadata  # From step 1
)

# Access the generated code
html_code = page['html_code']
scss_code = page['scss_code']
ts_code = page['ts_code']

print(f"Component: {page['component_name']}")
print(f"Selector: {page['selector']}")
print(f"Path: {page['path_name']}")
```

### 3. Complete Pipeline

Run both steps in one go:

```python
from backend.modular_pipeline import run_complete_pipeline

# Generate metadata and pages
result = await run_complete_pipeline(
    page_descriptions=[
        "Create a dashboard page",
        "Create a settings page"
    ],
    regenerate_metadata=False,  # Use existing metadata if available
    save_metadata=True
)

# Access results
metadata = result['metadata']
pages = result['pages']

for page in pages:
    print(f"Generated: {page['component_name']}")
```

## Pipeline Details

### Component Metadata Pipeline

**Purpose**: Analyze existing Angular components and extract structured metadata

**Input**: Directory containing Angular components

**Output**: List of component metadata dictionaries

**Each metadata contains**:
- `name`: Component class name
- `description`: What the component does and how to use it
- `import_path`: Import path for the component
- `id_name`: Selector/tag name to use in HTML
- `html_code`: Component HTML template
- `scss_code`: Component styles
- `ts_code`: Component TypeScript code

**Example**:
```python
from backend.component_metadata_pipeline import ComponentMetadataPipeline

pipeline = ComponentMetadataPipeline(
    components_dir="path/to/components",
    save_to_file=True  # Optional
)

metadata = await pipeline.run()
```

### Page Generation Pipeline

**Purpose**: Generate new Angular pages using LLM and component metadata

**Input**: 
- Page description (user request)
- Component metadata (from step 1)

**Output**: Dictionary containing generated code

**Generated code includes**:
- `component_name`: PascalCase component name
- `path_name`: kebab-case path name
- `selector`: Angular selector
- `html_code`: Complete HTML template
- `scss_code`: Complete SCSS styles
- `ts_code`: Complete TypeScript component

**Example**:
```python
from backend.page_generation_pipeline import PageGenerationPipeline

pipeline = PageGenerationPipeline()
pipeline.load_component_metadata("component_metadata.json")

page = await pipeline.generate_page("Create a login page")
```

## API Reference

### `generate_component_metadata()`

Generate component metadata from a directory.

**Parameters**:
- `components_dir` (Path, optional): Directory containing components
- `save_to_file` (bool): Whether to save to JSON file
- `output_json` (Path, optional): JSON output path
- `output_readme` (Path, optional): README output path

**Returns**: `List[Dict[str, Any]]` - List of component metadata

---

### `generate_page()`

Generate a single Angular page.

**Parameters**:
- `page_description` (str): Description of the page to create
- `component_metadata_file` (Path, optional): Path to metadata JSON
- `component_metadata` (List[Dict], optional): Pre-loaded metadata

**Returns**: `Optional[Dict[str, Any]]` - Generated page data or None

---

### `generate_multiple_pages()`

Generate multiple Angular pages.

**Parameters**:
- `page_descriptions` (List[str]): List of page descriptions
- `component_metadata_file` (Path, optional): Path to metadata JSON
- `component_metadata` (List[Dict], optional): Pre-loaded metadata

**Returns**: `List[Dict[str, Any]]` - List of generated page data

---

### `run_complete_pipeline()`

Run both metadata generation and page generation.

**Parameters**:
- `page_descriptions` (List[str]): List of pages to generate
- `components_dir` (Path, optional): Components directory
- `regenerate_metadata` (bool): Whether to regenerate metadata
- `save_metadata` (bool): Whether to save metadata to file

**Returns**: `Dict[str, Any]` - Complete results with metadata and pages

## Configuration

Configure paths and settings in `config.py`:

```python
# Base directories
COMPONENTS_DIR = Path("path/to/components")
MASTER_DIR = Path("path/to/master")

# Output files
COMPONENT_METADATA_FILE = Path("component_metadata.json")
COMPONENT_README_FILE = Path("COMPONENT_METADATA_README.md")

# LLM settings
LLM_MAX_TOKENS = 35000
LLM_TEMPERATURE = 0.3
```

## Optional File Saving

While the pipelines return code by default, you can optionally save files:

```python
from pathlib import Path

# For component metadata
metadata = await generate_component_metadata(
    save_to_file=True,
    output_json=Path("my_metadata.json"),
    output_readme=Path("MY_README.md")
)

# For pages (manual saving)
from backend.page_generation_pipeline import PageGenerationPipeline

pipeline = PageGenerationPipeline()
page = await pipeline.generate_page("Create a dashboard")

# Save to specific location
pipeline.save_page_files(
    page_data=page,
    output_dir=Path("output/pages")
)
```

## Example Scripts

See the `examples/` directory for complete working examples:

- `example_metadata_generation.py` - Generate component metadata
- `example_page_generation.py` - Generate single/multiple pages
- `example_complete_workflow.py` - Run the complete pipeline
- `example_custom_integration.py` - Custom integration patterns

## Integration with Frontend

The generated code can be easily integrated with a frontend:

```python
# Backend API endpoint
@app.post("/api/generate-page")
async def generate_page_endpoint(request: PageRequest):
    page = await generate_page(
        page_description=request.description,
        component_metadata_file="component_metadata.json"
    )
    
    return {
        "success": True,
        "page": page
    }
```

The frontend can then display or use the generated code:

```javascript
// Frontend
const response = await fetch('/api/generate-page', {
    method: 'POST',
    body: JSON.stringify({ description: 'Create a dashboard' })
});

const { page } = await response.json();

// Display the code
console.log(page.html_code);
console.log(page.scss_code);
console.log(page.ts_code);
```

## Key Differences from Previous Version

| Feature | Old Version | New Modular Version |
|---------|-------------|---------------------|
| File Saving | Always saves files | Returns code, optional saving |
| Module Updates | Modifies module.ts | No module modifications |
| Pipeline Independence | Tightly coupled | Fully independent |
| API | Class-based only | Functions + Classes |
| Flexibility | Fixed workflow | Flexible workflows |
| Return Values | Side effects | Direct returns |

## Best Practices

1. **Generate metadata once**: Store and reuse component metadata
2. **Use async/await**: All pipeline functions are async
3. **Handle errors**: Check for None returns from generation functions
4. **Save when needed**: Only save files when absolutely necessary
5. **Batch operations**: Use `generate_multiple_pages()` for efficiency

## Troubleshooting

**Issue**: "No component metadata loaded"
- **Solution**: Call `load_component_metadata()` or pass metadata directly

**Issue**: "Components directory not found"
- **Solution**: Check `components_dir` path in config.py or pass correct path

**Issue**: "LLM error"
- **Solution**: Verify AWS credentials and `get_secrets.run_model()` configuration

## License

[Your License]

## Support

For questions or issues, please contact [Your Contact]
