import traceback
from typing import Any, Dict, Optional
from uuid import uuid4

import better_exceptions
import structlog


# Service Imports
from autostack_engine.services.environment.services.technologies import TechnologyService
from autostack_engine.services.project.services.project import ProjectService
from autostack_engine.services.component.services.components import ComponentService
from autostack_engine.services.environment.services.production import ProductionService
from autostack_engine.utils.orchestration.models import BaseService


better_exceptions.hook()
logger = structlog.get_logger()


class OrchestrationService(BaseService):
    """
    Main orchestration service that coordinates all other services.
    Handles complete project creation workflow.
    """
    
    service_name = "ORCHESTRATION"
    
    def __init__(self):
        super().__init__()
        self.project_service = ProjectService()
        self.technology_service = TechnologyService()
        self.component_service = ComponentService()
        self.production_service = ProductionService()
    
    def validate_input(self, data: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """Validate input data structure"""
        if not data.get('project'):
            return False, "Missing 'project' data"
        
        project = data['project']
        if not project.get('name'):
            return False, "Project name is required"
        
        return True, None
    
    def transform_project_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform input data for project creation"""
        project = data['project']
        
        project_id = project.get('id') or str(uuid4())
        return {
            'id': project_id,
            'name': project['name'],
            'author': project.get('author', 'Unknown'),
            'description': project.get('description', ''),
            'version': project.get('version', '1.0.0'),
            'metadata': {
                'tags': project.get('tags', []),
                'environment': project.get('environment', 'development')
            },
            'chat_id': project.get('chat_id', '')
            
        }
    
    def transform_technologies_data(self, data: Dict[str, Any], project_id: str) -> list[Dict[str, Any]]:
        """Transform technologies data"""
        technologies = data.get('technologies', [])
        
        transformed = []
        for tech in technologies:
            tech_data = {
                'id': tech.get('id', str(uuid4())),
                'project_id': project_id,
                'name': tech['name'],
                'category': tech.get('type', tech.get('category', 'OTHER')),
                'version': tech.get('version', 'latest'),
                'enabled': tech.get('enabled', True),
                'port': tech.get('port'),
                'environment_variables': tech.get('environment_variables', {}),
                'configuration': tech.get('configuration')
            }
            transformed.append(tech_data)
        
        return transformed
    
    def transform_components_data(self, data: Dict[str, Any], project_id: str) -> tuple[list, list]:
        """Transform components and connections data"""
        components = data.get('components', [])
        connections = data.get('connections', [])
        
        # Transform components
        transformed_components = []
        for comp in components:
            comp_data = {
                'id': comp.get('component_id', comp.get('id', str(uuid4()))),
                'project_id': project_id,
                'name': comp['name'],
                'type': comp.get('type', 'SERVICE'),
                'technology': comp.get('technology', 'python'),
                'framework': comp.get('framework'),
                'port': comp.get('port'),
                'environment_variables': comp.get('environment_variables', {}),
                'volumes': comp.get('volumes', []),
                'dependencies': comp.get('dependencies', [])
            }
            transformed_components.append(comp_data)
        
        # Transform connections
        transformed_connections = []
        for conn in connections:
            conn_data = {
                'id': conn.get('id', str(uuid4())),
                'project_id': project_id,
                'source': conn.get('source'),
                'target': conn.get('target'),
                'type': conn.get('type'),
                'port': conn.get('port')
            }
            transformed_connections.append(conn_data)
        
        return transformed_components, transformed_connections
    
    async def orchestrate_full_project(self, input_data: Dict[str, Any]) -> tuple[bool, Optional[str], Optional[str]]:
        """
        Execute the complete project creation workflow.
        
        Steps:
        1. Create project directory and database record
        2. Setup development environment with technologies (devbox)
        3. Create components and connections
        4. Generate production docker-compose configuration
        
        Args:
            input_data: Complete project specification
            
        Returns:
            tuple: (success: bool, project_id: Optional[str], error_message: Optional[str])
        """
        project_id = None
        
        try:
            # Validate input
            is_valid, error_msg = self.validate_input(input_data)
            if not is_valid:
                self.log_error(f"Invalid input: {error_msg}")
                return False, None, error_msg
            
            self.log_info("========================================")
            self.log_info(f"Beginning orchestration for: {input_data['project']['name']}")
            self.log_info("========================================")
            
            # Step 1: Create Project
            self.log_info("Step 1/4: Creating project...")
            project_data = self.transform_project_data(input_data)
            
            success, project_id, error = await self.project_service.create_project(project_data)
            if not success:
                self.log_error(f"Failed to create project: {error}")
                return False, None, error
            
            self.log_info(f"✓ Project '{project_data['name']}' created with ID: {project_id}")
            
            # Step 2: Setup Development Environment (Technologies)
            if input_data.get('technologies'):
                self.log_info("Step 2/4: Setting up development environment...")
                tech_data = self.transform_technologies_data(input_data, project_id)
                
                success, tech_ids, error = await self.technology_service.create_technologies(
                    project_id, tech_data, initialize_devbox=True
                )
                if not success:
                    self.log_error(f"Failed to create technologies: {error}")
                    return False, project_id, error
                
                self.log_info(f"✓ Development environment configured with {len(tech_ids)} technologies")
            else:
                self.log_info("Step 2/4: Skipped (no technologies specified)")
            
            # Step 3: Create Components and Connections
            if input_data.get('components'):
                self.log_info("Step 3/4: Creating components and connections...")
                comp_data, conn_data = self.transform_components_data(input_data, project_id)
                
                success, comp_ids, error = await self.component_service.create_components(
                    project_id, comp_data, conn_data, initialize_locally=True
                )
                if not success:
                    self.log_error(f"Failed to create components: {error}")
                    return False, project_id, error
                
                self.log_info(f"✓ Created {len(comp_ids)} components with {len(conn_data)} connections")
            else:
                self.log_info("Step 3/4: Skipped (no components specified)")
            
            # Step 4: Generate Production Configuration
            if input_data.get('components') and input_data.get('technologies'):
                self.log_info("Step 4/4: Generating production configuration...")
                
                success, compose_path, error = await self.production_service.generate_docker_compose(project_id)
                if not success:
                    self.log_error(f"Failed to generate docker-compose: {error}")
                    return False, project_id, error
                
                self.log_info(f"✓ Production docker-compose.yml generated at {compose_path}")
            else:
                self.log_info("Step 4/4: Skipped (requires both components and technologies)")
            
            self.log_info("========================================")
            self.log_info(f"✓✓✓ Successfully orchestrated project '{project_data['name']}' (ID: {project_id})")
            self.log_info("========================================")
            
            return True, project_id, None
            
        except Exception as e:
            error_msg = f"Orchestration failed at project_id={project_id}: {str(e)}"
            self.log_error(error_msg)
            self.log_error(traceback.format_exc())
            return False, project_id, error_msg
    
    async def orchestrate_project_only(self, project_data: Dict[str, Any]) -> tuple[bool, Optional[str], Optional[str]]:
        """Create only the project (for GraphQL project.create mutation)"""
        try:
            transformed = self.transform_project_data({'project': project_data})
            return await self.project_service.create_project(transformed)
        except Exception as e:
            error_msg = f"Failed to create project: {str(e)}"
            self.log_error(error_msg)
            return False, None, error_msg
    
    async def orchestrate_technologies_only(
        self, 
        project_id: str, 
        technologies: list[Dict[str, Any]]
    ) -> tuple[bool, Optional[list[str]], Optional[str]]:
        """Add technologies to existing project (for GraphQL technologies.create mutation)"""
        try:
            return await self.technology_service.create_technologies(
                project_id, technologies, initialize_devbox=True
            )
        except Exception as e:
            error_msg = f"Failed to create technologies: {str(e)}"
            self.log_error(error_msg)
            return False, None, error_msg
    
    async def orchestrate_components_only(
        self,
        project_id: str,
        components: list[Dict[str, Any]],
        connections: Optional[list[Dict[str, Any]]] = None
    ) -> tuple[bool, Optional[list[str]], Optional[str]]:
        """Add components to existing project (for GraphQL components.create mutation)"""
        try:
            return await self.component_service.create_components(
                project_id, components, connections, initialize_locally=True
            )
        except Exception as e:
            error_msg = f"Failed to create components: {str(e)}"
            self.log_error(error_msg)
            return False, None, error_msg
    
    async def orchestrate_production_only(self, project_id: str) -> tuple[bool, Optional[str], Optional[str]]:
        """Generate production config for existing project (for GraphQL production.generate mutation)"""
        try:
            return await self.production_service.generate_docker_compose(project_id)
        except Exception as e:
            error_msg = f"Failed to generate production config: {str(e)}"
            self.log_error(error_msg)
            return False, None, error_msg
                
            
