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
import shutil
import tempfile
from pathlib import Path
from typing import List, Dict, Optional
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from component_metadata_pipeline import ComponentMetadataPipeline
from page_generation_pipeline import PageGenerationPipeline
from component_selector import (
    select_components_for_request, 
    get_selected_components_with_metadata,
    update_component_metadata_with_selection
)
from session_manager import save_session, load_session, clear_session
from get_secrets import run_model
from utils import extract_json_from_response


# Pydantic Models for Request/Response validation
# Note: UploadAndAnalyzeRequest is now handled via FormData, not JSON

class ComponentSelectRequest(BaseModel):
    pageRequest: str

class ComponentSelectResponse(BaseModel):
    status: str
    all_components: List[Dict]
    selected_component_ids: List[str]
    reasoning: Dict[str, str]
    selected_components: List[Dict]

class UpdateComponentMetadataRequest(BaseModel):
    components: List[Dict]  # List of components with updated required and reasoning fields

class UpdateComponentMetadataResponse(BaseModel):
    status: str
    message: str

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
class ResetResponse(BaseModel):
    status: str
    message: str

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    status: str
    html_code: str
    scss_code: str
    ts_code: str
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
async def upload_and_analyze(
    files: List[UploadFile] = File(...),
    pageRequest: str = Form(...)
):
    """
    Analyze components from uploaded files.
    
    - **files**: List of uploaded files from the components directory
    - **pageRequest**: User's page generation request
    
    Returns component metadata for all analyzed components.
    """
    temp_dir = None
    try:
        if not pageRequest or not pageRequest.strip():
            raise HTTPException(status_code=400, detail="Page request is required")
        
        if not files or len(files) == 0:
            raise HTTPException(status_code=400, detail="No files uploaded")
        
        print(f"\n✓ Received {len(files)} files")
        print(f"✓ Page request: {pageRequest[:100]}...")
        
        # Save page request to file
        save_page_request(pageRequest)
        
        # Create temporary directory to store uploaded files
        temp_dir = Path(tempfile.mkdtemp(prefix="angular_components_"))
        print(f"✓ Created temporary directory: {temp_dir}")
        
        # Save all uploaded files maintaining directory structure
        for file in files:
            # The filename contains the relative path (sent from frontend)
            relative_path = file.filename
            if not relative_path:
                continue
            
            # Create full path in temp directory
            file_path = temp_dir / relative_path
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write file content
            content = await file.read()
            file_path.write_bytes(content)
        
        print(f"✓ Saved {len(files)} files to temporary directory")
        
        # Generate component metadata from the temporary directory
        print("\nGenerating component metadata...")
        
        pipeline = ComponentMetadataPipeline(
            components_dir=temp_dir,
            save_to_file=True,  # Save to file instead of memory
            output_json_file=METADATA_STORAGE_FILE
        )
        
        # Native async - no event loop needed!
        metadata = await pipeline.run()
        
        if not metadata:
            raise HTTPException(
                status_code=500, 
                detail="Failed to generate component metadata. No components were successfully processed. Check that component directories contain .ts, .html, or .scss files."
            )
        
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
    finally:
        # Clean up temporary directory
        if temp_dir and temp_dir.exists():
            try:
                shutil.rmtree(temp_dir)
                print(f"✓ Cleaned up temporary directory: {temp_dir}")
            except Exception as e:
                print(f"⚠ Warning: Could not clean up temp directory: {e}")


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
        
        # Update component metadata with required and reasoning fields based on LLM selection
        updated_metadata = update_component_metadata_with_selection(
            selection_data,
            component_metadata
        )
        
        # Save updated metadata back to file
        save_metadata(updated_metadata)
        print(f"✓ Updated component metadata with required/reasoning fields")
        
        # Get full metadata for selected components
        selected_components = get_selected_components_with_metadata(
            selection_data,
            updated_metadata
        )
        
        print(f"✓ Selected {len(selected_components)} components")
        
        return {
            "status": "success",
            "all_components": updated_metadata,
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

@app.post('/api/update-component-metadata', response_model=UpdateComponentMetadataResponse, tags=["Components"])
async def update_component_metadata(request_data: UpdateComponentMetadataRequest):
    """
    Update component metadata with user's manual changes (required and reasoning fields).
    
    - **components**: List of component metadata with updated required and reasoning fields
    
    This endpoint is called when the user manually changes component preferences on the 2nd page.
    """
    try:
        if not request_data.components:
            raise HTTPException(status_code=400, detail="Components list is required")
        
        # Validate that all components have required fields
        for comp in request_data.components:
            if 'name' not in comp:
                raise HTTPException(status_code=400, detail="All components must have a 'name' field")
            if 'required' not in comp:
                raise HTTPException(status_code=400, detail="All components must have a 'required' field")
            if 'reasoning' not in comp:
                raise HTTPException(status_code=400, detail="All components must have a 'reasoning' field")
        
        # Save updated metadata to file
        save_metadata(request_data.components)
        
        # Log detailed information about what was saved
        required_components = [c for c in request_data.components if c.get('required', False) is True]
        not_required_components = [c for c in request_data.components if c.get('required', False) is not True]
        
        print(f"✓ Updated component metadata: {len(request_data.components)} components")
        print(f"  Required components ({len(required_components)}): {[c.get('id_name') or c.get('id') or c.get('name') for c in required_components]}")
        print(f"  Not required components ({len(not_required_components)}): {[c.get('id_name') or c.get('id') or c.get('name') for c in not_required_components]}")
        
        # Verify the saved data
        for comp in request_data.components:
            comp_id = comp.get('id_name') or comp.get('id') or comp.get('name', 'Unknown')
            required_status = comp.get('required', False)
            print(f"    - {comp_id}: required={required_status} (type: {type(required_status).__name__})")
        
        return {
            "status": "success",
            "message": f"Successfully updated metadata for {len(request_data.components)} components"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error updating component metadata: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post('/api/generate-page', response_model=GeneratePageResponse, tags=["Generation"])
async def generate_page(request_data: GeneratePageRequest):
    """
    Generate Angular page code (HTML, SCSS, TypeScript).
    
    - **pageRequest**: User's page generation request (from 1st page)
    - **selectedComponentIds**: Optional list of component IDs (deprecated - now uses required:true from metadata)
    
    Returns generated HTML, SCSS, and TypeScript code.
    
    This endpoint uses:
    1. The page request from the 1st page
    2. Only components with required:true from component_metadata.json (updated in 2nd page)
    """
    try:
        page_request = request_data.pageRequest or load_page_request()
        
        if not page_request:
            raise HTTPException(status_code=400, detail="Page request is required")
        
        # Load metadata from file (this should have the updated required/reasoning from 2nd page)
        component_metadata = load_metadata()
        
        if not component_metadata:
            raise HTTPException(
                status_code=400,
                detail="No component metadata available. Please upload components first."
            )
        
        # Filter metadata to only include components with required:true
        # This ensures we use the components selected by LLM and/or manually updated by user in 2nd page
        # IMPORTANT: User can manually set required=false even if AI selected it, and we must respect that
        metadata_to_use = []
        excluded_components = []
        
        for comp in component_metadata:
            required_value = comp.get('required', False)
            comp_id = comp.get('id_name') or comp.get('id') or comp.get('name', 'Unknown')
            
            # Explicitly check for True (handle both boolean True and string "true")
            # This ensures user's manual deselection (required=false) is always respected
            is_required = False
            if isinstance(required_value, bool):
                is_required = required_value is True
            elif isinstance(required_value, str):
                is_required = required_value.lower() == 'true'
            else:
                is_required = bool(required_value) and required_value is not False
            
            if is_required:
                metadata_to_use.append(comp)
            else:
                excluded_components.append(comp_id)
        
        if not metadata_to_use:
            raise HTTPException(
                status_code=400,
                detail="No required components found. Please select components in the elements page first."
            )
        
        print(f"\n{'='*60}")
        print("GENERATING PAGE")
        print(f"{'='*60}")
        print(f"Request: {page_request[:100]}...")
        print(f"Loaded {len(component_metadata)} total components from file")
        print(f"Using {len(metadata_to_use)} required components (required:true)")
        
        if excluded_components:
            print(f"Excluded {len(excluded_components)} components (required=false): {', '.join(excluded_components)}")
        
        # Log which components are being used
        for comp in metadata_to_use:
            comp_id = comp.get('id_name') or comp.get('id') or comp.get('name', 'Unknown')
            reasoning = comp.get('reasoning', '')
            print(f"  ✓ {comp_id}: {reasoning[:50]}..." if reasoning else f"  ✓ {comp_id}")
        
        # Native async - no event loop needed!
        pipeline = PageGenerationPipeline(component_metadata=metadata_to_use)
        page_data = await pipeline.generate_page(page_request)
        
        if not page_data:
            raise HTTPException(status_code=500, detail="Failed to generate page")
            
        # Save to session context
        save_session(
            page_data['html_code'],
            page_data['scss_code'],
            page_data['ts_code'],
            page_request
        )
        
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


@app.post('/api/chat', response_model=ChatResponse, tags=["Chat"])
async def chat_with_page(request_data: ChatRequest):
    """
    Chat with the current page to make edits.
    
    - **message**: User's request (e.g., "Make the button blue")
    
    Returns updated HTML, SCSS, and TypeScript code.
    """
    try:
        user_message = request_data.message
        if not user_message:
            raise HTTPException(status_code=400, detail="Message is required")
            
        # Load current session
        session = load_session()
        if not session:
            raise HTTPException(
                status_code=400, 
                detail="No active session found. Please generate a page first."
            )
            
        current_state = session.get('current_state', {})
        html = current_state.get('html', '')
        scss = current_state.get('scss', '')
        ts = current_state.get('ts', '')
        
        if not html:
            raise HTTPException(status_code=400, detail="Current session has no code to edit")
            
        print(f"\\n{'='*60}")
        print(f"CHAT REQUEST: {user_message}")
        print(f"{'='*60}")
        
        # Construct prompt for the LLM
        system_prompt = """You are an expert Angular developer.
You have the current state of an Angular component (HTML, SCSS, TS).
Your task is to modify this code based on the user's request.

CRITICAL INSTRUCTIONS:
1. Return ONLY the modified code in a JSON format.
2. Do NOT explain your changes.
3. Keep the existing functionality unless asked to change it.
4. Use the existing component structure.

REQUIRED JSON STRUCTURE:
{
  "html_code": "modified HTML...",
  "scss_code": "modified SCSS...",
  "ts_code": "modified TypeScript..."
}
"""

        user_prompt = f"""
CURRENT CODE:

--- HTML ---
{html}

--- SCSS ---
{scss}

--- TYPESCRIPT ---
{ts}

USER REQUEST:
{user_message}

Please modify the code to satisfy the user's request.
"""

        print("⏳ Calling LLM for edits...")
        response = await run_model(system_prompt=system_prompt, user_message=user_prompt)
        
        # Parse response
        response_text = extract_json_from_response(response)
        if not response_text:
            raise HTTPException(status_code=500, detail="Failed to parse LLM response")
            
        data = json.loads(response_text)
        
        new_html = data.get('html_code', html)
        new_scss = data.get('scss_code', scss)
        new_ts = data.get('ts_code', ts)
        
        # Update session
        save_session(new_html, new_scss, new_ts, user_message)
        
        return {
            "status": "success",
            "html_code": new_html,
            "scss_code": new_scss,
            "ts_code": new_ts,
            "message": "Successfully updated code"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error in chat_with_page: {e}")
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
        
    # Clear session context
    clear_session()
    
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
