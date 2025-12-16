from uuid import UUID
import uuid
from beanie import Document
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from datetime import datetime
from pymongo import IndexModel
from enum import Enum

class ComponentType(str, Enum):
    DATABASE = "database"
    CACHE = "cache"
    API = "api"
    WEB = "web"
    GATEWAY = "gateway"
    EXTERNAL = "external"

class ComponentStatus(str, Enum):
    PENDING = "pending"
    SCAFFOLDING = "scaffolding"
    RUNNING = "running"
    FAILED = "failed"

class Framework(str, Enum):
    # Backend frameworks
    DJANGO = "django"
    FLASK = "flask"
    FASTAPI = "fastapi"
    EXPRESS = "express"
    NESTJS = "nestjs"
    
    # Frontend frameworks
    REACT = "react"
    NEXTJS = "nextjs"
    ANGULAR = "angular"
    VUE = "vue"
    SVELTE = "svelte"
    
    
    # No framework
    VANILLA = "vanilla"
    NONE = "none"

class Component(Document):
    id: UUID = Field(default_factory=uuid.uuid4, alias="_id")
    project_id: UUID = Field(..., index=True)
    component_id: str  # User-defined ID like "user-db", "auth-api"
    type: ComponentType
    name: str
    technology: Optional[str] = None  # References technology name (e.g., "node", "python")
    framework: Optional[Framework] = None  # Framework for the component
    port: Optional[int] = None
    environment_variables: Optional[Dict[str, Any]] = None
    dependencies: Optional[List[str]] = None  # List of component_ids this depends on
    status: ComponentStatus = ComponentStatus.PENDING
    
    # Path information
    directory: Optional[str] = None  # Relative path from project root
    
    # Audit fields
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    class Settings:
        name = "components"
        indexes = [
            IndexModel([("project_id", 1)]),
            IndexModel([("component_id", 1)]),
            IndexModel([("type", 1)]),
            IndexModel([("framework", 1)]),
            IndexModel([("project_id", 1), ("component_id", 1)], unique=True),
        ]
    
    def requires_scaffolding(self) -> bool:
        """Check if this component needs framework scaffolding"""
        return self.framework and self.framework not in [Framework.VANILLA, Framework.NONE]
    
    def get_scaffold_command(self) -> Optional[str]:
        """Get the command to scaffold this framework"""
        if not self.requires_scaffolding():
            return None
        
        scaffold_commands = {
            # Backend
            Framework.DJANGO: "django-admin startproject {name} .",
            Framework.FLASK: None,  
            Framework.FASTAPI: None,  
            Framework.EXPRESS: "npx express-generator {name}",
            Framework.NESTJS: "npx @nestjs/cli new {name} --skip-git",
            
            # Frontend
            Framework.REACT: "npx create-react-app {name}",
            Framework.NEXTJS: "npx create-next-app@latest {name} --typescript --tailwind --app --no-src-dir",
            Framework.ANGULAR: "npx @angular/cli new {name} --skip-git",
            Framework.VUE: "npx create-vue@latest {name}",
            Framework.SVELTE: "npx create-svelte@latest {name}",
            
        }
        
        cmd = scaffold_commands.get(self.framework)
        if cmd:
            return cmd.format(name=self.component_id.replace('-', '_'))
        return None
    
    def get_required_devbox_packages(self) -> List[str]:
        """Get devbox packages required for this framework"""
        if not self.framework or self.framework in [Framework.VANILLA, Framework.NONE]:
            return []
        
        package_map = {
            # Backend
            Framework.DJANGO: ["python", "pip"],
            Framework.FLASK: ["python", "pip"],
            Framework.FASTAPI: ["python", "pip"],
            Framework.EXPRESS: ["nodejs", "npm"],
            Framework.NESTJS: ["nodejs", "npm"],
            
            # Frontend
            Framework.REACT: ["nodejs", "npm"],
            Framework.NEXTJS: ["nodejs", "npm"],
            Framework.ANGULAR: ["nodejs", "npm"],
            Framework.VUE: ["nodejs", "npm"],
            Framework.SVELTE: ["nodejs", "npm"],
            
        }
        
        return package_map.get(self.framework, [])
    
    def __repr__(self) -> str:
        return f"<Component {self.component_id}:{self.name} ({self.framework or 'no framework'})>"

