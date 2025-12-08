import asyncio
import os
import importlib.util
from pathlib import Path
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
import logging

from autostack_engine.utils.database.models.beanie import Migration


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseMigrator:
    def __init__(self, migrations_dir: str = "migrations"):
        self.migrations_dir = Path(migrations_dir)
        self.client = None
        
    async def connect(self):
        """Connect to the database"""
        mongodb_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
        database_name = os.getenv("DATABASE_NAME", "autostack")
        
        self.client = AsyncIOMotorClient(mongodb_url)
        await init_beanie(
            database=self.client[database_name],
            document_models=[Migration]
        )
        
    async def get_executed_migrations(self):
        """Get list of already executed migrations"""
        executed = await Migration.find_all().to_list()
        return {m.version for m in executed}
        
    def get_migration_files(self):
        """Get all migration files sorted by version"""
        if not self.migrations_dir.exists():
            logger.warning(f"Migrations directory {self.migrations_dir} does not exist")
            return []
            
        migration_files = []
        for file_path in self.migrations_dir.glob("*.py"):
            if file_path.name.startswith("_"):
                continue
            migration_files.append(file_path)
            
        return sorted(migration_files, key=lambda x: x.stem)
        
    async def load_migration_module(self, file_path: Path):
        """Load a migration module dynamically"""
        spec = importlib.util.spec_from_file_location(file_path.stem, file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
        
    async def execute_migration(self, file_path: Path, version: str):
        """Execute a single migration"""
        try:
            logger.info(f"Executing migration: {version}")
            
            module = await self.load_migration_module(file_path)
            
            if hasattr(module, 'up'):
                await module.up()
                
            # Record successful migration
            migration = Migration(
                version=version,
                name=file_path.stem,
                success=True
            )
            await migration.insert()
            
            logger.info(f"Migration {version} executed successfully")
            
        except Exception as e:
            logger.error(f"Migration {version} failed: {e}")
            
            # Record failed migration
            migration = Migration(
                version=version,
                name=file_path.stem,
                success=False,
                error_message=str(e)
            )
            await migration.insert()
            raise
            
    async def rollback_migration(self, version: str):
        """Rollback a specific migration"""
        try:
            migration_record = await Migration.find_one(Migration.version == version)
            if not migration_record:
                logger.error(f"Migration {version} not found")
                return
                
            # Find the migration file
            migration_file = self.migrations_dir / f"{migration_record.name}.py"
            if not migration_file.exists():
                logger.error(f"Migration file {migration_file} not found")
                return
                
            module = await self.load_migration_module(migration_file)
            
            if hasattr(module, 'down'):
                await module.down()
                logger.info(f"Migration {version} rolled back successfully")
            else:
                logger.warning(f"Migration {version} has no rollback method")
                
            # Remove migration record
            await migration_record.delete()
            
        except Exception as e:
            logger.error(f"Rollback of migration {version} failed: {e}")
            raise
            
    async def migrate(self):
        """Run all pending migrations"""
        await self.connect()
        
        executed_migrations = await self.get_executed_migrations()
        migration_files = self.get_migration_files()
        
        pending_migrations = []
        for file_path in migration_files:
            version = file_path.stem
            if version not in executed_migrations:
                pending_migrations.append((file_path, version))
                
        if not pending_migrations:
            logger.info("No pending migrations")
            return
            
        logger.info(f"Found {len(pending_migrations)} pending migrations")
        
        for file_path, version in pending_migrations:
            await self.execute_migration(file_path, version)
            
        logger.info("All migrations completed")
        
    async def status(self):
        """Show migration status"""
        await self.connect()
        
        executed_migrations = await self.get_executed_migrations()
        migration_files = self.get_migration_files()
        
        print("\nMigration Status:")
        print("-" * 50)
        
        for file_path in migration_files:
            version = file_path.stem
            status = "✓ Executed" if version in executed_migrations else "✗ Pending"
            print(f"{version:<30} {status}")
            
        print(f"\nTotal migrations: {len(migration_files)}")
        print(f"Executed: {len(executed_migrations)}")
        print(f"Pending: {len(migration_files) - len(executed_migrations)}")

def main():
    """Main entry point for migration script"""
    import sys
    
    migrator = DatabaseMigrator()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "status":
            asyncio.run(migrator.status())
        elif command == "rollback" and len(sys.argv) > 2:
            version = sys.argv[2]
            asyncio.run(migrator.rollback_migration(version))
        elif command == "migrate":
            asyncio.run(migrator.migrate())
        else:
            print("Usage: migrate-database [migrate|status|rollback <version>]")
    else:
        asyncio.run(migrator.migrate())

if __name__ == "__main__":
    main()

