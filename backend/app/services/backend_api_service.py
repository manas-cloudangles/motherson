import json
import re
from pathlib import Path
from typing import List, Dict, Any, Optional

from app.config.config import BACKEND_API_METADATA_FILE, BACKEND_API_README_FILE
from app.services.llm_service import run_model
from app.utils.parsers import extract_json_from_response
from app.utils.file_ops import read_file_safe

class BackendApiService:
    """
    Service for analyzing backend PHP files and extracting API endpoint metadata.
    """
    
    def __init__(self):
        self.metadata_file = BACKEND_API_METADATA_FILE
        self.readme_file = BACKEND_API_README_FILE
    
    def load_metadata(self) -> List[Dict]:
        """Load backend API metadata from JSON file."""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading backend API metadata: {e}")
        return []

    def save_metadata(self, metadata: List[Dict]) -> None:
        """Save backend API metadata to JSON file."""
        try:
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            print(f"Saved backend API metadata to {self.metadata_file}")
            
            # Also save README
            self.save_readme(metadata)
        except Exception as e:
            print(f"Error saving backend API metadata: {e}")

    def generate_readme(self, metadata_list: List[Dict]) -> str:
        """Generate README documentation for backend APIs."""
        readme = "# Backend API Metadata\n\n"
        readme += f"Total APIs: {len(metadata_list)}\n\n"
        readme += "---\n\n"
        
        for idx, metadata in enumerate(metadata_list, 1):
            name = metadata.get('name', 'Unknown')
            description = metadata.get('description', 'N/A')
            file_path = metadata.get('file_path', 'N/A')
            endpoints = metadata.get('endpoints', [])
            
            readme += f"## {idx}. {name}\n\n"
            readme += f"**Description**: {description}\n\n"
            readme += f"**File Path**: `{file_path}`\n\n"
            
            if endpoints:
                readme += "**Endpoints**:\n\n"
                for endpoint in endpoints:
                    method = endpoint.get('method', 'GET')
                    path = endpoint.get('path', '/api/endpoint')
                    endpoint_desc = endpoint.get('description', '')
                    readme += f"- `{method} {path}`: {endpoint_desc}\n"
                readme += "\n"
            
            readme += "---\n\n"
        
        return readme

    def save_readme(self, metadata_list: List[Dict]) -> bool:
        """Save README documentation for backend APIs."""
        if not metadata_list:
            return False
        
        try:
            readme_content = self.generate_readme(metadata_list)
            
            with open(self.readme_file, 'w', encoding='utf-8') as f:
                f.write(readme_content)
            
            print(f"Saved Backend API README: {self.readme_file}")
            return True
        except Exception as e:
            print(f"Error saving Backend API README: {e}")
            return False

    async def analyze_apis_from_files(self, temp_dir: Path) -> List[Dict]:
        """
        Analyze PHP files in a directory and extract API metadata.
        """
        print(f"Analyzing backend APIs from files: {temp_dir}")
        
        php_files = self._discover_php_files(temp_dir)
        print(f"Discovered {len(php_files)} PHP files")
        
        metadata_list = []
        
        for php_file_info in php_files:
            print(f"Analyzing PHP file: {php_file_info['file_name']}")
            meta = await self._analyze_single_php_file(php_file_info, temp_dir)
            
            if meta:
                metadata_list.append(meta)
                print(f"✓ Successfully analyzed: {php_file_info['file_name']}")
            else:
                print(f"✗ Failed to analyze: {php_file_info['file_name']}")
        
        print(f"Total backend API metadata generated: {len(metadata_list)} files")
        
        return metadata_list

    def _discover_php_files(self, root_dir: Path) -> List[Dict]:
        """
        Discover PHP files that contain API endpoints (controllers, routes, etc.).
        """
        php_files = list(root_dir.rglob('*.php'))
        
        print(f"Found {len(php_files)} .php files")
        
        discovered_files = []
        
        for php_file in php_files:
            # Filter out common non-API files
            file_name = php_file.name.lower()
            
            # Skip config files, vendor files, tests, etc.
            if any(skip in str(php_file).lower() for skip in ['vendor', 'test', 'config.php', 'index.php']):
                continue
            
            discovered_files.append({
                'file_name': php_file.stem,
                'file_path': php_file,
                'relative_path': php_file.relative_to(root_dir) if php_file.is_relative_to(root_dir) else php_file
            })
        
        print(f"Discovered {len(discovered_files)} PHP API files (after filtering)")
        
        return discovered_files

    async def _analyze_single_php_file(self, php_file_info: Dict, root_dir: Path) -> Optional[Dict]:
        """
        Analyze a single PHP file to extract API metadata.
        """
        php_content = read_file_safe(php_file_info['file_path'])
        if not php_content:
            return None
        
        # Use LLM to analyze PHP file
        system_prompt = self._get_php_analysis_system_prompt()
        user_prompt = self._format_php_analysis_user_prompt(
            php_file_info['file_name'],
            php_content
        )
        
        try:
            response = await run_model(system_prompt, user_prompt)
            json_str = extract_json_from_response(response)
            metadata = json.loads(json_str)
            
            # Enrich metadata
            metadata['php_code'] = php_content
            metadata['file_path'] = str(php_file_info['relative_path'])
            metadata['required'] = False
            metadata['reasoning'] = ''
            
            # Generate a unique ID
            if not metadata.get('id'):
                metadata['id'] = self._generate_api_id(php_file_info['file_name'])
            
            return metadata
        except Exception as e:
            print(f"Error analyzing PHP file {php_file_info['file_name']}: {e}")
            return None

    def _generate_api_id(self, file_name: str) -> str:
        """Generate a unique ID for an API based on file name."""
        # Convert to kebab-case
        api_id = re.sub(r'(?<!^)(?=[A-Z])', '-', file_name).lower()
        api_id = api_id.replace('_', '-').replace('controller', '').replace('api', '')
        api_id = api_id.strip('-')
        return f"api-{api_id}"

    def _get_php_analysis_system_prompt(self) -> str:
        """System prompt for analyzing PHP API files."""
        return """You are an expert PHP backend developer analyzing API code.

Your task is to analyze a PHP file (controller, API handler, or similar) and extract metadata about the API endpoints it provides.

You MUST return ONLY a valid JSON object with this exact structure:
{
    "name": "descriptive name of the API/Controller",
    "description": "detailed description of what this API provides, what data it handles, and when to use it",
    "id": "unique-kebab-case-identifier",
    "endpoints": [
        {
            "method": "GET|POST|PUT|DELETE|PATCH",
            "path": "/api/endpoint/path",
            "function_name": "functionName in the PHP code",
            "description": "what this endpoint does",
            "parameters": ["param1", "param2"],
            "returns": "description of what this endpoint returns"
        }
    ],
    "database_tables": ["list of database tables used by this API"],
    "dependencies": ["list of other classes or APIs this depends on"]
}

Rules:
1. Extract ALL public methods that appear to be API endpoints
2. Infer the HTTP method from the function name (e.g., "getUsers" → GET, "createUser" → POST, "updateUser" → PUT, "deleteUser" → DELETE)
3. Infer the API path from the function name and class name (e.g., "UserController::getUsers" → "/api/users/list")
4. List all parameters the endpoint accepts (from function parameters and $_GET/$_POST usage)
5. Describe what data the endpoint returns
6. Identify which database tables are accessed (look for SQL queries, $this->db->select(), etc.)
7. Note any dependencies on other classes or services

Return ONLY the JSON object, no additional text or explanation."""

    def _format_php_analysis_user_prompt(self, file_name: str, php_content: str) -> str:
        """Format user prompt for PHP analysis."""
        return f"""Analyze this PHP API file: {file_name}

--- PHP CODE ---
{php_content}

Please extract the API metadata in the specified JSON format.
Identify all API endpoints, their methods, paths, parameters, and what they do."""

    async def select_apis(self, page_request: str, available_apis: List[Dict]) -> Dict:
        """
        Select relevant backend APIs based on a user request.
        """
        # Build doc string
        doc = "Available Backend APIs:\n\n"
        for idx, api in enumerate(available_apis, 1):
            doc += f"{idx}. API: {api['name']}\n"
            doc += f"   ID: {api.get('id', 'N/A')}\n"
            doc += f"   Description: {api.get('description', 'N/A')}\n"
            doc += f"   Endpoints:\n"
            for endpoint in api.get('endpoints', []):
                doc += f"     - {endpoint.get('method', 'GET')} {endpoint.get('path', '/api/endpoint')}: {endpoint.get('description', '')}\n"
            doc += f"   ---\n\n"
        
        system_prompt = self._get_api_selection_system_prompt()
        user_prompt = self._format_api_selection_user_prompt(page_request, doc)
        
        try:
            response = await run_model(system_prompt, user_prompt)
            json_str = extract_json_from_response(response)
            selection_data = json.loads(json_str)
            return selection_data
        except Exception as e:
            print(f"Error selecting backend APIs: {e}")
            return {"selected_apis": [], "reasoning": {}}

    def _get_api_selection_system_prompt(self) -> str:
        """System prompt for selecting relevant backend APIs."""
        return """You are an expert backend developer analyzing which existing APIs are relevant for a page request.

You have been provided with:
1. A list of available backend PHP APIs with their endpoints
2. A user's request for a new page

Your task is to analyze which APIs from the available list would be most appropriate for implementing the backend functionality needed by the requested page.

You MUST return ONLY a valid JSON object with this exact structure:
{
    "selected_apis": ["api_id_1", "api_id_2", ...],
    "reasoning": {
        "api_id_1": "Clear explanation of why this API is needed and how it will be used",
        "api_id_2": "Clear explanation of why this API is needed and how it will be used",
        ...
    }
}

CRITICAL RULES:
1. Use the EXACT "ID" value from the API list for selected_apis
2. Only select APIs that are actually needed for the page request
3. Provide clear, specific reasoning for each selected API
4. The reasoning should explain HOW the API will be used in the requested page
5. Don't select APIs just because they're available - only if they're relevant
6. Be practical and realistic about API usage
7. Match the API IDs exactly as shown in the list (case-sensitive)

Return ONLY the JSON object, no additional text or explanation."""

    def _format_api_selection_user_prompt(self, page_request: str, apis_doc: str) -> str:
        """Format user prompt for API selection."""
        return f"""Page Generation Request:
"{page_request}"

{apis_doc}

IMPORTANT: When selecting APIs, use the EXACT "ID" value shown above (e.g., "api-user-management", "api-product").
Do NOT use file names or class names - use the ID value.

Please analyze the request and select which backend APIs from the list above would be most appropriate.
Provide clear reasoning for each selection explaining how each API will be used in the requested page."""

    def update_metadata_with_selection(self, selection_data: Dict, all_apis: List[Dict]) -> List[Dict]:
        """Update API metadata with selection results."""
        selected_ids = set(selection_data.get('selected_apis', []))
        reasoning = selection_data.get('reasoning', {})
        
        updated = []
        for api in all_apis:
            api_copy = api.copy()
            api_id = api.get('id') or api.get('name')
            if api_id in selected_ids:
                api_copy['required'] = True
                api_copy['reasoning'] = reasoning.get(api_id, '')
            else:
                api_copy['required'] = False
                api_copy['reasoning'] = ''
            updated.append(api_copy)
        return updated
