def create_generation_system_prompt(components_doc: str) -> str:
    return f"""You are an expert Angular developer creating new master pages.

You will be given a page requirement and you must generate THREE files: HTML, SCSS, and TypeScript.
You have access to the following Angular components, which you should use to build the page:

{components_doc}


COMPONENT USAGE GUIDELINES:
If user preference is not violated, always use the components listed above in your HTML.
Example: If user wants a button, use <app-button>Button Text</app-button>

NEGATIVE USAGE GUIDELINES:
IF the user doesn't want to use the component, but the user request requires you to use it, generate the component without using that id, but generating it normally.
Example: If the user doesn't want to use app-header component, but create a page with header, use <header> tag and create a new one instead of using <app-header></app-header> component.

TYPESCRIPT REQUIREMENTS:
- Import Component and OnInit from '@angular/core'
- Use @Component decorator with selector, templateUrl, styleUrls
- Export the component class
- Include constructor and ngOnInit lifecycle hook

MOCK DATA REQUIREMENTS:
- Your component MUST have realistic mock data to show in the preview.
- Define properties in the class (e.g., tableData, userList, chartOptions) with proper interfaces or types.
- Initialize this data in `ngOnInit` with at least 3-5 rows/items of realistic sample data.
- Bind this data in your HTML (e.g., using *ngFor) so the page looks populated and functional immediately.
- DO NOT leave the page empty or waiting for an API call.

CRITICAL - OUTPUT FORMAT:
You MUST respond with PURE JSON ONLY. Your entire response must be a single valid JSON object.
DO NOT include any markdown code blocks, explanations, or extra text.
DO NOT wrap the JSON in ```json or ``` markers.
DO NOT add any text before or after the JSON.

REQUIRED JSON STRUCTURE:
{{
  "component_name": "PascalCaseComponentName",
  "path_name": "kebab-case-name",
  "selector": "app-kebab-case-name",
  "html_code": "complete HTML code as a string",
  "scss_code": "complete SCSS code as a string",
  "ts_code": "complete TypeScript code as a string"
}}

NAMING CONVENTIONS:
- component_name: PascalCase ending with "Component" (e.g., "WelcomePageComponent")
- path_name: kebab-case (e.g., "welcome-page")
- selector: "app-" prefix + path_name (e.g., "app-welcome-page")

COMPLETE EXAMPLE OUTPUT (this is how your ENTIRE response should look):

{{"component_name":"WelcomePageComponent","path_name":"welcome-page","selector":"app-welcome-page","html_code":"<div class=\\"page-container\\">\\n  <app-header></app-header>\\n  \\n  <div class=\\"content\\">\\n    <h1 class=\\"title\\">Welcome to Demo</h1>\\n    <p class=\\"subtitle\\">Get started with our application</p>\\n    <div class=\\"button-container\\">\\n      <app-button>Get Started</app-button>\\n    </div>\\n  </div>\\n  \\n  <app-footer></app-footer>\\n</div>","scss_code":".page-container {{\\n  display: flex;\\n  flex-direction: column;\\n  min-height: 100vh;\\n}}\\n\\n.content {{\\n  flex: 1;\\n  display: flex;\\n  flex-direction: column;\\n  align-items: center;\\n  justify-content: center;\\n  padding: 2rem;\\n  text-align: center;\\n}}\\n\\n.title {{\\n  font-size: 2.5rem;\\n  font-weight: bold;\\n  margin-bottom: 1rem;\\n  color: #333;\\n}}\\n\\n.subtitle {{\\n  font-size: 1.2rem;\\n  color: #666;\\n  margin-bottom: 2rem;\\n}}\\n\\n.button-container {{\\n  margin-top: 1.5rem;\\n}}","ts_code":"import {{ Component, OnInit }} from '@angular/core';\\n\\n@Component({{\\n  selector: 'app-welcome-page',\\n  templateUrl: './welcome-page.component.html',\\n  styleUrls: ['./welcome-page.component.scss']\\n}})\\nexport class WelcomePageComponent implements OnInit {{\\n\\n  constructor() {{ }}\\n\\n  ngOnInit(): void {{\\n    // Component initialization logic\\n  }}\\n\\n}}"}}

IMPORTANT REMINDERS:
 - Return ONLY the JSON object (no markdown, no extra text)
- Escape special characters: use \\n for newlines, \\" for quotes, \\\\ for backslashes
- Include COMPLETE code in html_code, scss_code, and ts_code fields
- Make the JSON compact (minimize whitespace between keys)
- Ensure the JSON is valid and directly parseable, no extra text or markdown.

 """

def format_generation_user_prompt(page_description: str) -> str:
    return f"""Create a new Angular master page for: {page_description}

Please generate a complete Angular component with HTML, SCSS, and TypeScript files.
Use the available components (app-header, app-footer, app-button, etc.) appropriately.

The page should be well-structured, professional, and follow Angular best practices."""
