import git
import strawberry
import uuid
import structlog
import yaml
from typing import Any, Dict, Optional, List
from datetime import datetime
from strawberry.scalars import JSON

from autostack_engine.services.ai.services.ai import AIService
from autostack_engine.utils.ai.util import generate_project_config

logger = structlog.get_logger()

@strawberry.type
class ChatInfo:
    """Type representing chat information"""
    id: str
    chat_title: Optional[str]
    prompt: str
    initial_schema: Optional[JSON]  # type: ignore
    created_at: str
    updated_at: str


@strawberry.type
class GenerateArchitectureResponse:
    """Response type for architecture generation"""
    success: bool
    schema: Optional[JSON]  # type: ignore
    chat_id: Optional[str]
    error: Optional[str]


@strawberry.type
class DeleteChatResponse:
    """Response type for chat deletion"""
    success: bool
    error: Optional[str]


@strawberry.type
class CreateProjectResponse:
    """Response type for project creation"""
    success: bool
    project_id: Optional[str]
    error: Optional[str]
    
    
@strawberry.type
class ModelQuery:
    @strawberry.field
    async def generate_architecture(
        self,
        description: str,
    ) -> GenerateArchitectureResponse:
        """
        Generate project architecture from description and save to database.
        
        Args:
            description: Natural language description of the project
            
        Returns:
            GenerateArchitectureResponse with schema and chat_id
        """
        try:
            ai_service = AIService()
            
            success, schema, chat_id, error = await ai_service.generate_project_config(description)
            
            if success:
                logger.info(f"Generated architecture for chat: {chat_id}")
                return GenerateArchitectureResponse(
                    success=True,
                    schema=schema,
                    chat_id=chat_id,
                    error=None
                )
            else:
                logger.error(f"Failed to generate architecture: {error}")
                return GenerateArchitectureResponse(
                    success=False,
                    schema=None,
                    chat_id=None,
                    error=error
                )
                
        except Exception as e:
            error_msg = f"Error generating architecture: {e}"
            logger.error(error_msg)
            return GenerateArchitectureResponse(
                success=False,
                schema=None,
                chat_id=None,
                error=error_msg
            )
    
    @strawberry.field
    async def get_chat(self, chat_id: str) -> Optional[ChatInfo]:
        """
        Get a specific chat by ID.
        
        Args:
            chat_id: The chat ID to retrieve
            
        Returns:
            ChatInfo or None if not found
        """
        try:
            ai_service = AIService()
            chat = await ai_service.get_chat(chat_id)
            
            if chat:
                return ChatInfo(
                    id=str(chat.id),
                    chat_title=chat.chat_title,
                    prompt=chat.prompt,
                    initial_schema=chat.initial_schema,
                    created_at=chat.created_at.isoformat(),
                    updated_at=chat.updated_at.isoformat()
                )
            return None
            
        except Exception as e:
            logger.error(f"Error fetching chat: {e}")
            return None
    
    @strawberry.field
    async def list_chats(self) -> List[ChatInfo]:
        """
        List all chats, sorted by most recent first.
        
        Returns:
            List of ChatInfo objects
        """
        try:
            ai_service = AIService()
            chats = await ai_service.list_chats()
            
            return [
                ChatInfo(
                    id=str(chat.id),
                    chat_title=chat.chat_title,
                    prompt=chat.prompt,
                    initial_schema=chat.initial_schema,
                    created_at=chat.created_at.isoformat(),
                    updated_at=chat.updated_at.isoformat()
                )
                for chat in chats
            ]
            
        except Exception as e:
            logger.error(f"Error listing chats: {e}")
            return []
