"""
Configuration API Endpoints for Ally Platform
Provides REST API for managing client configurations.
"""

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, ValidationError
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime, timezone

from .config_manager import get_config_manager, ConfigurationManager, ConfigurationError

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/v1/config", tags=["Configuration Management"])

# Security
security = HTTPBearer()


# Pydantic models for API requests/responses
class ConfigResponse(BaseModel):
    """Response model for configuration data"""

    success: bool
    data: Dict[str, Any]
    message: str
    timestamp: str


class ConfigListResponse(BaseModel):
    """Response model for configuration list"""

    success: bool
    data: List[Dict[str, Any]]
    message: str
    timestamp: str
    total: int


class ErrorResponse(BaseModel):
    """Response model for errors"""

    success: bool = False
    error: str
    code: str
    timestamp: str


class ConfigUpdateRequest(BaseModel):
    """Request model for configuration updates"""

    config: Dict[str, Any]
    validate_only: bool = False


class FeatureFlagResponse(BaseModel):
    """Response model for feature flag"""

    success: bool
    feature_name: str
    enabled: bool
    client_id: str
    timestamp: str


class BrandingResponse(BaseModel):
    """Response model for branding configuration"""

    success: bool
    branding: Dict[str, Any]
    client_id: str
    timestamp: str


def get_current_timestamp() -> str:
    """Get current timestamp in ISO format"""
    return datetime.now(timezone.utc).isoformat()


async def verify_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> str:
    """
    Verify JWT token (placeholder implementation)
    In production, implement proper JWT verification
    """
    # TODO: Implement actual JWT verification
    # For now, just return the token
    return credentials.credentials


async def get_client_id_from_token(token: str = Depends(verify_token)) -> str:
    """
    Extract client ID from JWT token (placeholder implementation)
    In production, decode the JWT and extract client_id
    """
    # TODO: Implement actual JWT decoding
    # For now, return a default client ID for testing
    return "ally-demo"


@router.get("/health", response_model=Dict[str, str])
async def config_health():
    """Health check endpoint for configuration service"""
    try:
        config_manager = get_config_manager()
        # Test database connectivity
        configs = config_manager.list_configurations()
        return {
            "status": "healthy",
            "message": "Configuration service is operational",
            "timestamp": get_current_timestamp(),
            "total_configs": str(len(configs)),
        }
    except Exception as e:
        logger.error(f"Configuration service health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Configuration service is unavailable",
        )


@router.get("/", response_model=ConfigResponse)
async def get_client_configuration(client_id: str = Depends(get_client_id_from_token)):
    """
    Get the complete configuration for the authenticated client
    """
    try:
        config_manager = get_config_manager()
        config = config_manager.get_configuration(client_id)

        return ConfigResponse(
            success=True,
            data=config,
            message=f"Configuration retrieved successfully for client: {client_id}",
            timestamp=get_current_timestamp(),
        )

    except ConfigurationError as e:
        logger.error(f"Configuration error for client {client_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Configuration error: {e.message}",
        )
    except Exception as e:
        logger.error(f"Unexpected error retrieving config for {client_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error retrieving configuration",
        )


@router.get("/public/{client_id}", response_model=ConfigResponse)
async def get_public_configuration(client_id: str):
    """
    Get public (non-sensitive) configuration for a client
    This endpoint doesn't require authentication and only returns safe data
    """
    try:
        config_manager = get_config_manager()
        full_config = config_manager.get_configuration(client_id)

        # Filter out sensitive information
        public_config = {
            "meta": {
                "version": full_config.get("meta", {}).get("version"),
                "clientId": full_config.get("meta", {}).get("clientId"),
                "configName": full_config.get("meta", {}).get("configName"),
            },
            "branding": full_config.get("branding", {}),
            "features": full_config.get("features", {}),
            "ui": full_config.get("ui", {}),
            "languages": full_config.get("languages", {}),
            "analytics": {
                "enabled": full_config.get("analytics", {}).get("enabled", False),
                "customEvents": full_config.get("analytics", {}).get(
                    "customEvents", False
                ),
            },
        }

        return ConfigResponse(
            success=True,
            data=public_config,
            message=f"Public configuration retrieved for client: {client_id}",
            timestamp=get_current_timestamp(),
        )

    except Exception as e:
        logger.error(f"Error retrieving public config for {client_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client configuration not found",
        )


