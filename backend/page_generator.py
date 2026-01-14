"""
Page Generator Module

This module generates new Angular master pages using LLM and component metadata.

The generator:
1. Takes a page description from the user
2. Uses LLM to generate HTML, SCSS, and TypeScript files
3. Creates the component directory structure
4. Saves all generated files
5. Updates the master.module.ts file with imports, routes, and declarations

This is the modular version of the logic from page_generator_agent.ipynb
"""

import json
import re
from pathlib import Path
from typing import Dict, Any, Optional, List

from .config import MASTER_DIR, MASTER_MODULE_FILE, COMPONENT_METADATA_FILE
from .utils import (
    to_kebab_case,
    to_pascal_case,
    extract_json_from_response,
    write_file_safe,
    read_file_safe
)
from get_secrets import run_model


class PageGenerator:
    """
    Generate new Angular master pages using LLM and component metadata.
    """
    
    def __init__(
        self,
        master_dir: Path = MASTER_DIR,
        master_module_file: Path = MASTER_MODULE_FILE,
        component_metadata_file: Path = COMPONENT_METADATA_FILE
    ):
        """
        Initialize the page generator.
        
        Args:
            master_dir: Directory where master pages are stored
            master_module_file: Path to master.module.ts file
            component_metadata_file: Path to component metadata JSON
        """
        self.master_dir = master_dir
        self.master_module_file = master_module_file
        self.component_metadata_file = component_metadata_file
        self.component_metadata: List[Dict[str, Any]] = []
        self.system_prompt = ""
        
        # Load component metadata
        self.load_component_metadata()
    
    def load_component_metadata(self) -> bool:
        """
        Load component metadata from JSON file.
        
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.component_metadata_file.exists():
            print(f"⚠ Component metadata file not found: {self.component_metadata_file}")
            print("Please run component_metadata_generator first.")
            return False
        
        try:
            with open(self.component_metadata_file, 'r', encoding='utf-8') as f:
                self.component_metadata = json.load(f)
            
            print(f"✓ Loaded metadata for {len(self.component_metadata)} components")
            for comp in self.component_metadata:
                print(f"  - {comp['name']} (id: {comp['id_name']})")
            
            # Create system prompt with loaded metadata
            self.system_prompt = self._create_system_prompt()
            
            return True
        except Exception as e:
            print(f"❌ Error loading component metadata: {e}")
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
            components_doc += f"---\n\n"
        
        system_prompt = f"""You are an expert Angular developer creating new master pages.

You will be given a page requirement and you must generate THREE files: HTML, SCSS, and TypeScript.
You have access to the following Angular components, which you have to use to build the page:
{components_doc}

IMPORTANT RULES:
1. Use the available components listed above in your HTML (If they are not violating the user preference, always try to use them)
2. For buttons, use: <app-button>Click Me</app-button>
3. For header, use: <app-header></app-header>
4. For footer, use: <app-footer></app-footer>
5. The TypeScript file MUST:
   - Import Component from '@angular/core'
   - Have proper @Component decorator with selector, templateUrl, styleUrls
   - Export the component class
   - Include OnInit lifecycle hook
   - Have proper constructor and ngOnInit method

EXAMPLE HTML:
```html
<div class="page-container">
  <app-header></app-header>
  
  <div class="content">
    <h1>My Page Title</h1>
    <app-button>Submit</app-button>
  </div>
  
  <app-footer></app-footer>
</div>
```

EXAMPLE SCSS:
```scss
.page-container {{
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}}

.content {{
  flex: 1;
  padding: 20px;
}}
```

EXAMPLE TypeScript:
```typescript
import {{ Component, OnInit }} from '@angular/core';

@Component({{
  selector: 'app-sample-program',
  templateUrl: './sample-program.component.html',
  styleUrls: ['./sample-program.component.scss']
}})
export class SampleProgramComponent implements OnInit {{

  constructor() {{ }}

  ngOnInit(): void {{
    // Initialization logic here
  }}

}}
```

You MUST return ONLY a valid JSON object with this exact structure:
{{
  "component_name": "SampleProgramComponent",
  "path_name": "sample-program",
  "selector": "app-sample-program",
  "html_code": "complete HTML code here",
  "scss_code": "complete SCSS code here",
  "ts_code": "complete TypeScript code here"
}}

Rules for naming:
- component_name: PascalCase with "Component" suffix (e.g., "SampleProgramComponent")
- path_name: kebab-case (e.g., "sample-program")
- selector: "app-" + path_name (e.g., "app-sample-program")

Return ONLY the JSON object, no additional text or markdown."""
        
        return system_prompt
    
    async def generate_page_code(self, page_description: str) -> Optional[Dict[str, Any]]:
        """
        Generate page files using LLM.
        
        Args:
            page_description: User's description of the page to create
            
        Returns:
            Optional[Dict]: Generated code and metadata, or None if failed
        """
        print(f"\n{'='*60}")
        print(f"GENERATING PAGE: {page_description}")
        print(f"{'='*60}\n")
        
        user_message = f"""Create a new Angular master page for: {page_description}

