import asyncio
from fastapi import APIRouter, HTTPException
from typing import Dict, Any, Optional
from pydantic import BaseModel

from app.services.integration_service import IntegrationService
from app.services.workspace_service import WorkspaceService
from app.services.task_store import TaskStore

router = APIRouter()

integration_service = IntegrationService()
workspace_service = WorkspaceService()
task_store = TaskStore()


# Request/Response Models
class GenerateIntegrationRequest(BaseModel):
    component_name: str
    html_code: Optional[str] = None
    ts_code: Optional[str] = None
    existing_controller: Optional[str] = ""
    use_workspace_files: Optional[bool] = True


class UpdateTemplateRequest(BaseModel):
    template_type: str  # "service" or "controller" or "base_class"
    template_content: str


class GenerateSnippetsRequest(BaseModel):
    component_name: str


async def process_integration_task(
    task_id: str,
    component_name: str,
    html_code: str,
    ts_code: str,
    existing_controller: str
):
    """Background task to generate integration files."""
    try:
        # Generate full stack (service + controller)
        result = await integration_service.generate_full_stack(
            component_name,
            html_code,
            ts_code,
            existing_controller
        )
        
        if not result:
            task_store.update_task_error(task_id, "Failed to generate integration files")
            return
        
        # Format the result
        final_result = {
            "status": "success",
            "service": result.get("service", {}),
            "controller": result.get("controller", {}),
            "routes": integration_service.format_routes_for_php(
                result.get("controller", {}).get("routes_config", [])
            )
        }
        
        # Mark task complete
        task_store.update_task_result(task_id, final_result)
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        task_store.update_task_error(task_id, str(e))


@router.post("/generate-integration", response_model=Dict[str, Any])
async def generate_integration(request_data: GenerateIntegrationRequest):
    """
    Generate Angular service and PHP controller for a component.
    
    This endpoint:
    1. Takes component HTML and TS code
    2. Generates Angular service with HTTP methods
    3. Generates PHP controller with API endpoints
    4. Returns routes configuration
    """
    try:
        # Get code from request or workspace
        html_code = request_data.html_code
        ts_code = request_data.ts_code
        
        if request_data.use_workspace_files and (not html_code or not ts_code):
            # Load from workspace if not provided
            workspace_data = workspace_service.load_state()
            if workspace_data:
                html_code = html_code or workspace_data.get('html', '')
                ts_code = ts_code or workspace_data.get('ts', '')
            else:
                print("⚠️  Warning: use_workspace_files=true but no workspace data found")
        
        if not html_code or not ts_code:
            error_msg = "HTML and TS code are required. "
            if request_data.use_workspace_files:
                error_msg += "Workspace files not found. Please provide html_code and ts_code in the request body."
            else:
                error_msg += "Please provide html_code and ts_code in the request body."
            
            print(f"❌ Integration generation failed: {error_msg}")
            print(f"   Component: {request_data.component_name}")
            print(f"   Has HTML: {bool(html_code)}, Has TS: {bool(ts_code)}")
            
            raise HTTPException(
                status_code=400,
                detail=error_msg
            )
        
        print(f"✅ Starting integration generation for: {request_data.component_name}")
        print(f"   HTML length: {len(html_code)}, TS length: {len(ts_code)}")
        
        # Create task
        task_id = task_store.create_task()
        
        # Start background process
        asyncio.create_task(
            process_integration_task(
                task_id,
                request_data.component_name,
                html_code,
                ts_code,
                request_data.existing_controller or ""
            )
        )
        
        # Return task ID
        return {
            "status": "processing",
            "task_id": task_id,
            "message": "Generating Angular service and PHP controller..."
        }
        
    except HTTPException as he:
        raise he
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-service-only", response_model=Dict[str, Any])
async def generate_service_only(request_data: GenerateIntegrationRequest):
    """
    Generate only the Angular service file (no PHP controller).
    """
    try:
        # Get code from request or workspace
        html_code = request_data.html_code
        ts_code = request_data.ts_code
        
        if request_data.use_workspace_files and (not html_code or not ts_code):
            workspace_data = workspace_service.load_state()
            if workspace_data:
                html_code = html_code or workspace_data.get('html', '')
                ts_code = ts_code or workspace_data.get('ts', '')
        
        if not ts_code:
            raise HTTPException(
                status_code=400,
                detail="TS code is required"
            )
        
        # Generate service
        service_data = await integration_service.generate_angular_service(
            request_data.component_name,
            ts_code,
            html_code or ""
        )
        
        if not service_data:
            raise HTTPException(
                status_code=500,
                detail="Failed to generate Angular service"
            )
        
        return {
            "status": "success",
            "service": service_data
        }
        
    except HTTPException as he:
        raise he
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-controller-only", response_model=Dict[str, Any])
async def generate_controller_only(request_data: GenerateIntegrationRequest):
    """
    Generate only the PHP controller (requires HTML and TS code).
    """
    try:
        # Get code from request or workspace
        html_code = request_data.html_code
        ts_code = request_data.ts_code
        
        if request_data.use_workspace_files and (not html_code or not ts_code):
            workspace_data = workspace_service.load_state()
            if workspace_data:
                html_code = html_code or workspace_data.get('html', '')
                ts_code = ts_code or workspace_data.get('ts', '')
        
        if not html_code or not ts_code:
            raise HTTPException(
                status_code=400,
                detail="HTML and TS code are required"
            )
        
        # Generate controller
        controller_data = await integration_service.generate_php_controller(
            request_data.component_name,
            html_code,
            ts_code,
            "",  # service_code
            None,  # api_endpoints
            request_data.existing_controller or ""
        )
        
        if not controller_data:
            raise HTTPException(
                status_code=500,
                detail="Failed to generate PHP controller"
            )
        
        # Format routes
        routes = integration_service.format_routes_for_php(
            controller_data.get("routes_config", [])
        )
        
        return {
            "status": "success",
            "controller": controller_data,
            "routes": routes
        }
        
    except HTTPException as he:
        raise he
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/update-template", response_model=Dict[str, str])
async def update_template(request_data: UpdateTemplateRequest):
    """
    Update the template for service or controller generation.
    
    This allows you to set exact formats for:
    - Angular service structure (template_type: "service")
    - PHP controller structure (template_type: "controller")
    - PHP base class name (template_type: "base_class")
    """
    try:
        template_type = request_data.template_type.lower()
        
        if template_type == "service":
            integration_service.set_service_template(request_data.template_content)
            return {
                "status": "success",
                "message": "Angular service template updated successfully"
            }
        elif template_type == "controller":
            integration_service.set_controller_template(request_data.template_content)
            return {
                "status": "success",
                "message": "PHP controller template updated successfully"
            }
        elif template_type == "base_class":
            integration_service.set_base_class_name(request_data.template_content)
            return {
                "status": "success",
                "message": f"PHP base class name set to: {request_data.template_content}"
            }
        else:
            raise HTTPException(
                status_code=400,
                detail="template_type must be 'service', 'controller', or 'base_class'"
            )
        
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/templates", response_model=Dict[str, Any])
async def get_templates():
    """
    Get current templates and configuration.
    """
    return {
        "service_template": integration_service.service_template or "Using default template",
        "controller_template": integration_service.controller_template or "Using default template",
        "base_class_name": integration_service.base_class_name
    }


