from typing import Optional
import strawberry


@strawberry.type
class DeleteResponse:
    success: bool
    message: Optional[str] = None
    error: Optional[str] = None