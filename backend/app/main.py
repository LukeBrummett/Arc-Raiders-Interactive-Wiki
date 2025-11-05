"""Main FastAPI application entry point"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

from app.routes import items, tasks, search

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Arc Raiders Interactive Wiki API",
    description="RESTful API for Arc Raiders game data - items, quests, expeditions, and workshops",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
origins = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:5173").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(items.router)
app.include_router(tasks.router)
app.include_router(search.router)

@app.get("/")
async def root():
    """API information endpoint"""
    return {
        "name": "Arc Raiders Interactive Wiki API",
        "version": "1.0.0",
        "status": "online",
        "endpoints": {
            "docs": "/docs",
            "redoc": "/redoc",
            "health": "/api/health",
            "search": "/api/search",
            "items": "/api/items",
            "tasks": "/api/tasks"
        }
    }
# app.include_router(expeditions.router, prefix="/api/expeditions", tags=["expeditions"])
# app.include_router(search.router, prefix="/api/search", tags=["search"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=os.getenv("API_HOST", "0.0.0.0"),
        port=int(os.getenv("API_PORT", 8000)),
        reload=os.getenv("DEBUG", "True") == "True"
    )
