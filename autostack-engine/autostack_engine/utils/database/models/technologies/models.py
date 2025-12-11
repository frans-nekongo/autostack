from uuid import UUID
import uuid
from beanie import Document, Indexed
from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Dict, Any, Optional, List
from datetime import datetime
from pymongo import IndexModel
from enum import Enum
import logging

from autostack_engine.utils.constants import TECHNOLOGY_CATALOG


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TechnologyCategory(str, Enum):
    RUNTIME = "runtime"
    DATABASE = "database"
    CACHE = "cache"
    QUEUE = "queue"
    SERVICE = "service"
    
    

class Technology(Document):
    id: UUID = Field(default_factory=uuid.uuid4, alias="_id")
    project_id: UUID = Field(..., index=True)
    name: str  # e.g., "postgresql", "node", "redis"
    version: str = "latest"  # e.g., "16", "20", "latest"
    category: Optional[TechnologyCategory] = None  # Auto-determined from catalog
    port: Optional[int] = None  # Port for services
    environment_variables: Optional[Dict[str, Any]] = None  # Env vars for the service
    configuration: Optional[Dict[str, Any]] = None  # Additional config
    enabled: bool = True  # Whether to include in deployment
    
    # Metadata from catalog (populated automatically)
    nix_package: Optional[str] = None
    available_versions: Optional[List[str]] = None
    
    # Audit fields
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    class Settings:
        name = "technology_configs"
        indexes = [
            IndexModel([("project_id", 1)]),
            IndexModel([("name", 1)]),
            IndexModel([("category", 1)]),
            IndexModel([("project_id", 1), ("name", 1)], unique=True),
        ]
    
    @field_validator('name')
    def validate_name(cls, v):
        """Ensure technology name exists in catalog"""
        if v not in TECHNOLOGY_CATALOG:
            available = list(TECHNOLOGY_CATALOG.keys())
            raise ValueError(f"Unknown technology '{v}'. Available: {available}")
        return v
    
    @field_validator('version')
    def validate_version(cls, v, values):
        """Validate version against catalog"""
        if v == "latest":
            return v
            
        name = values.data.get('name')
        if name and name in TECHNOLOGY_CATALOG:
            available_versions = TECHNOLOGY_CATALOG[name].get('versions', [])
            if available_versions and v not in available_versions:
                raise ValueError(
                    f"Invalid version '{v}' for {name}. Available: {available_versions + ['latest']}"
                )
        return v
    
    def __init__(self, **data):
        super().__init__(**data)
        # Auto-populate metadata from catalog
        if self.name in TECHNOLOGY_CATALOG:
            catalog_info = TECHNOLOGY_CATALOG[self.name]
            if not self.category:
                self.category = catalog_info.get('category')
            if not self.nix_package:
                self.nix_package = catalog_info.get('nix_package', self.name)
            self.available_versions = catalog_info.get('versions', [])
    
    def get_nix_package_name(self) -> str:
        """Get the Nix package name, potentially with version suffix"""
        base_name = self.nix_package or self.name
        if self.version and self.version != "latest":
            # Handle version formatting for Nix (replace dots with nothing)
            version_suffix = self.version.replace('.', '')
            return f"{base_name}_{version_suffix}"
        return base_name
    
    def is_service(self) -> bool:
        """Check if this technology should run as a service"""
        service_categories = ["database", "cache", "queue", "search", "monitoring", "proxy"]
        return self.category and self.category.value in service_categories
    
    def get_devbox_service_config(self) -> Optional[Dict[str, Any]]:
        """Generate devbox service configuration"""
        if not self.is_service():
            return None
            
        config = {
            "command": self.name,
            "env": self.environment_variables or {}
        }
        
        if self.port:
            config["port"] = self.port
            
        if self.configuration:
            config.update(self.configuration)
            
        return config
    
    def __repr__(self) -> str:
        return f"<Technology {self.name}:{self.version} for project {self.project_id}>"

