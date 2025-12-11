from datetime import datetime
from typing import Optional, Dict, Any, List
from uuid import UUID
import uuid
from enum import Enum
from beanie import Document
from pydantic import Field, BaseModel
from pymongo import IndexModel


class ActivityType(str, Enum):
    """Enum for activity types"""
    UPDATE_PROJECT = "update_project"
    UPDATE_PROJECT_COMPONENT = "update_project_component"
    DELETE_PROJECT = "delete_project"
    DELETE_CHAT = "delete_chat"
    DELETE_COMPONENT = "delete_component"
    CREATE_PROJECT = "create_project"
    CREATE_CHAT = "create_chat"
    CREATE_COMPONENT = "create_component"


class FieldChange(BaseModel):
    """Model for tracking field changes"""
    field: str
    old_value: Optional[Any]
    new_value: Optional[Any]


class ProjectUpdateDetails(BaseModel):
    """Details specific to project updates"""
    field_changes: List[FieldChange] = []
    


class ComponentUpdateDetails(BaseModel):
    """Details specific to component updates"""
    component_id: str  # Using component_id (e.g., "user-db") instead of UUID
    field_changes: List[FieldChange] = []
    # Framework changes
    old_framework: Optional[str] = None
    new_framework: Optional[str] = None
    # Title changes
    old_name: Optional[str] = None
    new_name: Optional[str] = None
    # Project connection changes
    old_connected_project_id: Optional[UUID] = None
    new_connected_project_id: Optional[UUID] = None
    # Other component field changes
    old_technology: Optional[str] = None
    new_technology: Optional[str] = None
    old_port: Optional[int] = None
    new_port: Optional[int] = None


class DeleteDetails(BaseModel):
    """Details for deletion activities"""
    target_id: UUID
    target_name: Optional[str]
    target_type: str


class CreateDetails(BaseModel):
    """Details for creation activities"""
    target_id: UUID
    target_name: Optional[str]
    target_type: str
    metadata: Optional[Dict[str, Any]] = {}
    



class ActivityLog(Document):
    """Document for storing system activities"""
    
    id: UUID = Field(default_factory=uuid.uuid4, alias="_id")
    
    # Activity type
    activity_type: ActivityType
    
    # Timestamp
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Target project (for project-related activities)
    project_id: Optional[UUID] = None
    project_name: Optional[str] = None
    
    # Target chat (for chat-related activities)
    chat_id: Optional[UUID] = None
    
    # Activity-specific details stored as a dictionary
    details: Optional[Dict[str, Any]] = None
    
    class Settings:
        name = "activity_logs"
        indexes = [
            IndexModel([("activity_type", 1)]),
            IndexModel([("created_at", -1)]),
            IndexModel([("project_id", 1)]),
            IndexModel([("chat_id", 1)]),
            IndexModel([("project_id", 1), ("created_at", -1)]),  # Project activity history
        ]
    
    def __repr__(self) -> str:
        return f"<ActivityLog {self.activity_type} at {self.created_at}>"


# Example usage with your models
def create_field_change(field_name: str, old_value: Any, new_value: Any) -> FieldChange:
    """Helper to create a field change record"""
    return FieldChange(field=field_name, old_value=old_value, new_value=new_value)
