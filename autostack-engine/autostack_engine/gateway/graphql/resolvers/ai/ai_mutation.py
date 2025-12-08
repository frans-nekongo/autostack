import strawberry
import structlog

from autostack_engine.gateway.graphql.resolvers.ai.ai_query import CreateProjectResponse, DeleteChatResponse
from autostack_engine.services.ai.services.ai import AIService
from autostack_engine.services.project.services.project import ProjectService


logger = structlog.get_logger()

@strawberry.type
class ModelMutation:
    
    @strawberry.mutation
    async def delete_chat(self, chat_id: str) -> DeleteChatResponse:
        """
        Delete a chat by ID.
        
        Args:
            chat_id: The chat ID to delete
            
        Returns:
            DeleteChatResponse indicating success or failure
        """
        try:
            ai_service = AIService()
            success, error = await ai_service.delete_chat(chat_id)
            
            if success:
                logger.info(f"Deleted chat: {chat_id}")
            else:
                logger.error(f"Failed to delete chat: {error}")
            
            return DeleteChatResponse(success=success, error=error)
            
        except Exception as e:
            error_msg = f"Error deleting chat: {e}"
            logger.error(error_msg)
            return DeleteChatResponse(success=False, error=error_msg)