class Connection(Document):
    id: UUID = Field(default_factory=uuid.uuid4, alias="_id")
    project_id: UUID = Field(..., index=True)
    source: str  # component_id
    target: str  # component_id
    type: str = "api"  # api, database, cache
    port: Optional[int] = None
    
    # Audit fields
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "connections"
        indexes = [
            IndexModel([("project_id", 1)]),
            IndexModel([("source", 1)]),
            IndexModel([("target", 1)]),
        ]
    
    def __repr__(self) -> str:
        return f"<Connection {self.source} -> {self.target}>"

class Environment(Document):
    id: UUID = Field(default_factory=uuid.uuid4, alias="_id")
    project_id: UUID = Field(..., index=True)
    name: str  # "development", "production"
    type: str  # "local", "vm"
    
    # Audit fields
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "environments"
        indexes = [
            IndexModel([("project_id", 1)]),
            IndexModel([("name", 1)]),
            IndexModel([("project_id", 1), ("name", 1)], unique=True),
        ]
    
    def __repr__(self) -> str:
        return f"<Environment {self.name} for project {self.project_id}>"


class ComponentManager:
    @staticmethod
    async def get_project_components(project_id: UUID) -> List[Component]:
        """Get all components for a project"""
        return await Component.find({"project_id": project_id}).to_list()
    
    @staticmethod
    async def get_project_connections(project_id: UUID) -> List[Connection]:
        """Get all connections for a project"""
        return await Connection.find({"project_id": project_id}).to_list()
    
    @staticmethod
    async def create_component(
        project_id: UUID,
        component_id: str,
        name: str,
        component_type: ComponentType,
        technology: Optional[str] = None,
        framework: Optional[Framework] = None,
        port: Optional[int] = None,
        environment_variables: Optional[Dict[str, Any]] = None,
        dependencies: Optional[List[str]] = None,
        directory: Optional[str] = None
    ) -> Component:
        """Create a new component"""
        component = Component(
            project_id=project_id,
            component_id=component_id,
            type=component_type,
            name=name,
            technology=technology,
            framework=framework,
            port=port,
            environment_variables=environment_variables,
            dependencies=dependencies or [],
            directory=directory
        )
        return await component.insert()
    
    @staticmethod
    async def create_connection(
        project_id: UUID,
        source: str,
        target: str,
        connection_type: str = "api",
        port: Optional[int] = None
    ) -> Connection:
        """Create a connection between components"""
        connection = Connection(
            project_id=project_id,
            source=source,
            target=target,
            type=connection_type,
            port=port
        )
        return await connection.insert()
    
    @staticmethod
    async def update_component_status(component_id: str, status: ComponentStatus) -> bool:
        """Update component status"""
        component = await Component.find_one({"component_id": component_id})
        if component:
            component.status = status
            component.updated_at = datetime.utcnow()
            await component.save()
            return True
        return False
    
    @staticmethod
    async def generate_project_architecture(project_id: UUID) -> Dict[str, Any]:
        """Generate a simple architecture overview"""
        components = await ComponentManager.get_project_components(project_id)
        connections = await ComponentManager.get_project_connections(project_id)
        
        return {
            "components": [
                {
                    "id": comp.component_id,
                    "name": comp.name,
                    "type": comp.type.value,
                    "technology": comp.technology,
                    "framework": comp.framework.value if comp.framework else None,
                    "port": comp.port,
                    "dependencies": comp.dependencies,
                    "status": comp.status.value
                }
                for comp in components
            ],
            "connections": [
                {
                    "source": conn.source,
                    "target": conn.target,
                    "type": conn.type
                }
                for conn in connections
            ]
        }