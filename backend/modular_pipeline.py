"""
Unified Modular Pipeline

This module provides the main entry point for the modular backend pipelines:
1. Component Metadata Generation Pipeline
2. Page Generation Pipeline

Both pipelines are designed to work independently or together, and they
return results without saving files by default (though saving is optional).

Usage Example:
    from backend.modular_pipeline import (
        generate_component_metadata,
        generate_page,
        generate_multiple_pages
    )
    
    # Step 1: Generate component metadata
    metadata = await generate_component_metadata(
        components_dir="path/to/components",
        save_to_file=True  # Optional: save to JSON
    )
    
    # Step 2: Generate pages using the metadata
    page = await generate_page(
        page_description="Create a user dashboard",
        component_metadata=metadata  # Use the metadata from step 1
    )
    
    # Access the generated code
    print(page['html_code'])
    print(page['scss_code'])
    print(page['ts_code'])
"""

import asyncio
from pathlib import Path
from typing import List, Dict, Any, Optional

from .component_metadata_pipeline import (
    ComponentMetadataPipeline,
    generate_component_metadata as _gen_metadata
)
from .page_generation_pipeline import (
    PageGenerationPipeline,
    generate_page as _gen_page,
    generate_multiple_pages as _gen_multiple
)
from .config import COMPONENTS_DIR, COMPONENT_METADATA_FILE


