import asyncio
from enum import Enum
from typing import Optional
import strawberry


@strawberry.enum
class ProjectCreationStatus(Enum):
    QUEUED = "QUEUED"
    VALIDATING = "VALIDATING"
    CREATING_PROJECT = "CREATING_PROJECT"
    CREATING_TECHNOLOGIES = "CREATING_TECHNOLOGIES"
    CREATING_COMPONENTS = "CREATING_COMPONENTS"
    CREATING_CONNECTIONS = "CREATING_CONNECTIONS"
    FINALIZING = "FINALIZING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    
@strawberry.type
class ProjectCreationUpdate:
    operation_id: str
    status: ProjectCreationStatus
    message: str
    progress: int  # 0-100
    project_id: Optional[str] = None
    error: Optional[str] = None
    
@strawberry.type
class InitiateProjectResponse:
    success: bool
    operation_id: str
    message: str
    error: Optional[str] = None
    
    
class OperationStoreProtocol:
    def __init__(self):
        self._operations = {}
        self._subscribers = {}
    
    async def create_operation(self, operation_id: str):
        self._operations[operation_id] = {
            'status': ProjectCreationStatus.QUEUED,
            'progress': 0,
            'message': 'Operation queued',
            'project_id': None,
            'error': None
        }
        self._subscribers[operation_id] = []
    
    async def update_operation(self, operation_id: str, status: ProjectCreationStatus, 
                              message: str, progress: int, project_id: Optional[str] = None,
                              error: Optional[str] = None):
        if operation_id in self._operations:
            self._operations[operation_id] = {
                'status': status,
                'progress': progress,
                'message': message,
                'project_id': project_id,
                'error': error
            }
            # Notify all subscribers
            for queue in self._subscribers.get(operation_id, []):
                await queue.put(ProjectCreationUpdate(
                    operation_id=operation_id,
                    status=status,
                    message=message,
                    progress=progress,
                    project_id=project_id,
                    error=error
                ))
    
    async def subscribe(self, operation_id: str) -> asyncio.Queue:
        queue = asyncio.Queue()
        if operation_id not in self._subscribers:
            self._subscribers[operation_id] = []
        self._subscribers[operation_id].append(queue)
        
        # Send current state immediately
        if operation_id in self._operations:
            op = self._operations[operation_id]
            await queue.put(ProjectCreationUpdate(
                operation_id=operation_id,
                status=op['status'],
                message=op['message'],
                progress=op['progress'],
                project_id=op['project_id'],
                error=op['error']
            ))
        
        return queue
    
    async def cleanup(self, operation_id: str, queue: asyncio.Queue):
        if operation_id in self._subscribers:
            if queue in self._subscribers[operation_id]:
                self._subscribers[operation_id].remove(queue)