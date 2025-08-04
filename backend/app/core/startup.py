"""
Application startup and initialization
"""

import logging
from app.core.environment import env_config
from app.core.database import create_database_tables
from app.config_manager import init_config_manager
from app.core.config import get_company_name

logger = logging.getLogger(__name__)


async def startup_handler():
    """Initialize application services on startup"""
    logger.info("🚀 Starting Ally Platform Backend...")

    try:
        # Initialize database tables
        logger.info("📋 Initializing database tables...")
        create_database_tables()
        logger.info("✅ Database tables initialized successfully")

        # Initialize configuration manager
        logger.info("⚙️ Initializing configuration manager...")
        database_url = env_config.get_database_url()
        redis_config = env_config.get_redis_config()
        redis_url = f"redis://{redis_config['host']}:{redis_config['port']}/{redis_config['db']}"

        init_config_manager(database_url, redis_url)
        logger.info("✅ Configuration manager initialized successfully")

        # Log startup completion
        company_name = get_company_name()
        logger.info(f"🎉 {company_name} Backend started successfully!")
        logger.info(f"📖 API Documentation available at: /docs")
        logger.info(f"🔧 Environment: {env_config.detect_environment()}")

    except Exception as e:
        logger.error(f"❌ Startup failed: {e}")
        # Don't crash the app, but log the error
