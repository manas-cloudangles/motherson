"""
Main Pipeline Orchestrator

This module provides a complete pipeline for:
1. Generating component metadata from a directory
2. Generating new Angular pages based on user requests

It orchestrates the entire workflow and can be used as the main entry point.
"""

import asyncio
from pathlib import Path
from typing import Optional, List, Dict, Any

from .component_metadata_generator import ComponentMetadataGenerator
from .page_generator import PageGenerator
from .config import (
    COMPONENTS_DIR,
    MASTER_DIR,
    COMPONENT_METADATA_FILE,
    COMPONENT_README_FILE,
    MASTER_MODULE_FILE
)


class AngularPageGenerationPipeline:
    """
    Complete pipeline for Angular page generation.
    
    This class orchestrates:
    1. Component metadata generation
    2. Page generation using the metadata
    """
    
    def __init__(
        self,
        components_dir: Path = COMPONENTS_DIR,
        master_dir: Path = MASTER_DIR,
        metadata_json_file: Path = COMPONENT_METADATA_FILE,
        metadata_readme_file: Path = COMPONENT_README_FILE,
        master_module_file: Path = MASTER_MODULE_FILE
    ):
        """
        Initialize the pipeline.
        
        Args:
            components_dir: Directory containing Angular components
            master_dir: Directory for master pages
            metadata_json_file: Path to save component metadata JSON
            metadata_readme_file: Path to save component metadata README
            master_module_file: Path to master.module.ts
        """
        self.components_dir = components_dir
        self.master_dir = master_dir
        self.metadata_json_file = metadata_json_file
        self.metadata_readme_file = metadata_readme_file
        self.master_module_file = master_module_file
        
        self.metadata_generator: Optional[ComponentMetadataGenerator] = None
        self.page_generator: Optional[PageGenerator] = None
        self.component_metadata: List[Dict[str, Any]] = []
    
    async def initialize_metadata_generator(self) -> bool:
        """
        Initialize and run the component metadata generator.
        
        Returns:
            bool: True if successful, False otherwise
        """
        print("\n" + "="*70)
        print("INITIALIZING COMPONENT METADATA GENERATOR")
        print("="*70 + "\n")
        
        self.metadata_generator = ComponentMetadataGenerator(
            components_dir=self.components_dir,
            output_json_file=self.metadata_json_file,
            output_readme_file=self.metadata_readme_file
        )
        
        success = await self.metadata_generator.run_full_pipeline()
        
        if success:
            self.component_metadata = self.metadata_generator.metadata_list
            print(f"\n✓ Metadata generator initialized with {len(self.component_metadata)} components")
        else:
            print("\n❌ Failed to initialize metadata generator")
        
        return success
    
    def initialize_page_generator(self) -> bool:
        """
        Initialize the page generator with existing metadata.
        
        Returns:
            bool: True if successful, False otherwise
        """
        print("\n" + "="*70)
        print("INITIALIZING PAGE GENERATOR")
        print("="*70 + "\n")
        
        self.page_generator = PageGenerator(
            master_dir=self.master_dir,
            master_module_file=self.master_module_file,
            component_metadata_file=self.metadata_json_file
        )
        
        if self.page_generator.component_metadata:
            print(f"✓ Page generator initialized with {len(self.page_generator.component_metadata)} components")
            return True
        else:
            print("❌ Failed to initialize page generator")
            return False
    
    async def generate_pages(self, page_descriptions: List[str]) -> Dict[str, bool]:
        """
        Generate multiple pages based on descriptions.
        
        Args:
            page_descriptions: List of page descriptions
            
        Returns:
            Dict[str, bool]: Dictionary mapping descriptions to success status
        """
        if not self.page_generator:
            print("❌ Page generator not initialized")
            return {}
        
        results = {}
        
        print("\n" + "="*70)
        print(f"GENERATING {len(page_descriptions)} PAGES")
        print("="*70 + "\n")
        
        for idx, description in enumerate(page_descriptions, 1):
            print(f"\n{'*'*70}")
            print(f"PAGE {idx}/{len(page_descriptions)}: {description}")
            print(f"{'*'*70}\n")
            
            success = await self.page_generator.generate_new_page(description)
            results[description] = success
            
            if success:
                print(f"✓ Successfully generated page {idx}")
            else:
                print(f"❌ Failed to generate page {idx}")
        
        # Summary
        successful = sum(1 for v in results.values() if v)
        print("\n" + "="*70)
        print(f"PAGE GENERATION SUMMARY")
        print("="*70)
        print(f"Total pages: {len(page_descriptions)}")
        print(f"Successful: {successful}")
        print(f"Failed: {len(page_descriptions) - successful}")
        print("="*70 + "\n")
        
        return results
    
    async def run_full_pipeline(
        self,
        page_descriptions: Optional[List[str]] = None,
        regenerate_metadata: bool = True
    ) -> bool:
        """
        Run the complete pipeline from metadata generation to page creation.
        
        Args:
            page_descriptions: List of pages to generate (optional)
            regenerate_metadata: Whether to regenerate component metadata
            
        Returns:
            bool: True if all steps successful, False otherwise
        """
        print("\n" + "#"*70)
        print("STARTING COMPLETE ANGULAR PAGE GENERATION PIPELINE")
        print("#"*70 + "\n")
        
        # Step 1: Generate/load component metadata
        if regenerate_metadata:
            metadata_success = await self.initialize_metadata_generator()
            if not metadata_success:
                print("❌ Pipeline failed at metadata generation")
                return False
        
        # Step 2: Initialize page generator
        page_gen_init = self.initialize_page_generator()
        if not page_gen_init:
            print("❌ Pipeline failed at page generator initialization")
            return False
        
        # Step 3: Generate pages (if descriptions provided)
        if page_descriptions:
            results = await self.generate_pages(page_descriptions)
            all_successful = all(results.values())
            
            if not all_successful:
                print("⚠ Some pages failed to generate")
        
        print("\n" + "#"*70)
        print("PIPELINE COMPLETE")
        print("#"*70 + "\n")
        
        return True


