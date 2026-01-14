# Backend Modular Pipelines - Complete Index

## 🎯 Quick Navigation

### Getting Started
- **[Quick Start](examples/quick_start.py)** - Run this first! ⚡
- **[README](README_MODULAR_PIPELINES.md)** - Complete documentation 📖
- **[Implementation Summary](IMPLEMENTATION_SUMMARY.md)** - What was done ✅
- **[Architecture](ARCHITECTURE.md)** - How it works 🏗️
- **[Migration Guide](MIGRATION_GUIDE.md)** - Upgrade from old version 🔄

---

## 📁 File Organization

### Core Pipelines (Use These!)
| File | Purpose | Status |
|------|---------|--------|
| `component_metadata_pipeline.py` | Analyze Angular components | ⭐ NEW |
| `page_generation_pipeline.py` | Generate new Angular pages | ⭐ NEW |
| `modular_pipeline.py` | Unified interface | ⭐ NEW |

### Configuration & Utilities
| File | Purpose | Status |
|------|---------|--------|
| `config.py` | Configuration settings | ✓ Active |
| `utils.py` | Helper functions | ✓ Active |
| `__init__.py` | Package exports | ✓ Updated |

### Documentation
| File | Description |
|------|-------------|
| `README_MODULAR_PIPELINES.md` | Complete usage guide |
| `IMPLEMENTATION_SUMMARY.md` | Summary of changes |
| `MIGRATION_GUIDE.md` | Old → New migration |
| `ARCHITECTURE.md` | Architecture diagrams |
| `INDEX.md` | This file |

### Examples
| File | What it shows |
|------|---------------|
| `examples/quick_start.py` | Quick demo of both pipelines |
| `examples/example_metadata_generation.py` | Component metadata examples |
| `examples/example_page_generation.py` | Page generation examples |
| `examples/example_complete_workflow.py` | Full workflow examples |

### Legacy (For Reference Only)
| File | Status |
|------|--------|
| `component_metadata_generator.py` | ⚠️ OLD (kept for reference) |
| `page_generator.py` | ⚠️ OLD (kept for reference) |
| `pipeline.py` | ⚠️ OLD (kept for reference) |

### Notebooks (Unchanged)
| File | Purpose |
|------|---------|
| `component_metadata_generator.ipynb` | Notebook version |
| `page_generator_agent.ipynb` | Notebook version |

---

## 🚀 Quick Start Guide

### 1. First Time Setup
```bash
# Navigate to examples
cd backend/examples

# Run quick start
python quick_start.py
```

### 2. Generate Component Metadata
```python
from backend import generate_component_metadata

metadata = await generate_component_metadata(save_to_file=True)
```

### 3. Generate a Page
```python
from backend import generate_page

page = await generate_page(
    page_description="Create a dashboard page",
    component_metadata=metadata
)

# Access the code
print(page['html_code'])
print(page['scss_code'])
print(page['ts_code'])
```

---

## 📚 Documentation Guide

### New to the Project?
1. Read [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) - Understand what was built
2. Read [README_MODULAR_PIPELINES.md](README_MODULAR_PIPELINES.md) - Learn how to use it
3. Run [examples/quick_start.py](examples/quick_start.py) - See it in action

### Migrating from Old Code?
1. Read [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md) - Compare old vs new
2. Check example scripts for patterns
3. Update your code gradually

### Want Deep Understanding?
1. Read [ARCHITECTURE.md](ARCHITECTURE.md) - See the design
2. Read source code docstrings
3. Explore example scripts

### Ready for Production?
1. Configure [config.py](config.py) with your paths
2. Test with [examples/example_complete_workflow.py](examples/example_complete_workflow.py)
3. Integrate with your application

---

## 🎓 Learning Path

### Beginner
```
1. examples/quick_start.py
2. README_MODULAR_PIPELINES.md (Quick Start section)
3. examples/example_metadata_generation.py
4. examples/example_page_generation.py
```

### Intermediate
```
1. ARCHITECTURE.md
2. examples/example_complete_workflow.py
3. Source code in component_metadata_pipeline.py
4. Source code in page_generation_pipeline.py
```

### Advanced
```
1. modular_pipeline.py (unified interface)
2. Custom integration patterns
3. API endpoint creation
4. Frontend integration
```

---

## 💡 Common Use Cases

### Use Case 1: Generate Metadata Once
```python
# Generate and save
metadata = await generate_component_metadata(save_to_file=True)
```

### Use Case 2: Generate Single Page
```python
# Load metadata from file
page = await generate_page(
    page_description="Create a login page",
    component_metadata_file="component_metadata.json"
)
```

### Use Case 3: Batch Generate Pages
```python
# Generate multiple pages
pages = await generate_multiple_pages(
    page_descriptions=["Dashboard", "Settings", "Profile"],
    component_metadata=metadata
)
```

