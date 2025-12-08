from datetime import datetime
from enum import Enum
from typing import Optional
import uuid
from beanie import Document
from pydantic import Field
import strawberry

@strawberry.enum
class JobStatus(Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    
@strawberry.type
class JobResult:
    id: str
    status: JobStatus
    result: Optional[str] = None
    error: Optional[str] = None
    created_at: str
    completed_at: Optional[str] = None

@strawberry.type
class JobCreated:
    job_id: str
    message: str
    
class Job(Document):
    job_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    status: str = JobStatus.PENDING.value
    user_input: str
    result: Optional[str] = None
    error: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None

    class Settings:
        name = "jobs"
        indexes = [
            "job_id",
            "status",
            "created_at"
        ]