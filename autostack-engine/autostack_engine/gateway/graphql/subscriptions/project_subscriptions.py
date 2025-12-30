import traceback
import strawberry
from strawberry.types import Info
from typing import AsyncGenerator

from autostack_engine.utils.project.subscription import ProjectCreationStatus, ProjectCreationUpdate
import logging
logger = logging.getLogger(__name__)

def get_operation_store(info: Info):
    """Get operation store from GraphQL context"""
    return info.context["operation_store"]


@strawberry.type
class ProjectSubscription:
    """Project-related subscriptions"""
    @strawberry.subscription
    async def project_creation_status(
        self,
        operation_id: str,
        info: Info
    ) -> AsyncGenerator[ProjectCreationUpdate, None]:
        
        operation_store = get_operation_store(info)
        
        # Subscribe to updates from Redis
        try:
            queue = await operation_store.subscribe(operation_id)
        except Exception as e:
            logger.error(f"Failed to subscribe to operation {operation_id}: {e}")
            # Yield an error status instead of failing
            yield ProjectCreationUpdate(
                operation_id=operation_id,
                status=ProjectCreationStatus.FAILED,
                message="Failed to subscribe to operation",
                progress=0,
                error=str(e)
            )
            return
        
        try:
            # Keep yielding updates until completion or failure
            async for update in ProjectSubscription._stream_updates(queue, operation_id):
                yield update
                
                # Stop after completion or failure
                if update.status in [
                    ProjectCreationStatus.COMPLETED,
                    ProjectCreationStatus.FAILED
                ]:
                    logger.info(f"Operation {operation_id} finished with status: {update.status}")
                    break
                    
        except Exception as e:
            logger.error(f"Error in subscription stream for {operation_id}: {traceback.format_exc()}")
            # Yield error update before closing
            yield ProjectCreationUpdate(
                operation_id=operation_id,
                status=ProjectCreationStatus.FAILED,
                message="Subscription error occurred",
                progress=0,
                error=str(e)
            )
            print(traceback.format_exc())
        finally:
            # Clean up subscription resources
            logger.info(f"Cleaning up subscription for operation: {operation_id}")
            await operation_store.cleanup(operation_id, queue)
    
    @staticmethod
    async def _stream_updates(queue, operation_id: str):
        """Helper to stream updates from queue with timeout protection"""
        import asyncio
        import logging
        logger = logging.getLogger(__name__)
        
        while True:
            try:
                # Wait for update with timeout to prevent hanging
                update = await asyncio.wait_for(queue.get(), timeout=1000.0)  # 5 min timeout
                
                if update is not None:
                    yield update
                else:
                    logger.warning(f"Received None update for operation {operation_id}")
                    continue
                    
            except asyncio.TimeoutError:
                logger.warning(f"Subscription timeout for operation {operation_id}")
                # Yield a timeout status
                yield ProjectCreationUpdate(
                    operation_id=operation_id,
                    status=ProjectCreationStatus.FAILED,
                    message="Operation timed out",
                    progress=0,
                    error="No updates received for 5 minutes"
                )
                break
            except Exception as e:
                logger.error(f"Error getting update from queue: {e}")
                break