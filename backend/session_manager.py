import json
from pathlib import Path
from typing import Dict, Optional, Any
from datetime import datetime, timezone

# File to store the current page context
CURRENT_PAGE_CONTEXT_FILE = Path("current_page_context.json")

def load_session() -> Optional[Dict[str, Any]]:
    """
    Load the current page context from file.
    
    Returns:
        Dict or None: The session data including current_state and last_user_request
    """
    if not CURRENT_PAGE_CONTEXT_FILE.exists():
        return None
        
    try:
        with open(CURRENT_PAGE_CONTEXT_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Error loading session: {e}")
        return None

def save_session(
    html: str, 
    scss: str, 
    ts: str, 
    user_request: str = ""
) -> bool:
    """
    Save the current page context to file.
    Overwrite the file with new state.
    
    Args:
        html: Current HTML code
        scss: Current SCSS code
        ts: Current TypeScript code
        user_request: The last user request (or original prompt)
        
    Returns:
        bool: True if successful
    """
    session_data = {
        "last_updated": datetime.now(timezone.utc).isoformat(),
        "current_state": {
            "html": html,
            "scss": scss,
            "ts": ts
        },
        "last_user_request": user_request
    }
    
    try:
        with open(CURRENT_PAGE_CONTEXT_FILE, 'w', encoding='utf-8') as f:
            json.dump(session_data, f, indent=2, ensure_ascii=False)
        print(f"✓ Saved session context to: {CURRENT_PAGE_CONTEXT_FILE.absolute()}")
        return True
    except Exception as e:
        print(f"❌ Error saving session: {e}")
        return False

def clear_session() -> bool:
    """
    Delete the current page context file.
    
    Returns:
        bool: True if successful
    """
    if CURRENT_PAGE_CONTEXT_FILE.exists():
        try:
            CURRENT_PAGE_CONTEXT_FILE.unlink()
            print(f"✓ Cleared session context file")
            return True
        except Exception as e:
            print(f"❌ Error clearing session: {e}")
            return False
    return True
