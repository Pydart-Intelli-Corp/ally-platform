#!/usr/bin/env python3
"""
Production Server Startup Script for Ally Platform
Optimized for production deployment with Azure MySQL
"""

import os
import uvicorn
from app.main import app

# Set production environment
os.environ["ENVIRONMENT"] = "production"

if __name__ == "__main__":
    # Production configuration
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,  # Disable reload in production
        log_level="info",
        workers=4,  # Use multiple workers for production
        access_log=True,
        server_header=False,  # Hide server information for security
        proxy_headers=True,  # Trust proxy headers
        forwarded_allow_ips="*",  # Allow all IPs for proxy forwarding
    )