@router.put("/", response_model=ConfigResponse)
async def update_client_configuration(
    request: ConfigUpdateRequest, client_id: str = Depends(get_client_id_from_token)
):
    """
    Update the configuration for the authenticated client
    """
    try:
        config_manager = get_config_manager()

        # Ensure client_id in config matches authenticated client
        if request.config.get("meta", {}).get("clientId") != client_id:
            request.config["meta"]["clientId"] = client_id

        if request.validate_only:
            # Only validate, don't save
            config_manager.validate_configuration(request.config)
            return ConfigResponse(
                success=True,
                data=request.config,
                message="Configuration validation successful",
                timestamp=get_current_timestamp(),
            )
        else:
            # Validate and save
            config_manager.save_configuration(client_id, request.config)

            # Retrieve the saved configuration
            saved_config = config_manager.get_configuration(client_id)

            return ConfigResponse(
                success=True,
                data=saved_config,
                message=f"Configuration updated successfully for client: {client_id}",
                timestamp=get_current_timestamp(),
            )

    except ConfigurationError as e:
        logger.error(f"Configuration error updating {client_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Configuration error: {e.message}",
        )
    except ValidationError as e:
        logger.error(f"Validation error updating {client_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Validation error: {e}",
        )
    except Exception as e:
        logger.error(f"Unexpected error updating config for {client_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error updating configuration",
        )


@router.delete("/", response_model=Dict[str, Any])
async def delete_client_configuration(
    client_id: str = Depends(get_client_id_from_token),
):
    """
    Delete the configuration for the authenticated client (soft delete)
    """
    try:
        config_manager = get_config_manager()
        success = config_manager.delete_configuration(client_id)

        if success:
            return {
                "success": True,
                "message": f"Configuration deleted successfully for client: {client_id}",
                "timestamp": get_current_timestamp(),
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Configuration not found"
            )

    except ConfigurationError as e:
        logger.error(f"Configuration error deleting {client_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Configuration error: {e.message}",
        )
    except Exception as e:
        logger.error(f"Unexpected error deleting config for {client_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error deleting configuration",
        )


@router.get("/feature/{feature_name}", response_model=FeatureFlagResponse)
async def get_feature_flag(
    feature_name: str, client_id: str = Depends(get_client_id_from_token)
):
    """
    Get a specific feature flag value for the authenticated client
    """
    try:
        config_manager = get_config_manager()
        enabled = config_manager.get_feature_flag(client_id, feature_name)

        return FeatureFlagResponse(
            success=True,
            feature_name=feature_name,
            enabled=enabled,
            client_id=client_id,
            timestamp=get_current_timestamp(),
        )

    except Exception as e:
        logger.error(f"Error getting feature flag {feature_name} for {client_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving feature flag",
        )


@router.get("/branding", response_model=BrandingResponse)
async def get_client_branding(client_id: str = Depends(get_client_id_from_token)):
    """
    Get branding configuration for the authenticated client
    """
    try:
        config_manager = get_config_manager()
        branding = config_manager.get_branding(client_id)

        return BrandingResponse(
            success=True,
            branding=branding,
            client_id=client_id,
            timestamp=get_current_timestamp(),
        )

    except Exception as e:
        logger.error(f"Error getting branding for {client_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving branding configuration",
        )


@router.get("/list", response_model=ConfigListResponse)
async def list_all_configurations():
    """
    List all client configurations (admin endpoint)
    TODO: Add admin authentication
    """
    try:
        config_manager = get_config_manager()
        configs = config_manager.list_configurations()

        return ConfigListResponse(
            success=True,
            data=configs,
            message="Configurations retrieved successfully",
            timestamp=get_current_timestamp(),
            total=len(configs),
        )

    except Exception as e:
        logger.error(f"Error listing configurations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving configuration list",
        )


@router.post("/validate", response_model=ConfigResponse)
async def validate_configuration(request: ConfigUpdateRequest):
    """
    Validate a configuration without saving it
    """
    try:
        config_manager = get_config_manager()
        config_manager.validate_configuration(request.config)

        return ConfigResponse(
            success=True,
            data=request.config,
            message="Configuration validation successful",
            timestamp=get_current_timestamp(),
        )

    except ConfigurationError as e:
        logger.error(f"Configuration validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Validation error: {e.message}",
        )
    except Exception as e:
        logger.error(f"Unexpected validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during validation",
        )


@router.get("/schema", response_model=Dict[str, Any])
async def get_configuration_schema():
    """
    Get the JSON schema for client configurations
    """
    try:
        config_manager = get_config_manager()
        return {
            "success": True,
            "schema": config_manager.schema,
            "message": "Configuration schema retrieved successfully",
            "timestamp": get_current_timestamp(),
        }

    except Exception as e:
        logger.error(f"Error retrieving configuration schema: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving configuration schema",
        )


@router.get("/default", response_model=ConfigResponse)
async def get_default_configuration():
    """
    Get the default configuration template
    """
    try:
        config_manager = get_config_manager()
        return ConfigResponse(
            success=True,
            data=config_manager.default_config,
            message="Default configuration retrieved successfully",
            timestamp=get_current_timestamp(),
        )

    except Exception as e:
        logger.error(f"Error retrieving default configuration: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving default configuration",
        )
