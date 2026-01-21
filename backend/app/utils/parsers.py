import re
import json

def extract_json_from_response(response_text: str) -> str:
    """
    Extract JSON object from a text that might contain markdown or other text.
    Handles basic cleaning.
    """
    if not response_text:
        return ""
    
    # 1. Try to find JSON in code blocks
    code_block_pattern = r"```(?:json)?\s*(\{.*?\})\s*```"
    match = re.search(code_block_pattern, response_text, re.DOTALL)
    if match:
        return match.group(1)
        
    # 2. Try to find the first '{' and last '}'
    start_idx = response_text.find('{')
    end_idx = response_text.rfind('}')
    
    if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
        return response_text[start_idx:end_idx+1]
        
    # 3. If it looks like JSON already, return it
    if response_text.strip().startswith('{') and response_text.strip().endswith('}'):
        return response_text.strip()
        
    return response_text

def to_kebab_case(s: str) -> str:
    return re.sub(r'(?<!^)(?=[A-Z])', '-', s).lower().replace(' ', '-')

def to_pascal_case(s: str) -> str:
    return ''.join(x.title() for x in s.replace('-', ' ').replace('_', ' ').split())