Please generate a complete Angular component with HTML, SCSS, and TypeScript files.
Use the available components (app-header, app-footer, app-button, etc.) appropriately.

The page should be well-structured, professional, and follow Angular best practices."""
        
        print("⏳ Calling LLM to generate page code...")
        
        try:
            response = await run_model(
                system_prompt=self.system_prompt,
                user_message=user_message
            )
            
            print("✓ Received response from LLM")
            
            # Parse JSON response
            response_text = extract_json_from_response(response)
            page_data = json.loads(response_text)
            
            print(f"\n✓ Successfully parsed page data:")
            print(f"  Component Name: {page_data.get('component_name')}")
            print(f"  Path Name: {page_data.get('path_name')}")
            print(f"  Selector: {page_data.get('selector')}")
            print(f"  HTML Code: {len(page_data.get('html_code', ''))} characters")
            print(f"  SCSS Code: {len(page_data.get('scss_code', ''))} characters")
            print(f"  TS Code: {len(page_data.get('ts_code', ''))} characters")
            
            return page_data
            
        except json.JSONDecodeError as e:
            print(f"❌ Error parsing JSON response: {e}")
            print(f"Response was: {response[:500]}...")
            return None
        except Exception as e:
            print(f"❌ Error generating page: {e}")
            return None
    
    def save_page_files(self, page_data: Dict[str, Any]) -> Optional[Path]:
        """
        Create directory and save all generated files.
        
        Args:
            page_data: Dictionary containing generated code and metadata
            
        Returns:
            Optional[Path]: Path to the created directory, or None if failed
        """
        if not page_data:
            print("❌ No page data to save")
            return None
        
        path_name = page_data['path_name']
        component_dir = self.master_dir / path_name
        
        print(f"\n{'='*60}")
        print(f"SAVING FILES")
        print(f"{'='*60}\n")
        
        # Create directory
        print(f"Creating directory: {component_dir}")
        component_dir.mkdir(parents=True, exist_ok=True)
        print("✓ Directory created")
        
        # Save HTML file
        html_file = component_dir / f"{path_name}.component.html"
        print(f"\nSaving: {html_file.name}")
        if write_file_safe(html_file, page_data['html_code']):
            print(f"✓ Saved ({len(page_data['html_code'])} chars)")
        
        # Save SCSS file
        scss_file = component_dir / f"{path_name}.component.scss"
        print(f"\nSaving: {scss_file.name}")
        if write_file_safe(scss_file, page_data['scss_code']):
            print(f"✓ Saved ({len(page_data['scss_code'])} chars)")
        
        # Save TypeScript file
        ts_file = component_dir / f"{path_name}.component.ts"
        print(f"\nSaving: {ts_file.name}")
        if write_file_safe(ts_file, page_data['ts_code']):
            print(f"✓ Saved ({len(page_data['ts_code'])} chars)")
        
        # Create spec file (basic template)
        spec_file = component_dir / f"{path_name}.component.spec.ts"
        print(f"\nCreating: {spec_file.name}")
        spec_content = self._generate_spec_file(page_data['component_name'], path_name)
        if write_file_safe(spec_file, spec_content):
            print(f"✓ Saved spec file")
        
        print(f"\n{'='*60}")
        print(f"ALL FILES SAVED SUCCESSFULLY")
        print(f"Location: {component_dir}")
        print(f"{'='*60}\n")
        
        return component_dir
    
    def _generate_spec_file(self, component_name: str, path_name: str) -> str:
        """
        Generate a basic spec file template.
        
        Args:
            component_name: Component class name
            path_name: Component path name
            
        Returns:
            str: Spec file content
        """
        return f"""import {{ ComponentFixture, TestBed }} from '@angular/core/testing';

import {{ {component_name} }} from './{path_name}.component';

