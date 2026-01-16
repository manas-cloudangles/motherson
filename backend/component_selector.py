"""
Component Selector Module

This module uses LLM to analyze a page generation request and determine
which components from the metadata should be used, along with reasoning.
"""

import json
from typing import List, Dict, Any, Optional

from utils import extract_json_from_response
from get_secrets import run_model


COMPONENT_SELECTION_PROMPT = """You are an expert Angular developer analyzing a page generation request.

You have been provided with:
1. A list of available Angular components with their descriptions and IDs/Selectors
2. A user's request for a new page

Your task is to analyze which components from the available list would be most appropriate
for implementing the user's request.

You MUST return ONLY a valid JSON object with this exact structure:
{
  "selected_components": ["component_id_1", "component_id_2", ...],
  "reasoning": {
    "component_id_1": "Clear explanation of why this component is needed for the request",
    "component_id_2": "Clear explanation of why this component is needed for the request",
    ...
  }
}

CRITICAL RULES:
1. Use the EXACT "ID/Selector" value from the component list for selected_components (e.g., "app-button", "app-table")
2. DO NOT use component class names (e.g., "AppButtonComponent") - use the ID/Selector instead
3. Only select components that are actually needed for the user's request
4. Provide clear, specific reasoning for each selected component
5. The reasoning should explain HOW the component will be used in the requested page
6. Don't select components just because they're available - only if they're relevant
7. Be practical and realistic about component usage
8. Match the component IDs exactly as shown in the list (case-sensitive)

Return ONLY the JSON object, no additional text or explanation."""


async def select_components_for_request(
    page_request: str,
    available_components: List[Dict[str, Any]]
) -> Optional[Dict[str, Any]]:
    """
    Use LLM to determine which components should be used for a page request.
    
    Args:
        page_request: User's description of the page to create
        available_components: List of component metadata dictionaries
        
    Returns:
        Optional[Dict]: {
            "selected_components": [...],  # List of component IDs/names
            "reasoning": {...}              # Dict of component_id -> reason
        }
    """
    if not available_components:
        print("⚠ No components available for selection")
        return None
    
    # Build components documentation
    components_doc = "Available Angular Components:\n\n"
    for idx, comp in enumerate(available_components, 1):
        components_doc += f"{idx}. Component: {comp['name']}\n"
        components_doc += f"   ID/Selector: {comp['id_name']}\n"
        components_doc += f"   Description: {comp['description']}\n"
        components_doc += f"   Import Path: {comp['import_path']}\n"
        components_doc += f"   ---\n\n"
    
    user_message = f"""Page Generation Request:
"{page_request}"

{components_doc}

IMPORTANT: When selecting components, use the EXACT "ID/Selector" value shown above (e.g., "app-button", "app-table").
Do NOT use component class names like "AppButtonComponent" - use the ID/Selector instead.

Please analyze the request and select which components from the list above would be most appropriate.
Provide clear reasoning for each selection explaining how each component will be used in the requested page."""
    
    print(f"\n{'='*60}")
    print("COMPONENT SELECTION")
    print(f"{'='*60}")
    print(f"Request: {page_request[:100]}...")
    print(f"Available components: {len(available_components)}")
    print("⏳ Calling LLM...")
    
    try:
        response = await run_model(
            system_prompt=COMPONENT_SELECTION_PROMPT,
            user_message=user_message
        )
        
        print("✓ Received response")
        
        # Parse JSON response
        response_text = extract_json_from_response(response)
        selection_data = json.loads(response_text)
        
        selected_count = len(selection_data.get('selected_components', []))
        print(f"✓ Selected {selected_count} components")
        
        # Validate that selected components exist in available components
        # Build a set of all possible identifiers (id_name or name as fallback)
        available_ids = set()
        id_to_comp = {}  # Map id to component for validation
        
        for comp in available_components:
            comp_id = comp.get('id_name') or comp.get('name')
            if comp_id:
                available_ids.add(comp_id)
                id_to_comp[comp_id] = comp
        
        print(f"Available component IDs: {sorted(available_ids)}")
        
        valid_selections = []
        invalid_selections = []
        
        for comp_id in selection_data.get('selected_components', []):
            if comp_id in available_ids:
                valid_selections.append(comp_id)
                comp_name = id_to_comp[comp_id].get('name', comp_id)
                print(f"  ✓ Selected: {comp_id} ({comp_name})")
            else:
                invalid_selections.append(comp_id)
                print(f"  ⚠ Component '{comp_id}' not found in available components")
                print(f"     Available IDs: {sorted(available_ids)}")
        
        if invalid_selections:
            print(f"⚠ Warning: {len(invalid_selections)} invalid component selections were ignored")
        
        selection_data['selected_components'] = valid_selections
        
        if len(valid_selections) == 0:
            print("⚠ Warning: No valid components were selected")
        
        return selection_data
        
    except json.JSONDecodeError as e:
        print(f"❌ Error parsing JSON: {e}")
        return None
    except Exception as e:
        print(f"❌ Error selecting components: {e}")
        return None


def update_component_metadata_with_selection(
    selection_data: Dict[str, Any],
    all_components: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Update component metadata with required and reasoning fields based on LLM selection.
    
    Args:
        selection_data: Component selection data with IDs and reasoning
        all_components: List of all component metadata
        
    Returns:
        List[Dict]: Updated component metadata with required and reasoning fields
    """
    selected_ids = set(selection_data.get('selected_components', []))
    reasoning = selection_data.get('reasoning', {})
    
    updated_components = []
    
    for comp in all_components:
        comp_id = comp.get('id_name') or comp.get('name')
        comp_copy = comp.copy()
        
        if comp_id and comp_id in selected_ids:
            # Component is required - set required to true and add reasoning
            comp_copy['required'] = True
            comp_copy['reasoning'] = reasoning.get(comp_id, '')
        else:
            # Component is not required - set required to false and clear reasoning
            comp_copy['required'] = False
            comp_copy['reasoning'] = ''
        
        updated_components.append(comp_copy)
    
    return updated_components


def get_selected_components_with_metadata(
    selection_data: Dict[str, Any],
    all_components: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Get full metadata for selected components.
    
    Args:
        selection_data: Component selection data with IDs and reasoning
        all_components: List of all component metadata
        
    Returns:
        List[Dict]: Selected components with full metadata + reasoning
    """
    selected_ids = set(selection_data.get('selected_components', []))
    reasoning = selection_data.get('reasoning', {})
    
    selected_components = []
    
    for comp in all_components:
        comp_id = comp.get('id_name') or comp.get('name')
        if comp_id and comp_id in selected_ids:
            # Add reasoning to the component metadata
            comp_with_reasoning = comp.copy()
            comp_with_reasoning['selection_reasoning'] = reasoning.get(comp_id, '')
            selected_components.append(comp_with_reasoning)
    
    return selected_components


if __name__ == "__main__":
    # Test the module
    import asyncio
    from pathlib import Path
    import json as json_module
    
    async def test():
        # Load component metadata
        metadata_file = Path("component_metadata.json")
        if not metadata_file.exists():
            print("Please generate component metadata first")
            return
        
        with open(metadata_file) as f:
            components = json_module.load(f)
        
        # Test selection
        test_request = "Create a user profile page with a form for editing user information"
        
        selection = await select_components_for_request(test_request, components)
        
        if selection:
            print(f"\nSelected Components:")
            for comp_id in selection['selected_components']:
                print(f"  - {comp_id}")
                print(f"    Reason: {selection['reasoning'].get(comp_id, 'N/A')}")
    
    asyncio.run(test())
