CHAT_SYSTEM_PROMPT = """You are an expert Angular developer.
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

def format_chat_user_prompt(html: str, scss: str, ts: str, user_message: str) -> str:
    return f"""
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
