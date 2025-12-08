from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import strawberry
from strawberry.fastapi import GraphQLRouter
import logging

from autostack_engine.gateway.graphql.schema import Mutation, Query, Subscription


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Autostack API Gateway",
    description="API Gateway for autostack engine",
    version="1.0.0"
)

schema = strawberry.Schema(query=Query, mutation=Mutation, subscription=Subscription)
graphql_app = GraphQLRouter(schema=schema, path="/graphql", graphql_ide="apollo-sandbox")
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
