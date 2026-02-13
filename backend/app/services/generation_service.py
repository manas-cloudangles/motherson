import json
from typing import List, Dict, Optional

from app.services.llm_service import run_model
from app.utils.parsers import extract_json_from_response
from app.prompts import Generation, Chat
from app.services.integration_service import IntegrationService

class GenerationService:
    async def generate_page(self, page_request: str, components: List[Dict], backend_apis: List[Dict] = None) -> Optional[Dict]:
        """
        Generate a page using the provided components and backend APIs.
        
        Args:
            page_request: User's page generation request
            components: List of frontend Angular components to use
            backend_apis: List of backend PHP APIs to leverage (optional)
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
        
        # Build backend API documentation
        backend_apis_doc = ""
        if backend_apis:
            backend_apis_doc = "\n\n═══════════════════════════════════════════════════════════════\n"
            backend_apis_doc += "AVAILABLE BACKEND APIs (PHP)\n"
            backend_apis_doc += "═══════════════════════════════════════════════════════════════\n\n"
            backend_apis_doc += "These are EXISTING backend API endpoints that you SHOULD LEVERAGE when generating the Angular service and component:\n\n"
            
            for api in backend_apis:
                backend_apis_doc += f"API: {api.get('name', 'Unknown')}\n"
                backend_apis_doc += f"Description: {api.get('description', 'N/A')}\n"
                backend_apis_doc += f"File: {api.get('file_path', 'N/A')}\n"
                
                endpoints = api.get('endpoints', [])
                if endpoints:
                    backend_apis_doc += "Endpoints:\n"
                    for endpoint in endpoints:
                        method = endpoint.get('method', 'GET')
                        path = endpoint.get('path', '/api/endpoint')
                        desc = endpoint.get('description', '')
                        params = endpoint.get('parameters', [])
                        backend_apis_doc += f"  - {method} {path}\n"
                        if desc:
                            backend_apis_doc += f"    Description: {desc}\n"
                        if params:
                            backend_apis_doc += f"    Parameters: {', '.join(params)}\n"
                
                if api.get('reasoning'):
                    backend_apis_doc += f"Usage Context: {api['reasoning']}\n"
                
                backend_apis_doc += "---\n\n"
            
            backend_apis_doc += "\nIMPORTANT INSTRUCTIONS FOR USING EXISTING APIS:\n"
            backend_apis_doc += "- When generating HTTP calls in the component, USE THE EXACT ENDPOINTS listed above\n"
            backend_apis_doc += "- Do NOT invent new API paths - use the existing ones\n"
            backend_apis_doc += "- The Angular service will be generated separately to match these endpoints\n"
            backend_apis_doc += "- If an endpoint matches the page's data needs, prefer using it over generic endpoints\n"
            backend_apis_doc += "═══════════════════════════════════════════════════════════════\n\n"
            
        system_prompt = Generation.system_prompt(components_doc + backend_apis_doc)
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