@router.post("/generate-snippets", response_model=Dict[str, Any])
async def generate_snippets(request_data: GenerateSnippetsRequest):
    """
    Generate Angular routing and sidebar module integration snippets.
    
    This endpoint generates the code snippets needed to integrate
    the generated component into:
    1. app-routing.module.ts (routing setup)
    2. layout-sidebar.module.ts (module declaration)
    
    Used by the frontend's Integration tab.
    """
    try:
        component_name = request_data.component_name
        
        # Convert to PascalCase with "Component" suffix
        # e.g., "User Profile" -> "UserProfileComponent"
        pascal_case_name = ''.join(word.capitalize() for word in component_name.split())
        if not pascal_case_name.endswith('Component'):
            pascal_case_name += 'Component'
        
        # Convert to kebab-case for file paths
        # e.g., "UserProfileComponent" -> "user-profile"
        kebab_case_name = component_name.lower().replace(' ', '-')
        
        # Convert to kebab-case with "page" suffix for routing
        # e.g., "user-profile-page"
        route_path = kebab_case_name
        if not route_path.endswith('-page'):
            route_path = route_path
        
        # Generate routing snippets
        routing_import = f"import {{ {pascal_case_name} }} from './pages/{kebab_case_name}/{kebab_case_name}.component';"
        
        routing_route = f"""{{
  path: '{route_path}',
  component: {pascal_case_name}
}}"""
        
        # Generate sidebar snippets
        sidebar_import = f"import {{ {pascal_case_name} }} from './pages/{kebab_case_name}/{kebab_case_name}.component';"
        sidebar_declaration = pascal_case_name
        
        return {
            "status": "success",
            "snippets": {
                "routing": {
                    "import": routing_import,
                    "route": routing_route
                },
                "sidebar": {
                    "import": sidebar_import,
                    "declaration": sidebar_declaration
                }
            }
        }
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {
            "status": "error",
            "message": str(e),
            "snippets": {
                "routing": {
                    "import": "Error generating snippets",
                    "route": "Error generating snippets"
                },
                "sidebar": {
                    "import": "Error generating snippets",
                    "declaration": "Error generating snippets"
                }
            }
        }
