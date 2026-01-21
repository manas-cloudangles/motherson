"""
Page Generation Pipeline

This module provides a clean, modular pipeline for generating new Angular pages
using LLM and component metadata. It returns the generated code without saving
to files or modifying module files.

Usage:
    from backend.page_generation_pipeline import PageGenerationPipeline
    
    # Initialize pipeline
    pipeline = PageGenerationPipeline()
    
    # Load component metadata
    pipeline.load_component_metadata("component_metadata.json")
    
    # Generate a page
    result = await pipeline.generate_page("Create a user profile page")
    
    # Access generated code
    print(result['html_code'])
    print(result['scss_code'])
    print(result['ts_code'])
"""

import asyncio
import json
from pathlib import Path
from typing import Dict, Any, Optional, List

from config import COMPONENT_METADATA_FILE
from utils import (
    to_kebab_case,
    to_pascal_case,
    extract_json_from_response
)
from get_secrets import run_model


class PageGenerationPipeline:
    """
    Modular pipeline for generating Angular pages.
    
    This pipeline:
    1. Loads component metadata
    2. Takes a page description
    3. Uses LLM to generate HTML, SCSS, and TypeScript code
    4. Returns the generated code as a dictionary
    
    Note: This pipeline does NOT save files or modify module.ts
    """
    
    def __init__(
        self,
        component_metadata_file: Optional[Path] = None,
        component_metadata: Optional[List[Dict[str, Any]]] = None
    ):
        """
        Initialize the page generation pipeline.
        
        Args:
            component_metadata_file: Path to component metadata JSON file
            component_metadata: Pre-loaded component metadata (optional)
        """
        self.component_metadata_file = component_metadata_file or COMPONENT_METADATA_FILE
        self.component_metadata: List[Dict[str, Any]] = component_metadata or []
        self.system_prompt: str = ""
        
        # Auto-load metadata if file provided and no metadata given
        if not self.component_metadata and self.component_metadata_file:
            self.load_component_metadata()
    
    def load_component_metadata(self, metadata_file: Optional[Path] = None) -> bool:
        """
        Load component metadata from JSON file.
        
        Args:
            metadata_file: Path to metadata JSON file (optional)
            
        Returns:
            bool: True if successful
        """
        file_path = metadata_file or self.component_metadata_file
        
        if not file_path.exists():
            print(f"⚠ Metadata file not found: {file_path}")
            return False
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                self.component_metadata = json.load(f)
            
            print(f"✓ Loaded metadata for {len(self.component_metadata)} components")
            
            # Generate system prompt
            self.system_prompt = self._create_system_prompt()
            
            return True
        except Exception as e:
            print(f"❌ Error loading metadata: {e}")
            return False
    
    
    def _create_system_prompt(self) -> str:
        """
        Create the system prompt for LLM page generation.
        
        Returns:
            str: Complete system prompt with component documentation
        """
        # Build components documentation
        components_doc = "Available Angular Components:\n\n"
        for comp in self.component_metadata:
            components_doc += f"Component: {comp['name']}\n"
            components_doc += f"Description: {comp['description']}\n"
            components_doc += f"HTML Tag/ID to use: {comp['id_name']}\n"
            components_doc += f"Import Path: {comp['import_path']}\n"
            
            # Add reasoning if provided (this comes from user's selection rationale)
            if comp.get('reasoning') and comp['reasoning'].strip():
                components_doc += f"Reasoning/Usage Note: {comp['reasoning']}\n"
                
            components_doc += f"---\n\n"
        
        system_prompt = f"""You are an expert Angular developer creating new master pages.

You will be given a page requirement and you must generate THREE files: HTML, SCSS, and TypeScript.
You have access to the following Angular components, which you should use to build the page:

{components_doc}


COMPONENT USAGE GUIDELINES:
If user preference is not violated, always use the components listed above in your HTML.
Example: If user wants a button, use <app-button>Button Text</app-button>

NEGATIVE USAGE GUIDELINES:
IF the user doesn't want to use the component, but the user request requires you to use it, generate the component without using that id, but generating it normally.
Example: If the user doesn't want to use app-header component, but create a page with header, use <header> tag and create a new one instead of using <app-header></app-header> component.

TYPESCRIPT REQUIREMENTS:
- Import Component and OnInit from '@angular/core'
- Use @Component decorator with selector, templateUrl, styleUrls
- Export the component class
- Include constructor and ngOnInit lifecycle hook

MOCK DATA REQUIREMENTS:
- Your component MUST have realistic mock data to show in the preview.
- Define properties in the class (e.g., tableData, userList, chartOptions) with proper interfaces or types.
- Initialize this data in `ngOnInit` with at least 3-5 rows/items of realistic sample data.
- Bind this data in your HTML (e.g., using *ngFor) so the page looks populated and functional immediately.
- DO NOT leave the page empty or waiting for an API call.

CRITICAL - OUTPUT FORMAT:
You MUST respond with PURE JSON ONLY. Your entire response must be a single valid JSON object.
DO NOT include any markdown code blocks, explanations, or extra text.
DO NOT wrap the JSON in ```json or ``` markers.
DO NOT add any text before or after the JSON.

REQUIRED JSON STRUCTURE:
{{
  "component_name": "PascalCaseComponentName",
  "path_name": "kebab-case-name",
  "selector": "app-kebab-case-name",
  "html_code": "complete HTML code as a string",
  "scss_code": "complete SCSS code as a string",
  "ts_code": "complete TypeScript code as a string"
}}

NAMING CONVENTIONS:
- component_name: PascalCase ending with "Component" (e.g., "WelcomePageComponent")
- path_name: kebab-case (e.g., "welcome-page")
- selector: "app-" prefix + path_name (e.g., "app-welcome-page")

COMPLETE EXAMPLE OUTPUT (this is how your ENTIRE response should look):

{{"component_name":"WelcomePageComponent","path_name":"welcome-page","selector":"app-welcome-page","html_code":"<div class=\\"page-container\\">\\n  <app-header></app-header>\\n  \\n  <div class=\\"content\\">\\n    <h1 class=\\"title\\">Welcome to Demo</h1>\\n    <p class=\\"subtitle\\">Get started with our application</p>\\n    <div class=\\"button-container\\">\\n      <app-button>Get Started</app-button>\\n    </div>\\n  </div>\\n  \\n  <app-footer></app-footer>\\n</div>","scss_code":".page-container {{\\n  display: flex;\\n  flex-direction: column;\\n  min-height: 100vh;\\n}}\\n\\n.content {{\\n  flex: 1;\\n  display: flex;\\n  flex-direction: column;\\n  align-items: center;\\n  justify-content: center;\\n  padding: 2rem;\\n  text-align: center;\\n}}\\n\\n.title {{\\n  font-size: 2.5rem;\\n  font-weight: bold;\\n  margin-bottom: 1rem;\\n  color: #333;\\n}}\\n\\n.subtitle {{\\n  font-size: 1.2rem;\\n  color: #666;\\n  margin-bottom: 2rem;\\n}}\\n\\n.button-container {{\\n  margin-top: 1.5rem;\\n}}","ts_code":"import {{ Component, OnInit }} from '@angular/core';\\n\\n@Component({{\\n  selector: 'app-welcome-page',\\n  templateUrl: './welcome-page.component.html',\\n  styleUrls: ['./welcome-page.component.scss']\\n}})\\nexport class WelcomePageComponent implements OnInit {{\\n\\n  constructor() {{ }}\\n\\n  ngOnInit(): void {{\\n    // Component initialization logic\\n  }}\\n\\n}}"}}

IMPORTANT REMINDERS:
 - Return ONLY the JSON object (no markdown, no extra text)
- Escape special characters: use \\n for newlines, \\" for quotes, \\\\ for backslashes
- Include COMPLETE code in html_code, scss_code, and ts_code fields
- Make the JSON compact (minimize whitespace between keys)
- Ensure the JSON is valid and directly parseable, no extra text or markdown.

 """
        
        return system_prompt
    
    async def generate_page(
        self,
        page_description: str,
        save_to_dict: bool = False
    ) -> Optional[Dict[str, Any]]:
        """
        Generate a new Angular page based on description.
        
        Args:
            page_description: Description of the page to create
            save_to_dict: If True, includes file paths in result (for optional saving)
            
        Returns:
            Optional[Dict]: Generated page data with code, or None if failed
            {
                "component_name": "ComponentName",
                "path_name": "component-name",
                "selector": "app-component-name",
                "html_code": "...",
                "scss_code": "...",
                "ts_code": "...",
                "description": "original description"
            }
        """
        if not self.component_metadata:
            print("❌ No component metadata loaded. Call load_component_metadata() first.")
            return None
        
        print(f"\n{'='*60}")
        print(f"GENERATING PAGE: {page_description}")
        print(f"{'='*60}\n")
        
        user_message = f"""Create a new Angular master page for: {page_description}

Please generate a complete Angular component with HTML, SCSS, and TypeScript files.
Use the available components (app-header, app-footer, app-button, etc.) appropriately.

The page should be well-structured, professional, and follow Angular best practices."""
        
        print("⏳ Calling LLM...")
        
        try:
            response = await run_model(
                system_prompt=self._create_system_prompt(),
                user_message=user_message
            )
            
            # print(f"System prompt: {self.system_prompt}")
            # print(f"User message: {user_message}")
            print("✓ Received response")
            print(f"📝 Raw response (first 500 chars):\n{response[:50]}\n")
            
            # Parse JSON response
            response_text = extract_json_from_response(response)
            
            if not response_text or not response_text.strip():
                print("❌ Error: LLM returned empty response")
                print(f"Full raw response:\n{response}\n")
                return None
            
            print(f"📝 Extracted JSON (first 500 chars):\n{response_text[:50]}\n")
            
            page_data = json.loads(response_text)
            
            # Add the original description
            page_data['description'] = page_description
            
            print(f"\n✓ Successfully generated page:")
            print(f"  Component: {page_data.get('component_name')}")
            print(f"  Path: {page_data.get('path_name')}")
            print(f"  Selector: {page_data.get('selector')}")
            print(f"  HTML: {len(page_data.get('html_code', ''))} chars")
            print(f"  SCSS: {len(page_data.get('scss_code', ''))} chars")
            print(f"  TS: {len(page_data.get('ts_code', ''))} chars")
            
            return page_data
            
        except json.JSONDecodeError as e:
            print(f"❌ Error parsing JSON: {e}")
            print(f"Failed JSON text (first 1000 chars):\n{response_text[:1000]}\n")
            print(f"Full raw response:\n{response}\n")
            return None
        except Exception as e:
            print(f"❌ Error generating page: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    async def generate_multiple_pages(
        self,
        page_descriptions: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Generate multiple pages from a list of descriptions.
        
        Args:
            page_descriptions: List of page descriptions
            
        Returns:
            List[Dict]: List of generated page data
        """
        results = []
        
        print(f"\n{'#'*60}")
        print(f"GENERATING {len(page_descriptions)} PAGES")
        print(f"{'#'*60}\n")
        
        for idx, description in enumerate(page_descriptions, 1):
            print(f"\n[{idx}/{len(page_descriptions)}]")
            
            page_data = await self.generate_page(description)
            
            if page_data:
                results.append(page_data)
                print(f"✓ Page {idx} generated successfully")
            else:
                print(f"❌ Failed to generate page {idx}")
        
        print(f"\n{'#'*60}")
        print(f"GENERATION COMPLETE: {len(results)}/{len(page_descriptions)} successful")
        print(f"{'#'*60}\n")
        
        return results
    
    def save_page_files(
        self,
        page_data: Dict[str, Any],
        output_dir: Path
    ) -> bool:
        """
        Optional: Save generated page files to a directory.
        
        Args:
            page_data: Generated page data
            output_dir: Directory to save files
            
        Returns:
            bool: True if successful
        """
        if not page_data:
            print("❌ No page data to save")
            return False
        
        path_name = page_data['path_name']
        component_dir = output_dir / path_name
        
        try:
            # Create directory
            component_dir.mkdir(parents=True, exist_ok=True)
            
            # Save HTML
            html_file = component_dir / f"{path_name}.component.html"
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(page_data['html_code'])
            
            # Save SCSS
            scss_file = component_dir / f"{path_name}.component.scss"
            with open(scss_file, 'w', encoding='utf-8') as f:
                f.write(page_data['scss_code'])
            
            # Save TypeScript
            ts_file = component_dir / f"{path_name}.component.ts"
            with open(ts_file, 'w', encoding='utf-8') as f:
                f.write(page_data['ts_code'])
            
            print(f"✓ Saved files to: {component_dir}")
            return True
            
        except Exception as e:
            print(f"❌ Error saving files: {e}")
            return False


# Convenience function
async def generate_page(
    page_description: str,
    component_metadata_file: Optional[Path] = None,
    component_metadata: Optional[List[Dict[str, Any]]] = None
) -> Optional[Dict[str, Any]]:
    """
    Generate a single page using the pipeline.
    
    Args:
        page_description: Description of the page to create
        component_metadata_file: Path to metadata JSON file
        component_metadata: Pre-loaded metadata (optional)
        
    Returns:
        Optional[Dict]: Generated page data or None
    """
    pipeline = PageGenerationPipeline(
        component_metadata_file=component_metadata_file,
        component_metadata=component_metadata
    )
    
    return await pipeline.generate_page(page_description)


async def generate_multiple_pages(
    page_descriptions: List[str],
    component_metadata_file: Optional[Path] = None,
    component_metadata: Optional[List[Dict[str, Any]]] = None
) -> List[Dict[str, Any]]:
    """
    Generate multiple pages using the pipeline.
    
    Args:
        page_descriptions: List of page descriptions
        component_metadata_file: Path to metadata JSON file
        component_metadata: Pre-loaded metadata (optional)
        
    Returns:
        List[Dict]: List of generated page data
    """
    pipeline = PageGenerationPipeline(
        component_metadata_file=component_metadata_file,
        component_metadata=component_metadata
    )
    
    return await pipeline.generate_multiple_pages(page_descriptions)


if __name__ == "__main__":
    # Example usage
    async def main():
        # Generate a single page
        page = await generate_page("Create a user profile page with a form")
        
        if page:
            print(f"\nGenerated: {page['component_name']}")
            print(f"\nHTML Preview:")
            print(page['html_code'][:200] + "...")
        
        # Generate multiple pages
        # pages = await generate_multiple_pages([
        #     "Create a dashboard page",
        #     "Create a settings page"
        # ])
    
    asyncio.run(main())
