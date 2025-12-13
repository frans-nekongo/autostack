from enum import Enum
import traceback
import strawberry
import uuid
import structlog
import yaml
from typing import Any, List, Optional
from datetime import datetime

from autostack_engine.services.orchestration.service.orchestration import OrchestrationService
from autostack_engine.services.project.services.project import ProjectService
from autostack_engine.utils.schema.models.components import ComponentInput, ConnectionInput
from autostack_engine.utils.schema.models.environments import ProductionResponse
from autostack_engine.utils.schema.models.generic import DeleteResponse
from autostack_engine.utils.schema.models.projects import ProjectInput, ProjectResponse
from autostack_engine.utils.schema.models.technologies import TechnologyInput


logger = structlog.get_logger()


def serialize_enums(obj: Any) -> Any:
    """Recursively convert enums to their values for JSON serialization."""
    if isinstance(obj, Enum):
        return obj.value
    elif isinstance(obj, dict):
        return {key: serialize_enums(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [serialize_enums(item) for item in obj]
    elif hasattr(obj, '__dict__'):
        # Handle dataclass-like objects
        return {key: serialize_enums(value) for key, value in obj.__dict__.items()}
    else:
        return obj

@strawberry.input
class FullProjectInput:
    project: ProjectInput
    technologies: Optional[List[TechnologyInput]] = None
    components: Optional[List[ComponentInput]] = None
    connections: Optional[List[ConnectionInput]] = None
    
    
def get_operation_store(info: strawberry.Info):
    """Get operation store from GraphQL context"""
    return info.context["operation_store"]


    
@strawberry.type
class ProjectMutuation:
    @strawberry.mutation
    async def create_full_project(self, input: FullProjectInput) -> ProjectResponse:
        """
        Create a complete project with technologies, components, and production config.
        This is the all-in-one mutation that orchestrates everything.
        """
        try:
            orchestrator = OrchestrationService()
            
            # Convert Strawberry input to dict
            input_dict = {
                'project': {
                    'name': input.project.name,
                    'author': input.project.author,
                    'description': input.project.description,
                    'version': input.project.version,
                    'chat_id': input.project.chatId
                }
            }
            
            if input.technologies:
                input_dict['technologies'] = [
                    {
                        'name': t.name,
                        'category': t.category,
                        'version': t.version,
                        'enabled': t.enabled,
                        'port': t.port,
                        'environment_variables': t.environment_variables,
                        'configuration': t.configuration
                    }
                    for t in input.technologies
                ]
            
            if input.components:
                input_dict['components'] = [
                    {
                        'component_id': c.component_id,
                        'type': c.type,
                        'name': c.name,
                        'technology': c.technology,
                        'framework': c.framework,
                        'port': c.port,
                        'environment_variables': c.environment_variables,
                        'dependencies': c.dependencies or []
                    }
                    for c in input.components
                ]
            
            if input.connections:
                input_dict['connections'] = [
                    {
                        'source': conn.source,
                        'target': conn.target,
                        'type': conn.type,
                        'port': conn.port
                    }
                    for conn in input.connections
                ]
            
            success, project_id, error = await orchestrator.orchestrate_full_project(input_dict)
            
            if success:
                return ProjectResponse(
                    success=True,
                    project_id=project_id,
                    message=f"Successfully created project: {input.project.name}"
                )
            else:
                return ProjectResponse(
                    success=False,
                    project_id=project_id,
                    error=error
                )
                
        except Exception as e:
            print(e)
            print(traceback.format_exc())
            return ProjectResponse(
                success=False,
                error=str(e)
            )
            
    @strawberry.mutation
    async def create_project(
        self,
        input: ProjectInput
    ) -> ProjectResponse:
        try:
            orchestrator = OrchestrationService()
            
            project_dict = {
                'name': input.name,
                'author': input.author,
                'description': input.description,
                'version': input.version,
                'environment': input.environment,
                'chat_id': input.chat_id
            }
            
            success, project_id, error = await orchestrator.orchestrate_project_only(project_dict)
            
            if success:
                return ProjectResponse(
                    success=True,
                    project_id=project_id,
                    message=f"Project '{input.name}' created successfully"
                )
            else:
                return ProjectResponse(success=False, error=error)
            
        except Exception as e:
            return ProjectResponse(success=False, error=str(e))
        
    @strawberry.mutation
    async def generate_production_config(self, project_id: str) -> ProductionResponse:
        """
        Generate docker-compose.yml for production.
        
        Example:
        ```graphql
        mutation {
          generateProductionConfig(projectId: "abc-123") {
            success
            composePath
            error
          }
        }
        ```
        """
        try:
            orchestrator = OrchestrationService()
            
            success, compose_path, error = await orchestrator.orchestrate_production_only(project_id)
            
            if success:
                return ProductionResponse(
                    success=True,
                    compose_path=compose_path,
                    message="Production config generated successfully"
                )
            else:
                return ProductionResponse(success=False, error=error)
                
        except Exception as e:
            return ProductionResponse(success=False, error=str(e))
        
    
    @strawberry.mutation
    async def update_project(
        self,
        project_id: str,
        name: Optional[str] = None,
        author: Optional[str] = None,
        description: Optional[str] = None,
        version: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> ProjectResponse:
        """Update project fields"""
        try:
            service = ProjectService()
            
            updates = {}
            if name is not None:
                updates['name'] = name
            if author is not None:
                updates['author'] = author
            if description is not None:
                updates['description'] = description
            if version is not None:
                updates['version'] = version
            if tags is not None:
                updates['metadata'] = {'tags': tags}
            
            success, error = await service.update_project(project_id, updates)
            
            if success:
                return ProjectResponse(
                    success=True,
                    project_id=project_id,
                    message="Project updated successfully"
                )
            else:
                return ProjectResponse(success=False, error=error)
                
        except Exception as e:
            return ProjectResponse(success=False, error=str(e))
        
    @strawberry.mutation
    async def delete_project(
        self, 
        project_id: str,
        delete_files: bool = False
    ) -> DeleteResponse:
        """
        Delete a project.
        """
        try:
            service = ProjectService()
            success, error = await service.delete_project(project_id, delete_files)
            
            if success:
                return DeleteResponse(
                    success=True,
                    message=f"Project deleted successfully"
                )
            else:
                return DeleteResponse(success=False, error=error)
                
        except Exception as e:
            return DeleteResponse(success=False, error=str(e))
    
    
        