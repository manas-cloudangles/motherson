import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Any

class IntegrationService:
    # Resolve absolute path to the templates file
    # This file is in app/services/, templates are in app/config/
    TEMPLATES_FILE = Path(__file__).parent.parent / "config" / "integration_templates.json"

    def generate_snippets(self, component_name: str) -> Dict[str, Dict[str, str]]:
        """
        Generates integration snippets based on templates.
        """
        try:
            templates = self._load_templates()
            kebab_name = self._to_kebab_case(component_name)
            class_name = component_name.replace(" ", "") + "Component"
            
            snippets = {
                "routing": {},
                "sidebar": {}
            }
            
            # Routing Snippets
            if "routing" in templates:
                snippets["routing"]["import"] = templates["routing"].get("importTemplate", "").replace("{{ClassName}}", class_name).replace("{{kebabName}}", kebab_name)
                snippets["routing"]["route"] = templates["routing"].get("routeTemplate", "").replace("{{ClassName}}", class_name).replace("{{kebabName}}", kebab_name)
                
            # Sidebar Snippets
            if "sidebar" in templates:
                snippets["sidebar"]["import"] = templates["sidebar"].get("importTemplate", "").replace("{{ClassName}}", class_name).replace("{{kebabName}}", kebab_name)
                snippets["sidebar"]["declaration"] = templates["sidebar"].get("declarationTemplate", "").replace("{{ClassName}}", class_name).replace("{{kebabName}}", kebab_name)
                
            return snippets
            
        except Exception as e:
            print(f"Error generating snippets: {e}")
            return {}

    def _load_templates(self) -> Dict[str, Any]:
        try:
            import json
            if self.TEMPLATES_FILE.exists():
                return json.loads(self.TEMPLATES_FILE.read_text(encoding="utf-8"))
            return {}
        except Exception as e:
            print(f"Error loading templates: {e}")
            return {}

    def _to_kebab_case(self, name: str) -> str:
        return "-".join(
            sub.lower() for sub in re.split(r"[\s_]+", name) if sub
        )
