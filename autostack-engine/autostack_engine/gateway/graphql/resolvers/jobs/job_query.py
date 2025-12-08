from enum import Enum
from typing import Dict, Optional
from grpc import Status
import strawberry

from autostack_engine.utils.database.models.jobs.models import Job, JobResult, JobStatus
from autostack_engine.utils.database.mongo_client import DatabaseManager
from autostack_engine.utils.jobs.util import job_to_graphql

    
@strawberry.type
class JobQuery:
    @strawberry.field
    async def get_job(self, job_id: str) -> Optional[JobResult]:
        """Get the status and result of a job"""
        try:
            db = DatabaseManager()
            await db.connect([Job])
            job = await Job.find_one(Job.job_id == job_id)
            if not job:
                return None
            
            return job_to_graphql(job)
        except Exception as e:
            return e
        
    @strawberry.field
    async def get_all_jobs(self, limit: int = 50, skip: int = 0) -> list[JobResult]:
        """Get all jobs with pagination"""
        jobs = await Job.find_all().skip(skip).limit(limit).to_list()
        return [job_to_graphql(job) for job in jobs]
    
    @strawberry.field
    async def get_jobs_by_status(self, status: JobStatus, limit: int = 50) -> list[JobResult]:
        """Get jobs filtered by status"""
        jobs = await Job.find(Job.status == status.value).limit(limit).to_list()
        return [job_to_graphql(job) for job in jobs]