async def run_metadata_generation_only(
    components_dir: Optional[Path] = None,
    output_json: Optional[Path] = None,
    output_readme: Optional[Path] = None
) -> List[Dict[str, Any]]:
    """
    Run only the component metadata generation.
    
    Args:
        components_dir: Directory containing components
        output_json: Output JSON file path
        output_readme: Output README file path
        
    Returns:
        List[Dict]: List of component metadata
    """
    from .component_metadata_generator import generate_component_metadata
    
    return await generate_component_metadata(
        components_dir=components_dir,
        output_json=output_json,
        output_readme=output_readme
    )


async def run_page_generation_only(
    page_descriptions: List[str],
    master_dir: Optional[Path] = None,
    master_module_file: Optional[Path] = None,
    component_metadata_file: Optional[Path] = None
) -> Dict[str, bool]:
    """
    Run only page generation (requires existing metadata).
    
    Args:
        page_descriptions: List of page descriptions
        master_dir: Directory for master pages
        master_module_file: Master module file path
        component_metadata_file: Component metadata JSON path
        
    Returns:
        Dict[str, bool]: Results for each page
    """
    generator = PageGenerator(
        master_dir=master_dir or MASTER_DIR,
        master_module_file=master_module_file or MASTER_MODULE_FILE,
        component_metadata_file=component_metadata_file or COMPONENT_METADATA_FILE
    )
    
    results = {}
    for description in page_descriptions:
        success = await generator.generate_new_page(description)
        results[description] = success
    
    return results


async def run_complete_pipeline(
    page_descriptions: List[str],
    regenerate_metadata: bool = True
) -> bool:
    """
    Convenience function to run the complete pipeline.
    
    Args:
        page_descriptions: List of page descriptions to generate
        regenerate_metadata: Whether to regenerate component metadata
        
    Returns:
        bool: True if successful, False otherwise
    """
    pipeline = AngularPageGenerationPipeline()
    return await pipeline.run_full_pipeline(
        page_descriptions=page_descriptions,
        regenerate_metadata=regenerate_metadata
    )


if __name__ == "__main__":
    # Example usage
    async def main():
        # Example 1: Run complete pipeline with page generation
        pages_to_generate = [
            "Create a user profile page with a form",
            "Create a dashboard with statistics cards"
        ]
        
        await run_complete_pipeline(
            page_descriptions=pages_to_generate,
            regenerate_metadata=True
        )
        
        # Example 2: Run only metadata generation
        # await run_metadata_generation_only()
        
        # Example 3: Run only page generation (requires existing metadata)
        # await run_page_generation_only(["Create a settings page"])
    
    asyncio.run(main())
