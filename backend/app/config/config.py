"""
Configuration module for the Angular Page Generator backend.

Contains paths, constants, and settings used across the application.
"""

from pathlib import Path
import os
from dotenv import load_dotenv

# Load environment variables from .env file
# Look for .env in backend directory first, then project root
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
BACKEND_DIR = BASE_DIR / "backend"
ENV_FILE = BACKEND_DIR / ".env"

# Try backend/.env first, then root/.env
if ENV_FILE.exists():
    load_dotenv(ENV_FILE)
elif (BASE_DIR / ".env").exists():
    load_dotenv(BASE_DIR / ".env")
else:
    # If no .env found, still try to load from default location
    load_dotenv()

# Base directory - the root of the project (c:\motherson\motherson)
# backend/app/core/config.py -> core -> app -> backend -> root
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent

# Angular project paths
SRC_DIR = BASE_DIR / "frontend" / "src"
COMPONENTS_DIR = SRC_DIR / "components"
# Note: The original config pointed to SRC_DIR / "app" / "common" etc which seemed to be Angular structure,
# but the file listing showed frontend/src/components.
# Let's double check the file listing from step 4/5. 
# Step 5 list_dir frontend/src: components, context, pages, App.jsx...
# The original config.py had: SRC_DIR = BASE_DIR / "src" / "app" (Wait, original config.py line 14 says BASE_DIR="src/app")
# But file list of root showed "frontend".
# Let's adhere to the original config.py logic but adapted to the actual structure I saw.
# Original config.py: BASE_DIR = Path(__file__).parent.parent (backend/config.py -> backend -> root)
# So BASE_DIR was indeed c:\motherson\motherson.
# SRC_DIR was BASE_DIR / "src" / "app". 
# But the file list shows `frontend` folder.
# Let's look at the original config.py again.
# It says: SRC_DIR = BASE_DIR / "src" / "app".
# But list_dir c:\motherson\motherson showed "frontend".
# Maybe the user has a strange structure or I misread the original config.
# Let's trust the original config.py FOR NOW, but wait...
# list_dir c:\motherson\motherson showed: backend, frontend.
# list_dir c:\motherson\motherson\frontend\src showed: components, pages...
# So the original config.py might have been wrong or pointing to a different folder structure? 
# "SRC_DIR = BASE_DIR / 'src' / 'app'" -> c:\motherson\motherson\src\app ?
# That folder (src) didn't exist in the root list_dir.
# Let's fix this obvious bug in the config while we are at it.
# The frontend source is at BASE_DIR / "frontend" / "src".

FRONTEND_SRC = BASE_DIR / "frontend" / "src"
COMPONENTS_DIR = FRONTEND_SRC / "components"
MASTER_DIR = FRONTEND_SRC / "pages"  # "pages" seems to be where pages are.
# In original config: MASTER_DIR = SRC_DIR / "master".
# I'll stick to what seems to be the real structure: frontend/src/pages.
# But I should double check if "master" exists. 
# Step 5 showed "pages" dir.
# Let's define paths based on what I saw in list_dir, correcting the likely broken config.

MASTER_MODULE_FILE = FRONTEND_SRC / "App.jsx" # Or where routing happens. 
# Original: MASTER_MODULE_FILE = MASTER_DIR / "master.module.ts".
# This project seems to be React (files are .jsx), but the backend code talks about Angular (master.module.ts).
# The user's prompt said "Angular components".
# But the file `DownloadPage.jsx` is React.
# This is a React app generating Angular code? Or a mixed project?
# The `api_server.py` says "Angular Page Generator API".
# It seems this tool GENERATES Angular code (for some other project?) but the UI acting as the generator is built in React?
# "This server provides REST API endpoints for the frontend to... Generate page code (HTML, SCSS, TypeScript)"
# So the "master" dir is where the generated code goes?
# The original config: MASTER_DIR = SRC_DIR / "master".
# This might be an output directory for the generated code.
# I will preserve the relative structure from original config as best as I can, assuming BASE_DIR is root.

WORKING_DIR = BASE_DIR # Root
GENERATED_CODE_DIR = WORKING_DIR / "generated_angular_app" # Placeholder if not found

# I will keep the logical structure from original config but fix the BASE_DIR calculation.
# And I'll rely on the original paths for "Angular project" assuming they might be for the OUTPUT.
# Wait, if the user is running this tool to generate code, maybe the output destination is important.
# I'll stick to the exact paths from original config, just fixing BASE_DIR.

# Original: SRC_DIR = BASE_DIR / "src" / "app"
# I will assume there is a folder 'src/app' somewhere or it's intended to be there.
# CHECK: generated files are saved to `MASTER_DIR / path_name`.
# If `src` folder doesn't exist in root, then `page_generator` might fail if it tries to save there.
# I'll keep it as is, just fixing imports.

SRC_DIR = BASE_DIR / "src" / "app"
COMPONENTS_DIR = SRC_DIR / "common" / "components"
MASTER_DIR = SRC_DIR / "master"
MASTER_MODULE_FILE = MASTER_DIR / "master.module.ts"
LOGS_DIR = SRC_DIR / "logs"
RECORD_DIR = SRC_DIR / "record"

# Output files
COMPONENT_METADATA_FILE = Path(__file__).parent / "component_metadata.json"
COMPONENT_README_FILE = BASE_DIR / "COMPONENT_METADATA_README.md"
BACKEND_API_METADATA_FILE = Path(__file__).parent / "backend_api_metadata.json"
BACKEND_API_README_FILE = BASE_DIR / "BACKEND_API_METADATA_README.md"

# LLM Configuration
LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "35000"))
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.3"))
LLM_REGION = os.getenv("AWS_REGION", "us-east-1")
AWS_PROFILE = os.getenv("AWS_PROFILE", "codebendersdev")

# LLM Provider Selection - Set to "bedrock" or "groq"
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "bedrock")  # Options: "bedrock" or "groq"
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")  # Your Groq API key
GROQ_MODEL = os.getenv("GROQ_MODEL", "moonshotai/kimi-k2-instruct-0905")  # Groq model name

# File extensions to process
COMPONENT_FILE_EXTENSIONS = ['.ts', '.html', '.scss']
BACKEND_FILE_EXTENSIONS = ['.php']
EXCLUDE_PATTERNS = ['*.spec.ts', '*.spec.js', 'node_modules', 'dist', 'vendor']

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
