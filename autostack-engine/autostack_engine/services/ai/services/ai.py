from datetime import datetime
from enum import Enum
import json
import traceback
from typing import Any, Dict, Optional
from uuid import UUID

from autostack_engine.utils.database.models.ai.models import ProjectChat, SchemaRating
from autostack_engine.utils.database.mongo_client import DatabaseManager
from autostack_engine.utils.orchestration.models import BaseService


from google import genai
import json
from dotenv import load_dotenv

from autostack_engine.utils.constants import TECHNOLOGY_CATALOG

load_dotenv()

unified_schema = {
    "type": "object",
    "properties": {
        "project": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "author": {"type": "string"},
                "description": {"type": "string"},
                "version": {"type": "string"},
            }
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
                }
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
                    "type": {"type": "string"},
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
                }
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
                }
            }
        },
        # Error fields (optional)
        "error": {
            "type": "object",
            "properties": {
                "message": {"type": "string"},
                "unsupported_technologies": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "unsupported_frameworks": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "unsupported_component_types": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "supported_technologies": {
                    "type": "object",
                    "properties": {
                        "runtime": {"type": "array", "items": {"type": "string"}},
                        "database": {"type": "array", "items": {"type": "string"}},
                        "cache": {"type": "array", "items": {"type": "string"}},
                        "queue": {"type": "array", "items": {"type": "string"}}
                    }
                },
                "supported_frameworks": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "supported_component_types": {
                    "type": "array",
                    "items": {"type": "string"}
                }
            },
            "required": ["message"]
        }
    }
}


class ComponentTypeInput(Enum):
    DATABASE = "database"
    CACHE = "cache"
    API = "api"
    WEB = "web"
    GATEWAY = "gateway"
    EXTERNAL = "external"

class Framework(str, Enum):
    # Backend frameworks
    FLASK = "flask"
    FASTAPI = "fastapi"
    EXPRESS = "express"
    NESTJS = "nestjs"
    
    # Frontend frameworks
    REACT = "react"
    NEXTJS = "nextjs"
    ANGULAR = "angular"
    VUE = "vue"
    SVELTE = "svelte"
    
    
    # No framework
    VANILLA = "vanilla"
    NONE = "none"
    

