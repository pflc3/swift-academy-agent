"""Main FastAPI application for the Swift Academy Agent."""
import uvicorn  # type: ignore
from fastapi import FastAPI  # type: ignore
from fastapi.middleware.cors import CORSMiddleware  # type: ignore

from api.routes import router

# Create FastAPI application
app = FastAPI(
    title="Swift Academy Agent",
    description="AI assistant agent for Swift Academy app",
    version="0.1.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development - restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include router
app.include_router(router, prefix="/api/v1")


@app.get("/")
async def root():
    """Root endpoint - health check and welcome message."""
    return {
        "status": "online",
        "message": "Welcome to the Swift Academy Agent API",
        "documentation": "/docs",
    }


if __name__ == "__main__":
    """Run the application with uvicorn when executed as a script."""
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)
