"""
Migration: setup
Created: 2025-09-21T09:21:56.718438
"""
import os
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
import logging


from autostack_engine.utils.database.models.components.models import Component, Connection, Environment
from autostack_engine.utils.database.models.project.models import Project
from autostack_engine.utils.database.models.technologies.models import Technology


logger = logging.getLogger(__name__)

async def up():
    """
    Apply the migration
    """
    logger.info('Applying migration: setup database')
    mongodb_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    database_name = os.getenv("DATABASE_NAME", "autostack")
    
    client = AsyncIOMotorClient(mongodb_url)
    database = client[database_name]
    
    #  Update documents
    await init_beanie(
        database=database,
        document_models=[
            Project,
            Technology,
            Environment,
            Component,
            Connection,
            
        ]
    )
    
    logger.info('Migration complete')


async def down():
    """
    Rollback the migration
    """
    # Add your rollback logic here
    pass
