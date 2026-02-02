import json
from pathlib import Path
from typing import Dict, Optional, Any
from datetime import datetime, timezone

CURRENT_PAGE_CONTEXT_FILE = Path(__file__).parent.parent / "config" / "current_page_context.json"
PAGE_REQUEST_FILE = Path("current_page_request.txt")

class WorkspaceService:
    def load_state(self) -> Optional[Dict[str, Any]]:
        if not CURRENT_PAGE_CONTEXT_FILE.exists():
            return None
        try:
            with open(CURRENT_PAGE_CONTEXT_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading workspace state: {e}")
            return None

    def save_state(self, html: str, scss: str, ts: str, user_request: str = "") -> bool:
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
            return True
        except Exception as e:
            print(f"Error saving workspace state: {e}")
            return False

    def clear_state(self) -> bool:
        try:
            if CURRENT_PAGE_CONTEXT_FILE.exists():
                CURRENT_PAGE_CONTEXT_FILE.unlink()
            if PAGE_REQUEST_FILE.exists():
                PAGE_REQUEST_FILE.unlink()
            return True
        except Exception as e:
             print(f"Error clearing workspace state: {e}")
             return False

    def save_page_request(self, request: str) -> None:
        PAGE_REQUEST_FILE.write_text(request, encoding='utf-8')

    def load_page_request(self) -> str:
        if PAGE_REQUEST_FILE.exists():
            return PAGE_REQUEST_FILE.read_text(encoding='utf-8')
        return ""
