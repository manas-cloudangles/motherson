"""
Angular Page Generator Backend Package

This package provides modular pipelines for:
1. Component Metadata Generation - Analyze existing Angular components
2. Page Generation - Generate new Angular pages using LLM

NEW MODULAR ARCHITECTURE (v2.0):
- component_metadata_pipeline.py - Clean component analysis pipeline
- page_generation_pipeline.py - Page generation pipeline (returns code, no file saving)
- modular_pipeline.py - Unified interface for both pipelines

Quick Start:
    from backend.modular_pipeline import (
        generate_component_metadata,
        generate_page
    )
    
    # Generate metadata
    metadata = await generate_component_metadata(save_to_file=True)
    
    # Generate a page
    page = await generate_page(
        page_description="Create a dashboard page",
        component_metadata=metadata
    )
    
    # Access the generated code
    print(page['html_code'])
    print(page['scss_code'])
    print(page['ts_code'])

For more examples, see backend/examples/
For documentation, see README_MODULAR_PIPELINES.md
"""

# Main modular pipeline exports
from .modular_pipeline import (
    generate_component_metadata,
    generate_page,
    generate_multiple_pages,
    run_complete_pipeline,
    ModularPipeline
)

from .component_metadata_pipeline import ComponentMetadataPipeline
from .page_generation_pipeline import PageGenerationPipeline

__all__ = [
    # Main convenience functions
    'generate_component_metadata',
    'generate_page',
    'generate_multiple_pages',
    'run_complete_pipeline',
    
    # Pipeline classes
    'ModularPipeline',
    'ComponentMetadataPipeline',
    'PageGenerationPipeline',
]

__version__ = "2.0.0"
__author__ = "CloudAngles"
