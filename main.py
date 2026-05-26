import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.api.endpoints import router as api_router
from app.db.database import Base, engine

Base.metadata.create_all(bind=engine)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up Client Management & Pipefy Integration API")
    yield
    logger.info("Shutting down Client Management & Pipefy Integration API")

app = FastAPI(
    title="Client Management & Pipefy Integration API",
    description="API for managing clients and integrating with Pipefy via GraphQL",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {
        "message": "Client Management & Pipefy Integration API",
        "docs": "/docs",
        "health": "/api/v1/health"
    }