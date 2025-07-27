"""
FastAPI application for Computer Use Agent Backend
Refactored with SOLID principles and proper architecture
"""
import logging
import os
from contextlib import asynccontextmanager
from typing import Dict, Any

# Load environment variables FIRST, before any other imports
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database.connection import create_tables, get_db
from app.core.validation import ValidationService
from app.repositories.session_repository import SQLAlchemySessionRepository
from app.services.session_service import SessionService
from app.providers.anthropic_provider import AnthropicProvider, FallbackProvider
from app.core.websocket_manager import websocket_manager
from app.api.endpoints import sessions, messages, websocket
from app.core.exceptions import BaseError, ValidationError, ServiceError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Dependency injection container
class DependencyContainer:
    """Dependency injection container for services"""
    
    def __init__(self):
        self.validation_service = ValidationService()
        self.anthropic_provider = AnthropicProvider(self.validation_service)
        self.fallback_provider = FallbackProvider()
    
    def get_validation_service(self) -> ValidationService:
        return self.validation_service
    
    def get_ai_provider(self):
        """Get the best available AI provider"""
        if self.anthropic_provider.is_available():
            return self.anthropic_provider
        return self.fallback_provider
    
    def get_session_repository(self, db: Session) -> SQLAlchemySessionRepository:
        return SQLAlchemySessionRepository(db, self.validation_service)
    
    def get_session_service(self, db: Session) -> SessionService:
        repository = self.get_session_repository(db)
        return SessionService(repository, self.validation_service)


# Global dependency container
container = DependencyContainer()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting Computer Use Agent Backend...")
    
    # Create database tables
    create_tables()
    logger.info("Database tables created/verified")
    
    # Check for API key
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        logger.warning("ANTHROPIC_API_KEY not set - using fallback provider")
    else:
        logger.info(f"ANTHROPIC_API_KEY found: {api_key[:10]}...")
    
    # Initialize providers
    ai_provider = container.get_ai_provider()
    if isinstance(ai_provider, AnthropicProvider):
        logger.info("Anthropic provider initialized successfully")
    else:
        logger.info("Using fallback provider")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Computer Use Agent Backend...")


# Create FastAPI app
app = FastAPI(
    title="Computer Use Agent Backend",
    description="FastAPI backend for Claude Computer Use Agent with session management and real-time streaming",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global exception handler
@app.exception_handler(BaseError)
async def custom_exception_handler(request, exc: BaseError):
    """Handle custom exceptions"""
    logger.error(f"Custom exception: {exc.message}")
    return {
        "error": exc.message,
        "error_code": exc.error_code,
        "detail": str(exc)
    }


# Dependency injection functions
def get_validation_service() -> ValidationService:
    return container.get_validation_service()


def get_session_service(db: Session = Depends(get_db)) -> SessionService:
    return container.get_session_service(db)


def get_ai_provider():
    return container.get_ai_provider()


# Include routers with dependency injection
app.include_router(
    sessions.router, 
    prefix="/api",
    dependencies=[Depends(get_validation_service)]
)
app.include_router(
    messages.router, 
    prefix="/api",
    dependencies=[Depends(get_session_service), Depends(get_ai_provider)]
)
app.include_router(websocket.router, prefix="/api")

# Mount static files for frontend
if os.path.exists("frontend/static"):
    app.mount("/static", StaticFiles(directory="frontend/static"), name="static")

# Health check endpoint
@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check database connection
        db = next(get_db())
        db.execute("SELECT 1")
        
        # Check AI provider
        ai_provider = container.get_ai_provider()
        provider_status = "available" if ai_provider.is_available() else "fallback"
        
        return {
            "status": "healthy",
            "service": "Computer Use Agent Backend",
            "version": "1.0.0",
            "database": "connected",
            "ai_provider": provider_status
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unhealthy")

# Root endpoint - serve frontend
@app.get("/")
async def root():
    """Root endpoint - serve the frontend HTML"""
    if os.path.exists("frontend/index.html"):
        return FileResponse("frontend/index.html")
    return {
        "message": "Computer Use Agent Backend API",
        "docs": "/docs",
        "health": "/api/health"
    }


if __name__ == "__main__":
    import uvicorn
    
    # Check for required environment variables
    required_vars = ['ANTHROPIC_API_KEY']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.warning(f"Missing environment variables: {missing_vars}")
        logger.warning("Application will run with limited functionality")
    
    # Start the application
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 