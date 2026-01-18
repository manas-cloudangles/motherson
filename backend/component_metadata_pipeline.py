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
    read_file_safe,
    extract_json_from_response,
    generate_import_path
)
from get_secrets import run_model


# System prompt for LLM metadata extraction
METADATA_EXTRACTION_PROMPT = """You are an expert Angular developer analyzing component code.

Your task is to analyze the provided Angular component files and extract metadata about THIS SPECIFIC COMPONENT ONLY.

CRITICAL: You are analyzing an INDIVIDUAL COMPONENT, not a module. Extract metadata for the component class itself (e.g., AppButtonComponent, AppTableComponent), NOT for any module (e.g., AppCommonModule, CommonModule).

You MUST return ONLY a valid JSON object with this exact structure:
{
    "name": "component class name",
    "description": "detailed description of what this component does and where it should be used",
    "import_path": "the exact import path that should be used to import this component in other Angular modules or components",
    "id_name": "the name of the unique identifier input property for this component that will be used in other files, or null if none exists"
}

Rules:
1. The "name" MUST be the component class name found in the TypeScript file (e.g., "AppButtonComponent", "AppTableComponent", "AppHeaderComponent"). It should match the class that has @Component decorator. DO NOT use module names.
2. The "description" should explain:
   - What THIS SPECIFIC COMPONENT does (not what other components do)
   - What inputs/outputs THIS COMPONENT has
   - When and where to use THIS COMPONENT
   - Any special features or behaviors of THIS COMPONENT
3. The "import_path" should be the relative path from the app root to THIS COMPONENT's file (e.g., "app/common/components/app-button/app-button.component")
4. The "id_name" is the component selector (e.g., "app-button" from selector: 'app-button') or the name of a unique identifier input property, or null if none exists. This is what will be used in HTML templates to reference this component.

IMPORTANT: If you see multiple components or a module declaration in the files, extract metadata ONLY for the component that matches the file names provided. Ignore any module declarations or other components.

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
    
    def discover_components(self) -> List[Dict[str, Any]]:
        """
        Discover all individual Angular components by finding .component.ts files.
        Groups related files (html, scss, ts) by component name.
        
        Returns:
            List[Dict]: List of component info dicts with 'base_path' and 'files' keys
        """
        if not self.components_dir.exists():
            print(f"❌ Components directory not found: {self.components_dir}")
            return []
        
        # Find all .component.ts files recursively
        component_ts_files = list(self.components_dir.rglob('*.component.ts'))
        
        # Filter out spec files
        component_ts_files = [f for f in component_ts_files if '.spec.' not in f.name]
        
        components = []
        
        for ts_file in component_ts_files:
            # Get component base name (e.g., "app-button" from "app-button.component.ts")
            base_name = ts_file.stem.replace('.component', '')
            base_path = ts_file.parent
            
            # Find related files (html, scss)
            html_file = base_path / f"{base_name}.component.html"
            scss_file = base_path / f"{base_name}.component.scss"
            
            component_info = {
                'base_path': base_path,
                'base_name': base_name,
                'ts_file': ts_file,
                'html_file': html_file if html_file.exists() else None,
                'scss_file': scss_file if scss_file.exists() else None
            }
            
            components.append(component_info)
        
        print(f"✓ Discovered {len(components)} individual components")
        return components
    
    async def analyze_component(self, component_info: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Analyze a single component and extract metadata.
        
        Args:
            component_info: Dict with 'base_path', 'base_name', 'ts_file', 'html_file', 'scss_file'
            
        Returns:
            Optional[Dict]: Component metadata or None if analysis fails
        """
        base_name = component_info['base_name']
        ts_file = component_info['ts_file']
        html_file = component_info.get('html_file')
        scss_file = component_info.get('scss_file')
        
        print(f"\nAnalyzing: {base_name}")
        print(f"  Component path: {ts_file.relative_to(self.components_dir)}")
        
        # Read component files
        files_content = {}
        
        # Read TypeScript file (required)
        if ts_file.exists():
            ts_content = read_file_safe(ts_file)
            if ts_content:
                files_content['ts'] = ts_content
            else:
                print(f"  ⚠ Could not read TypeScript file: {ts_file}")
                return None
        else:
            print(f"  ⚠ TypeScript file not found: {ts_file}")
            return None
        
        # Read HTML file (optional)
        if html_file and html_file.exists():
            html_content = read_file_safe(html_file)
            if html_content:
                files_content['html'] = html_content
        
        # Read SCSS file (optional)
        if scss_file and scss_file.exists():
            scss_content = read_file_safe(scss_file)
            if scss_content:
                files_content['scss'] = scss_content
        
        print(f"  ✓ Read {len(files_content)} file(s)")
        
        # Construct the user message with all file contents
        user_message = f"Analyze this Angular component: {base_name}\n\n"
        user_message += "Here are the component files:\n\n"
        
        if 'ts' in files_content:
            user_message += f"--- TypeScript ({ts_file.name}) ---\n{files_content['ts']}\n\n"
        if 'html' in files_content:
            user_message += f"--- HTML ({html_file.name}) ---\n{files_content['html']}\n\n"
        if 'scss' in files_content:
            user_message += f"--- SCSS ({scss_file.name}) ---\n{files_content['scss']}\n\n"
        
        user_message += "\nIMPORTANT: Extract metadata for THIS SPECIFIC COMPONENT only, not for any module or other components. "
        user_message += "The component name should be the actual component class name (e.g., AppButtonComponent, AppTableComponent), "
        user_message += "NOT a module name (e.g., AppCommonModule)."
        user_message += "\n\nPlease provide the component metadata in the specified JSON format."
        
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
            
            # Extract selector from TypeScript code if id_name is null
            if not metadata.get('id_name') and 'ts' in files_content:
                import re
                ts_code = files_content['ts']
                # Look for selector in @Component decorator
                selector_match = re.search(r"selector\s*:\s*['\"]([^'\"]+)['\"]", ts_code)
                if selector_match:
                    metadata['id_name'] = selector_match.group(1)
                    print(f"  ✓ Extracted selector: {metadata['id_name']}")
                else:
                    # Fallback to component name in kebab-case
                    comp_name = metadata.get('name', base_name)
                    # Convert PascalCase to kebab-case
                    kebab_name = re.sub(r'(?<!^)(?=[A-Z])', '-', comp_name).lower()
                    metadata['id_name'] = kebab_name
                    print(f"  ✓ Using fallback selector: {metadata['id_name']}")
            
            # Add the actual file contents to the metadata
            metadata['html_code'] = files_content.get('html', '')
            metadata['scss_code'] = files_content.get('scss', '')
            metadata['ts_code'] = files_content.get('ts', '')
            
            # Add required and reasoning fields for component management
            metadata['required'] = False
            metadata['reasoning'] = ''
            
            return metadata
            
        except json.JSONDecodeError as e:
            print(f"  ❌ Error parsing JSON: {e}")
            return None
        except Exception as e:
            print(f"  ❌ Error analyzing component: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    async def generate_all_metadata(self) -> List[Dict[str, Any]]:
        """
        Generate metadata for all components.
        
        Returns:
            List[Dict]: List of metadata dictionaries
        """
        components = self.discover_components()
        
        if not components:
            print("❌ No components found")
            return []
        
        print(f"\n{'='*60}")
        print(f"Processing {len(components)} components...")
        print(f"{'='*60}\n")
        
        self.metadata_list = []
        
        for idx, component_info in enumerate(components, 1):
            print(f"[{idx}/{len(components)}]", end=" ")
            
            metadata = await self.analyze_component(component_info)
            
            if metadata:
                self.metadata_list.append(metadata)
        
        print(f"\n{'='*60}")
        print(f"✓ Successfully processed {len(self.metadata_list)}/{len(components)} components")
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
