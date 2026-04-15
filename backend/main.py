"""
Main FastAPI application entry point.
Starts the server, mounts routes, and manages lifecycle events.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import logging
import os

from backend.config import settings
from backend.db.mongodb import connect_to_mongo, close_mongo_connection
from backend.routes.auth_routes import router as auth_router
from backend.routes.user_routes import router as user_router
from backend.routes.admin_routes import router as admin_router
from backend.routes.health_routes import router as health_router
from backend.utils.logger import setup_logger

# Setup logging
logger = setup_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application startup and shutdown."""
    logger.info("[START] Starting Loan Underwriting AI...")
    await connect_to_mongo()
    logger.info("[OK] Startup complete")
    yield
    await close_mongo_connection()
    logger.info("[STOP] Application shutdown complete")


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-powered loan underwriting system with 6 sequential agents",
    lifespan=lifespan,
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for uploaded documents
uploads_dir = os.path.abspath(settings.UPLOAD_DIR)
os.makedirs(uploads_dir, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")

# Mount routers
app.include_router(auth_router)
app.include_router(user_router)
app.include_router(admin_router)
app.include_router(health_router)

@app.get("/")
async def root():
    return {"message": f"{settings.APP_NAME} v{settings.APP_VERSION} is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)