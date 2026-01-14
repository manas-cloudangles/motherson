"""
FastAPI Server for Angular Page Generator

This server provides REST API endpoints for the frontend to:
1. Upload components directory and generate metadata
2. Select components for a page request
3. Generate page code (HTML, SCSS, TypeScript)

Features:
- Automatic OpenAPI/Swagger documentation at /docs
- Native async/await support for better performance
- Type validation with Pydantic models
- Optimized for production scaling
"""

import os
import json
from pathlib import Path
from typing import List, Dict, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from component_metadata_pipeline import ComponentMetadataPipeline
from page_generation_pipeline import PageGenerationPipeline
from component_selector import select_components_for_request, get_selected_components_with_metadata


# Pydantic Models for Request/Response validation
class UploadAndAnalyzeRequest(BaseModel):
    folderPath: str
    pageRequest: str

class ComponentSelectRequest(BaseModel):
    pageRequest: str

class ComponentSelectResponse(BaseModel):
    status: str
    all_components: List[Dict]
    selected_component_ids: List[str]
    reasoning: Dict[str, str]
    selected_components: List[Dict]

class GeneratePageRequest(BaseModel):
    pageRequest: str
    selectedComponentIds: Optional[List[str]] = []

class GeneratePageResponse(BaseModel):
    status: str
    html_code: str
    scss_code: str
    ts_code: str
    component_name: str
    path_name: str
    selector: str

class HealthResponse(BaseModel):
    status: str
    message: str

class ResetResponse(BaseModel):
    status: str
    message: str


