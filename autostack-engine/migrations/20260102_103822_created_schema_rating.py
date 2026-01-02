"""
Migration: created schema rating
Created: 2026-01-02T10:38:22.277697
"""

import os
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
import logging

from autostack_engine.utils.database.models.ai.models import SchemaRating



logger = logging.getLogger(__name__)

async def up():
    """
    Apply the migration
    """
    # Add your migration logic here
    logger.info('Applying migration: Created Schema Rating')
    mongodb_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    database_name = os.getenv("DATABASE_NAME", "autostack")
    
    client = AsyncIOMotorClient(mongodb_url)
    database = client[database_name]
    
    #  Update documents
    await init_beanie(
        database=database,
        document_models=[
            SchemaRating
        ]
    )
    
    logger.info('Migration complete')


async def down():
    """
    Rollback the migration
    """
    # Add your rollback logic here
    pass