### Use Case 4: API Endpoint
```python
@app.post("/api/generate-page")
async def api_generate_page(request):
    page = await generate_page(
        page_description=request.description,
        component_metadata_file="component_metadata.json"
    )
    return page
```

### Use Case 5: Complete Workflow
```python
# One command does everything
result = await run_complete_pipeline(
    page_descriptions=["Dashboard", "Settings"],
    regenerate_metadata=False
)
```

---

## 🔧 Configuration

### Essential Settings (config.py)
```python
# Where your Angular components are
COMPONENTS_DIR = Path("path/to/components")

# Where to save metadata
COMPONENT_METADATA_FILE = Path("component_metadata.json")

# LLM settings
LLM_MAX_TOKENS = 35000
LLM_TEMPERATURE = 0.3
```

### Optional Settings
- `COMPONENT_README_FILE` - README output path
- `COMPONENT_FILE_EXTENSIONS` - Which files to analyze
- `EXCLUDE_PATTERNS` - Patterns to ignore

---

## 🎯 Key Features

### Component Metadata Pipeline
✅ Discovers all components in a directory
✅ Analyzes code with LLM
✅ Extracts structured metadata
✅ Returns data (optional file saving)

### Page Generation Pipeline
✅ Takes page description
✅ Uses component metadata as context
✅ Generates HTML, SCSS, and TypeScript
✅ Returns code (no forced saving)
✅ No module.ts modifications

### Unified Interface
✅ Simple function API
✅ Can use pipelines together or separately
✅ Handles metadata caching
✅ Complete error handling

---

## 📊 API Reference

### Main Functions

#### `generate_component_metadata()`
```python
metadata = await generate_component_metadata(
    components_dir=None,      # Path to components
    save_to_file=False,       # Save to JSON?
    output_json=None,         # JSON path
    output_readme=None        # README path
)
# Returns: List[Dict[str, Any]]
```

#### `generate_page()`
```python
page = await generate_page(
    page_description,         # What to create
    component_metadata_file=None,  # Metadata JSON path
    component_metadata=None   # Or pre-loaded metadata
)
# Returns: Optional[Dict[str, Any]]
```

#### `generate_multiple_pages()`
```python
pages = await generate_multiple_pages(
    page_descriptions,        # List of descriptions
    component_metadata_file=None,
    component_metadata=None
)
# Returns: List[Dict[str, Any]]
```

#### `run_complete_pipeline()`
```python
result = await run_complete_pipeline(
    page_descriptions,        # Pages to generate
    components_dir=None,
    regenerate_metadata=False,
    save_metadata=True
)
# Returns: Dict with 'metadata' and 'pages'
```

---

## 🐛 Troubleshooting

### Issue: "No component metadata loaded"
**Solution**: Load metadata first:
```python
metadata = await generate_component_metadata()
# or
pipeline.load_component_metadata("file.json")
```

### Issue: "Components directory not found"
**Solution**: Check `COMPONENTS_DIR` in config.py:
```python
COMPONENTS_DIR = Path(r"C:\correct\path\to\components")
```

### Issue: "LLM error"
**Solution**: Verify AWS credentials and `get_secrets.run_model()` setup

### Issue: Import errors
**Solution**: Ensure proper imports:
```python
from backend.modular_pipeline import generate_page
# NOT from backend.page_generator
```

---

## 📈 What's New in v2.0

### Major Changes
- ✅ New modular architecture
- ✅ Returns code instead of saving files
- ✅ No automatic module.ts updates
- ✅ Simple function API
- ✅ Better error handling
- ✅ Complete documentation
- ✅ Working examples

### Improvements
- Better separation of concerns
- More flexible usage
- Easier testing
- Perfect for APIs
- Frontend-friendly
- Production-ready

### What's Removed
- ❌ Forced file saving
- ❌ Automatic module.ts updates
- ❌ Tight coupling between pipelines

---

## 🤝 Contributing

### Code Style
- Use type hints
- Add docstrings
- Follow existing patterns
- Include examples

### Adding Features
1. Create feature in appropriate pipeline
2. Add example in `examples/`
3. Update documentation
4. Test thoroughly

---

## 📞 Support

### Resources
- **Documentation**: All markdown files in backend/
- **Examples**: backend/examples/
- **Source Code**: Fully documented with docstrings

### Getting Help
1. Check documentation
2. Review examples
3. Read source code
4. Contact maintainers

---

## 🎉 Summary

You now have:
- ✅ Two independent, modular pipelines
- ✅ Clean API with simple functions
- ✅ Code generation that returns results
- ✅ Complete documentation and examples
- ✅ Production-ready architecture

**Start here**: Run `examples/quick_start.py` and see it in action!

---

## Version Info

**Current Version**: 2.0.0
**Author**: CloudAngles
**Last Updated**: January 2025

---

## License

[Your License Here]
