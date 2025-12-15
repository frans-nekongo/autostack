import asyncio
from enum import Enum
import traceback
import git
import strawberry
import uuid
import structlog
from typing import Any, List, Optional

from autostack_engine.gateway.graphql.resolvers.project.project_query import GitInfo, get_git_info
from autostack_engine.services.orchestration.service.orchestration import OrchestrationService
from autostack_engine.services.project.services.project import ProjectService
from autostack_engine.utils.project.subscription import ProjectCreationStatus, ProjectDeletionStatus
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
        return {key: serialize_enums(value) for key, value in obj.__dict__.items()}
    else:
        return obj

@strawberry.input
class FullProjectInput:
    project: ProjectInput
    technologies: Optional[List[TechnologyInput]] = None
    components: Optional[List[ComponentInput]] = None
    connections: Optional[List[ConnectionInput]] = None
    
@strawberry.type
class InitiateProjectResponse:
    """Response when initiating a project creation operation"""
    success: bool
    operation_id: str
    message: str
    error: Optional[str] = None
  
@strawberry.type
class GitInitialiseResponse:
    success: bool
    git_info: GitInfo
    message: str
    error: Optional[str] = None  
    
def get_operation_store(info: strawberry.Info):
    """Get operation store from GraphQL context"""
    return info.context["operation_store"]


