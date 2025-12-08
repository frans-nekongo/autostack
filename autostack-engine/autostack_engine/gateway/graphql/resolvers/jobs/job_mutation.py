import asyncio
import strawberry

from autostack_engine.utils.database.models.jobs.models import Job, JobCreated
from autostack_engine.utils.database.mongo_client import DatabaseManager
from autostack_engine.utils.jobs.util import process_ollama_job


@strawberry.type
class JobMutation:
    @strawberry.mutation
    async def create_project_description(self, user_input: str) -> JobCreated:
        """Create a new job to process the project description"""
        # Create new job document
        try: 
            db = DatabaseManager()
            await db.connect([Job])
            job = Job(user_input=user_input)
            await job.insert()
            
            # Start background task
            asyncio.create_task(process_ollama_job(job.job_id))
            
            return JobCreated(
                job_id=job.job_id,
                message="Job created successfully. Use subscribeToJob to monitor progress."
            )
        except Exception as e:
            return e
        
    
    @strawberry.mutation
    async def delete_job(self, job_id: str) -> bool:
        """Delete a job by ID"""
        try:
            db = DatabaseManager()
            await db.connect([Job])
                
            job = await Job.find_one(Job.job_id == job_id)
            if job:
                await job.delete()
                return True
            
        except Exception as e:
            return e
            