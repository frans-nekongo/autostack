import traceback
import git
import strawberry
import uuid
import structlog
import yaml
from typing import Optional, List
from datetime import datetime

from autostack_engine.services.project.services.project import ProjectService
from autostack_engine.utils.database.models.project.models import Project
from autostack_engine.utils.database.models.components.models import Component, Connection
from autostack_engine.utils.database.models.technologies.models import Technology
from autostack_engine.utils.database.mongo_client import DatabaseManager

logger = structlog.get_logger()

# Define output types for your queries
@strawberry.type
class ProjectMetadata:
    created_date: Optional[str] = None
    last_modified: Optional[str] = None
    tags: Optional[List[str]] = None
    environment: Optional[str] = None
    directory: Optional[str] = None

@strawberry.type
class GitInfo:
    latest_commit: Optional[str] = None
    branch: Optional[str] = None
    is_dirty: Optional[bool] = None
    commits: Optional[List[str]] = None  # Fixed: Added type annotation and default

@strawberry.type
class ProjectInfo:
    id: str
    name: str
    author: Optional[str] = None
    description: Optional[str] = None
    version: str = "1.0.0"
    status: Optional[str] = "created"
    metadata: Optional[ProjectMetadata] = None
    git_info: Optional[GitInfo] = None
    

@strawberry.type
class ProjectArchitectureResponse:
    success: bool
    data: Optional[strawberry.scalars.JSON] = None # type: ignore
    error: Optional[str] = None
    message: Optional[str] = None
    
    
def get_git_info(directory: Optional[str]) -> Optional[GitInfo]:
    """Get Git repository information safely."""
    if not directory:
        return None
        
    try:
        repository = git.Repo(directory)
        
        # Get commits (limited to recent ones for performance)
        commits = []
        try:
            # Limit to 10 most recent commits to avoid performance issues
            for commit in repository.iter_commits(max_count=10):
                commits.append(commit.hexsha)
        except Exception as commit_error:
            logger.warning(f"Could not fetch commits: {commit_error}")
            commits = None
        
        return GitInfo(
            latest_commit=repository.head.commit.hexsha[:8] if repository.head.commit else None,
            branch=repository.active_branch.name if repository.branches else None,
            is_dirty=repository.is_dirty(),
            commits=commits
        )
    except (git.InvalidGitRepositoryError, git.NoSuchPathError):
        logger.debug(f"No Git repository found at {directory}")
        return None
    except Exception as e:
        logger.error(f"Error reading Git repository at {directory}: {e}")
        return None

@strawberry.type
class ProjectQuery:
    @strawberry.field
    async def fetch_project(
        self,
        project_id: str,
    ) -> Optional[ProjectInfo]:
        """Fetch a project by the project ID"""
        service = ProjectService()
        result = await service.get_project(project_id=project_id)
        
        if not result:
            logger.error(f"[GRAPHQL] Project with ID '{project_id}' does not exist.")
            return None
        
        metadata = None
        project_directory = None
        
        if result.metadata:
            metadata = ProjectMetadata(
                created_date=result.metadata.created_date,
                last_modified=result.metadata.last_modified,
                tags=result.metadata.tags,
                environment=result.metadata.environment,
                directory=result.metadata.directory
            )
            project_directory = result.metadata.directory
        
        # Get git info safely
        git_info = get_git_info(project_directory)
        
        return ProjectInfo(
            id=result.id,
            name=result.name,
            author=result.author,
            description=result.description,
            version=result.version,
            status=result.status.value if hasattr(result.status, 'value') else result.status,
            metadata=metadata,
            git_info=git_info
        )
        
    @strawberry.field
    async def fetch_all_projects() -> List[Optional[ProjectInfo]]:
        try:
            service = ProjectService()
            result = await service.list_projects()
            
            # Handle both return types - direct list or (success, error) tuple
            if isinstance(result, tuple) and len(result) == 2:
                success, projects_or_error = result
                if success:
                    projects = projects_or_error
                else:
                    logger.error(f"Error listing projects: {projects_or_error}")
                    return []
            else:
                # Assume result is directly the list of projects
                projects = result
            
            if projects:
                project_infos = []
                count = 0
                for project in projects:
                    
                    git_info = get_git_info(project.metadata.directory)
                    
                    project_info = ProjectInfo(
                        id=project.id,
                        name=project.name,
                        author=project.author,
                        description=project.description,
                        version=project.version,
                        status=project.status.value if project.status else "created",
                        metadata=project.metadata,
                        git_info=git_info
                    )
                    project_infos.append(project_info)
                    count += 1
                    
                    if count == 4:
                        break
                
                return project_infos
            else:
                return []
                
        except Exception as e:
            logger.error(f"Error fetching all projects: {e}")
            return []
        
    @strawberry.field
    async def fetch_project_architecture(self, project_id: str) -> ProjectArchitectureResponse:
        """
        Fetch complete project architecture including technologies, components, and connections
        Returns consolidated JSON format for C4 diagram generation
        """
        try:
            db = DatabaseManager()
            await db.connect([Project, Connection, Component, Technology])
            project = await Project.get(project_id)
            
            if not project:
                return ProjectArchitectureResponse(
                    success=False,
                    error="Project not found",
                    message=f"No project found with ID: {project_id}"
                )
            
            # Build technologies list
            technologies = await Technology.find({'project_id': uuid.UUID(project_id)}).to_list()
            components = await Component.find({'project_id': uuid.UUID(project_id)}).to_list()
            connections = await Connection.find({'project_id': uuid.UUID(project_id)}).to_list()
            
            
            # Consolidated architecture data
            architecture_data = {
                "project_id": project_id,
                "project_name": getattr(project, 'name', project_id),
                "technologies": [tech.model_dump(mode='json') for tech in technologies],
                "components": [comp.model_dump(mode='json') for comp in components],
                "connections": [conn.model_dump(mode='json') for conn in connections],
                "metadata": {
                    "component_count": len(components),
                    "connection_count": len(connections),
                    "technology_count": len(technologies)
                }
            }
            
            return ProjectArchitectureResponse(
                success=True,
                data=architecture_data,
                message="Architecture fetched successfully"
            )
            
        except Exception as e:
            print(traceback.format_exc())
            return ProjectArchitectureResponse(
                success=False,
                error=str(e),
                message="Failed to fetch project architecture"
            )
            
        