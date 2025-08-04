"""
Configuration Loader for Ally Platform
Handles loading and caching of client configuration with Redis support and environment overrides.
"""

import json
import os
from functools import lru_cache
from pathlib import Path
from typing import Dict, Any, Optional
import logging
import redis
from redis.exceptions import ConnectionError as RedisConnectionError

# Import environment configuration
from .environment import env_config, get_redis_config

# Configure logging
logger = logging.getLogger(__name__)

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent

# Redis configuration with environment override support
redis_config = get_redis_config()
REDIS_HOST = redis_config["host"]
REDIS_PORT = redis_config["port"]
REDIS_DB = redis_config["db"]
REDIS_PASSWORD = redis_config["password"]
REDIS_TTL = redis_config["ttl"]

# Initialize Redis client with environment configuration
try:
    redis_client = redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        db=REDIS_DB,
        password=REDIS_PASSWORD,
        decode_responses=True,
    )
    # Test connection
    redis_client.ping()
    REDIS_AVAILABLE = True
    logger.info(f"Redis connection established: {REDIS_HOST}:{REDIS_PORT}")
except (RedisConnectionError, Exception) as e:
    redis_client = None
    REDIS_AVAILABLE = False
    logger.warning(f"Redis not available, falling back to memory caching: {e}")


def get_redis_key(config_file: str) -> str:
    """Generate Redis key for configuration file."""
    return f"config:{config_file}"


def get_cached_config(
    config_file: str = "client-config.json",
) -> Optional[Dict[str, Any]]:
    """
    Get configuration from Redis cache.

    Args:
        config_file: Name of the configuration file

    Returns:
        Cached configuration data or None if not cached/Redis unavailable
    """
    if not REDIS_AVAILABLE:
        return None

    try:
        redis_key = get_redis_key(config_file)
        cached_data = redis_client.get(redis_key)
        if cached_data:
            logger.info(f"Configuration loaded from Redis cache: {config_file}")
            return json.loads(cached_data)
    except Exception as e:
        logger.warning(f"Failed to get configuration from Redis: {e}")

    return None


def set_cached_config(config_file: str, config_data: Dict[str, Any]) -> bool:
    """
    Set configuration in Redis cache.

    Args:
        config_file: Name of the configuration file
        config_data: Configuration data to cache

    Returns:
        True if successfully cached, False otherwise
    """
    if not REDIS_AVAILABLE:
        return False

    try:
        redis_key = get_redis_key(config_file)
        redis_client.setex(redis_key, REDIS_TTL, json.dumps(config_data))
        logger.info(f"Configuration cached in Redis: {config_file} (TTL: {REDIS_TTL}s)")
        return True
    except Exception as e:
        logger.warning(f"Failed to cache configuration in Redis: {e}")
        return False


def clear_cached_config(config_file: str = None) -> bool:
    """
    Clear configuration from Redis cache.

    Args:
        config_file: Specific config file to clear, or None to clear all configs

    Returns:
        True if successfully cleared, False otherwise
    """
    if not REDIS_AVAILABLE:
        return False

    try:
        if config_file:
            redis_key = get_redis_key(config_file)
            result = redis_client.delete(redis_key)
            logger.info(f"Cleared Redis cache for: {config_file}")
            return result > 0
        else:
            # Clear all config keys
            pattern = get_redis_key("*")
            keys = redis_client.keys(pattern)
            if keys:
                result = redis_client.delete(*keys)
                logger.info(f"Cleared {result} configuration entries from Redis cache")
                return result > 0
            return True
    except Exception as e:
        logger.warning(f"Failed to clear Redis cache: {e}")
        return False


