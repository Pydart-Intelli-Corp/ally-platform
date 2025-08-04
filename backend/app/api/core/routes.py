"""
Core API routes for essential endpoints
"""

from fastapi import APIRouter
from datetime import datetime

router = APIRouter()


@router.get("/")
async def root():
    """Root endpoint to test FastAPI"""
    return {"message": "✅ FastAPI is working!", "status": "healthy"}


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "message": "All systems operational ✅",
        "timestamp": datetime.now().isoformat(),
    }