@strawberry.type
class ProjectMutuation:
    @strawberry.mutation
    async def create_full_project_async(self, input: FullProjectInput, info: strawberry.Info) -> InitiateProjectResponse:
        """
        Initiate project creation asynchronously.
        Returns an operation_id to track progress via subscription.
        """
        operation_store = get_operation_store(info)
        
        try:
            operation_id = str(uuid.uuid4())
            await operation_store.create_operation(operation_id)
            
            asyncio.create_task(
                ProjectMutuation._execute_project_creation(
                    operation_id,
                    input,
                    operation_store
                )
            )
            
            return InitiateProjectResponse(
                success=True,
                operation_id=operation_id,
                message=f"Project creation initiated for '{input.project.name}'. Use the operation ID to track progress."
            )
            
                
        except Exception as e:
            logger.error(
                "project_creation_initiation_failed",
                error=str(e),
                traceback=traceback.format_exc()
            )
            return InitiateProjectResponse(
                success=False,
                operation_id="",
                message="Failed to initiate project creation",
                error=str(e)
            )
          
    @staticmethod
    async def _execute_project_creation(
        operation_id: str,
        input: FullProjectInput,
        operation_store  
    ): 
        """
        Background task that performs the actual project creation.
        Updates Redis with progress at each step.
        """
        
        try:
            # Step 1: Validating (10%) - kept in mutation
            await operation_store.update_operation(
                operation_id,
                ProjectCreationStatus.VALIDATING,
                "Validating input data and project configuration",
                10
            )
            
            logger.info(
                "project_creation_validating",
                operation_id=operation_id,
                project_name=input.project.name
            )
            
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
            
            # Execute orchestration with progress tracking
            orchestrator = OrchestrationService()
            success, project_id, error = await orchestrator.orchestrate_full_project(
                input_dict,
                operation_store=operation_store,
                operation_id=operation_id
            )
            
            if success:
                logger.info(
                    "project_creation_completed",
                    operation_id=operation_id,
                    project_id=project_id,
                    project_name=input.project.name
                )
            else:
                logger.error(
                    "project_creation_failed",
                    operation_id=operation_id,
                    error=error,
                    project_name=input.project.name
                )
                
        except Exception as e:
            error_msg = str(e)
            await operation_store.update_operation(
                operation_id,
                ProjectCreationStatus.FAILED,
                "An unexpected error occurred during project creation",
                100,
                error=error_msg
            )
            
            logger.error(
                "project_creation_exception",
                operation_id=operation_id,
                error=error_msg,
                traceback=traceback.format_exc()
            )
    
    @strawberry.mutation
    async def create_full_project(self, input: FullProjectInput) -> ProjectResponse:
        """
        Legacy synchronous project creation.
        Use create_full_project_async for better UX with progress tracking.
        """
        try:
            orchestrator = OrchestrationService()
            
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
        """Generate docker-compose.yml for production."""
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
    async def delete_project_async(self, project_id: str, project_name: str, info: strawberry.Info) -> InitiateProjectResponse:
        operation_store = get_operation_store(info)
        
        try:
            operation_id = str(uuid.uuid4())
            await operation_store.create_operation(operation_id)
            
            logger.info(
                "project_deletion_initiated",
                operation_id=operation_id,
                project_name=project_name
            )
            
            asyncio.create_task(
                self._execute_project_deletion(
                    operation_id,
                    project_id,
                    project_name,
                    operation_store
                )
            )
            
            return InitiateProjectResponse(
                success=True,
                operation_id=operation_id,
                message=f"Project deletion initiated for '{project_name}'. Use the operation ID to track progress."
            )
            
        except Exception as e:
            logger.error(
                "project_deletion_initiation_failed",
                error=str(e),
                traceback=traceback.format_exc()
            )
            return InitiateProjectResponse(
                success=False,
                operation_id="",
                message="Failed to initiate project deletion",
                error=str(e)
            )


    async def _execute_project_deletion(
        self,
        operation_id: str,
        project_id: str,
        project_name: str,
        operation_store  
    ):
        try:
            await operation_store.update_operation(
                operation_id,
                ProjectDeletionStatus.DELETING_PROJECT,
                f"Searching for {project_name} to delete",
                10
            )
            
            service = ProjectService()
            success, error = await service.delete_project(project_id, True)
            
            if success:
                await operation_store.update_operation(
                    operation_id,
                    ProjectDeletionStatus.COMPLETED,
                    f"Successfully deleted project: {project_name}",
                    100
                )
            else:
                await operation_store.update_operation(
                    operation_id,
                    ProjectDeletionStatus.FAILED,
                    f"Error deleting project: {project_name}",
                    100,
                    error=error
                )
                
        except Exception as e:
            error_msg = str(e)
            await operation_store.update_operation(
                operation_id,
                ProjectDeletionStatus.FAILED,
                "An unexpected error occurred during project deletion",
                100,
                error=error_msg
            )
            
            logger.error(
                "project_deletion_exception",
                operation_id=operation_id,
                error=error_msg,
                traceback=traceback.format_exc()
            )
        
    @strawberry.mutation
    async def delete_project(
        self, 
        project_id: str,
        delete_files: bool = False
    ) -> DeleteResponse:
        """Delete a project."""
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
        
    
    @strawberry.mutation
    async def initialise_git(
        self,
        project_id: str
    ) -> GitInitialiseResponse:
        try:
            service = ProjectService()
            result = await service.get_project(project_id=project_id)
            if not result:
                logger.error(f"[GRAPHQL] Project with ID '{project_id}' does not exist.")
                return GitInitialiseResponse(
                    success=False,
                    git_info=None,
                    message="",
                    error=f"Project with ID '{project_id}' does not exist."
                )
            
            project_directory = None
            if result.metadata:
                project_directory = result.metadata.directory
            
            if not project_directory:
                return GitInitialiseResponse(
                    success=False,
                    git_info=None,
                    message="",
                    error="Project directory not found in metadata."
                )
            
            # Initialize git repository
            repository = git.Repo.init(project_directory)
            repository.git.add(A=True)
            repository.index.commit("initial commit")
            
            # Get git info using your existing function
            git_info = get_git_info(project_directory)
            
            return GitInitialiseResponse(
                success=True,
                git_info=git_info,
                message=f"Git repository successfully initialized at {project_directory}",
                error=None
            )
            
        except Exception as e:
            logger.error(f"[GRAPHQL] Error initializing git repository: {str(e)}")
            return GitInitialiseResponse(
                success=False,
                git_info=None,
                message="",
                error=str(e)
            )
        