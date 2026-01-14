"""
Component Metadata Generator Module

This module analyzes Angular components in a directory and generates
structured metadata for each component using an LLM.

The metadata includes:
- Component name and description
- Import path
- ID/selector name
- Full source code (HTML, SCSS, TypeScript)

This is the modular version of the logic from component_metadata_generator.ipynb
"""

import json
from pathlib import Path
from typing import List, Dict, Any, Optional
import asyncio

from .config import (
    COMPONENTS_DIR, 
    COMPONENT_METADATA_FILE,
    COMPONENT_README_FILE,
    COMPONENT_FILE_EXTENSIONS
)
from .utils import (
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


class ComponentMetadataGenerator:
    """
    Generate metadata for Angular components using LLM analysis.
    """
    
    def __init__(
        self, 
        components_dir: Path = COMPONENTS_DIR,
        output_json_file: Path = COMPONENT_METADATA_FILE,
        output_readme_file: Path = COMPONENT_README_FILE
    ):
        """
        Initialize the metadata generator.
        
        Args:
            components_dir: Directory containing Angular components
            output_json_file: Path to save JSON metadata
            output_readme_file: Path to save README documentation
        """
        self.components_dir = components_dir
        self.output_json_file = output_json_file
        self.output_readme_file = output_readme_file
        self.metadata_list: List[Dict[str, Any]] = []
    
    def discover_components(self) -> List[Path]:
        """
        Discover all component directories in the components folder.
        
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
        
        return component_dirs
    
    async def analyze_component(self, component_dir: Path) -> Optional[Dict[str, Any]]:
        """
        Analyze a single component and extract metadata using LLM.
        
        Args:
            component_dir: Path to the component directory
            
        Returns:
            Optional[Dict]: Component metadata or None if analysis fails
        """
        component_name = component_dir.name
        print(f"\n{'='*60}")
        print(f"Analyzing: {component_name}")
        print(f"{'='*60}")
        
        # Read all files in the component directory
        files_content = read_component_files(component_dir, COMPONENT_FILE_EXTENSIONS)
        
        if not files_content:
            print(f"⚠ No files found for {component_name}")
            return None
        
        print(f"✓ Read {len(files_content)} files")
        
        # Construct the user message with all file contents
        user_message = f"Analyze this Angular component: {component_name}\n\n"
        user_message += "Here are all the files in this component:\n\n"
        
        for filename, content in files_content.items():
            user_message += f"--- {filename} ---\n{content}\n\n"
        
        user_message += "\nPlease provide the component metadata in the specified JSON format."
        
        print(f"✓ Constructed prompt ({len(user_message)} characters)")
        print("⏳ Calling LLM...")
        
        try:
            # Call the LLM
            response = await run_model(
                system_prompt=METADATA_EXTRACTION_PROMPT,
                user_message=user_message
            )
            
            print(f"✓ Received response from LLM")
            
            # Parse the JSON response
            response_text = extract_json_from_response(response)
            metadata = json.loads(response_text)
            
            print(f"✓ Successfully parsed metadata")
            print(f"  Component: {metadata.get('name')}")
            print(f"  Import: {metadata.get('import_path')}")
            print(f"  ID Name: {metadata.get('id_name')}")
            
            # Add the actual file contents to the metadata
            metadata['html_code'] = files_content.get(f"{component_name}.component.html", "")
            metadata['scss_code'] = files_content.get(f"{component_name}.component.scss", "")
            metadata['ts_code'] = files_content.get(f"{component_name}.component.ts", "")
            
            print(f"✓ Added source code to metadata")
            
            return metadata
            
        except json.JSONDecodeError as e:
            print(f"❌ Error parsing JSON response: {e}")
            print(f"Response was: {response[:200]}...")
            return None
        except Exception as e:
            print(f"❌ Error analyzing component: {e}")
            return None
    
    async def generate_all_metadata(self) -> List[Dict[str, Any]]:
        """
        Generate metadata for all components in the directory.
        
        Returns:
            List[Dict]: List of metadata dictionaries for all components
        """
        component_dirs = self.discover_components()
        
        if not component_dirs:
            print("❌ No components found to analyze")
            return []
        
        print(f"\n{'#'*60}")
        print(f"STARTING COMPONENT METADATA GENERATION")
        print(f"Total components to process: {len(component_dirs)}")
        print(f"{'#'*60}\n")
        
        self.metadata_list = []
        
        # Process each component
        for idx, component_dir in enumerate(component_dirs, 1):
            print(f"\n[{idx}/{len(component_dirs)}] Processing {component_dir.name}...")
            
            metadata = await self.analyze_component(component_dir)
            
            if metadata:
                self.metadata_list.append(metadata)
                print(f"✓ Successfully added metadata for {component_dir.name}")
            else:
                print(f"⚠ Skipped {component_dir.name} due to errors")
        
        print(f"\n{'#'*60}")
        print(f"PROCESSING COMPLETE")
        print(f"Successfully processed: {len(self.metadata_list)}/{len(component_dirs)} components")
        print(f"{'#'*60}\n")
        
        return self.metadata_list
    
    def save_metadata_json(self) -> bool:
        """
        Save metadata to JSON file.
        
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.metadata_list:
            print("⚠ No metadata to save")
            return False
        
        try:
            with open(self.output_json_file, 'w', encoding='utf-8') as f:
                json.dump(self.metadata_list, f, indent=2, ensure_ascii=False)
            
            file_size = self.output_json_file.stat().st_size
            print(f"\n✓ Metadata saved to JSON: {self.output_json_file}")
            print(f"  File size: {file_size} bytes")
            print(f"  Components included: {len(self.metadata_list)}")
            
            return True
        except Exception as e:
            print(f"❌ Error saving JSON metadata: {e}")
            return False
    
    def generate_readme(self) -> str:
        """
        Generate a README documentation from the metadata.
        
        Returns:
            str: README content in Markdown format
        """
        readme_content = "# Angular Component Metadata\n\n"
        readme_content += "This document contains metadata for all Angular components in the project.\n"
        readme_content += f"Generated from: `{self.components_dir}`\n\n"
        readme_content += "---\n\n"
        readme_content += f"## Summary\n\n"
        readme_content += f"- **Total Components**: {len(self.metadata_list)}\n"
        readme_content += f"- **Components Directory**: `{self.components_dir}`\n\n"
        readme_content += "---\n\n"
        readme_content += "## Components\n\n"
        
        for idx, metadata in enumerate(self.metadata_list, 1):
            name = metadata.get('name', 'Unknown')
            description = metadata.get('description', 'No description available')
            import_path = metadata.get('import_path', 'N/A')
            id_name = metadata.get('id_name', 'null')
            
            readme_content += f"### {idx}. {name}\n\n"
            readme_content += f"**Description**: {description}\n\n"
            readme_content += f"**Import Path**: `{import_path}`\n\n"
            readme_content += f"**ID/Selector**: `{id_name}`\n\n"
            
            # Add code snippets
            html_code = metadata.get('html_code', '')
            scss_code = metadata.get('scss_code', '')
            ts_code = metadata.get('ts_code', '')
            
            if html_code:
                readme_content += "**HTML Template**:\n```html\n"
                readme_content += html_code[:500]  # Limit for readability
                if len(html_code) > 500:
                    readme_content += "\n... (truncated)"
                readme_content += "\n```\n\n"
            
            if ts_code:
                readme_content += "**TypeScript**:\n```typescript\n"
                readme_content += ts_code[:500]  # Limit for readability
                if len(ts_code) > 500:
                    readme_content += "\n... (truncated)"
                readme_content += "\n```\n\n"
            
            readme_content += "---\n\n"
        
        return readme_content
    
    def save_readme(self) -> bool:
        """
        Save metadata as README documentation.
        
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.metadata_list:
            print("⚠ No metadata to generate README")
            return False
        
        try:
            readme_content = self.generate_readme()
            
            with open(self.output_readme_file, 'w', encoding='utf-8') as f:
                f.write(readme_content)
            
            file_size = self.output_readme_file.stat().st_size
            print(f"\n✓ README saved: {self.output_readme_file}")
            print(f"  File size: {file_size} bytes")
            print(f"  Components documented: {len(self.metadata_list)}")
            
            return True
        except Exception as e:
            print(f"❌ Error saving README: {e}")
            return False
    
    async def run_full_pipeline(self) -> bool:
        """
        Run the complete metadata generation pipeline.
        
        Returns:
            bool: True if successful, False otherwise
        """
        print("\n" + "="*60)
        print("COMPONENT METADATA GENERATION PIPELINE")
        print("="*60 + "\n")
        
        # Step 1: Generate metadata
        metadata = await self.generate_all_metadata()
        
        if not metadata:
            print("❌ Failed to generate metadata")
            return False
        
        # Step 2: Save JSON
        json_success = self.save_metadata_json()
        
        # Step 3: Save README
        readme_success = self.save_readme()
        
        print("\n" + "="*60)
        print("PIPELINE COMPLETE")
        print("="*60)
        print(f"JSON saved: {'✓' if json_success else '❌'}")
        print(f"README saved: {'✓' if readme_success else '❌'}")
        
        return json_success and readme_success


async def generate_component_metadata(
    components_dir: Optional[Path] = None,
    output_json: Optional[Path] = None,
    output_readme: Optional[Path] = None
) -> List[Dict[str, Any]]:
    """
    Convenience function to generate component metadata.
    
    Args:
        components_dir: Directory containing components (defaults to config value)
        output_json: Output JSON file path (defaults to config value)
        output_readme: Output README file path (defaults to config value)
        
    Returns:
        List[Dict]: List of component metadata
    """
    generator = ComponentMetadataGenerator(
        components_dir=components_dir or COMPONENTS_DIR,
        output_json_file=output_json or COMPONENT_METADATA_FILE,
        output_readme_file=output_readme or COMPONENT_README_FILE
    )
    
    await generator.run_full_pipeline()
    return generator.metadata_list


if __name__ == "__main__":
    # Test the module
    async def main():
        generator = ComponentMetadataGenerator()
        await generator.run_full_pipeline()
    
    asyncio.run(main())
