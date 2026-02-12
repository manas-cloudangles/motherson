import json
import re
from pathlib import Path
from typing import List, Dict, Any, Optional

from app.config.config import COMPONENT_METADATA_FILE, COMPONENTS_DIR, COMPONENT_README_FILE
from app.services.llm_service import run_model
from app.utils.parsers import extract_json_from_response
from app.utils.file_ops import read_file_safe
from app.prompts import Metadata, Selection

class MetadataService:
    def __init__(self):
        self.metadata_file = COMPONENT_METADATA_FILE
        self.readme_file = COMPONENT_README_FILE
    
    def load_metadata(self) -> List[Dict]:
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading metadata: {e}")
        return []

    def save_metadata(self, metadata: List[Dict]) -> None:
        try:
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            print(f"Saved metadata to {self.metadata_file}")
            
            # Also save README
            self.save_readme(metadata)
        except Exception as e:
            print(f"Error saving metadata: {e}")

    def generate_readme(self, metadata_list: List[Dict]) -> str:
        """
        Generate README documentation.
        """
        readme = "# Angular Component Metadata\n\n"
        readme += f"Total Components: {len(metadata_list)}\n\n"
        readme += "---\n\n"
        
        for idx, metadata in enumerate(metadata_list, 1):
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

    def save_readme(self, metadata_list: List[Dict]) -> bool:
        """
        Save README documentation.
        """
        if not metadata_list:
            return False
        
        try:
            readme_content = self.generate_readme(metadata_list)
            
            with open(self.readme_file, 'w', encoding='utf-8') as f:
                f.write(readme_content)
            
            print(f"Saved README: {self.readme_file}")
            return True
        except Exception as e:
            print(f"Error saving README: {e}")
            return False

    async def analyze_components_from_files(self, temp_dir: Path) -> List[Dict]:
        """
        Analyze components in a directory (recursively) and return metadata.
        """
        print(f"Analyzing components from files: {temp_dir}")
        
        components = self._discover_components(temp_dir)
        print(f"Discovered {len(components)} components after filtering")
        
        metadata_list = []
        
        for comp_info in components:
            print(f"Analyzing component: {comp_info['base_name']}")
            meta = await self._analyze_single_component(comp_info, temp_dir)
            
            if meta:
                metadata_list.append(meta)
                print(f"✓ Successfully analyzed: {comp_info['base_name']}")
            else:
                print(f"✗ Failed to analyze: {comp_info['base_name']}")
        
        print(f"Total metadata generated: {len(metadata_list)} components")
        
        return metadata_list

    def _discover_components(self, root_dir: Path) -> List[Dict]:
        ts_files = list(root_dir.rglob('*.component.ts'))
        ts_files = [f for f in ts_files if '.spec.' not in f.name]
        
        print(f"Found {len(ts_files)} .component.ts files (excluding .spec files)")
        
        components = []
        filtered_out = []
        
        for ts_file in ts_files:
            # Legacy-style filtering: Only accept components from 'common' or 'shared' folders
            try:
                rel_path = ts_file.relative_to(root_dir)
                path_parts = [p.lower() for p in rel_path.parts]
                
                if 'common' not in path_parts and 'shared' not in path_parts:
                    filtered_out.append((str(rel_path), "Missing 'common' or 'shared' in path"))
                    continue
            except Exception as e:
                # If path manipulation fails, skip safely
                filtered_out.append((str(ts_file), f"Path error: {e}"))
                continue

            base_name = ts_file.stem.replace('.component', '')
            base_path = ts_file.parent
            html_file = base_path / f"{base_name}.component.html"
            scss_file = base_path / f"{base_name}.component.scss"
            
            components.append({
                'base_name': base_name,
                'ts_file': ts_file,
                'html_file': html_file if html_file.exists() else None,
                'scss_file': scss_file if scss_file.exists() else None
            })
        
        if filtered_out:
            print(f"⚠ Filtered out {len(filtered_out)} components:")
            for path, reason in filtered_out:
                print(f"  - {path}: {reason}")
        
        return components

    async def _analyze_single_component(self, comp_info: Dict, root_dir: Path) -> Optional[Dict]:
        ts_content = read_file_safe(comp_info['ts_file'])
        if not ts_content:
            return None
            
        html_content = read_file_safe(comp_info['html_file']) if comp_info['html_file'] else ""
        scss_content = read_file_safe(comp_info['scss_file']) if comp_info['scss_file'] else ""
        
        user_msg = Metadata.format_metadata_user_prompt(comp_info['base_name'], ts_content, html_content, scss_content)
        
        try:
            response = await run_model(Metadata.system_prompt, user_msg)
            json_str = extract_json_from_response(response)
            metadata = json.loads(json_str)
            
            # Enrich metadata
            metadata['html_code'] = html_content
            metadata['scss_code'] = scss_content
            metadata['ts_code'] = ts_content
            metadata['required'] = False
            metadata['reasoning'] = ''
            
            # Fallback for ID name if LLM missed it
            if not metadata.get('id_name'):
                match = re.search(r"selector\s*:\s*['\"]([^'\"]+)['\"]", ts_content)
                if match:
                    metadata['id_name'] = match.group(1)
                else:
                    # Kebab case fallback
                    metadata['id_name'] = re.sub(r'(?<!^)(?=[A-Z])', '-', metadata.get('name', comp_info['base_name'])).lower()
            
            return metadata
        except Exception as e:
            print(f"Error analyzing component {comp_info['base_name']}: {e}")
            return None

    async def select_components(self, page_request: str, available_components: List[Dict]) -> Dict:
        """
        Select components based on a user request.
        """
        # Build doc string
        doc = "Available Angular Components:\n\n"
        for idx, comp in enumerate(available_components, 1):
             doc += f"{idx}. Component: {comp['name']}\n"
             doc += f"   ID/Selector: {comp.get('id_name', 'N/A')}\n"
             doc += f"   Description: {comp.get('description', 'N/A')}\n"
             doc += f"   ---\n\n"
        
        user_msg = Selection.format_selection_user_prompt(page_request, doc)
        
        try:
            response = await run_model(Selection.system_prompt, user_msg)
            json_str = extract_json_from_response(response)
            selection_data = json.loads(json_str)
            return selection_data
        except Exception as e:
            print(f"Error selecting components: {e}")
            return {"selected_components": [], "reasoning": {}}

    def update_metadata_with_selection(self, selection_data: Dict, all_components: List[Dict]) -> List[Dict]:
        selected_ids = set(selection_data.get('selected_components', []))
        reasoning = selection_data.get('reasoning', {})
        
        updated = []
        for comp in all_components:
            comp_copy = comp.copy()
            id_name = comp.get('id_name') or comp.get('name')
            if id_name in selected_ids:
                comp_copy['required'] = True
                comp_copy['reasoning'] = reasoning.get(id_name, '')
            else:
                comp_copy['required'] = False
                comp_copy['reasoning'] = ''
            updated.append(comp_copy)
        return updated