# Initialize FastAPI app
app = FastAPI(
    title="Angular Page Generator API",
    description="API for generating Angular components with LLM assistance",
    version="2.0.0",
    docs_url="/docs",  # Swagger UI
    redoc_url="/redoc"  # ReDoc UI
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# File-based storage paths
METADATA_STORAGE_FILE = Path("component_metadata.json")
PAGE_REQUEST_FILE = Path("current_page_request.txt")


def load_metadata() -> List[Dict]:
    """Load component metadata from file"""
    if METADATA_STORAGE_FILE.exists():
        with open(METADATA_STORAGE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []


def save_metadata(metadata: List[Dict]) -> None:
    """Save component metadata to file"""
    with open(METADATA_STORAGE_FILE, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    print(f"✓ Saved metadata to: {METADATA_STORAGE_FILE.absolute()}")


def load_page_request() -> str:
    """Load current page request from file"""
    if PAGE_REQUEST_FILE.exists():
        return PAGE_REQUEST_FILE.read_text(encoding='utf-8')
    return ""


def save_page_request(request: str) -> None:
    """Save page request to file"""
    PAGE_REQUEST_FILE.write_text(request, encoding='utf-8')


@app.get('/api/health', response_model=HealthResponse, tags=["System"])
async def health_check():
    """Health check endpoint to verify API is running"""
    return {"status": "ok", "message": "API is running"}


@app.post('/api/upload-and-analyze', tags=["Components"])
async def upload_and_analyze(request_data: UploadAndAnalyzeRequest):
    """
    Analyze components from a local folder path.
    
    - **folderPath**: Absolute path to the components directory
    - **pageRequest**: User's page generation request
    
    Returns component metadata for all analyzed components.
    """
    try:
        folder_path = Path(request_data.folderPath)
        
        if not request_data.pageRequest:
            raise HTTPException(status_code=400, detail="Page request is required")
        
        if not request_data.folderPath:
            raise HTTPException(status_code=400, detail="Folder path is required")
        
        # Validate folder exists
        if not folder_path.exists():
            raise HTTPException(status_code=400, detail=f"Folder path does not exist: {folder_path}")
        
        if not folder_path.is_dir():
            raise HTTPException(status_code=400, detail=f"Path is not a directory: {folder_path}")
        
        print(f"\n✓ Analyzing components from: {folder_path}")
        print(f"✓ Page request: {request_data.pageRequest[:100]}...")
        
        # Save page request to file
        save_page_request(request_data.pageRequest)
        
        # Generate component metadata directly from the provided path
        print("\nGenerating component metadata...")
        
        pipeline = ComponentMetadataPipeline(
            components_dir=folder_path,
            save_to_file=True,  # Save to file instead of memory
            output_json_file=METADATA_STORAGE_FILE
        )
        
        # Native async - no event loop needed!
        metadata = await pipeline.run()
        
        if not metadata:
            raise HTTPException(status_code=500, detail="Failed to generate component metadata")
        
        print(f"✓ Generated metadata for {len(metadata)} components")
        
        # Return components to frontend
        return {
            "status": "success",
            "components": metadata,
            "message": f"Analyzed {len(metadata)} components successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error in upload_and_analyze: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post('/api/select-components', response_model=ComponentSelectResponse, tags=["Components"])
async def select_components(request_data: ComponentSelectRequest):
    """
    Use LLM to determine which components are needed for the page request.
    
    - **pageRequest**: User's page generation request
    
    Returns selected component IDs, reasoning, and full metadata.
    """
    try:
        page_request = request_data.pageRequest or load_page_request()
        
        if not page_request:
            raise HTTPException(status_code=400, detail="Page request is required")
        
        # Load metadata from file
        component_metadata = load_metadata()
        
        if not component_metadata:
            raise HTTPException(
                status_code=400, 
                detail="No component metadata available. Please upload components first."
            )
        
        print(f"\n{'='*60}")
        print("SELECTING COMPONENTS FOR REQUEST")
        print(f"{'='*60}")
        print(f"Request: {page_request[:100]}...")
        print(f"Loaded {len(component_metadata)} components from file")
        
        # Native async - no event loop needed!
        selection_data = await select_components_for_request(page_request, component_metadata)
        
        if not selection_data:
            raise HTTPException(status_code=500, detail="Failed to select components")
        
        # Get full metadata for selected components
        selected_components = get_selected_components_with_metadata(
            selection_data,
            component_metadata
        )
        
        print(f"✓ Selected {len(selected_components)} components")
        
        return {
            "status": "success",
            "all_components": component_metadata,
            "selected_component_ids": selection_data['selected_components'],
            "reasoning": selection_data['reasoning'],
            "selected_components": selected_components
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error in select_components: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post('/api/generate-page', response_model=GeneratePageResponse, tags=["Generation"])
async def generate_page(request_data: GeneratePageRequest):
    """
    Generate Angular page code (HTML, SCSS, TypeScript).
    
    - **pageRequest**: User's page generation request
    - **selectedComponentIds**: Optional list of component IDs to use
    
    Returns generated HTML, SCSS, and TypeScript code.
    """
    try:
        page_request = request_data.pageRequest or load_page_request()
        selected_ids = request_data.selectedComponentIds or []
        
        if not page_request:
            raise HTTPException(status_code=400, detail="Page request is required")
        
        # Load metadata from file
        component_metadata = load_metadata()
        
        if not component_metadata:
            raise HTTPException(
                status_code=400,
                detail="No component metadata available. Please upload components first."
            )
        
        # Filter metadata to only include selected components if provided
        metadata_to_use = component_metadata
        if selected_ids:
            metadata_to_use = [
                comp for comp in component_metadata
                if comp.get('id_name') in selected_ids or comp.get('name') in selected_ids
            ]
            print(f"Using {len(metadata_to_use)} selected components")
        
        print(f"\n{'='*60}")
        print("GENERATING PAGE")
        print(f"{'='*60}")
        print(f"Request: {page_request[:100]}...")
        print(f"Loaded {len(component_metadata)} components from file")
        
        # Native async - no event loop needed!
        pipeline = PageGenerationPipeline(component_metadata=metadata_to_use)
        page_data = await pipeline.generate_page(page_request)
        
        if not page_data:
            raise HTTPException(status_code=500, detail="Failed to generate page")
        
        print(f"✓ Generated page: {page_data['component_name']}")
        
        return {
            "status": "success",
            "html_code": page_data['html_code'],
            "scss_code": page_data['scss_code'],
            "ts_code": page_data['ts_code'],
            "component_name": page_data['component_name'],
            "path_name": page_data['path_name'],
            "selector": page_data['selector']
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error in generate_page: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post('/api/reset', response_model=ResetResponse, tags=["System"])
async def reset_session():
    """Reset the server session state and clear stored files"""
    # Delete metadata file
    if METADATA_STORAGE_FILE.exists():
        METADATA_STORAGE_FILE.unlink()
    
    # Delete page request file
    if PAGE_REQUEST_FILE.exists():
        PAGE_REQUEST_FILE.unlink()
    
    return {"status": "success", "message": "Session reset - all stored data cleared"}


if __name__ == '__main__':
    import uvicorn
    
    print("\n" + "="*60)
    print("ANGULAR PAGE GENERATOR API SERVER (FastAPI)")
    print("="*60)
    print("\nEndpoints:")
    print("  POST /api/upload-and-analyze  - Analyze components from folder path")
    print("  POST /api/select-components   - Select components for page request")
    print("  POST /api/generate-page       - Generate page code")
    print("  POST /api/reset               - Reset session")
    print("  GET  /api/health              - Health check")
    print("\nDocumentation:")
    print("  📖 Swagger UI:  http://localhost:5000/docs")
    print("  📖 ReDoc:       http://localhost:5000/redoc")
    print("\nServer starting on http://localhost:5000")
    print("="*60 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=5000, log_level="info")
