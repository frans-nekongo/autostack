import traceback
import git
import strawberry
import uuid
import structlog
import yaml
from typing import Optional, List
from datetime import datetime

from autostack_engine.services.component.services.components import ComponentService
from autostack_engine.services.project.services.project import ProjectService
from autostack_engine.utils.database.models.project.models import Project
from autostack_engine.utils.database.models.components.models import Component, Connection
from autostack_engine.utils.database.models.technologies.models import Technology
from autostack_engine.utils.database.mongo_client import DatabaseManager
from autostack_engine.utils.project.icon_generator import IdenticonGenerator

logger = structlog.get_logger()


@strawberry.type
class ComponentInfo:
    component_id: str
    name: str
    framework: Optional[str] = None
    technology: str
    dependencies: Optional[List[str]]

@strawberry.type
class ComponentsResponse:
    project_id: str
    components: List[ComponentInfo]
    success: bool
    error: Optional[str] = None
    message: Optional[str] = None
    


@strawberry.type
class ComponentsQuery:
    @strawberry.field
    async def fetch_project_components(
        self,
        project_id: str,
    ) -> Optional[ComponentsResponse]:
        """Fetch a project by the project ID"""
        try:
            service = ComponentService()
            result = await service.list_components(project_id=project_id)
            
            if not result:
                logger.error(f"[GRAPHQL] Components for project with ID '{project_id}' do not exist.")
                return ComponentsResponse(
                    project_id=project_id,
                    components=[],
                    success=False,
                    error="Components not found",
                    message=f"No components found for project {project_id}"
                )
            
            if result:
                component_infos = []
                for component in result:
                    try:
                        component_info = ComponentInfo(
                            component_id=component.component_id,
                            name=component.name,
                            framework=component.framework.value if component.framework else None,
                            technology=component.technology or "",
                            dependencies=component.dependencies
                        )
                        component_infos.append(component_info)
                    except AttributeError as ae:
                        logger.error(f"[GRAPHQL] Missing attribute in component {component.component_id}: {str(ae)}")
                        continue
                    except Exception as e:
                        logger.error(f"[GRAPHQL] Error processing component {component.component_id}: {str(e)}")
                        continue
                
                return ComponentsResponse(
                    project_id=project_id,
                    components=component_infos,
                    success=True,
                    error=None,
                    message=f"Successfully fetched {len(component_infos)} components"
                )
        
        except ConnectionError as ce:
            logger.error(f"[GRAPHQL] Database connection error: {str(ce)}")
            return ComponentsResponse(
                project_id=project_id,
                components=[],
                success=False,
                error="Database connection failed",
                message="Unable to connect to the database"
            )
        
        except TimeoutError as te:
            logger.error(f"[GRAPHQL] Request timeout for project {project_id}: {str(te)}")
            return ComponentsResponse(
                project_id=project_id,
                components=[],
                success=False,
                error="Request timeout",
                message="The request took too long to complete"
            )
        
        except Exception as e:
            logger.error(f"[GRAPHQL] Unexpected error fetching components for project {project_id}: {str(e)}")
            return ComponentsResponse(
                project_id=project_id,
                components=[],
                success=False,
                error="Internal server error",
                message=f"An unexpected error occurred: {str(e)}"
            )
        

            
    
    
        