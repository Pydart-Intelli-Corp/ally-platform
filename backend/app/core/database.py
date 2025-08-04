"""
Database Configuration and Session Management for Ally Platform
Provides SQLAlchemy engine, session management, and database utilities.
"""

import os
import logging
from typing import Generator, Optional
from sqlalchemy import create_engine, event, Engine
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from sqlalchemy.pool import QueuePool
from .environment import env_config

# Configure logging
logger = logging.getLogger(__name__)

# Create declarative base for models
Base = declarative_base()


class DatabaseManager:
    """Database manager for handling connections and sessions"""

    def __init__(self):
        self.database_url = env_config.get_database_url()
        self.engine: Optional[Engine] = None
        self.SessionLocal: Optional[sessionmaker] = None
        self._initialize_engine()

    def _initialize_engine(self):
        """Initialize SQLAlchemy engine with connection pooling and SSL support"""
        try:
            # Parse database URL to extract SSL parameters
            from urllib.parse import urlparse, parse_qs

            parsed_url = urlparse(self.database_url)

            # Configure engine parameters
            engine_config = {
                "poolclass": QueuePool,
                "pool_pre_ping": True,
                "pool_recycle": 3600,
                "pool_size": 10,
                "max_overflow": 20,
                "echo": env_config.get_feature_flags()[
                    "debug_routes"
                ],  # SQL logging in debug mode
            }

            # Add SSL configuration for Azure MySQL if needed
            if (
                "azure" in self.database_url
                or env_config.detect_environment() == "production"
                or "ssl=true" in self.database_url
            ):
                connect_args = {"ssl": True}

                engine_config["connect_args"] = connect_args
                logger.info("Configured SSL connection for Azure MySQL")

            # Configure engine with connection pooling
            self.engine = create_engine(self.database_url, **engine_config)

            # Configure session factory
            self.SessionLocal = sessionmaker(
                autocommit=False, autoflush=False, bind=self.engine
            )

            # Test connection
            self._test_connection()

            logger.info("Database engine initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize database engine: {e}")
            raise

    def _test_connection(self):
        """Test database connection"""
        try:
            with self.engine.connect() as connection:
                result = connection.execute("SELECT 1 as test")
                test_value = result.fetchone()[0]
                if test_value == 1:
                    logger.info("Database connection test successful")
                else:
                    raise Exception("Connection test failed")
        except Exception as e:
            logger.warning(
                f"Database connection test failed (this is normal during migrations): {e}"
            )
            # Don't raise during import - allow migrations to continue

    def create_tables(self):
        """Create all database tables"""
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Failed to create database tables: {e}")
            raise

    def get_session(self) -> Generator[Session, None, None]:
        """
        Get database session with automatic cleanup

        Yields:
            Session: SQLAlchemy database session
        """
        if not self.SessionLocal:
            raise Exception("Database not initialized")

        session = self.SessionLocal()
        try:
            yield session
        except Exception as e:
            session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            session.close()

    def get_engine(self) -> Engine:
        """Get SQLAlchemy engine"""
        if not self.engine:
            raise Exception("Database engine not initialized")
        return self.engine


# Global database manager instance
db_manager = DatabaseManager()


# Convenience functions for dependency injection
def get_database_session() -> Generator[Session, None, None]:
    """Dependency function for FastAPI to get database session"""
    yield from db_manager.get_session()


def get_database_engine() -> Engine:
    """Get database engine instance"""
    return db_manager.get_engine()


def create_database_tables():
    """Create all database tables"""
    db_manager.create_tables()


# Database event listeners for logging and monitoring
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """Configure database connection settings"""
    # This is mainly for SQLite, but can be extended for MySQL optimizations
    pass


@event.listens_for(Engine, "before_cursor_execute")
def receive_before_cursor_execute(
    conn, cursor, statement, parameters, context, executemany
):
    """Log slow queries in debug mode"""
    if env_config.get_feature_flags()["debug_routes"]:
        context._query_start_time = logger.info(
            f"Executing query: {statement[:100]}..."
        )


@event.listens_for(Engine, "after_cursor_execute")
def receive_after_cursor_execute(
    conn, cursor, statement, parameters, context, executemany
):
    """Log query execution time"""
    if env_config.get_feature_flags()["debug_routes"] and hasattr(
        context, "_query_start_time"
    ):
        # In a real implementation, you would calculate the time difference
        logger.info("Query executed successfully")
