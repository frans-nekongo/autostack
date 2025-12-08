from beanie import Document
from pydantic import Field
from typing import List, Optional
from datetime import datetime

class ConversationMessage(Document):
    """Individual message in a conversation."""
    role: str  # "user" or "model"
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "conversation_messages"
        
class ConversationSession(Document):
    """Store conversation history for project configuration generation."""
    session_id: str = Field(index=True, unique=True)
    user_id: Optional[str] = None  # Optional user tracking
    messages: List[dict] = []  # List of {role, content, timestamp}
    last_generated_config: Optional[dict] = None  # Store the latest config
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "conversation_sessions"
        indexes = [
            "session_id",
            "user_id",
            "updated_at",
        ]
    
    async def add_message(self, role: str, content: str) -> None:
        """Add a message to the conversation history."""
        self.messages.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now()
        })
        self.updated_at = datetime.now()
        await self.save()
    
    async def clear_messages(self) -> None:
        """Clear all messages in the session."""
        self.messages = []
        self.last_generated_config = None
        self.updated_at = datetime.now()
        await self.save()
    
    def get_gemini_history(self) -> List[dict]:
        """Convert stored messages to Gemini API format."""
        return [
            {
                "role": msg["role"],
                "parts": [{"text": msg["content"]}]
            }
            for msg in self.messages
        ]