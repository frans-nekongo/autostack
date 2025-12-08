"""
Migration: implemented logging
Created: 2025-11-04T17:35:01.459619
"""
import os
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
import logging

from autostack_engine.utils.logging.services import ServiceLog

logger = logging.getLogger(__name__)

async def up():
    """
    Apply the migration
    """
    # Add your migration logic here
    logger.info('Applying migration: Implemented Logging')
    mongodb_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    database_name = os.getenv("DATABASE_NAME", "autostack")
    
    client = AsyncIOMotorClient(mongodb_url)
    database = client[database_name]
    
    #  Update documents
    await init_beanie(
        database=database,
        document_models=[
            ServiceLog
        ]
    )
    
    logger.info('Migration complete')


async def down():
    """
    Rollback the migration
    """
    # Add your rollback logic here
    pass
