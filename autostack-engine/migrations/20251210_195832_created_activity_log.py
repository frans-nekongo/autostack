"""
Migration: created activity log
Created: 2025-12-10T19:58:32.508363
"""
import os
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
import logging

from autostack_engine.utils.database.models.activities.models import ActivityLog



logger = logging.getLogger(__name__)

async def up():
    """
    Apply the migration
    """
    # Add your migration logic here
    logger.info('Applying migration: created activity log')
    mongodb_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    database_name = os.getenv("DATABASE_NAME", "autostack")
    
    client = AsyncIOMotorClient(mongodb_url)
    database = client[database_name]
    
    #  Update documents
    await init_beanie(
        database=database,
        document_models=[
            ActivityLog
        ]
    )
    
    logger.info('Migration complete')


async def down():
    """
    Rollback the migration
    """
    # Add your rollback logic here
    pass
