from pydantic import Field
import strawberry
from typing import Any, Dict, Optional, List
from enum import Enum

from autostack_engine.utils.constants import TECHNOLOGY_CATALOG

# JSON scalar for flexible nested data
JSON = strawberry.scalar(
    Dict[str, Any],
    serialize=lambda v: v,
    parse_value=lambda v: v,
)

@strawberry.enum
class TechnologyCategory(Enum):
    RUNTIME = "runtime"          # node, python, java, etc.
    DATABASE = "database"        # postgresql, mysql, mongodb, etc.
    CACHE = "cache"             # redis, memcached
    QUEUE = "queue"             # rabbitmq, kafka
    SERVICE = "service"        # custom services


@strawberry.input
class Configurations:
    name: str
    value: str
        
@strawberry.input
class EnvironmentVariables:
    name: str
    value: str

@strawberry.input
class TechnologyInput:
    name: str                                   
    version: Optional[str] = "latest"         
    category: Optional[TechnologyCategory] = None 
    port: Optional[int] = None                  
    environment_variables: Optional[List[EnvironmentVariables]] = None
    configuration: Optional[List[Configurations]] = None 
    enabled: bool = True                        

@strawberry.type
class TechnologyResponse:
    success: bool
    technology_ids: Optional[List[str]] = None
    error: Optional[str] = None
    message: Optional[str] = None

class TechnologyManager:
    @staticmethod
    def get_devbox_technologies(technologies: List[TechnologyInput]) -> List[str]:
        """Generate list of devbox package specifications in format: package@version or package"""
        packages = []
        
        for tech in technologies:
            if not tech.enabled:
                continue
                
            # Check if technology exists in catalog
            if tech.name not in TECHNOLOGY_CATALOG:
                continue
                
            # Use devbox format: package@version or just package
            if tech.version and tech.version != "latest":
                packages.append(f"{tech.name}@{tech.version}")
            else:
                packages.append(tech.name)
        
        return packages

    @staticmethod
    def get_devbox_services(technologies: List[TechnologyInput]) -> Dict[str, Any]:
        """Generate devbox.json services configuration"""
        services = {}
        
        for tech in technologies:
            if not tech.enabled:
                continue
                
            catalog_info = TECHNOLOGY_CATALOG.get(tech.name, {})
            
            # Add service configuration if it's a service category
            if catalog_info.get("category") in ["database", "cache", "queue"]:
                service_config = {
                    "command": f"{tech.name}",
                    "env": tech.environment_variables or {}
                }
                
                if tech.port:
                    service_config["port"] = tech.port
                
                if tech.configuration:
                    service_config.update(tech.configuration)
                
                services[tech.name] = service_config
        
        return services
    
    @staticmethod
    def get_nix_packages(technologies: List[TechnologyInput]) -> List[str]:
        """Generate list of Nix packages for production installation"""
        packages = []
        
        for tech in technologies:
            if not tech.enabled:
                continue
                
            catalog_info = TECHNOLOGY_CATALOG.get(tech.name, {})
            nix_package = catalog_info.get("nix_package", tech.name)
            
            # Use latest version if no version specified or version is "latest"
            if not tech.version or tech.version == "latest":
                packages.append(nix_package)
            else:
                # Handle specific version
                packages.append(f"{nix_package}_{tech.version.replace('.', '')}")
        
        return packages