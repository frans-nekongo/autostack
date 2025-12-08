from typing import Dict, Any, Optional, List
from autostack_engine.utils.schema.models.components import ComponentInput, ConnectionInput
from autostack_engine.utils.schema.models.environments import EnvironmentInput
from autostack_engine.utils.schema.models.projects import ProjectConfigInput, ProjectInfoInput
from autostack_engine.utils.schema.models.technologies import TechnologyInput


class ProjectConfigHelper:
    """
    Helper class to work with GraphQL ProjectConfigInput similar to ArchitectureConfigParser
    """
    
    def __init__(self, config_input: ProjectConfigInput):
        self.config = config_input
        self._build_component_dict()
        self._build_connection_dict()
        self._build_technology_dict()
        self._build_environment_dict()
    
    def _build_component_dict(self):
        """Build a dictionary of components for easy lookup"""
        self.components = {}
        if self.config.components:
            for comp in self.config.components:
                self.components[comp.id] = comp
    
    def _build_connection_dict(self):
        """Build a dictionary of connections for easy lookup"""
        self.connections = {}
        if self.config.connections:
            for conn in self.config.connections:
                self.connections[conn.id] = conn
    
    def _build_technology_dict(self):
        """Build a dictionary of technologies for easy lookup"""
        self.technologies = {}
        if self.config.technologies:
            for tech in self.config.technologies:
                self.technologies[tech.name] = tech
    
    def _build_environment_dict(self):
        """Build a dictionary of environments for easy lookup"""
        self.environments = {}
        if self.config.environments:
            for env in self.config.environments:
                self.environments[env.name] = env
    
    # Project Information Methods
    def get_project_info(self) -> ProjectInfoInput:
        """Get project information"""
        return self.config.project
    
    def get_project_name(self) -> str:
        """Get project name"""
        return self.config.project.name
    
    def get_project_version(self) -> str:
        """Get project version"""
        return self.config.project.version
    
    def get_technologies(self) -> Optional[Dict[str, TechnologyInput]]:
        """Get all configured technologies"""
        return self.technologies if self.technologies else None
    
    def get_technology(self, tech_name: str) -> Optional[TechnologyInput]:
        """Get specific technology configuration"""
        return self.technologies.get(tech_name)
    
    # Environment Methods
    def get_environments(self) -> Optional[Dict[str, EnvironmentInput]]:
        """Get all environment configurations"""
        return self.environments if self.environments else None
    
    def get_environment(self, env_name: str) -> Optional[EnvironmentInput]:
        """Get specific environment configuration"""
        return self.environments.get(env_name)
    
    # Component Methods
    def get_all_components(self) -> Dict[str, ComponentInput]:
        """Get all components"""
        return self.components
    
    def get_component(self, component_id: str) -> Optional[ComponentInput]:
        """Get specific component by ID"""
        return self.components.get(component_id)
    
    def get_components_by_type(self, component_type: str) -> List[ComponentInput]:
        """Get all components of a specific type"""
        return [comp for comp in self.components.values() if comp.type == component_type]
    
    def get_components_by_technology(self, technology: str) -> List[ComponentInput]:
        """Get all components using a specific technology"""
        return [comp for comp in self.components.values() if comp.technology == technology]
    
    def get_microservices(self) -> List[ComponentInput]:
        """Get all microservice components"""
        return self.get_components_by_type('microservice')
    
    def get_databases(self) -> List[ComponentInput]:
        """Get all database components"""
        return self.get_components_by_type('database')
    
    def get_caches(self) -> List[ComponentInput]:
        """Get all cache components"""
        return self.get_components_by_type('cache')
    
    def get_external_services(self) -> List[ComponentInput]:
        """Get all external service components"""
        return self.get_components_by_type('external_service')
    
    def get_component_port(self, component_id: str) -> Optional[int]:
        """Get port for a specific component"""
        component = self.get_component(component_id)
        if component and component.properties:
            return component.properties.get('port')
        return None
    
    
    # Connection Methods
    def get_all_connections(self) -> Dict[str, ConnectionInput]:
        """Get all connections"""
        return self.connections
    
    def get_connection(self, connection_id: str) -> Optional[ConnectionInput]:
        """Get specific connection by ID"""
        return self.connections.get(connection_id)
    
    def get_connections_from_component(self, component_id: str) -> List[ConnectionInput]:
        """Get all connections originating from a component"""
        return [conn for conn in self.connections.values() if conn.source == component_id]
    
    def get_connections_to_component(self, component_id: str) -> List[ConnectionInput]:
        """Get all connections targeting a component"""
        return [conn for conn in self.connections.values() if conn.target == component_id]
    
    def get_connections_by_type(self, connection_type: str) -> List[ConnectionInput]:
        """Get connections by type"""
        return [conn for conn in self.connections.values() if conn.type == connection_type]
    
    # Security Methods
    def get_security_config(self) -> Optional[Dict[str, Any]]:
        """Get global security configuration"""
        return self.config.security
    
    def get_components_with_encryption(self) -> List[ComponentInput]:
        """Get components with encryption enabled"""
        encrypted_components = []
        for component in self.components.values():
            if (hasattr(component, 'security') and component.security and 
                hasattr(component.security, 'encryption_at_rest') and
                component.security.encryption_at_rest):
                encrypted_components.append(component)
        return encrypted_components
    
    
    # Analysis Methods
    def get_component_graph(self) -> Dict[str, List[str]]:
        """Get component dependency graph"""
        graph = {}
        for component_id in self.components.keys():
            connections = self.get_connections_from_component(component_id)
            graph[component_id] = [conn.target for conn in connections]
        return graph
    
    
    def get_technology_usage(self) -> Dict[str, List[str]]:
        """Get which components use each technology"""
        tech_usage = {}
        for component in self.components.values():
            if component.technology:
                if component.technology not in tech_usage:
                    tech_usage[component.technology] = []
                tech_usage[component.technology].append(component.id)
        return tech_usage
    
    def validate_connections(self) -> List[str]:
        """Validate that all connections reference existing components"""
        issues = []
        for connection in self.connections.values():
            if connection.source not in self.components:
                issues.append(f"Connection {connection.id}: source '{connection.source}' not found")
            if connection.target not in self.components:
                issues.append(f"Connection {connection.id}: target '{connection.target}' not found")
        return issues
    
    def input_to_dict(self, input_obj) -> dict:
        """Convert a Strawberry input object to a dictionary"""
        return {field: getattr(input_obj, field) for field in input_obj.__annotations__}
    
    def __repr__(self) -> str:
        """String representation"""
        project_name = self.get_project_name()
        num_components = len(self.components)
        num_connections = len(self.connections)
        return f"ProjectConfigHelper(project='{project_name}', components={num_components}, connections={num_connections})"