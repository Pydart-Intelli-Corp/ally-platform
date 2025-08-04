"""
Ally Platform Backend API

A clean, minimal FastAPI application with environment-specific configuration
and modular route organization.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging

# Import configuration and startup modules
from .core.environment import env_config
from .core.startup import startup_handler

# Import routers
from .api.core.routes import router as core_router
from .api.v1.config.route_config import router as route_config_router
from .api.v1.test.routes import router as test_router

# Configure logging with environment settings
log_config = env_config.get_logging_config()
logging.basicConfig(
    level=getattr(logging, log_config["level"]),
    format=(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        if log_config["format"] == "development"
        else '{"timestamp": "%(asctime)s", "name": "%(name)s", "level": "%(levelname)s", "message": "%(message)s"}'
    ),
)

# Get configuration from environment
server_config = env_config.get_server_config()
security_config = env_config.get_security_config()
feature_flags = env_config.get_feature_flags()

# Initialize FastAPI app
app = FastAPI(
    title="Ally Platform API",
    description="Backend API for Ally Platform with environment-specific configuration management",
    version="1.0.0",
    docs_url="/docs" if feature_flags["debug_routes"] else None,
    redoc_url="/redoc" if feature_flags["debug_routes"] else None,
    debug=server_config["debug"],
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=security_config["cors_origins"],
    allow_credentials=security_config["cors_credentials"],
    allow_methods=security_config["cors_methods"],
    allow_headers=security_config["cors_headers"],
)

# Include routers
app.include_router(core_router)
app.include_router(route_config_router, prefix="/api/v1/config")

# Include test routes only if debug is enabled
if feature_flags["debug_routes"]:
    app.include_router(test_router, prefix="/test", tags=["Testing"])


# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize application services on startup"""
    await startup_handler()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
