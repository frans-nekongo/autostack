from google import genai
import json
from dotenv import load_dotenv

from autostack_engine.utils.constants import TECHNOLOGY_CATALOG

load_dotenv()

client = genai.Client()

json_schema = {
    "type": "object",
    "properties": {
        "project": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "author": {"type": "string"},
                "description": {"type": "string"},
                "version": {"type": "string"},
            },
            "required": ["name", "author", "description"]
        },
        "technologies": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "type": {"type": "string"},
                    "version": {"type": "string"},
                    "environment_variables": {"type": "string"}
                },
                "required": ["name", "type"]
            }
        },
        "components": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "component_id": {"type": "string"},
                    "name": {"type": "string"},
                    "technology": {"type": "string"},
                    "framework": {"type": "string"},
                    "port": {"type": "integer"},
                    "environment_variables": {
                        "type": "object",
                        "properties": {
                            "DATABASE_URL": {"type": "string"},
                            "DEBUG": {"type": "string"},
                            "SECRET_KEY": {"type": "string"}
                        }
                    },
                    "dependencies": {
                        "type": "array",
                        "items": {"type": "string"}
                    }
                },
                "required": ["component_id", "name", "technology", "framework"]
            }
        },
        "connections": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "source": {"type": "string"},
                    "target": {"type": "string"},
                    "type": {"type": "string"},
                    "port": {"type": "integer"}
                },
                "required": ["source", "target"]
            }
        }
    },
    "required": ["project", "technologies", "components", "connections"]
}

def generate_project_config(user_prompt: str) -> dict:
    """
    Generate project configuration JSON from natural language prompt
    using Google's Gemini model with structured output.
    """
    
    available_techs = "Available Technologies:\n"
    for category in ["runtime", "database", "cache", "queue"]:
        techs_in_category = [tech for tech, info in TECHNOLOGY_CATALOG.items() if info["category"] == category]
        available_techs += f"- {category.title()}: {', '.join(techs_in_category)}\n"

    # Add version information
    available_techs += "\nAvailable Versions for Each Technology:\n"
    for tech, info in sorted(TECHNOLOGY_CATALOG.items()):
        versions_str = ', '.join([v for v in info["versions"] if v != "latest"])
        available_techs += f"- {tech}: {versions_str} (or 'latest')\n"

    # System instructions
    system_prompt = f"""You are an AI assistant that generates project configuration JSON 
    based on user requirements. Use the provided schema to create appropriate project, 
    technologies, components, connections, and environments.

    Follow these rules:
    - Assign unique component_ids (e.g., "auth-service", "user-service", "frontend")
    - Set appropriate ports for each technology (8000-9000 range)
    - Create logical connections between components
    - Include all necessary environment variables
    - Use realistic directory structures

    TECHNOLOGY RESTRICTIONS:
    {available_techs}
    - ONLY use technologies from the list above
    - For technology "type" field, use the category (runtime, database, cache, queue)
    - Use "latest" as version UNLESS the user specifies a specific version in their requirements
    - If user specifies a version, use the exact version string from the available versions list
    - If no version is specified, default to "latest"

    Return ONLY valid JSON without any additional text, markdown, or code formatting.
    """
    
    # Combine system prompt with user prompt
    full_prompt = f"{system_prompt}\n\nUser Request: {user_prompt}"
    
    try:
        # Generate response with JSON schema
        response = client.models.generate_content(
            model='gemini-2.0-flash-exp',
            contents=full_prompt,
            config={
                'response_mime_type': 'application/json',
                'response_schema': json_schema
            }
        )
        
        # The response should already be parsed JSON
        return json.loads(response.text)
        
    except Exception as e:
        print(f"Error generating content: {e}")
        return {"error", e}

