"""
Configuration Manager for Ally Platform
Handles client-specific configurations with validation and caching.
"""

import json
import os
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
from pathlib import Path
import logging
from dataclasses import dataclass
from pydantic import BaseModel, ValidationError, Field
import redis
from sqlalchemy import create_engine, Column, String, Text, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

Base = declarative_base()


class ClientConfiguration(Base):
    """Database model for client configurations"""

    __tablename__ = "client_configurations"

    client_id = Column(String(50), primary_key=True)
    config_data = Column(Text, nullable=False)
    version = Column(String(20), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)


class ConfigMeta(BaseModel):
    """Pydantic model for configuration metadata"""

    version: str = Field(..., pattern=r"^\d+\.\d+\.\d+$")
    clientId: str = Field(..., pattern=r"^[a-zA-Z0-9_-]{3,50}$")
    lastUpdated: str
    configName: Optional[str] = None
    description: Optional[str] = None


class BrandingConfig(BaseModel):
    """Pydantic model for branding configuration"""

    companyName: str = Field(..., min_length=1, max_length=100)
    logoUrl: Optional[str] = None
    faviconUrl: Optional[str] = None
    primaryColor: str = Field(..., pattern=r"^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$")
    secondaryColor: Optional[str] = Field(
        None, pattern=r"^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$"
    )
    accentColor: Optional[str] = Field(
        None, pattern=r"^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$"
    )
    font: Optional[str] = "inter"
    customCss: Optional[str] = None


class FeaturesConfig(BaseModel):
    """Pydantic model for feature toggles"""

    chatEnabled: bool = True
    voiceEnabled: bool = False
    fileUploadEnabled: bool = True
    realTimeEnabled: bool = True
    analyticsEnabled: bool = True
    notificationsEnabled: bool = True
    collaborationEnabled: bool = False
    apiAccessEnabled: bool = False
    exportEnabled: bool = True


class UIConfig(BaseModel):
    """Pydantic model for UI configuration"""

    layout: str = Field("modern", pattern=r"^(modern|classic|minimal|dashboard)$")
    darkMode: bool = True
    themeToggle: bool = True
    sidebarCollapsible: bool = True
    compactMode: bool = False
    animationsEnabled: bool = True
    accessibilityMode: bool = False


class AIConfig(BaseModel):
    """Pydantic model for AI configuration"""

    model: str = Field(
        ...,
        pattern=r"^(gemini-2\.5-flash-lite|gemini-2\.5-flash|gemini-2\.0-flash-exp|gpt-4o|gpt-4o-mini|claude-3-5-sonnet|claude-3-5-haiku)$",
    )
    promptTemplate: Optional[str] = None
    temperature: float = Field(0.7, ge=0, le=2)
    maxTokens: int = Field(2000, ge=100, le=8000)
    systemMessage: Optional[str] = None
    responseFormat: str = Field("markdown", pattern=r"^(text|markdown|json)$")


class SecurityConfig(BaseModel):
    """Pydantic model for security configuration"""

    jwtExpiration: int = Field(3600, ge=300, le=86400)
    refreshTokenExpiration: int = Field(604800, ge=3600, le=2592000)
    rateLimit: int = Field(1000, ge=10, le=10000)
    sessionTimeout: int = Field(7200, ge=300, le=28800)
    mfaEnabled: bool = False


class ClientConfigModel(BaseModel):
    """Complete client configuration model"""

    meta: ConfigMeta
    branding: BrandingConfig
    features: FeaturesConfig
    ui: UIConfig
    ai: AIConfig
    security: SecurityConfig


@dataclass
class ConfigurationError(Exception):
    """Custom exception for configuration errors"""

    message: str
    code: str = "CONFIG_ERROR"


