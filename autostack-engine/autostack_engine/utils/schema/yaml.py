import yaml
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from datetime import datetime

@dataclass
class Component:
    """Represents a system component with all its properties"""
    id: str
    type: str
    name: str
    technology: Optional[str] = None
    properties: Optional[Dict[str, Any]] = None
    deployment: Optional[Dict[str, Any]] = None
    security: Optional[Dict[str, Any]] = None
    monitoring: Optional[Dict[str, Any]] = None
    dependencies: Optional[List[Dict[str, str]]] = None
    routing: Optional[List[Dict[str, str]]] = None

@dataclass
class Connection:
    """Represents a connection between components"""
    id: str
    source: str
    target: str
    type: str
    properties: Optional[Dict[str, Any]] = None
    
class ArchitectureConfigParser:
    """
    Parser for YAML architecture file
    """
    
    def __init__(self, yaml_content: str = None, yaml_file: str = None):
        """
        Initalise parser with content from file or code input
        """
        if yaml_content:
            self.config = yaml.safe_load(yaml_content)
        elif yaml_file:
            with open(yaml_file, 'r') as file:
                self.config = yaml.safe_load(file)
        else:
            raise ValueError("Provide the yaml content or file")
        
        self._parse_components()
        self._parse_connections()
        
    def _parse_components(self):
        """Parse components into Component objects"""
        self.components = {}
        if 'components' in self.config:
            for comp_data in self.config['components']:
                component = Component(
                    id=comp_data['id'],
                    type=comp_data['type'],
                    name=comp_data['name'],
                    technology=comp_data.get('technology'),
                    properties=comp_data.get('properties'),
                    deployment=comp_data.get('deployment'),
                    security=comp_data.get('security'),
                    monitoring=comp_data.get('monitoring'),
                    dependencies=comp_data.get('dependencies'),
                    routing=comp_data.get('routing')
                )
                self.components[comp_data['id']] = component
                
    def _parse_connections(self):
        """Parse connections into Connection objects"""
        self.connections = {}
        if 'connections' in self.config:
            for conn_data in self.config['connections']:
                connection = Connection(
                    id=conn_data['id'],
                    source=conn_data['source'],
                    target=conn_data['target'],
                    type=conn_data['type'],
                    properties=conn_data.get('properties')
                )
                self.connections[conn_data['id']] = connection
                
    # Project Information Methods
    def get_project_info(self) -> Dict[str, Any]:
        """Get basic project information"""
        return self.config.get('project', {})
    
    def get_project_name(self) -> str:
        """Get project name"""
        return self.config.get('project', {}).get('name', '')
    
    def get_project_version(self) -> str:
        """Get project version"""
        return self.config.get('project', {}).get('version', '')
    
    def get_technologies(self) -> Dict[str, Any]:
        """Get all configured technologies"""
        return self.config.get('technologies', {})
    
    def get_technology(self, tech_name: str) -> Dict[str, Any]:
        """Get specific technology configuration"""
        return self.config.get('technologies', {}).get(tech_name, {})
    
    # Environment Methods
    def get_environments(self) -> Dict[str, Any]:
        """Get all environment configurations"""
        return self.config.get('environments', {})
    
    def get_environment(self, env_name: str) -> Dict[str, Any]:
        """Get specific environment configuration"""
        return self.config.get('environments', {}).get(env_name, {})
    
    def get_environment_scaling(self, env_name: str) -> Dict[str, Any]:
        """Get scaling configuration for an environment"""
        env = self.get_environment(env_name)
        return env.get('scaling', {})
    
    def get_environment_resources(self, env_name: str) -> Dict[str, Any]:
        """Get resource configuration for an environment"""
        env = self.get_environment(env_name)
        return env.get('resources', {})
    
    # Component Methods
    def get_all_components(self) -> Dict[str, Component]:
        """Get all components as Component objects"""
        return self.components
    
    def get_component(self, component_id: str) -> Optional[Component]:
        """Get specific component by ID"""
        return self.components.get(component_id)
    
    def get_components_by_type(self, component_type: str) -> List[Component]:
        """Get all components of a specific type"""
        return [comp for comp in self.components.values() if comp.type == component_type]
    
    def get_components_by_technology(self, technology: str) -> List[Component]:
        """Get all components using a specific technology"""
        return [comp for comp in self.components.values() if comp.technology == technology]
    
    def get_microservices(self) -> List[Component]:
        """Get all microservice components"""
        return self.get_components_by_type('microservice')
    
    def get_databases(self) -> List[Component]:
        """Get all database components"""
        return self.get_components_by_type('database')
    
    def get_caches(self) -> List[Component]:
        """Get all cache components"""
        return self.get_components_by_type('cache')
    
    def get_external_services(self) -> List[Component]:
        """Get all external service components"""
        return self.get_components_by_type('external_service')
    
    def get_component_port(self, component_id: str) -> Optional[int]:
        """Get port for a specific component"""
        component = self.get_component(component_id)
        if component and component.properties:
            return component.properties.get('port')
        return None
    
    def get_component_dependencies(self, component_id: str) -> List[Dict[str, str]]:
        """Get dependencies for a specific component"""
        component = self.get_component(component_id)
        if component and component.dependencies:
            return component.dependencies
        return []
    
    # Connection Methods
    def get_all_connections(self) -> Dict[str, Connection]:
        """Get all connections"""
        return self.connections
    
    def get_connection(self, connection_id: str) -> Optional[Connection]:
        """Get specific connection by ID"""
        return self.connections.get(connection_id)
    
    def get_connections_from_component(self, component_id: str) -> List[Connection]:
        """Get all connections originating from a component"""
        return [conn for conn in self.connections.values() if conn.source == component_id]
    
    def get_connections_to_component(self, component_id: str) -> List[Connection]:
        """Get all connections targeting a component"""
        return [conn for conn in self.connections.values() if conn.target == component_id]
    
    def get_connections_by_type(self, connection_type: str) -> List[Connection]:
        """Get connections by type (e.g., 'api_call', 'database_query')"""
        return [conn for conn in self.connections.values() if conn.type == connection_type]
    
    # Security Methods
    def get_security_config(self) -> Dict[str, Any]:
        """Get global security configuration"""
        return self.config.get('security', {})
    
    def get_component_security(self, component_id: str) -> Dict[str, Any]:
        """Get security configuration for a specific component"""
        component = self.get_component(component_id)
        if component and component.security:
            return component.security
        return {}
    
    def get_components_with_encryption(self) -> List[Component]:
        """Get components with encryption enabled"""
        encrypted_components = []
        for component in self.components.values():
            if component.security and component.security.get('encryption_at_rest'):
                encrypted_components.append(component)
        return encrypted_components
    
    
    # Deployment Methods
    def get_deployment_config(self) -> Dict[str, Any]:
        """Get global deployment configuration"""
        return self.config.get('deployment', {})
    
    def get_component_deployment(self, component_id: str) -> Dict[str, Any]:
        """Get deployment configuration for a specific component"""
        component = self.get_component(component_id)
        if component and component.deployment:
            return component.deployment
        return {}
    
    def get_scalable_components(self) -> List[Component]:
        """Get components with auto-scaling enabled"""
        scalable_components = []
        for component in self.components.values():
            if (component.deployment and 
                component.deployment.get('scaling', {}).get('max_replicas')):
                scalable_components.append(component)
        return scalable_components
    
    # Observability Methods
    def get_observability_config(self) -> Dict[str, Any]:
        """Get observability configuration"""
        return self.config.get('observability', {})
    
    def get_monitoring_config(self, component_id: str) -> Dict[str, Any]:
        """Get monitoring configuration for a component"""
        component = self.get_component(component_id)
        if component and component.monitoring:
            return component.monitoring
        return {}
    
    # Analysis Methods
    def get_component_graph(self) -> Dict[str, List[str]]:
        """Get component dependency graph"""
        graph = {}
        for component_id in self.components.keys():
            connections = self.get_connections_from_component(component_id)
            graph[component_id] = [conn.target for conn in connections]
        return graph
    
    def find_critical_path(self) -> List[str]:
        """Find components in critical path (components with critical dependencies)"""
        critical_components = []
        for component in self.components.values():
            if component.dependencies:
                for dep in component.dependencies:
                    if dep.get('critical'):
                        critical_components.append(component.id)
                        break
        return critical_components
    
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
    
    def __repr__(self) -> str:
        """String representation of the parser"""
        project_name = self.get_project_name()
        num_components = len(self.components)
        num_connections = len(self.connections)
        return f"ArchitectureConfigParser(project='{project_name}', components={num_components}, connections={num_connections})"
    
    
    