@lru_cache()
def load_config(config_file: str = "client-config.json") -> Dict[str, Any]:
    """
    Load configuration from JSON file with Redis caching and environment overrides.

    Args:
        config_file: Name of the configuration file to load

    Returns:
        Dictionary containing the configuration data with environment overrides applied

    Raises:
        FileNotFoundError: If the configuration file doesn't exist
        json.JSONDecodeError: If the configuration file is not valid JSON
    """
    # Try Redis cache first
    cached_config = get_cached_config(config_file)
    if cached_config:
        # Still apply environment overrides to cached config
        return apply_environment_overrides(cached_config)

    # Load from file if not cached
    config_path = PROJECT_ROOT / "config" / config_file

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config_data = json.load(f)
            logger.info(f"Configuration loaded from file: {config_path}")

            # Apply environment overrides before caching
            config_with_overrides = apply_environment_overrides(config_data)

            # Cache the base config (without environment overrides) in Redis
            # Environment overrides are applied at runtime
            set_cached_config(config_file, config_data)

            return config_with_overrides
    except FileNotFoundError:
        logger.error(f"Configuration file not found: {config_path}")
        # Try to load default configuration as fallback
        default_path = PROJECT_ROOT / "config" / "default-config.json"
        if default_path.exists():
            logger.info(f"Loading default configuration from {default_path}")
            with open(default_path, "r", encoding="utf-8") as f:
                fallback_config = json.load(f)
                # Apply environment overrides to fallback config
                fallback_with_overrides = apply_environment_overrides(fallback_config)
                # Cache the base fallback config
                set_cached_config(config_file, fallback_config)
                return fallback_with_overrides
        else:
            # Create minimal default configuration with environment values
            logger.warning(
                "No configuration files found, creating minimal default with environment values"
            )
            minimal_config = create_minimal_default_config()
            return apply_environment_overrides(minimal_config)
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in configuration file {config_path}: {e}")
        raise


@lru_cache()
def load_default_config() -> Dict[str, Any]:
    """Load the default configuration."""
    return load_config("default-config.json")


@lru_cache()
def load_production_config() -> Dict[str, Any]:
    """Load the production configuration."""
    return load_config("production-config.json")


def create_minimal_default_config() -> Dict[str, Any]:
    """
    Create a minimal default configuration when no config files are available.

    Returns:
        Minimal configuration dictionary with environment-based defaults
    """
    return {
        "branding": {
            "companyName": env_config.get("CONFIG_DEFAULT_COMPANY", "Ally Platform"),
            "logoUrl": "/logo.png",
            "primaryColor": "#007bff",
            "secondaryColor": "#6c757d",
        },
        "features": {
            "chatEnabled": True,
            "notificationsEnabled": True,
            "analyticsEnabled": env_config.is_production(),
            "darkModeEnabled": True,
        },
        "ui": {"theme": "light", "language": "en", "timezone": "UTC"},
        "api": {
            "timeout": 30,
            "retryCount": 3,
            "baseUrl": f"http://localhost:{env_config.get('PORT', 8002)}",
        },
        "company": {
            "name": env_config.get("CONFIG_DEFAULT_COMPANY", "Ally Platform"),
            "contactEmail": "support@allyplatform.com",
            "supportUrl": "https://support.allyplatform.com",
        },
    }


