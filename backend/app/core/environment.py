"""
Environment Configuration Manager
Handles environment-specific configuration loading and validation.
"""

import os
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Union
from dotenv import load_dotenv

logger = logging.getLogger(__name__)


class EnvironmentConfig:
    """
    Environment configuration manager that loads and validates
    environment-specific settings with secure defaults.
    """

    def __init__(self, env_name: Optional[str] = None):
        """
        Initialize environment configuration.

        Args:
            env_name: Environment name (development, production, etc.)
        """
        self.env_name = env_name or self.detect_environment()
        self.project_root = Path(__file__).parent.parent.parent.parent
        self.load_environment_file()

    def detect_environment(self) -> str:
        """Detect the current environment from various sources."""
        # Check environment variables
        env = os.getenv("ENVIRONMENT", os.getenv("ENV", "development"))

        # Check for common production indicators
        if any(
            indicator in os.environ
            for indicator in ["PRODUCTION", "PROD", "RAILWAY_ENVIRONMENT"]
        ):
            return "production"

        return env.lower()

    def load_environment_file(self) -> bool:
        """Load the appropriate .env file for the current environment."""
        env_file = self.project_root / f".env.{self.env_name}"

        if env_file.exists():
            load_dotenv(env_file, override=True)
            logger.info(f"Loaded environment configuration: {env_file}")
            return True
        else:
            logger.warning(f"Environment file not found: {env_file}")

            # Try to load default .env file
            default_env = self.project_root / ".env"
            if default_env.exists():
                load_dotenv(default_env, override=False)
                logger.info(f"Loaded default environment configuration: {default_env}")
                return True

        return False

    def get(self, key: str, default: Any = None, cast_type: type = str) -> Any:
        """
        Get environment variable with type casting and default fallback.

        Args:
            key: Environment variable name
            default: Default value if not found
            cast_type: Type to cast the value to

        Returns:
            Environment variable value cast to specified type
        """
        value = os.getenv(key, default)

        if value is None:
            return default

        if cast_type == bool:
            return str(value).lower() in ("true", "1", "yes", "on")
        elif cast_type == list:
            # Handle list parsing for CORS origins, etc.
            if isinstance(value, str):
                if value.startswith("[") and value.endswith("]"):
                    # Parse JSON-like list
                    try:
                        import json

                        return json.loads(value)
                    except json.JSONDecodeError:
                        # Fallback to comma-separated parsing
                        return [
                            item.strip().strip("\"'")
                            for item in value.strip("[]").split(",")
                        ]
                else:
                    return [item.strip() for item in value.split(",")]
            return value
        elif cast_type in (int, float):
            try:
                return cast_type(value)
            except (ValueError, TypeError):
                logger.warning(
                    f"Could not cast {key}={value} to {cast_type}, using default: {default}"
                )
                return default

        return cast_type(value) if value is not None else default

    def get_database_url(self) -> str:
        """Get database URL with environment-specific fallbacks."""
        database_url = self.get("DATABASE_URL")

        # If we have a direct DATABASE_URL, return it
        if database_url:
            # Handle .NET style connection string format
            if database_url.startswith("Server="):
                # Convert .NET connection string to MySQL URL
                parts = {}
                for part in database_url.split(";"):
                    if "=" in part:
                        key, value = part.split("=", 1)
                        parts[key.strip()] = value.strip()

                # Extract connection details
                server = parts.get("Server", "localhost")
                port = parts.get("Port", "3306")
                user = parts.get("UserID", "root")
                password = parts.get("Password", "")
                database = parts.get("Database", "ally-db")

                # URL encode the password to handle special characters
                import urllib.parse

                encoded_password = urllib.parse.quote(password, safe="")

                # Construct MySQL URL with SSL
                return f"mysql://{user}:{encoded_password}@{server}:{port}/{database}?ssl=true"
            else:
                # Return standard MySQL URL as-is
                return database_url

        # Fallback to constructing from individual components
        return (
            f"mysql://{self.get('MYSQL_USER', 'root')}:"
            f"{self.get('MYSQL_PASSWORD', 'password')}@"
            f"{self.get('MYSQL_HOST', 'localhost')}:"
            f"{self.get('MYSQL_PORT', 3306, int)}/"
            f"{self.get('MYSQL_DATABASE', 'ally_db')}"
        )

    def get_redis_config(self) -> Dict[str, Any]:
        """Get Redis configuration with environment-specific settings."""
        return {
            "host": self.get("REDIS_HOST", "localhost"),
            "port": self.get("REDIS_PORT", 6379, int),
            "db": self.get("REDIS_DB", 0, int),
            "password": self.get("REDIS_PASSWORD") or None,
            "ttl": self.get("REDIS_TTL", 3600, int),
        }

    def get_api_keys(self) -> Dict[str, Optional[str]]:
        """Get API keys with secure handling."""
        return {
            "openai": self.get("OPENAI_API_KEY"),
            "stripe": self.get("STRIPE_API_KEY"),
            "sendgrid": self.get("SENDGRID_API_KEY"),
            "google_ai": self.get("GOOGLE_AI_API_KEY"),
            "weaviate_url": self.get("WEAVIATE_URL"),
            "weaviate_key": self.get("WEAVIATE_API_KEY"),
            "aws_access_key": self.get("AWS_ACCESS_KEY_ID"),
            "aws_secret_key": self.get("AWS_SECRET_ACCESS_KEY"),
        }

    def get_security_config(self) -> Dict[str, Any]:
        """Get security configuration with environment-specific settings."""
        return {
            "secret_key": self.get("SECRET_KEY", "dev-fallback-change-in-production"),
            "jwt_secret": self.get(
                "JWT_SECRET_KEY", "dev-jwt-fallback-change-in-production"
            ),
            "jwt_algorithm": self.get("JWT_ALGORITHM", "HS256"),
            "jwt_expiration_hours": self.get("JWT_EXPIRATION_HOURS", 24, int),
            "cors_origins": self.get(
                "CORS_ORIGINS", ["http://localhost:3000", "http://localhost:3001"], list
            ),
            "cors_credentials": self.get("CORS_ALLOW_CREDENTIALS", True, bool),
            "cors_methods": self.get("CORS_ALLOW_METHODS", ["*"], list),
            "cors_headers": self.get("CORS_ALLOW_HEADERS", ["*"], list),
        }

    def get_feature_flags(self) -> Dict[str, bool]:
        """Get feature flags with environment-specific defaults."""
        return {
            "debug_routes": self.get(
                "ENABLE_DEBUG_ROUTES", self.env_name == "development", bool
            ),
            "admin_panel": self.get("ENABLE_ADMIN_PANEL", True, bool),
            "analytics": self.get(
                "ENABLE_ANALYTICS", self.env_name == "production", bool
            ),
            "rate_limiting": self.get(
                "ENABLE_RATE_LIMITING", self.env_name == "production", bool
            ),
        }

    def get_logging_config(self) -> Dict[str, Any]:
        """Get logging configuration with environment-specific settings."""
        return {
            "level": self.get(
                "LOG_LEVEL", "DEBUG" if self.env_name == "development" else "INFO"
            ),
            "format": self.get(
                "LOG_FORMAT",
                "development" if self.env_name == "development" else "json",
            ),
            "to_file": self.get("LOG_TO_FILE", False, bool),
            "rotation": self.get("LOG_ROTATION", False, bool),
        }

    def get_server_config(self) -> Dict[str, Any]:
        """Get server configuration with environment-specific settings."""
        return {
            "host": self.get("HOST", "0.0.0.0"),
            "port": self.get("PORT", 8002, int),
            "debug": self.get("DEBUG", self.env_name == "development", bool),
            "reload": self.get("RELOAD", self.env_name == "development", bool),
        }

    def get_config_management_settings(self) -> Dict[str, Any]:
        """Get configuration management specific settings."""
        return {
            "cache_ttl": self.get("CONFIG_CACHE_TTL", 3600, int),
            "auto_reload": self.get(
                "CONFIG_AUTO_RELOAD", self.env_name == "development", bool
            ),
            "schema_validation": self.get("CONFIG_SCHEMA_VALIDATION", True, bool),
            "default_company": self.get("CONFIG_DEFAULT_COMPANY", "Ally Platform"),
        }

    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.env_name == "production"

    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.env_name == "development"

    def validate_required_vars(self, required_vars: list) -> Dict[str, bool]:
        """
        Validate that required environment variables are set.

        Args:
            required_vars: List of required variable names

        Returns:
            Dictionary with validation results
        """
        results = {}
        for var in required_vars:
            value = os.getenv(var)
            results[var] = value is not None and value.strip() != ""

            if not results[var]:
                logger.warning(f"Required environment variable not set: {var}")

        return results

    def get_all_config(self) -> Dict[str, Any]:
        """Get complete configuration dictionary."""
        return {
            "environment": self.env_name,
            "database": self.get_database_url(),
            "redis": self.get_redis_config(),
            "api_keys": self.get_api_keys(),
            "security": self.get_security_config(),
            "features": self.get_feature_flags(),
            "logging": self.get_logging_config(),
            "server": self.get_server_config(),
            "config_management": self.get_config_management_settings(),
        }


# Global environment configuration instance
env_config = EnvironmentConfig()


# Convenience functions for backward compatibility
def get_env_var(key: str, default: Any = None, cast_type: type = str) -> Any:
    """Get environment variable with type casting."""
    return env_config.get(key, default, cast_type)


def get_database_url() -> str:
    """Get database URL."""
    return env_config.get_database_url()


def get_redis_config() -> Dict[str, Any]:
    """Get Redis configuration."""
    return env_config.get_redis_config()


def is_production() -> bool:
    """Check if running in production."""
    return env_config.is_production()


def is_development() -> bool:
    """Check if running in development."""
    return env_config.is_development()
