"""
Utility functions for the Angular Page Generator backend.

Contains helper functions for string manipulation, file operations, etc.
"""

import re
from pathlib import Path
from typing import List, Dict, Any


def to_kebab_case(text: str) -> str:
    """
    Convert text to kebab-case.
    
    Examples:
        'Sample Program' -> 'sample-program'
        'SampleProgram' -> 'sample-program'
        'sample_program' -> 'sample-program'
    
    Args:
        text: Input text to convert
        
    Returns:
        str: Kebab-case formatted string
    """
    # Replace spaces and underscores with hyphens, convert to lowercase
    text = re.sub(r'[_\s]+', '-', text)
    # Insert hyphens between camelCase transitions
    text = re.sub(r'([a-z0-9])([A-Z])', r'\1-\2', text)
    return text.lower().strip('-')


def to_pascal_case(text: str) -> str:
    """
    Convert text to PascalCase.
    
    Examples:
        'sample program' -> 'SampleProgram'
        'sample-program' -> 'SampleProgram'
        'sample_program' -> 'SampleProgram'
    
    Args:
        text: Input text to convert
        
    Returns:
        str: PascalCase formatted string
    """
    words = re.split(r'[_\s-]+', text)
    return ''.join(word.capitalize() for word in words if word)


def to_camel_case(text: str) -> str:
    """
    Convert text to camelCase.
    
    Examples:
        'sample program' -> 'sampleProgram'
        'sample-program' -> 'sampleProgram'
    
    Args:
        text: Input text to convert
        
    Returns:
        str: camelCase formatted string
    """
    pascal = to_pascal_case(text)
    return pascal[0].lower() + pascal[1:] if pascal else ''


def read_file_safe(file_path: Path, encoding: str = 'utf-8') -> str:
    """
    Safely read a file with error handling.
    
    Args:
        file_path: Path to the file
        encoding: File encoding (default: utf-8)
        
    Returns:
        str: File contents or empty string if error
    """
    try:
        with open(file_path, 'r', encoding=encoding) as f:
            return f.read()
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return ""


def write_file_safe(file_path: Path, content: str, encoding: str = 'utf-8') -> bool:
    """
    Safely write content to a file with error handling.
    
    Args:
        file_path: Path to the file
        content: Content to write
        encoding: File encoding (default: utf-8)
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Create parent directories if they don't exist
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'w', encoding=encoding) as f:
            f.write(content)
        return True
    except Exception as e:
        print(f"Error writing to {file_path}: {e}")
        return False


def read_component_files(component_dir: Path, extensions: List[str] = None) -> Dict[str, str]:
    """
    Read all relevant files in a component directory.
    
    Args:
        component_dir: Path to the component directory
        extensions: List of file extensions to include (e.g., ['.ts', '.html', '.scss'])
                   If None, defaults to ['.ts', '.html', '.scss']
        
    Returns:
        dict: Dictionary mapping file names to their contents
    """
    if extensions is None:
        extensions = ['.ts', '.html', '.scss']
    
    files_content = {}
    
    if not component_dir.exists() or not component_dir.is_dir():
        return files_content
    
    for file_path in component_dir.iterdir():
        if file_path.is_file():
            # Skip spec files
            if '.spec.' in file_path.name:
                continue
            
            if file_path.suffix in extensions:
                content = read_file_safe(file_path)
                if content:
                    files_content[file_path.name] = content
    
    return files_content


def format_progress_bar(current: int, total: int, width: int = 50) -> str:
    """
    Create a simple text progress bar.
    
    Args:
        current: Current progress value
        total: Total/maximum value
        width: Width of the progress bar in characters
        
    Returns:
        str: Formatted progress bar string
    """
    if total == 0:
        return "[" + " " * width + "] 0%"
    
    percentage = min(100, int((current / total) * 100))
    filled = int((current / total) * width)
    bar = "=" * filled + " " * (width - filled)
    
    return f"[{bar}] {percentage}%"


def extract_json_from_response(response: str) -> str:
    """
    Extract JSON content from LLM response that might be wrapped in markdown code blocks.
    
    Args:
        response: Raw response text from LLM
        
    Returns:
        str: Extracted JSON string
    """
    response_text = response.strip()
    
    # Check if wrapped in markdown code blocks
    if response_text.startswith("```"):
        lines = response_text.split('\n')
        
        # Find the JSON content between code fences
        json_start = 1
        json_end = len(lines) - 1
        
        # Skip the first line (```json or ```)
        for i, line in enumerate(lines):
            if i > 0 and line.strip() and not line.strip().startswith('```'):
                json_start = i
                break
        
        # Find the closing ```
        for i in range(len(lines) - 1, 0, -1):
            if lines[i].strip().startswith('```'):
                json_end = i
                break
        
        response_text = '\n'.join(lines[json_start:json_end])
    
    return response_text


def generate_component_selector(path_name: str) -> str:
    """
    Generate Angular component selector from path name.
    
    Args:
        path_name: Component path name in kebab-case
        
    Returns:
        str: Angular selector (e.g., 'app-sample-program')
    """
    return f"app-{path_name}"


def generate_import_path(component_dir: Path, base_dir: Path) -> str:
    """
    Generate the Angular import path for a component.
    
    Args:
        component_dir: Path to the component directory
        base_dir: Base directory for relative path calculation
        
    Returns:
        str: Import path (e.g., 'app/common/components/app-button/app-button.component')
    """
    rel_path = component_dir.relative_to(base_dir)
    # Convert Windows path to forward slashes
    import_path = str(rel_path).replace('\\', '/')
    
    # Add component filename (assuming standard naming convention)
    component_name = component_dir.name
    return f"{import_path}/{component_name}.component"


if __name__ == "__main__":
    # Test utilities
    print("Testing utility functions:")
    print("=" * 60)
    
    test_cases = [
        "Sample Program",
        "SampleProgram",
        "sample_program",
        "sample-program"
    ]
    
    for test in test_cases:
        print(f"\nInput: '{test}'")
        print(f"  Kebab-case: {to_kebab_case(test)}")
        print(f"  PascalCase: {to_pascal_case(test)}")
        print(f"  camelCase: {to_camel_case(test)}")
        print(f"  Selector: {generate_component_selector(to_kebab_case(test))}")
    
    print("\n" + "=" * 60)
    print("\nProgress bar examples:")
    for i in range(0, 101, 20):
        print(f"{i}/100: {format_progress_bar(i, 100)}")
