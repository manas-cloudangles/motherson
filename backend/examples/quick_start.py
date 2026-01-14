"""
Quick Start Guide

This script provides a quick way to get started with the modular pipelines.
Run this to see the pipelines in action!
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from backend.modular_pipeline import (
    generate_component_metadata,
    generate_page,
    run_complete_pipeline
)


async def quick_start():
    """
    Quick start demonstration
    """
    print("\n" + "#"*70)
    print("MODULAR BACKEND PIPELINES - QUICK START")
    print("#"*70 + "\n")
    
    print("This script demonstrates the two main pipelines:\n")
    print("1️⃣  Component Metadata Generation")
    print("2️⃣  Page Generation\n")
    
    # Option 1: Just generate metadata
    print("="*70)
    print("OPTION 1: Generate Component Metadata Only")
    print("="*70 + "\n")
    
    print("Analyzing Angular components...")
    metadata = await generate_component_metadata(
        save_to_file=True
    )
    
    print(f"\n✓ Generated metadata for {len(metadata)} components")
    print(f"  Saved to: component_metadata.json")
    
    # Show a sample
    if metadata:
        sample = metadata[0]
        print(f"\nSample Component:")
        print(f"  Name: {sample['name']}")
        print(f"  Selector: {sample['id_name']}")
        print(f"  Description: {sample['description'][:100]}...")
    
    # Option 2: Generate a page
    print("\n" + "="*70)
    print("OPTION 2: Generate a New Page")
    print("="*70 + "\n")
    
    print("Generating an Angular page...")
    page = await generate_page(
        page_description="Create a welcome page with a hero section and call-to-action button",
        component_metadata=metadata
    )
    
    if page:
        print(f"\n✓ Page generated successfully!")
        print(f"\nPage Details:")
        print(f"  Component Name: {page['component_name']}")
        print(f"  Selector: {page['selector']}")
        print(f"  Path: {page['path_name']}")
        
        print(f"\n📄 Generated Files:")
        print(f"  HTML: {len(page['html_code'])} characters")
        print(f"  SCSS: {len(page['scss_code'])} characters")
        print(f"  TypeScript: {len(page['ts_code'])} characters")
        
        print(f"\n📋 HTML Preview:")
        print("-" * 70)
        print(page['html_code'][:400])
        if len(page['html_code']) > 400:
            print("...")
        print("-" * 70)
        
        # Save the page to a file for inspection
        output_file = Path("generated_welcome_page.json")
        import json
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(page, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Complete page saved to: {output_file}")
        print("   You can inspect the HTML, SCSS, and TS code in this file.")
    
    # Summary
    print("\n" + "#"*70)
    print("QUICK START COMPLETE!")
    print("#"*70 + "\n")
    
    print("What you just did:")
    print("  ✓ Analyzed existing Angular components")
    print("  ✓ Generated structured metadata")
    print("  ✓ Used LLM to create a new Angular page")
    print("  ✓ Got HTML, SCSS, and TypeScript code\n")
    
    print("Next steps:")
    print("  1. Check the generated files:")
    print("     - component_metadata.json (component metadata)")
    print("     - generated_welcome_page.json (page code)")
    print()
    print("  2. Explore the examples:")
    print("     - examples/example_metadata_generation.py")
    print("     - examples/example_page_generation.py")
    print("     - examples/example_complete_workflow.py")
    print()
    print("  3. Read the documentation:")
    print("     - README_MODULAR_PIPELINES.md")
    print()
    print("  4. Integrate with your application!")
    print()


if __name__ == "__main__":
    try:
        asyncio.run(quick_start())
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nMake sure you have:")
        print("  - Configured the components directory in config.py")
        print("  - Set up AWS credentials for the LLM")
        print("  - Installed all required dependencies")
