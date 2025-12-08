# autostack_engine/scripts/setup_database.py
import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
import logging

from autostack_engine.utils.database.models.beanie import Migration


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def setup_database():
    """Initialize database connection and create collections/indexes"""
    try:
        # Get MongoDB connection string from environment
        mongodb_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
        database_name = os.getenv("DATABASE_NAME", "autostack")
        
        logger.info(f"Connecting to MongoDB at {mongodb_url}")
        
        # Create motor client
        client = AsyncIOMotorClient(mongodb_url)
        
        # Initialize beanie with the document models
        await init_beanie(
            database=client[database_name],
            document_models=[Migration]
        )
        
        logger.info("Database initialized successfully")
        logger.info("Collections and indexes created")
        
        return client
        
    except Exception as e:
        logger.error(f"Failed to setup database: {e}")
        raise

def main():
    """Main entry point for the setup-database script"""
    asyncio.run(setup_database())

if __name__ == "__main__":
    main()

