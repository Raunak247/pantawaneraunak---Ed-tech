from fastapi import APIRouter, Depends, FastAPI
from .routes import users, subjects, assessment, learning, analytics

# Import all route modules
from .database import db_manager
from .config import settings
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware

def create_app():
    app = FastAPI(
        title="Adaptive Learning API",
        description="Adaptive learning platform with BKT-based assessment and personalized learning paths",
        version="1.0.0"
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # In production, you should specify your frontend domains
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Connect to database on startup
    @app.on_event("startup")
    async def startup_db_client():
        await db_manager.connect()
    
    # Close database connection on shutdown
    @app.on_event("shutdown")
    async def shutdown_db_client():
        await db_manager.close()
    
    # Include all routers
    app.include_router(users.router)
    app.include_router(subjects.router)
    app.include_router(assessment.router)
    app.include_router(learning.router)
    app.include_router(analytics.router)
    
    # Root endpoint
    @app.get("/", tags=["Root"])
    async def read_root():
        return {
            "name": "Adaptive Learning API",
            "version": "1.0.0",
            "storage": "Firebase" if not db_manager.is_using_memory() else "In-Memory Fallback",
            "docs_url": "/docs",
            "redoc_url": "/redoc"
        }
    
    # Health check endpoint
    @app.get("/health", tags=["Root"])
    async def health_check():
        return {
            "status": "healthy",
            "storage": "Firebase" if not db_manager.is_using_memory() else "In-Memory Fallback",
            "timestamp": str(datetime.utcnow())
        }
    
    return app