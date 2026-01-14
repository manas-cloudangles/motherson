"""
Example: Page Generation

This script demonstrates how to use the page generation pipeline
to create new Angular pages.

The pipeline uses LLM to generate HTML, SCSS, and TypeScript files
based on a page description and available component metadata.
"""

import asyncio
from pathlib import Path
import sys
import json

# Add parent directory to path to import backend modules
sys.path.append(str(Path(__file__).parent.parent.parent))

from backend.modular_pipeline import (
    generate_page,
    generate_multiple_pages,
    generate_component_metadata
)


async def example_generate_single_page():
    """
    Example: Generate a single page
    """
    print("\n" + "="*70)
    print("EXAMPLE 1: Generate Single Page")
    print("="*70 + "\n")
    
    # First, ensure we have component metadata
    # (In production, you'd load from file or generate once)
    print("Step 1: Loading component metadata...")
    metadata = await generate_component_metadata(save_to_file=False)
    
    print("\nStep 2: Generating page...")
    
    # Generate a page
    page = await generate_page(
        page_description="Create a user profile page with a form for editing name and email",
        component_metadata=metadata
    )
    
    if page:
        print(f"\n✓ Page Generated Successfully!")
        print(f"\nComponent Details:")
        print(f"  Name: {page['component_name']}")
        print(f"  Selector: {page['selector']}")
        print(f"  Path: {page['path_name']}")
        print(f"\nGenerated Files:")
        print(f"  HTML: {len(page['html_code'])} characters")
        print(f"  SCSS: {len(page['scss_code'])} characters")
        print(f"  TypeScript: {len(page['ts_code'])} characters")
        
        # Preview HTML
        print(f"\nHTML Preview (first 300 chars):")
        print("-" * 70)
        print(page['html_code'][:300])
        print("...")
        print("-" * 70)
    else:
        print("❌ Failed to generate page")


async def example_generate_multiple_pages():
    """
    Example: Generate multiple pages at once
    """
    print("\n" + "="*70)
    print("EXAMPLE 2: Generate Multiple Pages")
    print("="*70 + "\n")
    
    # Load metadata
    print("Loading component metadata...")
    metadata = await generate_component_metadata(save_to_file=False)
    
    print("\nGenerating pages...")
    
    # Generate multiple pages
    page_descriptions = [
        "Create a dashboard page with statistics cards",
        "Create a settings page with user preferences",
        "Create a notifications page showing recent alerts"
    ]
    
    pages = await generate_multiple_pages(
        page_descriptions=page_descriptions,
        component_metadata=metadata
    )
    
    print(f"\n✓ Generated {len(pages)} pages successfully!\n")
    
    for idx, page in enumerate(pages, 1):
        print(f"{idx}. {page['component_name']}")
        print(f"   Selector: {page['selector']}")
        print(f"   Description: {page['description']}")
        print()


async def example_save_generated_page():
    """
    Example: Generate a page and save to files
    """
    print("\n" + "="*70)
    print("EXAMPLE 3: Generate and Save Page Files")
    print("="*70 + "\n")
    
    from backend.page_generation_pipeline import PageGenerationPipeline
    
    # Initialize pipeline
    pipeline = PageGenerationPipeline()
    
    # Load metadata from file (assumes you've generated it before)
    metadata_file = Path("component_metadata.json")
    if not metadata_file.exists():
        print("Generating metadata first...")
        metadata = await generate_component_metadata(save_to_file=True)
        pipeline.set_component_metadata(metadata)
    else:
        pipeline.load_component_metadata(metadata_file)
    
    # Generate page
    print("\nGenerating page...")
    page = await pipeline.generate_page("Create a welcome page with a hero section")
    
    if page:
        # Save to files
        output_dir = Path("generated_pages")
        print(f"\nSaving files to: {output_dir}")
        
        success = pipeline.save_page_files(
            page_data=page,
            output_dir=output_dir
        )
        
        if success:
            print(f"\n✓ Files saved successfully!")
            print(f"  Location: {output_dir / page['path_name']}")
            print(f"  Files:")
            print(f"    - {page['path_name']}.component.html")
            print(f"    - {page['path_name']}.component.scss")
            print(f"    - {page['path_name']}.component.ts")


async def example_inspect_generated_code():
    """
    Example: Generate a page and inspect the code in detail
    """
    print("\n" + "="*70)
    print("EXAMPLE 4: Inspect Generated Code")
    print("="*70 + "\n")
    
    # Generate metadata
    metadata = await generate_component_metadata(save_to_file=False)
    
    # Generate page
    page = await generate_page(
        page_description="Create a contact form page",
        component_metadata=metadata
    )
    
    if page:
        print("\n" + "="*70)
        print("GENERATED HTML")
        print("="*70)
        print(page['html_code'])
        
        print("\n" + "="*70)
        print("GENERATED SCSS")
        print("="*70)
        print(page['scss_code'])
        
        print("\n" + "="*70)
        print("GENERATED TYPESCRIPT")
        print("="*70)
        print(page['ts_code'])


async def example_export_to_json():
    """
    Example: Generate pages and export to JSON
    """
    print("\n" + "="*70)
    print("EXAMPLE 5: Export Generated Pages to JSON")
    print("="*70 + "\n")
    
    # Generate metadata
    metadata = await generate_component_metadata(save_to_file=False)
    
    # Generate pages
    pages = await generate_multiple_pages(
        page_descriptions=[
            "Create a login page",
            "Create a registration page"
        ],
        component_metadata=metadata
    )
    
    # Export to JSON
    output_file = Path("generated_pages.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(pages, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Exported {len(pages)} pages to: {output_file}")
    print(f"  File size: {output_file.stat().st_size} bytes")


async def main():
    """
    Run all examples
    """
    print("\n" + "#"*70)
    print("PAGE GENERATION EXAMPLES")
    print("#"*70)
    
    # Run examples (uncomment the ones you want to try)
    await example_generate_single_page()
    
    # Uncomment to run other examples:
    # await example_generate_multiple_pages()
    # await example_save_generated_page()
    # await example_inspect_generated_code()
    # await example_export_to_json()
    
    print("\n" + "#"*70)
    print("EXAMPLES COMPLETE")
    print("#"*70 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