class AIService(BaseService):
    """Service for managing AI-generated project configurations and chats"""
    
    service_name = "AI"
    
    def __init__(self):
        super().__init__()
        self.client = genai.Client()
        
    def _generate_chat_title(self, prompt: str) -> str:
        """
        Generate a concise chat title from the user prompt.
        Takes the first 50 characters or first sentence, whichever is shorter.
        """
        try:
            # Split by common sentence endings
            sentences = prompt.replace('?', '.').replace('!', '.').split('.')
            first_sentence = sentences[0].strip()
            
            # Use first sentence if it's reasonable length, otherwise truncate
            if len(first_sentence) <= 50:
                return first_sentence
            else:
                return first_sentence[:47] + "..."
        except Exception as e:
            self.log_warning(f"Error generating chat title: {e}")
            return prompt[:50] + "..." if len(prompt) > 50 else prompt
        
    
    async def generate_project_config(
        self, 
        user_prompt: str, 
    ) -> tuple[bool, Optional[Dict[str, Any]], Optional[str], Optional[str]]:
        """
        Generate project configuration JSON from natural language prompt
        using Google's Gemini model with structured output.
        
        Args:
            user_prompt: Natural language description of the project
            
        Returns:
            tuple: (success: bool, result/error_object: Optional[Dict], chat_id: Optional[str], error_message: Optional[str])
            - On success: (True, schema_dict, chat_id, None)
            - On validation error: (False, error_object_dict, chat_id, error_message)
            - On other error: (False, None, None, error_message)
        """
        
        try:
            db = DatabaseManager()
            await db.connect([ProjectChat])
            
            supported_techs_by_category = {
                "runtime": [],
                "database": [],
                "cache": [],
                "queue": []
            }
                
            for tech, info in TECHNOLOGY_CATALOG.items():
                category = info["category"]
                if category in supported_techs_by_category:
                    supported_techs_by_category[category].append(tech)

            supported_frameworks = [f.value for f in Framework]
            supported_component_types = [c.value for c in ComponentTypeInput]

            available_techs = "Available Technologies:\n"
            for category, techs in supported_techs_by_category.items():
                available_techs += f"- {category.title()}: {', '.join(techs)}\n"

            available_component_types = "Available Component Types:\n- " + "\n- ".join(supported_component_types)
            available_frameworks = "Available Frameworks:\n- " + "\n- ".join(supported_frameworks)
            
            # System instructions
            system_prompt = f"""You are an AI assistant that generates project configuration JSON 
            based on user requirements.

            CRITICAL: If the user requests ANY technologies, frameworks, or component types that are 
            NOT in the supported lists below, you MUST return an error response.

            TECHNOLOGY RESTRICTIONS:
            {available_techs}
            - ONLY use technologies from the list above
            - For technology "type" field, use the category (runtime, database, cache, queue)
            - Use "latest" as version unless specified otherwise

            COMPONENT TYPE RESTRICTIONS:
            {available_component_types}
            - ONLY use component types from the above list

            FRAMEWORK RESTRICTIONS:
            {available_frameworks}
            - ONLY use frameworks from the above list

            RESPONSE FORMAT:

            For ERRORS (unsupported items):
            {{
            "error": {{
                "message": "Clear description of what's unsupported",
                "unsupported_technologies": ["list", "of", "unsupported", "techs"],
                "unsupported_frameworks": ["list", "of", "unsupported", "frameworks"],
                "unsupported_component_types": ["list", "of", "unsupported", "types"],
                "supported_technologies": {{
                "runtime": {supported_techs_by_category.get('runtime', [])},
                "database": {supported_techs_by_category.get('database', [])},
                "cache": {supported_techs_by_category.get('cache', [])},
                "queue": {supported_techs_by_category.get('queue', [])}
                }},
                "supported_frameworks": {supported_frameworks},
                "supported_component_types": {supported_component_types}
            }}
            }}

            For SUCCESS (all items supported):
            {{
            "project": {{
                "name": "project name",
                "author": "author name",
                "description": "description",
                "version": "version"
            }},
            "technologies": [...],
            "components": [...],
            "connections": [...]
            }}

            RULES:
            - Return ERROR response if ANY requested item is unsupported
            - Assign unique component_ids (e.g., "auth-service", "user-service", "frontend")
            - Set appropriate ports for each technology (8000-9000 range)
            - Create logical connections between components
            - Include all necessary environment variables

            Return ONLY valid JSON without any additional text, markdown, or code formatting.
            """
            
            # Combine system prompt with user prompt
            full_prompt = f"{system_prompt}\n\nUser Request: {user_prompt}"
            
            # Generate response with JSON schema
            response = self.client.models.generate_content(
                model='gemini-2.0-flash-exp',
                contents=full_prompt,
                config={
                    'response_mime_type': 'application/json',
                    'response_schema': unified_schema
                }
            )
            
            result = json.loads(response.text)
            
            # Generate chat title
            chat_title = self._generate_chat_title(user_prompt)
            
            # Check if it's an error response
            if "error" in result:
                error_info = result["error"]
                error_message = error_info.get("message", "Unsupported technologies or frameworks requested")
                
                self.log_warning(f"Validation error: {error_message}")
                
                # Save the chat WITH the validation error details
                project_chat = ProjectChat(
                    chat_title=chat_title,
                    prompt=user_prompt,
                    initial_schema=None,
                    has_validation_error=True,
                    validation_error=error_info,  # Store the full error object
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
                
                await project_chat.insert()
                
                return (False, result, str(project_chat.id), error_message)
            else:
                # Success - save to database
                project_chat = ProjectChat(
                    chat_title=chat_title,
                    prompt=user_prompt,
                    initial_schema=result,
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
                
                await project_chat.insert()
                
                self.log_info(f"Generated project config and saved chat with ID: {project_chat.id}")
                return (True, result, str(project_chat.id), None)
            
        except json.JSONDecodeError as e:
            error_msg = f"Failed to parse AI response as JSON: {str(e)}"
            self.log_error(error_msg)
            return (False, None, None, error_msg)
            
        except Exception as e:
            error_msg = f"Error generating schema: {traceback.format_exc()}"
            self.log_error(error_msg)
            return (False, None, None, str(e))
      
    async def regenerate_project_config(
        self,
        chat_id: str,
        user_prompt: str,
    ) -> tuple[bool, Optional[Dict[str, Any]], Optional[str], Optional[str]]:
        """
        Regenerate project configuration for an existing chat.
        
        Args:
            chat_id: ID of the existing chat
            user_prompt: Updated natural language description
            
        Returns:
            tuple: (success, result/error_object, chat_id, error_message)
        """
        try:
            db = DatabaseManager()
            await db.connect([ProjectChat])
            
            # Load existing chat
            existing_chat = await ProjectChat.get(chat_id)
            if not existing_chat:
                return (False, None, None, "Chat not found")
            
            # Use the same generation logic as generate_project_config
            # ... (copy the generation code from generate_project_config)
            
            supported_techs_by_category = {
                "runtime": [],
                "database": [],
                "cache": [],
                "queue": []
            }
                
            for tech, info in TECHNOLOGY_CATALOG.items():
                category = info["category"]
                if category in supported_techs_by_category:
                    supported_techs_by_category[category].append(tech)

            supported_frameworks = [f.value for f in Framework]
            supported_component_types = [c.value for c in ComponentTypeInput]

            available_techs = "Available Technologies:\n"
            for category, techs in supported_techs_by_category.items():
                available_techs += f"- {category.title()}: {', '.join(techs)}\n"

            available_component_types = "Available Component Types:\n- " + "\n- ".join(supported_component_types)
            available_frameworks = "Available Frameworks:\n- " + "\n- ".join(supported_frameworks)
            
            system_prompt = f"""You are an AI assistant that generates project configuration JSON 
            based on user requirements.

            CRITICAL: If the user requests ANY technologies, frameworks, or component types that are 
            NOT in the supported lists below, you MUST return an error response.

            TECHNOLOGY RESTRICTIONS:
            {available_techs}
            - ONLY use technologies from the list above
            - For technology "type" field, use the category (runtime, database, cache, queue)
            - Use "latest" as version unless specified otherwise

            COMPONENT TYPE RESTRICTIONS:
            {available_component_types}
            - ONLY use component types from the above list

            FRAMEWORK RESTRICTIONS:
            {available_frameworks}
            - ONLY use frameworks from the above list

            RESPONSE FORMAT:

            For ERRORS (unsupported items):
            {{
            "error": {{
                "message": "Clear description of what's unsupported",
                "unsupported_technologies": ["list", "of", "unsupported", "techs"],
                "unsupported_frameworks": ["list", "of", "unsupported", "frameworks"],
                "unsupported_component_types": ["list", "of", "unsupported", "types"],
                "supported_technologies": {{
                "runtime": {supported_techs_by_category.get('runtime', [])},
                "database": {supported_techs_by_category.get('database', [])},
                "cache": {supported_techs_by_category.get('cache', [])},
                "queue": {supported_techs_by_category.get('queue', [])}
                }},
                "supported_frameworks": {supported_frameworks},
                "supported_component_types": {supported_component_types}
            }}
            }}

            For SUCCESS (all items supported):
            {{
            "project": {{
                "name": "project name",
                "author": "author name",
                "description": "description",
                "version": "version"
            }},
            "technologies": [...],
            "components": [...],
            "connections": [...]
            }}

            RULES:
            - Return ERROR response if ANY requested item is unsupported
            - Assign unique component_ids (e.g., "auth-service", "user-service", "frontend")
            - Set appropriate ports for each technology (8000-9000 range)
            - Create logical connections between components
            - Include all necessary environment variables

            Return ONLY valid JSON without any additional text, markdown, or code formatting.
            """
            
            full_prompt = f"{system_prompt}\n\nUser Request: {user_prompt}"
            
            response = self.client.models.generate_content(
                model='gemini-2.0-flash-exp',
                contents=full_prompt,
                config={
                    'response_mime_type': 'application/json',
                    'response_schema': unified_schema
                }
            )
            
            result = json.loads(response.text)
            
            # Check if it's an error response
            if "error" in result:
                error_info = result["error"]
                error_message = error_info.get("message", "Unsupported technologies or frameworks requested")
                
                self.log_warning(f"Validation error: {error_message}")
                
                # Update chat with validation error
                existing_chat.prompt = user_prompt
                existing_chat.initial_schema = None
                existing_chat.has_validation_error = True
                existing_chat.validation_error = error_info  # Store the full error object
                existing_chat.updated_at = datetime.now()
                await existing_chat.save()
                
                return (False, result, chat_id, error_message)
            else:
                # Success - update chat with new schema
                existing_chat.prompt = user_prompt
                existing_chat.initial_schema = result
                existing_chat.has_validation_error = False
                existing_chat.validation_error = None
                existing_chat.updated_at = datetime.now()
                await existing_chat.save()
                
                self.log_info(f"Regenerated project config for chat: {chat_id}")
                return (True, result, chat_id, None)
            
        except json.JSONDecodeError as e:
            error_msg = f"Failed to parse AI response as JSON: {str(e)}"
            self.log_error(error_msg)
            return (False, None, chat_id, error_msg)
            
        except Exception as e:
            error_msg = f"Error regenerating schema: {traceback.format_exc()}"
            self.log_error(error_msg)
            return (False, None, chat_id, str(e))  
        
        
    async def get_chat(self, chat_id: str) -> Optional[ProjectChat]:
        """
        Get a specific chat by ID.
        
        Args:
            chat_id: The chat ID to retrieve
            
        Returns:
            Optional[ProjectChat]: The chat document or None if not found
        """
        try:
            db = DatabaseManager()
            await db.connect([ProjectChat])
            
            chat = await ProjectChat.get(chat_id)
            if chat:
                self.log_info(f"Retrieved chat: {chat_id}")
            else:
                self.log_warning(f"Chat not found: {chat_id}")
            
            return chat
            
        except Exception as e:
            self.log_error(f"Error fetching chat: {e}")
            return None
    
    
    async def list_chats(self) -> list[ProjectChat]:
        """
        List all chats, sorted by most recent first.
        
        Returns:
            list[ProjectChat]: List of chat documents
        """
        try:
            db = DatabaseManager()
            await db.connect([ProjectChat])
            
            chats = await ProjectChat.find_all().sort("-created_at").to_list()
            self.log_info(f"Retrieved {len(chats)} total chats")
            
            return chats
            
        except Exception as e:
            self.log_error(f"Error listing chats: {e}")
            return []
    
    async def delete_chat(self, chat_id: str) -> tuple[bool, Optional[str]]:
        """
        Delete a chat by ID.
        
        Args:
            chat_id: The chat ID to delete
            
        Returns:
            tuple: (success: bool, error_message: Optional[str])
        """
        try:
            db = DatabaseManager()
            await db.connect([ProjectChat])
            
            chat = await ProjectChat.get(chat_id)
            if not chat:
                return False, f"Chat '{chat_id}' not found"
            
            chat_title = chat.chat_title
            await chat.delete()
            
            self.log_info(f"Deleted chat '{chat_title}' (ID: {chat_id})")
            return True, None
            
        except Exception as e:
            error_msg = f"Error deleting chat: {str(e)}"
            self.log_error(error_msg)
            return False, error_msg
    
    async def update_chat(self, chat_id: str, updates: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """
        Update an existing chat.
        
        Args:
            chat_id: The chat ID to update
            updates: Dict containing fields to update
            
        Returns:
            tuple: (success: bool, error_message: Optional[str])
        """
        try:
            db = DatabaseManager()
            await db.connect([ProjectChat])
            
            chat = await ProjectChat.get(chat_id)
            if not chat:
                return False, f"Chat '{chat_id}' not found"
            
            # Update allowed fields
            if "chat_title" in updates:
                chat.chat_title = updates["chat_title"]
            if "prompt" in updates:
                chat.prompt = updates["prompt"]
            if "initial_schema" in updates:
                chat.initial_schema = updates["initial_schema"]
            
            chat.updated_at = datetime.now()
            await chat.save()
            
            self.log_info(f"Updated chat '{chat_id}'")
            return True, None
            
        except Exception as e:
            error_msg = f"Error updating chat: {str(e)}"
            self.log_error(error_msg)
            return False, error_msg
        
        
    async def rate_chat(self, chat_id: str, score: int, comment: str) -> tuple[bool, Optional[str], Optional[str]]:
        """
        Rate an existing chat.
        
        Args:
            chat_id: The chat ID to update
            score: the score for the generated 
            comment: any comments on the schema
            
            
        Returns:
            tuple: (success: bool, error_message: Optional[str])
        """
        try:
            db = DatabaseManager()
            await db.connect([SchemaRating])
            
            rating = await SchemaRating.get(chat_id)
            if not rating:
                schema_rating = SchemaRating(
                    id=UUID(chat_id),
                    score=score,
                    comment=comment
                )
                
                await schema_rating.insert()
                
                self.log_info(f"Saved rating for chat with ID: {chat_id}")
                return (True, "Thank you for rating the generated schema", None)
            else:
                # Update rating
                if score:
                    rating.score = score
                    
                if comment:
                    rating.comment = comment
                
                rating.updated_at = datetime.now()
                await rating.save()
            
                self.log_info(f"Updated rating '{chat_id}'")
                return (True, "Thank you for rating the generated schema", "None")
            
        except Exception as e:
            error_msg = f"Error rating chat: {str(e)}"
            self.log_error(error_msg)
            return (False, None, error_msg)
    
   