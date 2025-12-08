from typing import Optional
import strawberry

@strawberry.input
class EnvironmentInput:
    name: str  # "development", "production"
    type: str  # "local", "vm"

@strawberry.type
class ProductionResponse:
    success: bool
    compose_path: Optional[str] = None
    error: Optional[str] = None
    message: Optional[str] = None
