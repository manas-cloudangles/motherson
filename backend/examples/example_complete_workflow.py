"""
Example: Complete Workflow

This script demonstrates running the complete pipeline:
1. Generate component metadata
2. Use that metadata to generate new pages

This is the recommended approach for production use.
"""

import asyncio
from pathlib import Path
import sys
import json

# Add parent directory to path to import backend modules
sys.path.append(str(Path(__file__).parent.parent.parent))

from backend.modular_pipeline import (
    ModularPipeline,
    run_complete_pipeline
)


async def example_simple_complete_workflow():
    """
    Example: Simple complete workflow using convenience function
    """
    print("\n" + "="*70)
    print("EXAMPLE 1: Simple Complete Workflow")
    print("="*70 + "\n")
    
    # Run the complete pipeline
    result = await run_complete_pipeline(
        page_descriptions=[
            "Create a dashboard with statistics",
            "Create a user management page"
        ],
        regenerate_metadata=True,  # Generate fresh metadata
        save_metadata=True  # Save metadata to file
    )
    
    # Display results
    if result['success']:
        print("\n✓ Pipeline completed successfully!")
        print(f"\nResults Summary:")
        print(f"  Components analyzed: {result['metadata_count']}")
        print(f"  Pages generated: {result['pages_count']}")
        
        print(f"\nGenerated Pages:")
        for page in result['pages']:
            print(f"  - {page['component_name']}")
            print(f"    Path: {page['path_name']}")
            print(f"    Description: {page['description']}")
            print()


async def example_step_by_step_workflow():
    """
    Example: Step-by-step workflow with more control
    """
    print("\n" + "="*70)
    print("EXAMPLE 2: Step-by-Step Workflow")
    print("="*70 + "\n")
    
    # Initialize pipeline
    pipeline = ModularPipeline(auto_save=True)
    
    # Step 1: Initialize metadata (will load from file if exists)
    print("Step 1: Initializing component metadata...")
    success = await pipeline.initialize_metadata(regenerate=False)
    
    if not success:
        print("❌ Failed to initialize metadata")
        return
    
    print(f"✓ Metadata ready: {len(pipeline.component_metadata)} components\n")
    
    # Step 2: Generate first page
    print("Step 2: Generating first page...")
    page1 = await pipeline.generate_page("Create a home page with a hero section")
    
    if page1:
        print(f"✓ Generated: {page1['component_name']}\n")
    
    # Step 3: Generate second page
    print("Step 3: Generating second page...")
    page2 = await pipeline.generate_page("Create an about us page")
    
    if page2:
        print(f"✓ Generated: {page2['component_name']}\n")
    
    # Step 4: Generate multiple pages
    print("Step 4: Generating multiple pages...")
    pages = await pipeline.generate_multiple_pages([
        "Create a contact page with a form",
        "Create a FAQ page",
        "Create a pricing page"
    ])
    
    print(f"\n✓ Generated {len(pages)} pages")
    
    # Summary
    total_pages = (1 if page1 else 0) + (1 if page2 else 0) + len(pages)
    print(f"\n{'='*70}")
    print(f"Workflow Complete!")
    print(f"Total pages generated: {total_pages}")
    print(f"{'='*70}\n")


async def example_reuse_metadata():
    """
    Example: Reuse existing metadata without regenerating
    """
    print("\n" + "="*70)
    print("EXAMPLE 3: Reuse Existing Metadata")
    print("="*70 + "\n")
    
    metadata_file = Path("component_metadata.json")
    
    # Check if metadata file exists
    if not metadata_file.exists():
        print("Metadata file not found. Generating first...")
        from backend.modular_pipeline import generate_component_metadata
        await generate_component_metadata(save_to_file=True)
    
    # Run pipeline using existing metadata
    print("\nUsing existing metadata to generate pages...")
    
    result = await run_complete_pipeline(
        page_descriptions=[
            "Create a blog list page",
            "Create a blog detail page"
        ],
        regenerate_metadata=False,  # Use existing metadata
        save_metadata=False
    )
    
    if result['success']:
        print(f"\n✓ Generated {result['pages_count']} pages using cached metadata")


async def example_custom_save_location():
    """
    Example: Generate pages and save to custom location
    """
    print("\n" + "="*70)
    print("EXAMPLE 4: Save Pages to Custom Location")
    print("="*70 + "\n")
    
    from backend.page_generation_pipeline import PageGenerationPipeline
    from backend.modular_pipeline import generate_component_metadata
    
    # Generate metadata
    print("Generating metadata...")
    metadata = await generate_component_metadata(save_to_file=False)
    
    # Create pipeline
    pipeline = PageGenerationPipeline(component_metadata=metadata)
    
    # Generate pages
    print("\nGenerating pages...")
    pages = await pipeline.generate_multiple_pages([
        "Create a products listing page",
        "Create a product detail page",
        "Create a shopping cart page"
    ])
    
    # Save each page to custom location
    output_base = Path("custom_output/pages")
    print(f"\nSaving pages to: {output_base}")
    
    for page in pages:
        success = pipeline.save_page_files(
            page_data=page,
            output_dir=output_base
        )
        if success:
            print(f"  ✓ Saved: {page['path_name']}")
    
    print(f"\n✓ All pages saved to {output_base}")


async def example_export_complete_results():
    """
    Example: Export complete results (metadata + pages) to JSON
    """
    print("\n" + "="*70)
    print("EXAMPLE 5: Export Complete Results")
    print("="*70 + "\n")
    
    # Run complete pipeline
    result = await run_complete_pipeline(
        page_descriptions=[
            "Create a team members page",
            "Create a careers page"
        ],
        regenerate_metadata=True,
        save_metadata=False
    )
    
    if result['success']:
        # Export everything to JSON
        export_data = {
            'timestamp': '2025-01-13',
            'metadata_count': result['metadata_count'],
            'pages_count': result['pages_count'],
            'component_metadata': result['metadata'],
            'generated_pages': result['pages']
        }
        
        output_file = Path("complete_results.json")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n✓ Exported complete results to: {output_file}")
        print(f"  Components: {result['metadata_count']}")
        print(f"  Pages: {result['pages_count']}")
        print(f"  File size: {output_file.stat().st_size:,} bytes")


async def main():
    """
    Run all examples
    """
    print("\n" + "#"*70)
    print("COMPLETE WORKFLOW EXAMPLES")
    print("#"*70)
    
    # Run examples (uncomment the ones you want to try)
    await example_simple_complete_workflow()
    
    # Uncomment to run other examples:
    # await example_step_by_step_workflow()
    # await example_reuse_metadata()
    # await example_custom_save_location()
    # await example_export_complete_results()
    
    print("\n" + "#"*70)
    print("EXAMPLES COMPLETE")
    print("#"*70 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
