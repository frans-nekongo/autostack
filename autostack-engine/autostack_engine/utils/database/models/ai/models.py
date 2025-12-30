from uuid import UUID
import uuid
from beanie import Document
from pydantic import Field
from typing import Optional, Dict, Any
from datetime import datetime
from pymongo import IndexModel

class ProjectChat(Document):
    id: UUID = Field(default_factory=uuid.uuid4, alias="_id")
    chat_title: Optional[str] = None
    prompt: str
    initial_schema: Optional[Dict[str, Any]] = None
    
    # Add validation error fields
    has_validation_error: bool = Field(default=False)
    validation_error: Optional[Dict[str, Any]] = None
    
    # Audit fields
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    class Settings:
        name = "project_chat"
        indexes = [
            IndexModel([("created_at", -1)]),
        ]