class ModularPipeline:
    """
    Unified pipeline that orchestrates both metadata generation and page generation.
    
    This class provides a high-level interface for:
    1. Generating component metadata
    2. Generating pages using that metadata
    3. Optionally saving results to files
    """
    
    def __init__(
        self,
        components_dir: Optional[Path] = None,
        component_metadata_file: Optional[Path] = None,
        auto_save: bool = False
    ):
        """
        Initialize the unified pipeline.
        
        Args:
            components_dir: Directory containing Angular components
            component_metadata_file: Path to component metadata JSON
            auto_save: Whether to automatically save results to files
        """
        self.components_dir = components_dir or COMPONENTS_DIR
        self.component_metadata_file = component_metadata_file or COMPONENT_METADATA_FILE
        self.auto_save = auto_save
        
        self.metadata_pipeline: Optional[ComponentMetadataPipeline] = None
        self.page_pipeline: Optional[PageGenerationPipeline] = None
        self.component_metadata: List[Dict[str, Any]] = []
    
    async def initialize_metadata(self, regenerate: bool = False) -> bool:
        """
        Initialize component metadata (generate or load existing).
        
        Args:
            regenerate: If True, regenerate metadata even if file exists
            
        Returns:
            bool: True if successful
        """
        print("\n" + "="*70)
        print("INITIALIZING COMPONENT METADATA")
        print("="*70 + "\n")
        
        # If file exists and not regenerating, load it
        if not regenerate and self.component_metadata_file.exists():
            print("Found existing metadata file, loading...")
            self.page_pipeline = PageGenerationPipeline(
                component_metadata_file=self.component_metadata_file
            )
            if self.page_pipeline.load_component_metadata():
                self.component_metadata = self.page_pipeline.component_metadata
                print(f"✓ Loaded {len(self.component_metadata)} components from file")
                return True
        
        # Otherwise, generate new metadata
        print("Generating new metadata...")
        self.metadata_pipeline = ComponentMetadataPipeline(
            components_dir=self.components_dir,
            save_to_file=self.auto_save,
            output_json_file=self.component_metadata_file
        )
        
        metadata = await self.metadata_pipeline.run()
        
        if metadata:
            self.component_metadata = metadata
            
            # Initialize page pipeline with the new metadata
            self.page_pipeline = PageGenerationPipeline(
                component_metadata=self.component_metadata
            )
            
            print(f"✓ Generated metadata for {len(self.component_metadata)} components")
            return True
        
        print("❌ Failed to initialize metadata")
        return False
    
    async def generate_page(self, page_description: str) -> Optional[Dict[str, Any]]:
        """
        Generate a single page.
        
        Args:
            page_description: Description of the page to create
            
        Returns:
            Optional[Dict]: Generated page data or None
        """
        if not self.page_pipeline:
            print("❌ Pipeline not initialized. Call initialize_metadata() first.")
            return None
        
        return await self.page_pipeline.generate_page(page_description)
    
    async def generate_multiple_pages(
        self,
        page_descriptions: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Generate multiple pages.
        
        Args:
            page_descriptions: List of page descriptions
            
        Returns:
            List[Dict]: List of generated page data
        """
        if not self.page_pipeline:
            print("❌ Pipeline not initialized. Call initialize_metadata() first.")
            return []
        
        return await self.page_pipeline.generate_multiple_pages(page_descriptions)
    
    async def run_complete_workflow(
        self,
        page_descriptions: List[str],
        regenerate_metadata: bool = False
    ) -> Dict[str, Any]:
        """
        Run the complete workflow: metadata generation + page generation.
        
        Args:
            page_descriptions: List of pages to generate
            regenerate_metadata: Whether to regenerate component metadata
            
        Returns:
            Dict: Results containing metadata and generated pages
        """
        print("\n" + "#"*70)
        print("RUNNING COMPLETE MODULAR PIPELINE")
        print("#"*70 + "\n")
        
        # Step 1: Initialize metadata
        success = await self.initialize_metadata(regenerate=regenerate_metadata)
        if not success:
            print("❌ Pipeline failed at metadata initialization")
            return {
                'success': False,
                'metadata': [],
                'pages': []
            }
        
        # Step 2: Generate pages
        pages = await self.generate_multiple_pages(page_descriptions)
        
        print("\n" + "#"*70)
        print("PIPELINE COMPLETE")
        print("#"*70 + "\n")
        
        return {
            'success': True,
            'metadata': self.component_metadata,
            'pages': pages,
            'metadata_count': len(self.component_metadata),
            'pages_count': len(pages)
        }


# Convenience functions for direct use

async def generate_component_metadata(
    components_dir: Optional[Path] = None,
    save_to_file: bool = False,
    output_json: Optional[Path] = None,
    output_readme: Optional[Path] = None
) -> List[Dict[str, Any]]:
    """
    Generate component metadata.
    
    Args:
        components_dir: Directory containing components
        save_to_file: Whether to save results to files
        output_json: Output JSON file path
        output_readme: Output README file path
        
    Returns:
        List[Dict]: Component metadata
    """
    return await _gen_metadata(
        components_dir=components_dir,
        save_to_file=save_to_file,
        output_json=output_json,
        output_readme=output_readme
    )


async def generate_page(
    page_description: str,
    component_metadata_file: Optional[Path] = None,
    component_metadata: Optional[List[Dict[str, Any]]] = None
) -> Optional[Dict[str, Any]]:
    """
    Generate a single page.
    
    Args:
        page_description: Description of the page
        component_metadata_file: Path to metadata JSON
        component_metadata: Pre-loaded metadata
        
    Returns:
        Optional[Dict]: Generated page data
    """
    return await _gen_page(
        page_description=page_description,
        component_metadata_file=component_metadata_file,
        component_metadata=component_metadata
    )


async def generate_multiple_pages(
    page_descriptions: List[str],
    component_metadata_file: Optional[Path] = None,
    component_metadata: Optional[List[Dict[str, Any]]] = None
) -> List[Dict[str, Any]]:
    """
    Generate multiple pages.
    
    Args:
        page_descriptions: List of page descriptions
        component_metadata_file: Path to metadata JSON
        component_metadata: Pre-loaded metadata
        
    Returns:
        List[Dict]: Generated page data
    """
    return await _gen_multiple(
        page_descriptions=page_descriptions,
        component_metadata_file=component_metadata_file,
        component_metadata=component_metadata
    )


async def run_complete_pipeline(
    page_descriptions: List[str],
    components_dir: Optional[Path] = None,
    regenerate_metadata: bool = False,
    save_metadata: bool = True
) -> Dict[str, Any]:
    """
    Run the complete pipeline from metadata to pages.
    
    Args:
        page_descriptions: List of pages to generate
        components_dir: Directory containing components
        regenerate_metadata: Whether to regenerate metadata
        save_metadata: Whether to save metadata to file
        
    Returns:
        Dict: Complete results
    """
    pipeline = ModularPipeline(
        components_dir=components_dir,
        auto_save=save_metadata
    )
    
    return await pipeline.run_complete_workflow(
        page_descriptions=page_descriptions,
        regenerate_metadata=regenerate_metadata
    )


# Example usage
if __name__ == "__main__":
    async def main():
        print("=== Example 1: Generate metadata only ===\n")
        metadata = await generate_component_metadata(save_to_file=True)
        print(f"\nGenerated metadata for {len(metadata)} components\n")
        
        print("\n=== Example 2: Generate a single page ===\n")
        page = await generate_page(
            page_description="Create a user profile page with a form",
            component_metadata=metadata
        )
        if page:
            print(f"\nGenerated: {page['component_name']}")
            print(f"Files ready: HTML, SCSS, TS")
        
        print("\n=== Example 3: Generate multiple pages ===\n")
        pages = await generate_multiple_pages(
            page_descriptions=[
                "Create a dashboard page",
                "Create a settings page"
            ],
            component_metadata=metadata
        )
        print(f"\nGenerated {len(pages)} pages")
        
        print("\n=== Example 4: Run complete pipeline ===\n")
        result = await run_complete_pipeline(
            page_descriptions=["Create a welcome page"],
            regenerate_metadata=False
        )
        print(f"\nComplete! Metadata: {result['metadata_count']}, Pages: {result['pages_count']}")
    
    asyncio.run(main())
