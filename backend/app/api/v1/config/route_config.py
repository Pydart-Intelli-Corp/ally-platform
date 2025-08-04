"""
Configuration API routes for Ally Platform.
Provides endpoints for accessing configuration data.
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import logging
import json

from ....core.config import (
    get_config_value,
    is_feature_enabled,
    get_company_name,
    reload_config,
    set_cached_config,
    clear_cached_config,
    redis_client,
    REDIS_AVAILABLE,
    load_config,
)

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()


@router.get("/")
def get_config() -> Dict[str, Any]:
    """
    Get the complete configuration.

    Returns:
        Dict containing all configuration data
    """
    try:
        logger.info("Configuration requested via API")
        return load_config()
    except Exception as e:
        logger.error(f"Error retrieving configuration: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve configuration")


@router.get("/branding")
def get_branding() -> Dict[str, Any]:
    """
    Get branding configuration only.

    Returns:
        Dict containing branding configuration
    """
    try:
        config = load_config()
        return config.get("branding", {})
    except Exception as e:
        logger.error(f"Error retrieving branding configuration: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to retrieve branding configuration"
        )


@router.get("/features")
def get_features() -> Dict[str, Any]:
    """
    Get features configuration only.

    Returns:
        Dict containing features configuration
    """
    try:
        config = load_config()
        return config.get("features", {})
    except Exception as e:
        logger.error(f"Error retrieving features configuration: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to retrieve features configuration"
        )


@router.get("/ui")
def get_ui_config() -> Dict[str, Any]:
    """
    Get UI configuration only.

    Returns:
        Dict containing UI configuration
    """
    try:
        config = load_config()
        return config.get("ui", {})
    except Exception as e:
        logger.error(f"Error retrieving UI configuration: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to retrieve UI configuration"
        )


@router.get("/ai")
def get_ai_config() -> Dict[str, Any]:
    """
    Get AI configuration only.

    Returns:
        Dict containing AI configuration
    """
    try:
        config = load_config()
        return config.get("ai", {})
    except Exception as e:
        logger.error(f"Error retrieving AI configuration: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to retrieve AI configuration"
        )


@router.get("/feature/{feature_name}")
def get_feature_flag(feature_name: str) -> Dict[str, Any]:
    """
    Get a specific feature flag status.

    Args:
        feature_name: Name of the feature to check

    Returns:
        Dict containing feature name and status
    """
    try:
        enabled = is_feature_enabled(feature_name)
        return {"feature": feature_name, "enabled": enabled}
    except Exception as e:
        logger.error(f"Error retrieving feature flag {feature_name}: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to retrieve feature flag: {feature_name}"
        )


@router.get("/company")
def get_company_info() -> Dict[str, Any]:
    """
    Get company information.

    Returns:
        Dict containing company name and basic info
    """
    try:
        config = load_config()
        return {
            "company_name": get_company_name(),
            "client_id": config.get("meta", {}).get("clientId", "unknown"),
            "version": config.get("meta", {}).get("version", "unknown"),
        }
    except Exception as e:
        logger.error(f"Error retrieving company information: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to retrieve company information"
        )


@router.get("/health")
def config_health_check() -> Dict[str, Any]:
    """
    Health check for configuration API.

    Returns:
        Dict containing health status
    """
    try:
        # Test configuration access
        config = load_config()
        company_name = get_company_name()
        config_sections = len(config.keys()) if config else 0

        return {
            "status": "healthy",
            "message": "Configuration API is working",
            "company_name": company_name,
            "config_sections": config_sections,
            "config_loaded": bool(config),
        }
    except Exception as e:
        logger.error(f"Configuration health check failed: {e}")
        raise HTTPException(status_code=500, detail="Configuration health check failed")


@router.post("/reload")
def reload_configuration() -> Dict[str, Any]:
    """
    Reload configuration from file and update cache.

    Admin endpoint to force configuration reload from disk.
    Clears both memory and Redis cache, then loads fresh configuration.

    Returns:
        Dict containing reload status and updated configuration info
    """
    try:
        logger.info("Configuration reload requested via API")

        # Get current configuration info for comparison
        current_config = load_config()
        old_company = get_company_name()
        old_version = current_config.get("meta", {}).get("version", "unknown")

        # Reload configuration (clears memory and Redis cache, loads from file)
        fresh_config = reload_config()

        # Manually update Redis cache with fresh config
        if REDIS_AVAILABLE:
            set_cached_config("client-config.json", fresh_config)
            logger.info("Configuration updated in Redis cache")

        # Get new configuration info
        new_company = fresh_config.get("branding", {}).get("companyName", "Unknown")
        new_version = fresh_config.get("meta", {}).get("version", "unknown")
        new_sections = len(fresh_config.keys()) if fresh_config else 0

        # Log the reload
        logger.info(f"Configuration reloaded: {old_company} -> {new_company}")

        return {
            "message": "Configuration reloaded successfully",
            "status": "success",
            "reload_timestamp": fresh_config.get("meta", {}).get(
                "lastUpdated", "unknown"
            ),
            "changes_detected": {
                "company_name_changed": old_company != new_company,
                "version_changed": old_version != new_version,
            },
            "configuration_info": {
                "company_name": new_company,
                "version": new_version,
                "sections": new_sections,
                "client_id": fresh_config.get("meta", {}).get("clientId", "unknown"),
            },
            "cache_info": {
                "memory_cache_cleared": True,
                "redis_cache_updated": REDIS_AVAILABLE,
                "redis_available": REDIS_AVAILABLE,
            },
        }

    except Exception as e:
        logger.error(f"Configuration reload failed: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to reload configuration: {str(e)}"
        )


@router.post("/clear-cache")
def clear_configuration_cache() -> Dict[str, Any]:
    """
    Clear configuration cache without reloading.

    Admin endpoint to clear both memory and Redis cache.
    Next configuration request will reload from file.

    Returns:
        Dict containing cache clear status
    """
    try:
        logger.info("Configuration cache clear requested via API")

        # Clear Redis cache
        redis_cleared = False
        if REDIS_AVAILABLE:
            redis_cleared = clear_cached_config("client-config.json")

        # Clear memory cache
        load_config.cache_clear()

        logger.info("Configuration cache cleared successfully")

        return {
            "message": "Configuration cache cleared successfully",
            "status": "success",
            "cache_info": {
                "memory_cache_cleared": True,
                "redis_cache_cleared": redis_cleared,
                "redis_available": REDIS_AVAILABLE,
            },
            "note": "Next configuration request will reload from file",
        }

    except Exception as e:
        logger.error(f"Configuration cache clear failed: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to clear configuration cache: {str(e)}"
        )


@router.get("/{section}")
def get_config_section(section: str) -> Dict[str, Any]:
    """
    Get a specific configuration section.

    Args:
        section: Name of the configuration section (e.g., 'app', 'database', 'security')

    Returns:
        Dict containing the requested configuration section
    """
    try:
        config = load_config()

        if section not in config:
            raise HTTPException(
                status_code=404, detail=f"Configuration section '{section}' not found"
            )

        return config[section]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving configuration section '{section}': {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve configuration section: {section}",
        )
