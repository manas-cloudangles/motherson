"""
Component Metadata Generation Pipeline

This module provides a clean, modular pipeline for generating metadata
for Angular components. It is designed to be used independently or as part
of a larger workflow.

Usage:
    from backend.component_metadata_pipeline import ComponentMetadataPipeline
    
    # Initialize pipeline
    pipeline = ComponentMetadataPipeline(components_dir="path/to/components")
    
    # Run pipeline
    metadata = await pipeline.run()
    
    # Access results
    print(f"Generated metadata for {len(metadata)} components")
"""

import asyncio
import json
from pathlib import Path
from typing import List, Dict, Any, Optional

from config import (
    COMPONENTS_DIR,
    COMPONENT_METADATA_FILE,
    COMPONENT_README_FILE,
    COMPONENT_FILE_EXTENSIONS
)
from utils import (
    read_component_files,
    extract_json_from_response,
    generate_import_path
)
from get_secrets import run_model


# System prompt for LLM metadata extraction
METADATA_EXTRACTION_PROMPT = """You are an expert Angular developer analyzing component code.

Your task is to analyze the provided Angular component files and extract metadata about the component.

You MUST return ONLY a valid JSON object with this exact structure:
{
    "name": "component name",
    "description": "detailed description of what this component does and where it should be used",
    "import_path": "the exact import path that should be used to import this component in other Angular modules or components",
    "id_name": "the name of the unique identifier input property for this component that will be used in other files, or null if none exists"
}

Rules:
1. The "name" should be the component class name (e.g., "AppButtonComponent")
2. The "description" should explain:
   - What the component does
   - What inputs/outputs it has
   - When and where to use it
   - Any special features or behaviors
3. The "import_path" should be the relative path from the app root (e.g., "app/common/components/app-button/app-button.component")
4. The "id_name" is the name of the unique identifier input property for this component that will be used in other files, or null if none exists. It is what we will be basically writing in the new html or ts files to reference this component.

Return ONLY the JSON object, no additional text or explanation."""


