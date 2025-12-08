from datetime import datetime
import os
from ollama import Client, chat
from dotenv import load_dotenv

from autostack_engine.utils.database.models.jobs.models import Job, JobResult, JobStatus
from autostack_engine.utils.database.mongo_client import DatabaseManager

load_dotenv()


async def process_ollama_job(job_id: str):
    """Process the Ollama request in the background"""
    try:
        # Get job from database
        db = DatabaseManager()
        await db.connect([Job])
        
        job = await Job.find_one(Job.job_id == job_id)
        if not job:
            return
        
        # Update job status to processing
        job.status = JobStatus.PROCESSING.value
        job.updated_at = datetime.now()
        await job.save()
        
        # Initialize Ollama client
        client = Client(
            host='https://ollama.com',
            headers={'Authorization': 'Bearer ' + os.environ.get('OLLAMA_API_KEY')}
        )
        
        messages = [
            {
                'role': 'user',
                'content': job.user_input
            }
        ]
        
        # Make the actual Ollama request
        response = chat(
            model='sakariadevelopment/autostack',
            messages=messages
        )
        
        # Update job with result
        job.status = JobStatus.COMPLETED.value
        job.result = response['message']['content']
        job.completed_at = datetime.now()
        job.updated_at = datetime.now()
        await job.save()
        
    except Exception as e:
        # Update job with error
        job = await Job.find_one(Job.job_id == job_id)
        if job:
            job.status = JobStatus.FAILED.value
            job.error = str(e)
            job.completed_at = datetime.now()
            job.updated_at = datetime.now()
            await job.save()
   
            
def job_to_graphql(job: Job) -> JobResult:
    """Convert Beanie Job document to GraphQL JobResult"""
    return JobResult(
        id=job.job_id,
        status=JobStatus(job.status),
        result=job.result,
        error=job.error,
        created_at=job.created_at.isoformat(),
        completed_at=job.completed_at.isoformat() if job.completed_at else None
    )