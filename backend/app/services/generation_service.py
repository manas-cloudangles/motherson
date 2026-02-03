import json
from typing import List, Dict, Optional

from app.services.llm_service import run_model
from app.utils.parsers import extract_json_from_response
from app.prompts import Generation, Chat

class GenerationService:
    async def generate_page(self, page_request: str, components: List[Dict]) -> Optional[Dict]:
        """
        Generate a page using the provided components.
        """
        # Build detailed component doc for generation
        components_doc = "Available Angular Components:\n\n"
        for comp in components:
            components_doc += f"Component: {comp['name']}\n"
            components_doc += f"Description: {comp['description']}\n"
            components_doc += f"HTML Tag/ID to use: {comp['id_name']}\n"
            # Include available inputs and outputs for proper binding
            inputs = comp.get('inputs', [])
            outputs = comp.get('outputs', [])
            if inputs:
                components_doc += f"Available Inputs (use with [inputName]): {', '.join(inputs)}\n"
            else:
                components_doc += "Available Inputs: NONE - Do NOT use property binding [] on this component\n"
            if outputs:
                components_doc += f"Available Outputs (use with (outputName)): {', '.join(outputs)}\n"
            else:
                components_doc += "Available Outputs: NONE - Do NOT use event binding () on this component\n"
            if comp.get('reasoning'):
                components_doc += f"Reasoning/Usage Note: {comp['reasoning']}\n"
            components_doc += "---\n\n"
        
        if not components:
            components_doc += "WARNING: NO REUSABLE COMPONENTS SELECTED/AVAILABLE.\n"
            components_doc += "You MUST generate all UI elements (headers, footers, tables, buttons) from scratch using standard HTML/SCSS.\n"
            components_doc += "Do not reference any <app-*> components that are not listed above.\n"
            
        system_prompt = Generation.system_prompt(components_doc)
        user_message = Generation.format_generation_user_prompt(page_request)
        
        try:
            response = await run_model(system_prompt, user_message)
            json_str = extract_json_from_response(response)
            page_data = json.loads(json_str)
            return page_data
        except Exception as e:
            print(f"Error generating page: {e}")
            return None

    async def chat_with_page(self, html: str, scss: str, ts: str, message: str) -> Optional[Dict]:
        """
        Modify existing page code based on chat message.
        """
        user_message = Chat.format_chat_user_prompt(html, scss, ts, message)
        
        try:
            response = await run_model(Chat.system_prompt, user_message)
            json_str = extract_json_from_response(response)
            data = json.loads(json_str)
            return data
        except Exception as e:
            print(f"Error chatting with page: {e}")
            return None
