import openai
import json
from dotenv import load_dotenv
import os
from datetime import datetime
import time

load_dotenv()

ai_client = openai.AzureOpenAI(
    api_key=os.environ.get('AI_KEY'),
    azure_endpoint=os.environ.get("AI_ENDPOINT"),
    api_version=os.environ.get("AI_API_VERSION")    
)

SYSTEM_PROMPT = """You are an AI assistant that generates concise project configurations as JSON.

Generate a JSON response with this EXACT structure:
{
  "project": {
    "name": "string (kebab-case)",
    "description": "brief description (max 100 chars)",
    "author": "string or null"
  },
  "technologies": [
    {
      "name": "string (from: postgresql, mysql, mongodb, redis, kafka, rabbitmq, node, python, java, go, rust)",
      "version": "string (e.g., '16', '20', 'latest')",
      "category": "string (runtime|database|cache|queue|service)",
      "port": "number or null",
      "environment_variables": {}
    }
  ],
  "components": [
    {
      "component_id": "string (kebab-case, e.g., 'auth-api')",
      "name": "string (display name)",
      "type": "string (database|cache|api|web|gateway|external)",
      "technology": "string (matches technology.name)",
      "framework": "string (django|flask|fastapi|express|nestjs|react|nextjs|angular|vue|svelte|none) or null",
      "port": "number or null",
      "directory": "string (relative path) or null",
      "dependencies": ["array of component_ids"],
      "environment_variables": {}
    }
  ],
  "connections": [
    {
      "source": "string (component_id)",
      "target": "string (component_id)",
      "type": "string (api|database|cache|queue)",
      "port": "number or null"
    }
  ],
  "environments": [
    {
      "name": "string (development|staging|production)",
      "type": "string (local|vm|cloud)"
    }
  ]
}

RULES:
1. Keep all descriptions under 100 characters
2. Use kebab-case for IDs (e.g., "academic-service", "industry-db")
3. Only include technologies that are actually used by components
4. Each component must reference a valid technology name
5. Connection source/target must reference valid component_ids
6. Omit null values from environment_variables if empty
7. Be concise - focus on architecture, not implementation details"""

def model_results(prompt, max_retries=2):
    """Generate project configuration with retry logic"""
    
    for attempt in range(max_retries):
        start_time = time.time()
        print(f"\n[Attempt {attempt + 1}] Starting AI request at {datetime.now()}")
        
        try:
            response = ai_client.chat.completions.create(
                model=os.environ.get('AI_DEPLOYMENT'),
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": f"Generate architecture for: {prompt}"}
                ],
                response_format={"type": "json_object"},
                temperature=0.1,
                timeout=90,
                max_tokens=6000  # Reduced for faster response
            )
            
            elapsed = time.time() - start_time
            print(f"✓ AI request completed in {elapsed:.2f}s")
            print(f"  Tokens - Prompt: {response.usage.prompt_tokens}, Completion: {response.usage.completion_tokens}")
            print(f"  Finish reason: {response.choices[0].finish_reason}")
            
            # Check if truncated
            if response.choices[0].finish_reason == "length":
                print("⚠ WARNING: Response truncated due to token limit")
                if attempt < max_retries - 1:
                    print("  Retrying with simplified prompt...")
                    continue
                else:
                    print("  Max retries reached, returning partial response")
            
            # Parse JSON
            result = json.loads(response.choices[0].message.content)
            
            # Validate structure
            if not validate_response_structure(result):
                raise ValueError("Invalid response structure")
            
            print(f"✓ Response validated successfully")
            return result
            
        except json.JSONDecodeError as e:
            print(f"✗ JSON Parse Error: {e}")
            if 'response' in locals():
                print(f"  Last 300 chars: {response.choices[0].message.content[-300:]}")
            if attempt < max_retries - 1:
                print("  Retrying...")
                continue
            return None
            
        except openai.APITimeoutError as e:
            print(f"✗ Timeout Error: {e}")
            if attempt < max_retries - 1:
                print("  Retrying...")
                continue
            return None
            
        except Exception as e:
            print(f"✗ Error after {time.time() - start_time:.2f}s: {e}")
            if attempt < max_retries - 1:
                print("  Retrying...")
                continue
            return None
    
    print("✗ All retry attempts failed")
    return None


def validate_response_structure(data):
    """Validate the response has required structure"""
    required_keys = ['project', 'technologies', 'components', 'connections', 'environments']
    
    if not all(key in data for key in required_keys):
        print(f"Missing keys. Expected: {required_keys}, Got: {list(data.keys())}")
        return False
    
    # Basic type checks
    if not isinstance(data['technologies'], list):
        print("'technologies' must be a list")
        return False
    
    if not isinstance(data['components'], list):
        print("'components' must be a list")
        return False
    
    if not isinstance(data['connections'], list):
        print("'connections' must be a list")
        return False
    
    if not isinstance(data['environments'], list):
        print("'environments' must be a list")
        return False
    
    return True

