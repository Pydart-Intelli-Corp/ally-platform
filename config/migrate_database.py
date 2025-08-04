#!/usr/bin/env python3
"""
Database Migration Script for Configuration Management
Creates the necessary database tables for the configuration system.
"""

import os
import sys
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import json

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app.config_manager import Base, ClientConfiguration, ConfigurationManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_tables(database_url: str):
    """Create all necessary tables"""
    try:
        engine = create_engine(database_url)
        Base.metadata.create_all(engine)
        logger.info("✅ Database tables created successfully")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to create tables: {e}")
        return False


def seed_default_configuration(database_url: str, redis_url: str = None):
    """Seed the database with a default configuration"""
    try:
        config_manager = ConfigurationManager(database_url, redis_url)

        # Check if default configuration already exists
        existing_config = config_manager.get_configuration("ally-demo")

        if (
            existing_config
            and existing_config.get("meta", {}).get("clientId") == "ally-demo"
        ):
            logger.info("Default configuration already exists, skipping seed")
            return True

        # Create default configuration
        default_config = {
            "meta": {
                "version": "1.0.0",
                "clientId": "ally-demo",
                "lastUpdated": datetime.now().isoformat(),
                "configName": "Ally Platform Demo Configuration",
                "description": "Default configuration for the Ally Platform demo client",
            },
            "branding": {
                "companyName": "Ally Platform Demo",
                "logoUrl": "/assets/ally-logo.svg",
                "faviconUrl": "/assets/favicon.ico",
                "primaryColor": "#3B82F6",
                "secondaryColor": "#64748B",
                "accentColor": "#EF4444",
                "font": "inter",
            },
            "features": {
                "chatEnabled": True,
                "voiceEnabled": False,
                "fileUploadEnabled": True,
                "realTimeEnabled": True,
                "analyticsEnabled": True,
                "notificationsEnabled": True,
                "collaborationEnabled": False,
                "apiAccessEnabled": False,
                "exportEnabled": True,
            },
            "ui": {
                "layout": "modern",
                "darkMode": True,
                "themeToggle": True,
                "sidebarCollapsible": True,
                "compactMode": False,
                "animationsEnabled": True,
                "accessibilityMode": False,
            },
            "ai": {
                "model": "gemini-2.5-flash-lite",
                "promptTemplate": "You are a helpful AI assistant for {companyName}. Always be professional, informative, and helpful. Respond in a clear and concise manner.",
                "temperature": 0.7,
                "maxTokens": 2000,
                "systemMessage": "You are an AI assistant integrated into the Ally Platform. Help users with their questions and tasks efficiently.",
                "responseFormat": "markdown",
            },
            "languages": {
                "default": "en",
                "supported": ["en", "hi", "ar"],
                "rtlSupport": True,
                "autoDetect": True,
            },
            "security": {
                "jwtExpiration": 3600,
                "refreshTokenExpiration": 604800,
                "rateLimit": 1000,
                "sessionTimeout": 7200,
                "mfaEnabled": False,
            },
            "analytics": {
                "enabled": True,
                "trackingId": "",
                "customEvents": True,
                "userJourneyTracking": False,
                "performanceMonitoring": True,
                "errorTracking": True,
            },
        }

        # Save the default configuration
        success = config_manager.save_configuration("ally-demo", default_config)

        if success:
            logger.info("✅ Default configuration seeded successfully")
            return True
        else:
            logger.error("❌ Failed to seed default configuration")
            return False

    except Exception as e:
        logger.error(f"❌ Error seeding default configuration: {e}")
        return False


def verify_setup(database_url: str, redis_url: str = None):
    """Verify that the configuration system is working"""
    try:
        config_manager = ConfigurationManager(database_url, redis_url)

        # Test retrieving configuration
        config = config_manager.get_configuration("ally-demo")

        if config and config.get("meta", {}).get("clientId") == "ally-demo":
            logger.info("✅ Configuration system verification passed")
            return True
        else:
            logger.error("❌ Configuration system verification failed")
            return False

    except Exception as e:
        logger.error(f"❌ Configuration system verification error: {e}")
        return False


def main():
    """Main migration function"""
    logger.info("🚀 Starting Configuration Management Database Migration")
    logger.info("=" * 60)

    # Get database configuration
    database_url = os.getenv(
        "DATABASE_URL", "mysql://ally_user:ally_password@localhost:3307/ally_db"
    )
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")

    logger.info(f"Database URL: {database_url}")
    logger.info(f"Redis URL: {redis_url}")

    # Step 1: Create tables
    logger.info("\n📋 Step 1: Creating database tables...")
    if not create_tables(database_url):
        logger.error("Failed to create tables, aborting migration")
        sys.exit(1)

    # Step 2: Seed default configuration
    logger.info("\n🌱 Step 2: Seeding default configuration...")
    if not seed_default_configuration(database_url, redis_url):
        logger.error("Failed to seed default configuration, aborting migration")
        sys.exit(1)

    # Step 3: Verify setup
    logger.info("\n✅ Step 3: Verifying configuration system...")
    if not verify_setup(database_url, redis_url):
        logger.error("Configuration system verification failed, aborting migration")
        sys.exit(1)

    logger.info("\n🎉 Configuration Management Migration Completed Successfully!")
    logger.info("=" * 60)
    logger.info("The configuration management system is now ready to use.")
    logger.info("You can test it by accessing the API endpoints:")
    logger.info("  • GET /api/v1/config/public/ally-demo")
    logger.info("  • GET /api/v1/config/schema")
    logger.info("  • GET /api/v1/config/default")


if __name__ == "__main__":
    main()
