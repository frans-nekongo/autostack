
from beanie import Document
from pydantic import Field
from typing import Optional
from datetime import datetime
from pymongo import IndexModel
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Migration(Document):
    version: str = Field(..., unique=True)
    name: str
    executed_at: datetime = Field(default_factory=datetime.now)
    success: bool = True
    error_message: Optional[str] = None
    
    class Settings:
        name = "migrations"
        indexes = [
            IndexModel([("version", 1)], unique=True),
            IndexModel([("executed_at", -1)]),
        ]
    
    def __repr__(self) -> str:
        return f"<Migration {self.version}: {self.name}>"

# Helper class for managing project relationships

    