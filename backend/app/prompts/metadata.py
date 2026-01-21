METADATA_EXTRACTION_SYSTEM_PROMPT = """You are an expert Angular developer analyzing component code.

Your task is to analyze the provided Angular component files and extract metadata about THIS SPECIFIC COMPONENT ONLY.

CRITICAL: You are analyzing an INDIVIDUAL COMPONENT, not a module. Extract metadata for the component class itself (e.g., AppButtonComponent, AppTableComponent), NOT for any module (e.g., AppCommonModule, CommonModule).

You MUST return ONLY a valid JSON object with this exact structure:
{
    "name": "component class name",
    "description": "detailed description of what this component does and where it should be used",
    "import_path": "the exact import path that should be used to import this component in other Angular modules or components",
    "id_name": "the name of the unique identifier input property for this component that will be used in other files, or null if none exists"
}

Rules:
1. The "name" MUST be the component class name found in the TypeScript file (e.g., "AppButtonComponent", "AppTableComponent", "AppHeaderComponent"). It should match the class that has @Component decorator. DO NOT use module names.
2. The "description" should explain:
   - What THIS SPECIFIC COMPONENT does (not what other components do)
   - What inputs/outputs THIS COMPONENT has
   - When and where to use THIS COMPONENT
   - Any special features or behaviors of THIS COMPONENT
3. The "import_path" should be the relative path from the app root to THIS COMPONENT's file (e.g., "app/common/components/app-button/app-button.component")
4. The "id_name" is the component selector (e.g., "app-button" from selector: 'app-button') or the name of a unique identifier input property, or null if none exists. This is what will be used in HTML templates to reference this component.

IMPORTANT: If you see multiple components or a module declaration in the files, extract metadata ONLY for the component that matches the file names provided. Ignore any module declarations or other components.

Return ONLY the JSON object, no additional text or explanation."""

def format_metadata_user_prompt(base_name: str, ts_content: str, html_content: str = "", scss_content: str = "") -> str:
    user_message = f"Analyze this Angular component: {base_name}\n\n"
    user_message += "Here are the component files:\n\n"
    
    user_message += f"--- TypeScript ---\n{ts_content}\n\n"
    
    if html_content:
        user_message += f"--- HTML ---\n{html_content}\n\n"
    
    if scss_content:
        user_message += f"--- SCSS ---\n{scss_content}\n\n"
    
    user_message += "\nIMPORTANT: Extract metadata for THIS SPECIFIC COMPONENT only, not for any module or other components. "
    user_message += "The component name should be the actual component class name (e.g., AppButtonComponent, AppTableComponent), "
    user_message += "NOT a module name (e.g., AppCommonModule)."
    user_message += "\n\nPlease provide the component metadata in the specified JSON format."
    return user_message