class ConfigurationManager:
    """
    Configuration Manager for handling client-specific configurations
    with database persistence, Redis caching, and JSON schema validation.
    """

    def __init__(self, database_url: str, redis_url: str = None):
        self.database_url = database_url
        self.redis_url = redis_url

        # Initialize database
        self.engine = create_engine(database_url)
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=self.engine
        )

        # Initialize Redis (optional)
        self.redis_client = None
        if redis_url:
            try:
                self.redis_client = redis.from_url(redis_url, decode_responses=True)
                self.redis_client.ping()
                logger.info("Redis connection established for configuration caching")
            except Exception as e:
                logger.warning(
                    f"Redis connection failed: {e}. Proceeding without caching."
                )

        # Load schema and default configuration
        self.schema_path = Path(__file__).parent / "client-config.schema.json"
        self.default_config_path = Path(__file__).parent / "default-config.json"

        self.schema = self._load_schema()
        self.default_config = self._load_default_config()

    def _load_schema(self) -> Dict[str, Any]:
        """Load the JSON schema for validation"""
        try:
            with open(self.schema_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"Schema file not found: {self.schema_path}")
            return {}
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in schema file: {e}")
            return {}

    def _load_default_config(self) -> Dict[str, Any]:
        """Load the default configuration"""
        try:
            with open(self.default_config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"Default config file not found: {self.default_config_path}")
            return {}
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in default config: {e}")
            return {}

    def _get_cache_key(self, client_id: str) -> str:
        """Generate Redis cache key for client configuration"""
        return f"config:client:{client_id}"

    def _get_from_cache(self, client_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve configuration from Redis cache"""
        if not self.redis_client:
            return None

        try:
            cached_data = self.redis_client.get(self._get_cache_key(client_id))
            if cached_data:
                return json.loads(cached_data)
        except Exception as e:
            logger.warning(f"Failed to retrieve from cache: {e}")

        return None

    def _set_cache(self, client_id: str, config: Dict[str, Any], ttl: int = 3600):
        """Store configuration in Redis cache"""
        if not self.redis_client:
            return

        try:
            cache_key = self._get_cache_key(client_id)
            self.redis_client.setex(cache_key, ttl, json.dumps(config, default=str))
        except Exception as e:
            logger.warning(f"Failed to set cache: {e}")

    def _invalidate_cache(self, client_id: str):
        """Remove configuration from Redis cache"""
        if not self.redis_client:
            return

        try:
            self.redis_client.delete(self._get_cache_key(client_id))
        except Exception as e:
            logger.warning(f"Failed to invalidate cache: {e}")

    def validate_configuration(self, config: Dict[str, Any]) -> bool:
        """
        Validate configuration against the schema and business rules

        Args:
            config: Configuration dictionary to validate

        Returns:
            bool: True if valid, raises ValidationError if invalid
        """
        try:
            # Validate using Pydantic model
            ClientConfigModel(**config)

            # Additional business rule validations
            self._validate_business_rules(config)

            logger.info("Configuration validation successful")
            return True

        except ValidationError as e:
            logger.error(f"Configuration validation failed: {e}")
            raise ConfigurationError(f"Validation failed: {e}", "VALIDATION_ERROR")
        except Exception as e:
            logger.error(f"Unexpected validation error: {e}")
            raise ConfigurationError(f"Validation error: {e}", "VALIDATION_ERROR")

    def _validate_business_rules(self, config: Dict[str, Any]):
        """Validate business-specific rules"""
        # Check that default language is in supported languages
        languages = config.get("languages", {})
        default_lang = languages.get("default")
        supported_langs = languages.get("supported", [])

        if default_lang and default_lang not in supported_langs:
            raise ValueError("Default language must be in supported languages list")

        # Validate AI model availability (you could extend this with actual API checks)
        ai_config = config.get("ai", {})
        model = ai_config.get("model")
        if model and not self._is_model_available(model):
            raise ValueError(f"AI model '{model}' is not available")

    def _is_model_available(self, model: str) -> bool:
        """Check if AI model is available (placeholder for actual implementation)"""
        # In a real implementation, you might check API availability
        available_models = [
            "gemini-2.5-flash-lite",
            "gemini-2.5-flash",
            "gemini-2.0-flash-exp",
            "gpt-4o",
            "gpt-4o-mini",
            "claude-3-5-sonnet",
            "claude-3-5-haiku",
        ]
        return model in available_models

    def get_configuration(self, client_id: str) -> Dict[str, Any]:
        """
        Retrieve configuration for a client

        Args:
            client_id: Unique client identifier

        Returns:
            Dict containing client configuration
        """
        # Try cache first
        config = self._get_from_cache(client_id)
        if config:
            logger.info(f"Configuration retrieved from cache for client: {client_id}")
            return config

        # Retrieve from database
        db = self.SessionLocal()
        try:
            db_config = (
                db.query(ClientConfiguration)
                .filter(
                    ClientConfiguration.client_id == client_id,
                    ClientConfiguration.is_active == True,
                )
                .first()
            )

            if db_config:
                config = json.loads(db_config.config_data)
                # Cache for future requests
                self._set_cache(client_id, config)
                logger.info(
                    f"Configuration retrieved from database for client: {client_id}"
                )
                return config
            else:
                # Return default configuration if client config doesn't exist
                logger.info(
                    f"No configuration found for client: {client_id}, returning default"
                )
                return self.default_config

        except Exception as e:
            logger.error(f"Failed to retrieve configuration for {client_id}: {e}")
            raise ConfigurationError(
                f"Failed to retrieve configuration: {e}", "RETRIEVAL_ERROR"
            )
        finally:
            db.close()

    def save_configuration(self, client_id: str, config: Dict[str, Any]) -> bool:
        """
        Save configuration for a client

        Args:
            client_id: Unique client identifier
            config: Configuration dictionary

        Returns:
            bool: True if successful
        """
        # Validate configuration first
        self.validate_configuration(config)

        # Update timestamp
        config["meta"]["lastUpdated"] = datetime.now(timezone.utc).isoformat()

        db = self.SessionLocal()
        try:
            # Check if configuration exists
            existing_config = (
                db.query(ClientConfiguration)
                .filter(ClientConfiguration.client_id == client_id)
                .first()
            )

            if existing_config:
                # Update existing configuration
                existing_config.config_data = json.dumps(config, default=str)
                existing_config.version = config["meta"]["version"]
                existing_config.updated_at = datetime.utcnow()
            else:
                # Create new configuration
                new_config = ClientConfiguration(
                    client_id=client_id,
                    config_data=json.dumps(config, default=str),
                    version=config["meta"]["version"],
                )
                db.add(new_config)

            db.commit()

            # Invalidate cache
            self._invalidate_cache(client_id)

            logger.info(f"Configuration saved successfully for client: {client_id}")
            return True

        except Exception as e:
            db.rollback()
            logger.error(f"Failed to save configuration for {client_id}: {e}")
            raise ConfigurationError(f"Failed to save configuration: {e}", "SAVE_ERROR")
        finally:
            db.close()

    def delete_configuration(self, client_id: str) -> bool:
        """
        Delete configuration for a client (soft delete)

        Args:
            client_id: Unique client identifier

        Returns:
            bool: True if successful
        """
        db = self.SessionLocal()
        try:
            config = (
                db.query(ClientConfiguration)
                .filter(ClientConfiguration.client_id == client_id)
                .first()
            )

            if config:
                config.is_active = False
                config.updated_at = datetime.utcnow()
                db.commit()

                # Invalidate cache
                self._invalidate_cache(client_id)

                logger.info(f"Configuration deleted for client: {client_id}")
                return True
            else:
                logger.warning(
                    f"No configuration found to delete for client: {client_id}"
                )
                return False

        except Exception as e:
            db.rollback()
            logger.error(f"Failed to delete configuration for {client_id}: {e}")
            raise ConfigurationError(
                f"Failed to delete configuration: {e}", "DELETE_ERROR"
            )
        finally:
            db.close()

    def list_configurations(self) -> List[Dict[str, Any]]:
        """
        List all active client configurations (metadata only)

        Returns:
            List of configuration metadata
        """
        db = self.SessionLocal()
        try:
            configs = (
                db.query(ClientConfiguration)
                .filter(ClientConfiguration.is_active == True)
                .all()
            )

            result = []
            for config in configs:
                config_data = json.loads(config.config_data)
                result.append(
                    {
                        "clientId": config.client_id,
                        "version": config.version,
                        "lastUpdated": config.updated_at.isoformat(),
                        "meta": config_data.get("meta", {}),
                    }
                )

            return result

        except Exception as e:
            logger.error(f"Failed to list configurations: {e}")
            raise ConfigurationError(
                f"Failed to list configurations: {e}", "LIST_ERROR"
            )
        finally:
            db.close()

    def get_feature_flag(self, client_id: str, feature_name: str) -> bool:
        """
        Get a specific feature flag value for a client

        Args:
            client_id: Unique client identifier
            feature_name: Name of the feature flag

        Returns:
            bool: Feature flag value
        """
        try:
            config = self.get_configuration(client_id)
            features = config.get("features", {})
            return features.get(feature_name, False)
        except Exception as e:
            logger.error(
                f"Failed to get feature flag {feature_name} for {client_id}: {e}"
            )
            return False

    def get_branding(self, client_id: str) -> Dict[str, Any]:
        """
        Get branding configuration for a client

        Args:
            client_id: Unique client identifier

        Returns:
            Dict containing branding configuration
        """
        try:
            config = self.get_configuration(client_id)
            return config.get("branding", {})
        except Exception as e:
            logger.error(f"Failed to get branding for {client_id}: {e}")
            return {}


# Global configuration manager instance
config_manager: Optional[ConfigurationManager] = None


def get_config_manager() -> ConfigurationManager:
    """Get the global configuration manager instance"""
    global config_manager
    if config_manager is None:
        database_url = os.getenv("DATABASE_URL", "sqlite:///./ally_config.db")
        redis_url = os.getenv("REDIS_URL")
        config_manager = ConfigurationManager(database_url, redis_url)
    return config_manager


def init_config_manager(database_url: str, redis_url: str = None):
    """Initialize the global configuration manager"""
    global config_manager
    config_manager = ConfigurationManager(database_url, redis_url)
    return config_manager
