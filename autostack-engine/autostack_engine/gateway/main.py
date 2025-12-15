from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
import strawberry
from strawberry.fastapi import GraphQLRouter
import logging
from contextlib import asynccontextmanager
from autostack_engine.gateway.graphql.schema import Mutation, Query, Subscription
from autostack_engine.utils.project.subscription import RedisOperationStore
from dotenv import load_dotenv
import os
from typing import Optional, Any

load_dotenv()
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global reference to the operation store
_operation_store: Optional[RedisOperationStore] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage Redis store lifecycle"""
    global _operation_store
    
    store = RedisOperationStore(
        redis_url=f'redis://{os.getenv("REDIS_USER")}:{os.getenv("REDIS_PASSWORD")}@{os.getenv("REDIS_HOST")}:6379/0',
        max_connections=100,
        operation_ttl=3600
    )
    try:
        await store.initialize()
        _operation_store = store
        app.state.operation_store = store
        logger.info("Redis operation store initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Redis: {e}")
        raise
    
    yield
    
    # Shutdown: Close Redis connections
    logger.info("Shutting down application...")
    await store.close()
    _operation_store = None
    logger.info("Redis connections closed")

async def get_context() -> dict:
    """
    Context getter for GraphQL - injects operation_store into resolvers.
    This function is called for every GraphQL request.
    """
    return {
        "operation_store": _operation_store
    }

app = FastAPI(
    title="Autostack API Gateway",
    description="API Gateway for autostack engine",
    version="1.0.0",
    lifespan=lifespan 
)

schema = strawberry.Schema(query=Query, mutation=Mutation, subscription=Subscription)
graphql_app = GraphQLRouter(
    schema=schema, 
    path="/graphql", 
    graphql_ide="apollo-sandbox", 
    context_getter=get_context,
    subscription_protocols=[
        "graphql-transport-ws", 
        "graphql-ws"
    ]
)
app.include_router(graphql_app)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Microservices API Gateway", "version": "1.0.0"}