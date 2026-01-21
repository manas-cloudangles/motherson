import json
from typing import List, Dict, Optional

from app.services.llm_service import run_model
from app.utils.parsers import extract_json_from_response
from app.prompts.generation import create_generation_system_prompt, format_generation_user_prompt
from app.prompts.chat import CHAT_SYSTEM_PROMPT, format_chat_user_prompt

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
            if comp.get('reasoning'):
                components_doc += f"Reasoning/Usage Note: {comp['reasoning']}\n"
            components_doc += "---\n\n"
            
        system_prompt = create_generation_system_prompt(components_doc)
        user_message = format_generation_user_prompt(page_request)
        
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
        user_message = format_chat_user_prompt(html, scss, ts, message)
        
        try:
            response = await run_model(CHAT_SYSTEM_PROMPT, user_message)
            json_str = extract_json_from_response(response)
            data = json.loads(json_str)
            return data
        except Exception as e:
            print(f"Error chatting with page: {e}")
            return None
