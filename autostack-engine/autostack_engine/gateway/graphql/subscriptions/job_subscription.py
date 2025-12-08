import asyncio
from datetime import datetime
from typing import AsyncGenerator
import strawberry

from autostack_engine.utils.database.models.jobs.models import Job, JobResult, JobStatus
from autostack_engine.utils.database.mongo_client import DatabaseManager
from autostack_engine.utils.jobs.util import job_to_graphql



@strawberry.type
class JobSubscription:
    @strawberry.subscription
    async def subscribe_to_job(self, job_id: str) -> AsyncGenerator[JobResult, None]:
        """Subscribe to job updates"""
        db = None
        try:
            db = DatabaseManager()
            await db.connect([Job])
            
            while True:
                job = await Job.find_one(Job.job_id == job_id)
            
                if not job:
                    yield JobResult(
                        id=job_id,
                        status=JobStatus.FAILED,
                        error="Job not found",
                        created_at=datetime.now().isoformat()
                    )
                    break
                
                # Yield current status
                yield job_to_graphql(job)
                
                # If job is completed or failed, stop subscription
                if job.status in [JobStatus.COMPLETED.value, JobStatus.FAILED.value]:
                    break
                
                # Wait before checking again (polling interval)
                await asyncio.sleep(1)
                
        except Exception as e:
            print(f"Subscription error: {e}")
            yield JobResult(
                id=job_id,
                status=JobStatus.FAILED,
                error=f"Subscription error: {str(e)}",
                created_at=datetime.now().isoformat()
            )
        finally:
            if db:
                await db.disconnect()