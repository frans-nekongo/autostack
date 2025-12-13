from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import strawberry
from strawberry.fastapi import GraphQLRouter
import logging
from contextlib import asynccontextmanager
from autostack_engine.gateway.graphql.schema import Mutation, Query, Subscription
from autostack_engine.utils.project.subscription import RedisOperationStore
from dotenv import load_dotenv
import os

load_dotenv()
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage Redis store lifecycle"""
    store = RedisOperationStore(
        redis_url=f'redis://{os.getenv('REDIS_USER')}:{os.getenv('REDIS_PASSWORD')}@{os.getenv('REDIS_HOST')}:6379/0',
        max_connections=50,
        operation_ttl=3600
    )
    try:
        await store.initialize()
        app.state.operation_store = store
        logger.info("Redis operation store initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Redis: {e}")
        raise
    
    yield
    
    # Shutdown: Close Redis connections
    logger.info("Shutting down application...")
    await store.close()
    logger.info("Redis connections closed")
    
async def get_context(
    custom_context: dict = None
) -> dict:
    """
    Context getter for GraphQL - injects operation_store into resolvers.
    This function is called for every GraphQL request.
    """
    # Get the FastAPI app instance
    from main import app
    
    context = {
        "operation_store": app.state.operation_store,
        "request": custom_context.get("request") if custom_context else None,
    }
    
    return context


def get_operation_store(info: strawberry.Info):
    """
    Helper function to get operation store from GraphQL context.
    Use this in your mutations/subscriptions.
    
    Example:
        @strawberry.mutation
        async def my_mutation(self, info: Info):
            store = get_operation_store(info)
            await store.create_operation(...)
    """
    return info.context["operation_store"]

app = FastAPI(
    title="Autostack API Gateway",
    description="API Gateway for autostack engine",
    version="1.0.0",
    lifespan=lifespan 
)

schema = strawberry.Schema(query=Query, mutation=Mutation, subscription=Subscription)
graphql_app = GraphQLRouter(schema=schema, path="/graphql", graphql_ide="apollo-sandbox", context_getter=get_context)
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
