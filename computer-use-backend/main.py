"""
FastAPI application for Computer Use Agent Backend
"""
import logging
import os
from contextlib import asynccontextmanager

# Load environment variables FIRST, before any other imports
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.database.connection import create_tables
from app.api.endpoints import sessions, messages, websocket

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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
        logger.warning("ANTHROPIC_API_KEY not set - agent functionality will not work")
    else:
        logger.info(f"ANTHROPIC_API_KEY found: {api_key[:10]}...")
    
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

# Include routers
app.include_router(sessions.router, prefix="/api")
app.include_router(messages.router, prefix="/api")
app.include_router(websocket.router, prefix="/api")

# Mount static files for frontend
if os.path.exists("frontend/static"):
    app.mount("/static", StaticFiles(directory="frontend/static"), name="static")

# Health check endpoint
@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Computer Use Agent Backend",
        "version": "1.0.0"
    }

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
    if not os.getenv('ANTHROPIC_API_KEY'):
        logger.error("ANTHROPIC_API_KEY environment variable must be set")
        print("\n⚠️  Please set your ANTHROPIC_API_KEY in the .env file")
        print("   Get your API key from: https://console.anthropic.com/")
        exit(1)
    
    # Run the application
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 