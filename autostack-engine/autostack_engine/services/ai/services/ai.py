from datetime import datetime
from enum import Enum
import json
import traceback
from typing import Any, Dict, Optional
from uuid import UUID

from autostack_engine.utils.database.models.ai.models import ProjectChat
from autostack_engine.utils.database.mongo_client import DatabaseManager
from autostack_engine.utils.orchestration.models import BaseService


from google import genai
import json
from dotenv import load_dotenv

from autostack_engine.utils.constants import TECHNOLOGY_CATALOG

load_dotenv()

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
                },
                "required": ["component_id", "name", "technology", "framework", "type"]
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

class ComponentTypeInput(Enum):
    DATABASE = "database"
    CACHE = "cache"
    API = "api"
    WEB = "web"
    GATEWAY = "gateway"
    EXTERNAL = "external"

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
            project_id: Optional UUID of the project to associate this chat with
            
        Returns:
            tuple: (success: bool, schema: Optional[Dict], chat_id: Optional[str], error_message: Optional[str])
        """
        
        try:
            db = DatabaseManager()
            await db.connect([ProjectChat])
                
            available_techs = "Available Technologies:\n"
            for category in ["runtime", "database", "cache", "queue"]:
                techs_in_category = [
                    tech for tech, info in TECHNOLOGY_CATALOG.items() 
                    if info["category"] == category
                ]
                available_techs += f"- {category.title()}: {', '.join(techs_in_category)}\n"
            
            available_component_types = "Available Component Types:\n- " + "\n- ".join(
                [f"{comp_type.value.title()}: {comp_type.value}" for comp_type in ComponentTypeInput]
            ) + "\n"
            
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
            - Use "latest" as version unless specified otherwise
            
            COMPONENT RESTRICTIONS:
            {available_component_types}
            - ONLY use the types from the above list
            - The type field should be from the category provided (database, cache, api, web, gateway, external)
            
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
                    'response_schema': json_schema
                }
            )
            
            schema_data = json.loads(response.text)
            
            # Generate chat title
            chat_title = self._generate_chat_title(user_prompt)
            
            # Save to database
            project_chat = ProjectChat(
                chat_title=chat_title,
                prompt=user_prompt,
                initial_schema=schema_data,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            await project_chat.insert()
            
            self.log_info(f"Generated project config and saved chat with ID: {project_chat.id}")
            return True, schema_data, str(project_chat.id), None
            
        except Exception as e:
            error_msg = f"Error generating schema: {traceback.format_exc()}"
            self.log_error(error_msg)
            return False, None, str(e)
        
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
    
   