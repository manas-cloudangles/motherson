import json
from typing import Dict, Optional, List

from app.services.llm_service import run_model
from app.utils.parsers import extract_json_from_response
from app.prompts import Integration, Backend


class IntegrationService:
    """
    Service for generating Angular service layer and PHP backend controller.
    """
    
    def __init__(self):
        # Placeholders for future template configurations
        self.service_template = ""  # Will be populated with exact Angular service template
        self.controller_template = ""  # Will be populated with exact PHP controller template
        self.base_class_name = "BaseController"  # Will be updated with actual base class name
    
    def set_service_template(self, template: str) -> None:
        """
        Set the Angular service template for future generations.
        This allows easy updating of the service structure.
        
        Args:
            template: The complete Angular service template
        """
        self.service_template = template
    
    def set_controller_template(self, template: str) -> None:
        """
        Set the PHP controller template for future generations.
        This allows easy updating of the controller structure.
        
        Args:
            template: The complete PHP controller template
        """
        self.controller_template = template
    
    def set_base_class_name(self, name: str) -> None:
        """
        Set the PHP base class name that controllers extend.
        
        Args:
            name: The base class name
        """
        self.base_class_name = name
    
    async def generate_angular_service(
        self,
        component_name: str,
        ts_code: str,
        html_code: str = ""
    ) -> Optional[Dict]:
        """
        Generate Angular service file with HTTP methods.
        
        Args:
            component_name: Name of the component
            ts_code: TypeScript component code
            html_code: Optional HTML code for additional context
            
        Returns:
            Dict containing service_name, file_name, service_code, and api_endpoints
            or None if generation fails
        """
        try:
            system_prompt = Integration.system_prompt(self.service_template)
            user_message = Integration.format_integration_user_prompt(
                component_name,
                ts_code,
                html_code
            )
            
            response = await run_model(system_prompt, user_message)
            json_str = extract_json_from_response(response)
            service_data = json.loads(json_str)
            
            return service_data
        except Exception as e:
            print(f"Error generating Angular service: {e}")
            return None
    
    async def generate_php_controller(
        self,
        component_name: str,
        html_code: str,
        ts_code: str,
        service_code: str = "",
        api_endpoints: List[Dict] = None,
        existing_controller: str = "",
        existing_backend_apis: List[Dict] = None
    ) -> Optional[Dict]:
        """
        Generate PHP controller with API methods.
        
        Args:
            component_name: Name of the component
            html_code: HTML code
            ts_code: TypeScript component code
            service_code: Optional Angular service code
            api_endpoints: Optional list of API endpoints from service generation
            existing_controller: Optional existing controller code to extend
            existing_backend_apis: Optional list of existing backend APIs to leverage
            
        Returns:
            Dict containing controller_name, file_name, controller_code,
            api_methods, and routes_config, or None if generation fails
        """
        try:
            # Build context from existing backend APIs
            existing_apis_context = ""
            if existing_backend_apis:
                existing_apis_context = "\n\n═══════════════════════════════════════════════════════════════\n"
                existing_apis_context += "EXISTING BACKEND APIs (REFERENCE)\n"
                existing_apis_context += "═══════════════════════════════════════════════════════════════\n\n"
                existing_apis_context += "The following PHP APIs already exist in the codebase. You can LEVERAGE and REUSE these existing endpoints:\n\n"
                
                for api in existing_backend_apis:
                    existing_apis_context += f"API: {api.get('name', 'Unknown')}\n"
                    existing_apis_context += f"File: {api.get('file_path', 'N/A')}\n"
                    
                    endpoints = api.get('endpoints', [])
                    if endpoints:
                        existing_apis_context += "Endpoints:\n"
                        for endpoint in endpoints:
                            method = endpoint.get('method', 'GET')
                            path = endpoint.get('path', '/api/endpoint')
                            func = endpoint.get('function_name', 'functionName')
                            desc = endpoint.get('description', '')
                            existing_apis_context += f"  - {method} {path} → {func}()\n"
                            if desc:
                                existing_apis_context += f"    {desc}\n"
                    
                    if api.get('php_code'):
                        # Include a snippet of the existing PHP code for reference
                        code_snippet = api['php_code'][:500] + "..." if len(api['php_code']) > 500 else api['php_code']
                        existing_apis_context += f"\nCode Reference:\n```php\n{code_snippet}\n```\n"
                    
                    existing_apis_context += "---\n\n"
                
                existing_apis_context += "\nINSTRUCTIONS FOR USING EXISTING APIs:\n"
                existing_apis_context += "- If an existing endpoint matches the needs of your new controller, REFERENCE or REUSE it\n"
                existing_apis_context += "- You can extend existing controllers or create similar patterns\n"
                existing_apis_context += "- Maintain consistency with existing API structures\n"
                existing_apis_context += "- If creating new endpoints, follow the same naming and structure conventions\n"
                existing_apis_context += "═══════════════════════════════════════════════════════════════\n\n"
            
            system_prompt = Backend.system_prompt(
                self.controller_template,
                self.base_class_name
            )
            user_message = existing_apis_context + Backend.format_backend_user_prompt(
                component_name,
                html_code,
                ts_code,
                service_code,
                api_endpoints,
                existing_controller
            )
            
            response = await run_model(system_prompt, user_message)
            json_str = extract_json_from_response(response)
            controller_data = json.loads(json_str)
            
            return controller_data
        except Exception as e:
            print(f"Error generating PHP controller: {e}")
            return None
    
    async def generate_full_stack(
        self,
        component_name: str,
        html_code: str,
        ts_code: str,
        existing_controller: str = "",
        existing_backend_apis: List[Dict] = None
    ) -> Optional[Dict]:
        """
        Generate both Angular service and PHP controller in one call.
        This is the main method to use for complete integration generation.
        
        Args:
            component_name: Name of the component
            html_code: HTML code
            ts_code: TypeScript component code
            existing_controller: Optional existing controller code
            existing_backend_apis: Optional list of existing backend APIs to leverage
            
        Returns:
            Dict containing both service and controller data:
            {
                "service": {...},
                "controller": {...}
            }
            or None if generation fails
        """
        try:
            # Step 1: Generate Angular service
            print(f"Generating Angular service for {component_name}...")
            service_data = await self.generate_angular_service(
                component_name,
                ts_code,
                html_code
            )
            
            if not service_data:
                print("Failed to generate Angular service")
                return None
            
            # Step 2: Generate PHP controller using service data and existing APIs
            print(f"Generating PHP controller for {component_name}...")
            if existing_backend_apis:
                print(f"  → Leveraging {len(existing_backend_apis)} existing backend APIs")
            
            controller_data = await self.generate_php_controller(
                component_name,
                html_code,
                ts_code,
                service_data.get('service_code', ''),
                service_data.get('api_endpoints', []),
                existing_controller,
                existing_backend_apis
            )
            
            if not controller_data:
                print("Failed to generate PHP controller")
                return None
            
            # Step 3: Return combined result
            return {
                "service": service_data,
                "controller": controller_data
            }
            
        except Exception as e:
            print(f"Error in full stack generation: {e}")
            return None
    
    def format_routes_for_php(self, routes_config: List[Dict]) -> str:
        """
        Helper method to format routes configuration for PHP routing file.
        This can be customized based on the routing framework used.
        
        Args:
            routes_config: List of route configurations
            
        Returns:
            Formatted routes as a string (will be updated with actual format later)
        """
        # Placeholder format - will be replaced with actual routing format
        routes_str = "// PHP Routes Configuration\n\n"
        
        for route in routes_config:
            method = route.get('http_method', 'GET')
            path = route.get('route', '')
            controller = route.get('controller', '')
            method_name = route.get('method', '')
            
            routes_str += f"// {method} {path}\n"
            routes_str += f"$router->map('{method}', '{path}', '{controller}@{method_name}');\n\n"
        
        return routes_str
