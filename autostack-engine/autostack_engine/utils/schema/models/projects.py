import strawberry
from typing import Optional, List
from datetime import datetime
from enum import Enum

from autostack_engine.utils.schema.models.components import ComponentInput, ConnectionInput
from autostack_engine.utils.schema.models.environments import EnvironmentInput
from autostack_engine.utils.schema.models.technologies import TechnologyInput


@strawberry.input
class ProjectMetadataInput:
    created_date: Optional[str] = None
    last_modified: Optional[str] = None
    tags: Optional[List[str]] = None
    environment: Optional[str] = None
    directory: Optional[str] = None

@strawberry.input
class ProjectInput:
    name: str
    author: Optional[str] = None
    description: Optional[str] = None
    version: str = "1.0.0"
    status: Optional[str] = "created"
    metadata: Optional[ProjectMetadataInput] = None
    chatId: Optional[str] = None

@strawberry.input
class ProjectConfigInput:
    project: ProjectInput
    technologies: Optional[List[TechnologyInput]] = None
    environments: Optional[List[EnvironmentInput]] = None
    components: Optional[List[ComponentInput]] = None
    connections: Optional[List[ConnectionInput]] = None
    
@strawberry.type
class ProjectResponse:
    success: bool
    project_id: Optional[str] = None
    error: Optional[str] = None
    message: Optional[str] = None
        