describe('{component_name}', () => {{
  let component: {component_name};
  let fixture: ComponentFixture<{component_name}>;

  beforeEach(async () => {{
    await TestBed.configureTestingModule({{
      declarations: [ {component_name} ]
    }})
    .compileComponents();
  }});

  beforeEach(() => {{
    fixture = TestBed.createComponent({component_name});
    component = fixture.componentInstance;
    fixture.detectChanges();
  }});

  it('should create', () => {{
    expect(component).toBeTruthy();
  }});
}});
"""
    
    def update_master_module(self, page_data: Dict[str, Any]) -> bool:
        """
        Update master.module.ts with import, route, and declaration.
        
        Args:
            page_data: Dictionary containing component metadata
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not page_data:
            print("❌ No page data to update module")
            return False
        
        print(f"\n{'='*60}")
        print(f"UPDATING master.module.ts")
        print(f"{'='*60}\n")
        
        component_name = page_data['component_name']
        path_name = page_data['path_name']
        
        # Read the current module file
        module_content = read_file_safe(self.master_module_file)
        
        if not module_content:
            print("❌ Failed to read master.module.ts")
            return False
        
        print("✓ Read master.module.ts")
        
        # 1. Add import statement
        import_statement = f"import {{ {component_name} }} from './{path_name}/{path_name}.component';"
        
        if import_statement in module_content:
            print(f"⚠ Import for {component_name} already exists")
        else:
            # Find the last import statement and add after it
            import_lines = [line for line in module_content.split('\n') if line.strip().startswith('import ')]
            if import_lines:
                last_import = import_lines[-1]
                module_content = module_content.replace(last_import, f"{last_import}\n{import_statement}")
                print(f"✓ Added import: {component_name}")
            else:
                print("❌ Could not find import section")
        
        # 2. Add route
        route_entry = f"  {{ path: '{path_name}', component: {component_name} }}"
        
        if route_entry not in module_content:
            # Find the routes array and add the new route
            routes_match = re.search(r'const routes = \[(.*?)\];', module_content, re.DOTALL)
            if routes_match:
                current_routes = routes_match.group(1)
                # Add new route before the closing bracket
                new_routes = current_routes.rstrip() + ",\n" + route_entry + "\n"
                module_content = module_content.replace(
                    f"const routes = [{current_routes}];",
                    f"const routes = [{new_routes}];"
                )
                print(f"✓ Added route: {path_name}")
            else:
                print("❌ Could not find routes array")
        else:
            print(f"⚠ Route for {path_name} already exists")
        
        # 3. Add to declarations
        if component_name not in module_content.split('declarations: [')[1].split(']')[0]:
            # Find the declarations array
            declarations_match = re.search(r'declarations: \[(.*?)\]', module_content, re.DOTALL)
            if declarations_match:
                current_declarations = declarations_match.group(1)
                # Add new component to declarations
                new_declarations = current_declarations.rstrip() + ",\n    " + component_name + "\n  "
                module_content = module_content.replace(
                    f"declarations: [{current_declarations}]",
                    f"declarations: [{new_declarations}]"
                )
                print(f"✓ Added to declarations: {component_name}")
            else:
                print("❌ Could not find declarations array")
        else:
            print(f"⚠ {component_name} already in declarations")
        
        # Write the updated content back
        if write_file_safe(self.master_module_file, module_content):
            print(f"\n{'='*60}")
            print(f"master.module.ts UPDATED SUCCESSFULLY")
            print(f"{'='*60}\n")
            return True
        else:
            print("❌ Failed to write master.module.ts")
            return False
    
    async def generate_new_page(self, page_description: str) -> bool:
        """
        Complete pipeline to generate a new Angular master page.
        
        Args:
            page_description: Description of the page to create
            
        Returns:
            bool: True if successful, False otherwise
        """
        print(f"\n{'#'*60}")
        print(f"STARTING PAGE GENERATION PIPELINE")
        print(f"Page: {page_description}")
        print(f"{'#'*60}\n")
        
        # Step 1: Generate code with LLM
        page_data = await self.generate_page_code(page_description)
        if not page_data:
            print("❌ Failed to generate page code")
            return False
        
        # Step 2: Save files to directory
        component_dir = self.save_page_files(page_data)
        if not component_dir:
            print("❌ Failed to save files")
            return False
        
        # Step 3: Update master.module.ts
        success = self.update_master_module(page_data)
        if not success:
            print("❌ Failed to update master.module.ts")
            return False
        
        print(f"\n{'#'*60}")
        print(f"PAGE GENERATION COMPLETE!")
        print(f"{'#'*60}\n")
        print(f"✓ Component created: {page_data['component_name']}")
        print(f"✓ Location: {component_dir}")
        print(f"✓ Route: /{page_data['path_name']}")
        print(f"✓ Module updated: master.module.ts")
        
        return True


async def generate_page(
    page_description: str,
    master_dir: Optional[Path] = None,
    master_module_file: Optional[Path] = None,
    component_metadata_file: Optional[Path] = None
) -> bool:
    """
    Convenience function to generate a new page.
    
    Args:
        page_description: Description of the page to create
        master_dir: Directory for master pages (defaults to config value)
        master_module_file: Master module file path (defaults to config value)
        component_metadata_file: Component metadata JSON path (defaults to config value)
        
    Returns:
        bool: True if successful, False otherwise
    """
    generator = PageGenerator(
        master_dir=master_dir or MASTER_DIR,
        master_module_file=master_module_file or MASTER_MODULE_FILE,
        component_metadata_file=component_metadata_file or COMPONENT_METADATA_FILE
    )
    
    return await generator.generate_new_page(page_description)


if __name__ == "__main__":
    # Test the module
    import asyncio
    
    async def main():
        test_description = "Create a welcome page with a centered button"
        generator = PageGenerator()
        await generator.generate_new_page(test_description)
    
    asyncio.run(main())