class ComponentMetadataPipeline:
    """
    Modular pipeline for generating component metadata.
    
    This pipeline:
    1. Discovers all components in a directory
    2. Analyzes each component using LLM
    3. Extracts structured metadata
    4. Returns metadata as a list of dictionaries
    """
    
    def __init__(
        self,
        components_dir: Optional[Path] = None,
        save_to_file: bool = False,
        output_json_file: Optional[Path] = None,
        output_readme_file: Optional[Path] = None
    ):
        """
        Initialize the component metadata pipeline.
        
        Args:
            components_dir: Directory containing Angular components (defaults to config)
            save_to_file: Whether to save results to files
            output_json_file: Path to save JSON metadata (if save_to_file=True)
            output_readme_file: Path to save README documentation (if save_to_file=True)
        """
        self.components_dir = components_dir or COMPONENTS_DIR
        self.save_to_file = save_to_file
        self.output_json_file = output_json_file or COMPONENT_METADATA_FILE
        self.output_readme_file = output_readme_file or COMPONENT_README_FILE
        self.metadata_list: List[Dict[str, Any]] = []
    
    def discover_components(self) -> List[Path]:
        """
        Discover all component directories.
        
        Returns:
            List[Path]: List of component directory paths
        """
        if not self.components_dir.exists():
            print(f"❌ Components directory not found: {self.components_dir}")
            return []
        
        component_dirs = [
            d for d in self.components_dir.iterdir()
            if d.is_dir() and not d.name.startswith('.')
        ]
        
        print(f"✓ Discovered {len(component_dirs)} components")
        return component_dirs
    
    async def analyze_component(self, component_dir: Path) -> Optional[Dict[str, Any]]:
        """
        Analyze a single component and extract metadata.
        
        Args:
            component_dir: Path to the component directory
            
        Returns:
            Optional[Dict]: Component metadata or None if analysis fails
        """
        component_name = component_dir.name
        print(f"\nAnalyzing: {component_name}")
        
        # Read all files in the component directory
        files_content = read_component_files(component_dir, COMPONENT_FILE_EXTENSIONS)
        
        if not files_content:
            print(f"⚠ No files found for {component_name}")
            return None
        
        print(f"  ✓ Read {len(files_content)} files")
        
        # Construct the user message with all file contents
        user_message = f"Analyze this Angular component: {component_name}\n\n"
        user_message += "Here are all the files in this component:\n\n"
        
        for filename, content in files_content.items():
            user_message += f"--- {filename} ---\n{content}\n\n"
        
        user_message += "\nPlease provide the component metadata in the specified JSON format."
        
        try:
            # Call the LLM
            response = await run_model(
                system_prompt=METADATA_EXTRACTION_PROMPT,
                user_message=user_message
            )
            
            # Parse the JSON response
            response_text = extract_json_from_response(response)
            metadata = json.loads(response_text)
            
            print(f"  ✓ Extracted metadata for {metadata.get('name')}")
            
            # Add the actual file contents to the metadata
            metadata['html_code'] = files_content.get(f"{component_name}.component.html", "")
            metadata['scss_code'] = files_content.get(f"{component_name}.component.scss", "")
            metadata['ts_code'] = files_content.get(f"{component_name}.component.ts", "")
            
            return metadata
            
        except json.JSONDecodeError as e:
            print(f"  ❌ Error parsing JSON: {e}")
            return None
        except Exception as e:
            print(f"  ❌ Error analyzing component: {e}")
            return None
    
    async def generate_all_metadata(self) -> List[Dict[str, Any]]:
        """
        Generate metadata for all components.
        
        Returns:
            List[Dict]: List of metadata dictionaries
        """
        component_dirs = self.discover_components()
        
        if not component_dirs:
            print("❌ No components found")
            return []
        
        print(f"\n{'='*60}")
        print(f"Processing {len(component_dirs)} components...")
        print(f"{'='*60}\n")
        
        self.metadata_list = []
        
        for idx, component_dir in enumerate(component_dirs, 1):
            print(f"[{idx}/{len(component_dirs)}]", end=" ")
            
            metadata = await self.analyze_component(component_dir)
            
            if metadata:
                self.metadata_list.append(metadata)
        
        print(f"\n{'='*60}")
        print(f"✓ Successfully processed {len(self.metadata_list)}/{len(component_dirs)} components")
        print(f"{'='*60}\n")
        
        return self.metadata_list
    
    def save_json(self) -> bool:
        """
        Save metadata to JSON file.
        
        Returns:
            bool: True if successful
        """
        if not self.metadata_list:
            print("⚠ No metadata to save")
            return False
        
        try:
            with open(self.output_json_file, 'w', encoding='utf-8') as f:
                json.dump(self.metadata_list, f, indent=2, ensure_ascii=False)
            
            print(f"✓ Saved JSON: {self.output_json_file}")
            return True
        except Exception as e:
            print(f"❌ Error saving JSON: {e}")
            return False
    
    def generate_readme(self) -> str:
        """
        Generate README documentation.
        
        Returns:
            str: README content
        """
        readme = "# Angular Component Metadata\n\n"
        readme += f"Total Components: {len(self.metadata_list)}\n\n"
        readme += "---\n\n"
        
        for idx, metadata in enumerate(self.metadata_list, 1):
            name = metadata.get('name', 'Unknown')
            description = metadata.get('description', 'N/A')
            import_path = metadata.get('import_path', 'N/A')
            id_name = metadata.get('id_name', 'null')
            
            readme += f"## {idx}. {name}\n\n"
            readme += f"**Description**: {description}\n\n"
            readme += f"**Import Path**: `{import_path}`\n\n"
            readme += f"**ID/Selector**: `{id_name}`\n\n"
            readme += "---\n\n"
        
        return readme
    
    def save_readme(self) -> bool:
        """
        Save README documentation.
        
        Returns:
            bool: True if successful
        """
        if not self.metadata_list:
            print("⚠ No metadata to save")
            return False
        
        try:
            readme_content = self.generate_readme()
            
            with open(self.output_readme_file, 'w', encoding='utf-8') as f:
                f.write(readme_content)
            
            print(f"✓ Saved README: {self.output_readme_file}")
            return True
        except Exception as e:
            print(f"❌ Error saving README: {e}")
            return False
    
    async def run(self) -> List[Dict[str, Any]]:
        """
        Run the complete pipeline.
        
        Returns:
            List[Dict]: List of component metadata
        """
        print("\n" + "#"*60)
        print("COMPONENT METADATA GENERATION PIPELINE")
        print("#"*60 + "\n")
        
        # Generate metadata
        metadata = await self.generate_all_metadata()
        
        # Save to files if requested
        if self.save_to_file and metadata:
            print("\nSaving results...")
            self.save_json()
            self.save_readme()
        
        print("\n" + "#"*60)
        print("PIPELINE COMPLETE")
        print("#"*60 + "\n")
        
        return metadata


# Convenience function
async def generate_component_metadata(
    components_dir: Optional[Path] = None,
    save_to_file: bool = False,
    output_json: Optional[Path] = None,
    output_readme: Optional[Path] = None
) -> List[Dict[str, Any]]:
    """
    Generate component metadata using the pipeline.
    
    Args:
        components_dir: Directory containing components
        save_to_file: Whether to save results to files
        output_json: Output JSON file path
        output_readme: Output README file path
        
    Returns:
        List[Dict]: List of component metadata
    """
    pipeline = ComponentMetadataPipeline(
        components_dir=components_dir,
        save_to_file=save_to_file,
        output_json_file=output_json,
        output_readme_file=output_readme
    )
    
    return await pipeline.run()


if __name__ == "__main__":
    # Example usage
    async def main():
        # Generate metadata and save to files
        metadata = await generate_component_metadata(save_to_file=True)
        
        print(f"\nGenerated metadata for {len(metadata)} components:")
        for comp in metadata:
            print(f"  - {comp['name']}")
    
    asyncio.run(main())