def apply_environment_overrides(config_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Apply environment variable overrides to configuration data.

    Environment variables follow the pattern: CONFIG_<SECTION>_<KEY>=value
    For nested keys, use underscores: CONFIG_BRANDING_COMPANY_NAME=value

    Args:
        config_data: Base configuration data

    Returns:
        Configuration data with environment overrides applied
    """
    overridden_config = config_data.copy()

    # Common configuration keys that can be overridden
    override_mappings = {
        # Branding overrides
        "CONFIG_BRANDING_COMPANY_NAME": ("branding", "companyName"),
        "CONFIG_BRANDING_LOGO_URL": ("branding", "logoUrl"),
        "CONFIG_BRANDING_PRIMARY_COLOR": ("branding", "primaryColor"),
        "CONFIG_BRANDING_SECONDARY_COLOR": ("branding", "secondaryColor"),
        # Feature flags
        "CONFIG_FEATURES_CHAT_ENABLED": ("features", "chatEnabled"),
        "CONFIG_FEATURES_NOTIFICATIONS_ENABLED": ("features", "notificationsEnabled"),
        "CONFIG_FEATURES_ANALYTICS_ENABLED": ("features", "analyticsEnabled"),
        "CONFIG_FEATURES_DARK_MODE_ENABLED": ("features", "darkModeEnabled"),
        # UI Configuration
        "CONFIG_UI_THEME": ("ui", "theme"),
        "CONFIG_UI_LANGUAGE": ("ui", "language"),
        "CONFIG_UI_TIMEZONE": ("ui", "timezone"),
        # API Configuration
        "CONFIG_API_TIMEOUT": ("api", "timeout"),
        "CONFIG_API_RETRY_COUNT": ("api", "retryCount"),
        "CONFIG_API_BASE_URL": ("api", "baseUrl"),
        # Company information
        "CONFIG_COMPANY_NAME": ("company", "name"),
        "CONFIG_COMPANY_CONTACT_EMAIL": ("company", "contactEmail"),
        "CONFIG_COMPANY_SUPPORT_URL": ("company", "supportUrl"),
    }

    # Apply environment overrides
    for env_var, (section, key) in override_mappings.items():
        env_value = env_config.get(env_var)
        if env_value is not None:
            # Ensure section exists
            if section not in overridden_config:
                overridden_config[section] = {}

            # Convert boolean strings
            if isinstance(env_value, str):
                if env_value.lower() in ("true", "false"):
                    env_value = env_value.lower() == "true"
                elif env_value.isdigit():
                    env_value = int(env_value)
                elif "." in env_value and env_value.replace(".", "").isdigit():
                    env_value = float(env_value)

            overridden_config[section][key] = env_value
            logger.info(
                f"Applied environment override: {env_var} -> {section}.{key} = {env_value}"
            )

    # Apply environment-specific feature flags
    feature_flags = env_config.get_feature_flags()
    if "features" not in overridden_config:
        overridden_config["features"] = {}

    overridden_config["features"].update(
        {
            "debugRoutes": feature_flags["debug_routes"],
            "adminPanel": feature_flags["admin_panel"],
            "analyticsEnabled": feature_flags["analytics"],
            "rateLimiting": feature_flags["rate_limiting"],
        }
    )

    # Apply default company name from environment
    company_name = env_config.get("CONFIG_DEFAULT_COMPANY")
    if company_name and "branding" in overridden_config:
        if not overridden_config["branding"].get("companyName"):
            overridden_config["branding"]["companyName"] = company_name

    return overridden_config


def get_config_value(
    key_path: str, default: Any = None, config_data: Optional[Dict[str, Any]] = None
) -> Any:
    """
    Get a configuration value using dot notation with environment override support.

    Args:
        key_path: Dot-separated path to the configuration key (e.g., "branding.companyName")
        default: Default value to return if key is not found
        config_data: Configuration data to search in (if None, loads default config)

    Returns:
        The configuration value with environment overrides applied, or default if not found

    Example:
        >>> get_config_value("branding.companyName")
        "Ally Platform"
        >>> get_config_value("features.chatEnabled")
        True
    """
    if config_data is None:
        config_data = load_config()

    # Apply environment overrides
    config_data = apply_environment_overrides(config_data)

    keys = key_path.split(".")
    current = config_data

    try:
        for key in keys:
            current = current[key]
        return current
    except (KeyError, TypeError):
        # Check for direct environment variable override
        env_var = f"CONFIG_{key_path.upper().replace('.', '_')}"
        env_value = env_config.get(env_var)
        if env_value is not None:
            logger.info(f"Using environment override for {key_path}: {env_value}")
            return env_value

        logger.warning(
            f"Configuration key '{key_path}' not found, returning default: {default}"
        )
        return default


def reload_config(config_file: str = "client-config.json") -> Dict[str, Any]:
    """
    Clear both memory and Redis cache and reload the configuration.

    Args:
        config_file: Name of the configuration file to reload

    Returns:
        Freshly loaded configuration data
    """
    # Clear memory cache
    load_config.cache_clear()

    # Clear Redis cache
    clear_cached_config(config_file)

    # Reload from file
    return load_config(config_file)


def validate_config_structure(config_data: Dict[str, Any]) -> bool:
    """
    Validate that the configuration has the required structure.

    Args:
        config_data: Configuration data to validate

    Returns:
        True if valid, False otherwise
    """
    required_sections = ["meta", "branding", "features", "ui", "ai"]

    for section in required_sections:
        if section not in config_data:
            logger.error(f"Required configuration section '{section}' is missing")
            return False

    # Validate required fields in meta section
    meta_required = ["version", "clientId", "lastUpdated"]
    for field in meta_required:
        if field not in config_data.get("meta", {}):
            logger.error(f"Required meta field '{field}' is missing")
            return False

    # Validate required fields in branding section
    branding_required = ["companyName", "primaryColor"]
    for field in branding_required:
        if field not in config_data.get("branding", {}):
            logger.error(f"Required branding field '{field}' is missing")
            return False

    # Validate AI model field
    if "model" not in config_data.get("ai", {}):
        logger.error("Required AI field 'model' is missing")
        return False

    logger.info("Configuration structure validation passed")
    return True


# Load the default configuration at module import
try:
    config = load_config()
    logger.info(
        f"Default configuration loaded: {config.get('meta', {}).get('configName', 'Unknown')}"
    )
except Exception as e:
    logger.error(f"Failed to load configuration at startup: {e}")
    config = {}


# Convenience function for backward compatibility
def get_company_name() -> str:
    """Get the company name from configuration."""
    return get_config_value("branding.companyName", "Ally Platform")


def get_primary_color() -> str:
    """Get the primary color from configuration."""
    return get_config_value("branding.primaryColor", "#3B82F6")


def is_feature_enabled(feature_name: str) -> bool:
    """Check if a specific feature is enabled."""
    return get_config_value(f"features.{feature_name}", False)


def get_ai_model() -> str:
    """Get the configured AI model."""
    return get_config_value("ai.model", "gemini-2.5-flash-lite")


def get_ai_temperature() -> float:
    """Get the configured AI temperature."""
    return get_config_value("ai.temperature", 0.7)


def get_max_tokens() -> int:
    """Get the configured maximum tokens."""
    return get_config_value("ai.maxTokens", 2000)


def get_cache_info() -> Dict[str, Any]:
    """
    Get information about caching status.

    Returns:
        Dictionary with cache information including Redis status and memory cache stats
    """
    cache_info = {
        "redis_available": REDIS_AVAILABLE,
        "redis_host": REDIS_HOST,
        "redis_port": REDIS_PORT,
        "redis_ttl": REDIS_TTL,
        "memory_cache_info": load_config.cache_info()._asdict(),
    }

    if REDIS_AVAILABLE:
        try:
            redis_info = redis_client.info()
            cache_info["redis_info"] = {
                "connected_clients": redis_info.get("connected_clients", 0),
                "used_memory_human": redis_info.get("used_memory_human", "0B"),
                "keyspace_hits": redis_info.get("keyspace_hits", 0),
                "keyspace_misses": redis_info.get("keyspace_misses", 0),
            }

            # Count config keys in Redis
            config_keys = redis_client.keys(get_redis_key("*"))
            cache_info["redis_config_keys"] = len(config_keys)
            cache_info["redis_config_key_names"] = [
                key.split(":")[-1] for key in config_keys
            ]

        except Exception as e:
            cache_info["redis_error"] = str(e)

    return cache_info


def test_redis_connection() -> Dict[str, Any]:
    """
    Test Redis connection and caching functionality.

    Returns:
        Test results including connection status and caching performance
    """
    test_results = {
        "redis_available": REDIS_AVAILABLE,
        "timestamp": json.dumps(os.path.getmtime(__file__)),
    }

    if not REDIS_AVAILABLE:
        test_results["message"] = "Redis not available, using memory cache only"
        return test_results

    try:
        # Test basic Redis operations
        test_key = "config:test"
        test_value = {
            "test": "redis_connectivity",
            "timestamp": test_results["timestamp"],
        }

        # Test set operation
        redis_client.setex(test_key, 60, json.dumps(test_value))
        test_results["set_operation"] = "success"

        # Test get operation
        retrieved = redis_client.get(test_key)
        if retrieved:
            parsed = json.loads(retrieved)
            test_results["get_operation"] = "success"
            test_results["data_integrity"] = parsed == test_value
        else:
            test_results["get_operation"] = "failed"
            test_results["data_integrity"] = False

        # Test delete operation
        deleted = redis_client.delete(test_key)
        test_results["delete_operation"] = "success" if deleted > 0 else "failed"

        # Test ping
        ping_result = redis_client.ping()
        test_results["ping"] = ping_result

        test_results["overall_status"] = "healthy"

    except Exception as e:
        test_results["error"] = str(e)
        test_results["overall_status"] = "unhealthy"

    return test_results
