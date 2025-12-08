# autostack_engine/scripts/seed_database.py
import asyncio
import json
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
import logging

from autostack_engine.services.environment.models.config_schema import ProjectConfig
from autostack_engine.utils.database.models.beanie import Migration

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def seed_sample_data():
    """Seed the database with sample data"""
    # Sample project configuration
    sample_config = {
        "project": {
            "name": "sample-microservice-app",
            "author": "AutoStack Team",
            "description": "A sample microservice application",
            "version": "1.0.0",
            "metadata": {
                "created_date": "2024-01-01",
                "tags": ["microservice", "demo", "sample"],
                "environment": "development"
            }
        },
        "technologies": [
            {
                "type": "runtime",
                "version": "3.11",
                "provider": "python",
                "framework": "fastapi",
                "configuration": {
                    "auto_reload": True,
                    "debug": True
                }
            }
        ],
        "components": [
            {
                "id": "api-gateway",
                "type": "gateway",
                "name": "API Gateway",
                "technology": "fastapi",
                "properties": {
                    "port": 8000,
                    "host": "0.0.0.0"
                },
                "routing": [
                    {
                        "path": "/api/v1/*",
                        "target": "user-service",
                        "timeout": "30s"
                    }
                ]
            },
            {
                "id": "user-service",
                "type": "service",
                "name": "User Service",
                "technology": "fastapi",
                "properties": {
                    "port": 8001
                },
                "dependencies": [
                    {
                        "component_id": "user-db",
                        "type": "database",
                        "critical": True
                    }
                ]
            },
            {
                "id": "user-db",
                "type": "database",
                "name": "User Database",
                "technology": "mongodb",
                "properties": {
                    "connection_string": "mongodb://localhost:27017/users"
                }
            }
        ],
        "connections": [
            {
                "id": "gateway-to-user-service",
                "source": "api-gateway",
                "target": "user-service",
                "type": "http",
                "properties": {
                    "protocol": "http",
                    "method": ["GET", "POST", "PUT", "DELETE"],
                    "timeout": "30s",
                    "load_balancing": True
                }
            },
            {
                "id": "user-service-to-db",
                "source": "user-service",
                "target": "user-db",
                "type": "database",
                "properties": {
                    "protocol": "mongodb",
                    "connection_pool_size": 10,
                    "query_timeout": "10s"
                }
            }
        ],
        "deployment": {
            "strategy": "docker-compose",
            "environments": ["development", "staging", "production"],
            "health_checks": {
                "enabled": True,
                "interval": "30s",
                "timeout": "5s",
                "retries": 3
            }
        }
    }
    
    try:
        # Check if sample data already exists
        existing = await ProjectConfig.find_one(
            ProjectConfig.project.name == sample_config["project"]["name"]
        )
        
        if existing:
            logger.info("Sample data already exists, skipping seed")
            return
        
        # Create the project config
        project_config = ProjectConfig(**sample_config)
        await project_config.insert()
        
        logger.info(f"Seeded sample project: {sample_config['project']['name']}")
        
    except Exception as e:
        logger.error(f"Failed to seed database: {e}")
        raise

def main():
    """Main entry point for seed script"""
    # Connect to database
    import os
    
    mongodb_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    database_name = os.getenv("DATABASE_NAME", "autostack")
    
    client = AsyncIOMotorClient(mongodb_url)
    asyncio.run(init_beanie(
        database=client[database_name],
        document_models=[ProjectConfig, Migration]
    ))
    
    asyncio(seed_sample_data())
    logger.info("Database seeding completed")

if __name__ == "__main__":
    
    main()