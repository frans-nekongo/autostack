from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
import os
from typing import List, Type, Optional, Set
from beanie import Document
from autostack_engine.utils.database.models.beanie import Migration


class DatabaseManager:
    """Manages MongoDB connections and Beanie document model initialization."""
    
    def __init__(self):
        self._client: Optional[AsyncIOMotorClient] = None
        self._initialized_models: Set[str] = set()
        self._mongodb_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
        self._database_name = os.getenv("DATABASE_NAME", "autostack")
    
    @property
    def client(self) -> Optional[AsyncIOMotorClient]:
        """Get the current database client."""
        return self._client
    
    @property
    def is_connected(self) -> bool:
        """Check if database is connected."""
        return self._client is not None
    
    @property
    def initialized_models(self) -> Set[str]:
        """Get the set of initialized model names."""
        return self._initialized_models.copy()
    
    async def connect(self, document_models: Optional[List[Type[Document]]] = None) -> AsyncIOMotorClient:
        """
        Connect to the database with specified document models.
        
        Args:
            document_models: List of Beanie document model classes to initialize.
                           If None, defaults to [Migration].
        
        Returns:
            AsyncIOMotorClient: The MongoDB client instance
        """
        # Set default models if none provided
        if document_models is None:
            document_models = [Migration]
        
        # Create client if it doesn't exist
        if self._client is None:
            self._client = AsyncIOMotorClient(self._mongodb_url)
        
        # Filter out models that are already initialized
        new_models = [model for model in document_models 
                      if model.__name__ not in self._initialized_models]
        
        # Only initialize if there are new models
        if new_models:
            # Initialize with all requested models (Beanie handles duplicates)
            await init_beanie(
                database=self._client[self._database_name],
                document_models=document_models
            )
            
            # Update our tracking set
            self._initialized_models.update(model.__name__ for model in document_models)
        
        return self._client
    
    async def add_models(self, document_models: List[Type[Document]]) -> None:
        """
        Add new document models to an existing connection.
        
        Args:
            document_models: List of Beanie document model classes to add.
        """
        if not self.is_connected:
            raise RuntimeError("Database not connected. Call connect() first.")
        
        await self.connect(document_models)
    
    async def disconnect(self) -> None:
        """Close the database connection and reset state."""
        if self._client:
            self._client.close()
            self._client = None
            self._initialized_models.clear()
    
    def get_database(self, name: Optional[str] = None):
        """
        Get a database instance.
        
        Args:
            name: Database name. If None, uses default database name.
        
        Returns:
            Database instance
        """
        if not self.is_connected:
            raise RuntimeError("Database not connected. Call connect() first.")
        
        db_name = name or self._database_name
        return self._client[db_name]


# Global instance for backward compatibility
_db_manager = DatabaseManager()

# Convenience functions for backward compatibility
async def connect_to_database(document_models: Optional[List[Type[Document]]] = None) -> AsyncIOMotorClient:
    """Connect to the database (backward compatibility function)."""
    return await _db_manager.connect(document_models)

async def get_client() -> Optional[AsyncIOMotorClient]:
    """Get the current database client (backward compatibility function)."""
    return _db_manager.client

async def disconnect_from_database() -> None:
    """Disconnect from database (backward compatibility function)."""
    await _db_manager.disconnect()