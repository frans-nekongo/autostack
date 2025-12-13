from uuid import UUID
import uuid
from beanie import Document
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from datetime import datetime
from pymongo import IndexModel
from enum import Enum
import logging

from autostack_engine.utils.constants import TECHNOLOGY_CATALOG
from autostack_engine.utils.database.models.components.models import Component, Connection, Environment
from autostack_engine.utils.database.models.technologies.models import Technology


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ProjectStatus(str, Enum):
    CREATED = "created"
    PROVISIONING = "provisioning" 
    DEVELOPING = "developing"
    DEPLOYING = "deploying"
    DEPLOYED = "deployed"
    FAILED = "failed"


class ProjectMetadata(BaseModel):
    created_date: Optional[str] = None
    last_modified: Optional[str] = None
    tags: Optional[List[str]] = None
    environment: Optional[str] = None
    directory: Optional[str] = None


class Resources(BaseModel):
    default_memory: Optional[str] = None
    memory: Optional[str] = None
    cpu: Optional[str] = None
    storage: Optional[str] = None


class Project(Document):
    id: UUID = Field(default_factory=uuid.uuid4, alias="_id")
    chat_id: Optional[UUID] = Field(default=None, index=True)
    name: str = Field(..., index=True, unique=True)
    author: Optional[str] = None
    description: Optional[str] = None
    version: str = "1.0.0"
    avatar_data: Optional[str] = None
    avatar_hash: Optional[str] = None
    status: ProjectStatus = ProjectStatus.CREATED
    metadata: Optional[ProjectMetadata] = None
    
    # Audit fields
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    class Settings:
        name = "projects"
        indexes = [
            IndexModel([("name", 1)], unique=True),
            IndexModel([("status", 1)]),
            IndexModel([("chat_id", 1)]),
            IndexModel([("created_at", -1)]),
            IndexModel([("updated_at", -1)]),
        ]
    
    def __repr__(self) -> str:
        return f"<Project {self.name} v{self.version}>"

# Helper class for managing project relationships
class ProjectManager:
    
    @staticmethod
    async def get_full_project(project_id: UUID) -> Dict[str, Any]:
        """Get project with all related documents"""
        project = await Project.get(project_id)
        if not project:
            return None
        
        # Get all related documents in parallel
        technologies = await Technology.find({"project_id": project_id}).to_list()
        environments = await Environment.find({"project_id": project_id}).to_list()
        components = await Component.find({"project_id": project_id}).to_list()
        connections = await Connection.find({"project_id": project_id}).to_list()
        
        return {
            "project": project,
            "technologies": technologies,
            "environments": environments,
            "components": components,
            "connections": connections,
        }
        
        
    @staticmethod
    async def delete_project_cascade(project_id: UUID) -> bool:
        """Delete project and all related documents"""
        try:
            # Delete in reverse dependency order
            await Connection.find({"project_id": project_id}).delete()
            await Component.find({"project_id": project_id}).delete()
            await Environment.find({"project_id": project_id}).delete()
            await Technology.find({"project_id": project_id}).delete()
            await Project.get(project_id).delete()
            return True
        except Exception as e:
            logger.error(f"Error deleting project {project_id}: {e}")
            return False
        
    @staticmethod
    async def get_project_technologies(project_id: UUID) -> List[Technology]:
        """Get all technologies for a project"""
        return await Technology.find({"project_id": project_id, "enabled": True}).to_list()
    
    @staticmethod
    async def generate_devbox_config(project_id: UUID) -> Dict[str, Any]:
        """Generate devbox.json configuration for a project"""
        technologies = await ProjectManager.get_project_technologies(project_id)
        
        packages = []
        services = {}
        
        for tech in technologies:
            # Add package
            packages.append(tech.get_nix_package_name())
            
            # Add service if applicable
            service_config = tech.get_devbox_service_config()
            if service_config:
                services[tech.name] = service_config
        
        return {
            "packages": packages,
            "services": services,
            "shell": {
                "init_hook": [
                    "echo 'Development environment ready!'",
                    "echo 'Available services: {}'".format(', '.join(services.keys()))
                ]
            }
        }
    
    @staticmethod
    async def generate_nix_packages(project_id: UUID) -> List[str]:
        """Generate list of Nix packages for production deployment"""
        technologies = await ProjectManager.get_project_technologies(project_id)
        return [tech.get_nix_package_name() for tech in technologies]
    
    @staticmethod
    async def add_technology_to_project(
        project_id: UUID,
        name: str,
        version: str = "latest",
        port: Optional[int] = None,
        environment_variables: Optional[Dict[str, Any]] = None,
        configuration: Optional[Dict[str, Any]] = None
    ) -> Technology:
        """Add a technology to a project"""
        technology = Technology(
            project_id=project_id,
            name=name,
            version=version,
            port=port,
            environment_variables=environment_variables,
            configuration=configuration
        )
        return await technology.insert()
    
    @staticmethod
    async def get_technology_suggestions() -> Dict[str, Any]:
        """Get available technologies with their metadata"""
        return {
            name: {
                "category": info["category"],
                "versions": info["versions"],
                "nix_package": info["nix_package"]
            }
            for name, info in TECHNOLOGY_CATALOG.items()
        }