"""
Configuration module for the Angular Page Generator backend.

Contains paths, constants, and settings used across the application.
"""

from pathlib import Path
import os

# Base directory - the root of the project
BASE_DIR = Path(__file__).parent.parent

# Angular project paths
SRC_DIR = BASE_DIR / "src" / "app"
COMPONENTS_DIR = SRC_DIR / "common" / "components"
MASTER_DIR = SRC_DIR / "master"
MASTER_MODULE_FILE = MASTER_DIR / "master.module.ts"
LOGS_DIR = SRC_DIR / "logs"
RECORD_DIR = SRC_DIR / "record"

# Output files
COMPONENT_METADATA_FILE = BASE_DIR / "component_metadata.json"
COMPONENT_README_FILE = BASE_DIR / "COMPONENT_METADATA_README.md"

# LLM Configuration
# These can be overridden by environment variables
LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "35000"))
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.3"))
LLM_REGION = os.getenv("AWS_REGION", "us-east-1")
AWS_PROFILE = os.getenv("AWS_PROFILE", "cloudangles-mlops")

# File extensions to process
COMPONENT_FILE_EXTENSIONS = ['.ts', '.html', '.scss']
EXCLUDE_PATTERNS = ['*.spec.ts', '*.spec.js', 'node_modules', 'dist']

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

def validate_paths():
    """
    Validate that all required paths exist.
    
    Returns:
        tuple: (is_valid, error_messages)
    """
    errors = []
    
    if not COMPONENTS_DIR.exists():
        errors.append(f"Components directory not found: {COMPONENTS_DIR}")
    
    if not MASTER_DIR.exists():
        errors.append(f"Master directory not found: {MASTER_DIR}")
    
    if not MASTER_MODULE_FILE.exists():
        errors.append(f"Master module file not found: {MASTER_MODULE_FILE}")
    
    return (len(errors) == 0, errors)


if __name__ == "__main__":
    # Test configuration
    is_valid, errors = validate_paths()
    
    print("Configuration Test")
    print("=" * 60)
    print(f"BASE_DIR: {BASE_DIR}")
    print(f"COMPONENTS_DIR: {COMPONENTS_DIR}")
    print(f"MASTER_DIR: {MASTER_DIR}")
    print(f"MASTER_MODULE_FILE: {MASTER_MODULE_FILE}")
    print(f"\nPath validation: {'✓ PASSED' if is_valid else '❌ FAILED'}")
    
    if errors:
        print("\nErrors:")
        for error in errors:
            print(f"  - {error}")
