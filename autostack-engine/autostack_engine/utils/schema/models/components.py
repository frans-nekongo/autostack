import strawberry
from typing import Dict, Any, Optional, List
from enum import Enum

# JSON scalar for flexible nested data
JSON = strawberry.scalar(
    Dict[str, Any],
    serialize=lambda v: v,
    parse_value=lambda v: v,
)

@strawberry.enum
class ComponentTypeInput(Enum):
    DATABASE = "database"
    CACHE = "cache"
    API = "api"
    WEB = "web"
    GATEWAY = "gateway"
    EXTERNAL = "external"


@strawberry.input
class ComponentInput:
    component_id: str  # component_id like "user-db", "auth-api"
    type: ComponentTypeInput
    name: str
    technology: Optional[str] = None  # References a technology name
    framework: Optional[str]
    port: Optional[int] = None
    environment_variables: Optional[strawberry.scalars.JSON] = None # type: ignore
    dependencies: Optional[List[str]] = None  # List of component IDs

@strawberry.input
class ConnectionInput:
    source: str  # component_id
    target: str  # component_id
    type: str = "api"  # api, database, cache
    port: Optional[int] = None

@strawberry.type
class ComponentResponse:
    success: bool
    component_ids: Optional[List[str]] = None
    error: Optional[str] = None
    message: Optional[str] = None
    
