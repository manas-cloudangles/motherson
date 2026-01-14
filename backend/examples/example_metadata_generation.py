"""
Example: Component Metadata Generation

This script demonstrates how to use the component metadata generation pipeline.

The pipeline analyzes Angular components and generates structured metadata
that can be used for code generation.
"""

import asyncio
from pathlib import Path
import sys

# Add parent directory to path to import backend modules
sys.path.append(str(Path(__file__).parent.parent.parent))

from backend.modular_pipeline import generate_component_metadata


async def example_basic_metadata_generation():
    """
    Basic example: Generate metadata and print results
    """
    print("\n" + "="*70)
    print("EXAMPLE 1: Basic Metadata Generation")
    print("="*70 + "\n")
    
    # Generate metadata (without saving to file)
    metadata = await generate_component_metadata(
        save_to_file=False
    )
    
    # Print results
    print(f"\nGenerated metadata for {len(metadata)} components:\n")
    for component in metadata:
        print(f"📦 {component['name']}")
        print(f"   Description: {component['description'][:100]}...")
        print(f"   Selector: {component['id_name']}")
        print(f"   Import: {component['import_path']}")
        print()


async def example_save_metadata_to_file():
    """
    Example: Generate metadata and save to JSON file
    """
    print("\n" + "="*70)
    print("EXAMPLE 2: Generate and Save Metadata")
    print("="*70 + "\n")
    
    # Generate metadata and save to files
    metadata = await generate_component_metadata(
        save_to_file=True,
        output_json=Path("component_metadata.json"),
        output_readme=Path("COMPONENT_METADATA_README.md")
    )
    
    print(f"\n✓ Metadata generated and saved!")
    print(f"  - component_metadata.json ({len(metadata)} components)")
    print(f"  - COMPONENT_METADATA_README.md")


async def example_custom_components_directory():
    """
    Example: Generate metadata from a custom directory
    """
    print("\n" + "="*70)
    print("EXAMPLE 3: Custom Components Directory")
    print("="*70 + "\n")
    
    # Specify custom directory
    custom_dir = Path(r"C:\path\to\your\components")
    
    # Only run if directory exists
    if not custom_dir.exists():
        print(f"⚠ Custom directory not found: {custom_dir}")
        print("Skipping this example...")
        return
    
    metadata = await generate_component_metadata(
        components_dir=custom_dir,
        save_to_file=True
    )
    
    print(f"\n✓ Generated metadata from: {custom_dir}")
    print(f"   Found {len(metadata)} components")


async def example_using_pipeline_class():
    """
    Example: Using the ComponentMetadataPipeline class directly
    """
    print("\n" + "="*70)
    print("EXAMPLE 4: Using Pipeline Class Directly")
    print("="*70 + "\n")
    
    from backend.component_metadata_pipeline import ComponentMetadataPipeline
    
    # Create pipeline instance
    pipeline = ComponentMetadataPipeline(
        save_to_file=False
    )
    
    # Discover components
    component_dirs = pipeline.discover_components()
    print(f"Discovered {len(component_dirs)} component directories")
    
    # Generate metadata
    metadata = await pipeline.generate_all_metadata()
    
    # Generate README
    readme_content = pipeline.generate_readme()
    print(f"\nGenerated README with {len(readme_content)} characters")
    
    # Access metadata
    print(f"\nFirst component:")
    if metadata:
        comp = metadata[0]
        print(f"  Name: {comp['name']}")
        print(f"  Description: {comp['description'][:100]}...")


async def main():
    """
    Run all examples
    """
    print("\n" + "#"*70)
    print("COMPONENT METADATA GENERATION EXAMPLES")
    print("#"*70)
    
    # Run examples
    await example_basic_metadata_generation()
    
    # Uncomment to run other examples:
    # await example_save_metadata_to_file()
    # await example_custom_components_directory()
    # await example_using_pipeline_class()
    
    print("\n" + "#"*70)
    print("EXAMPLES COMPLETE")
    print("#"*70 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
