import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.api.routes import router as api_router
from app.ml.model import ml_classifier
from app.db.seeder import seed_database

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("scamshield")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown lifecycle management with MySQL seeding."""
    logger.info(f"Initializing {settings.PROJECT_NAME} v{settings.VERSION}...")
    
    # 1. Initialize and Seed MySQL Database
    try:
        seed_database()
        logger.info("MySQL Database connected and verified.")
    except Exception as e:
        logger.error(f"MySQL Database connection error: {e}")

    # 2. Warm up ML model
    if ml_classifier.pipeline is None:
        logger.info("Initializing ML Classifier model...")
        ml_classifier.train()
    logger.info("ML Classifier and Hybrid Risk Engine initialized successfully.")
    yield
    logger.info("Shutting down ScamShield API service.")


app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    version=settings.VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount modular API v1 router
app.include_router(api_router, prefix=settings.API_V1_STR, tags=["Scam Detection Engine"])


@app.get("/", summary="Root Health & Info")
async def root():
    return {
        "app": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "online",
        "docs_url": "/docs",
        "api_v1": settings.API_V1_STR
    }
