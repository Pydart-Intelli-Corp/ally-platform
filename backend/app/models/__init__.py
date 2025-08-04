"""
Database Models for Ally Platform
Comprehensive models for multi-tenancy, chat management, and configuration storage.
"""

import uuid
from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Boolean,
    DateTime,
    ForeignKey,
    JSON,
    Enum,
    Index,
    UniqueConstraint,
    CheckConstraint,
    DECIMAL,
)
from sqlalchemy.orm import relationship, validates
from sqlalchemy.dialects.mysql import CHAR
import enum

from ..core.database import Base


# Enums for type safety
class UserRole(enum.Enum):
    SUPER_ADMIN = "super_admin"
    TENANT_ADMIN = "tenant_admin"
    USER = "user"
    VIEWER = "viewer"


class ChatStatus(enum.Enum):
    ACTIVE = "active"
    ARCHIVED = "archived"
    DELETED = "deleted"


class MessageType(enum.Enum):
    TEXT = "text"
    IMAGE = "image"
    FILE = "file"
    SYSTEM = "system"


class ConfigurationType(enum.Enum):
    BRANDING = "branding"
    FEATURES = "features"
    AI_SETTINGS = "ai_settings"
    UI_PREFERENCES = "ui_preferences"
    SECURITY = "security"


# Core Models


class Tenant(Base):
    """Multi-tenant organization model"""

    __tablename__ = "tenants"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    domain = Column(String(255), unique=True, nullable=False)
    subdomain = Column(String(100), unique=True, nullable=False)

    # Subscription and billing
    subscription_plan = Column(String(50), default="basic")
    subscription_status = Column(String(50), default="active")
    billing_email = Column(String(255))

    # Limits and quotas
    max_users = Column(Integer, default=10)
    max_storage_gb = Column(Integer, default=5)
    max_ai_requests_per_month = Column(Integer, default=1000)

    # Status and metadata
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    users = relationship("User", back_populates="tenant", cascade="all, delete-orphan")
    configurations = relationship(
        "Configuration", back_populates="tenant", cascade="all, delete-orphan"
    )
    chat_sessions = relationship(
        "ChatSession", back_populates="tenant", cascade="all, delete-orphan"
    )

    # Indexes
    __table_args__ = (
        Index("idx_tenant_domain", "domain"),
        Index("idx_tenant_subdomain", "subdomain"),
        Index("idx_tenant_status", "is_active", "subscription_status"),
    )

    @validates("domain")
    def validate_domain(self, key, domain):
        if not domain or len(domain) < 3:
            raise ValueError("Domain must be at least 3 characters long")
        return domain.lower()

    @validates("subdomain")
    def validate_subdomain(self, key, subdomain):
        if not subdomain or len(subdomain) < 2:
            raise ValueError("Subdomain must be at least 2 characters long")
        return subdomain.lower()


class User(Base):
    """User model with role-based access control"""

    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), ForeignKey("tenants.id"), nullable=False)

    # Authentication
    email = Column(String(255), nullable=False)
    username = Column(String(100), nullable=False)
    password_hash = Column(String(255), nullable=False)

    # Profile information
    first_name = Column(String(100))
    last_name = Column(String(100))
    avatar_url = Column(String(500))
    bio = Column(Text)

    # Role and permissions
    role = Column(Enum(UserRole), default=UserRole.USER)
    permissions = Column(JSON, default=dict)

    # Status and verification
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    email_verified_at = Column(DateTime)
    last_login_at = Column(DateTime)
    last_activity_at = Column(DateTime)

    # Security
    failed_login_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime)
    password_changed_at = Column(DateTime)

    # Metadata
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    tenant = relationship("Tenant", back_populates="users")
    chat_sessions = relationship(
        "ChatSession", back_populates="user", cascade="all, delete-orphan"
    )
    messages = relationship(
        "Message", back_populates="user", cascade="all, delete-orphan"
    )

    # Indexes and constraints
    __table_args__ = (
        UniqueConstraint("tenant_id", "email", name="uq_tenant_email"),
        UniqueConstraint("tenant_id", "username", name="uq_tenant_username"),
        Index("idx_user_email", "email"),
        Index("idx_user_tenant", "tenant_id"),
        Index("idx_user_role", "tenant_id", "role"),
        Index("idx_user_status", "is_active", "is_verified"),
    )

    @property
    def full_name(self) -> str:
        """Get user's full name"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username

    @validates("email")
    def validate_email(self, key, email):
        if not email or "@" not in email:
            raise ValueError("Invalid email address")
        return email.lower()


class Configuration(Base):
    """Multi-tenant configuration storage"""

    __tablename__ = "configurations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), ForeignKey("tenants.id"), nullable=False)

    # Configuration details
    config_type = Column(Enum(ConfigurationType), nullable=False)
    config_key = Column(String(100), nullable=False)
    config_value = Column(JSON, nullable=False)

    # Version control
    version = Column(String(20), default="1.0.0")
    schema_version = Column(String(20), default="1.0.0")

    # Metadata
    is_active = Column(Boolean, default=True)
    created_by = Column(String(36), ForeignKey("users.id"))
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    tenant = relationship("Tenant", back_populates="configurations")
    creator = relationship("User", foreign_keys=[created_by])

    # Indexes and constraints
    __table_args__ = (
        UniqueConstraint(
            "tenant_id", "config_type", "config_key", name="uq_tenant_config"
        ),
        Index("idx_config_tenant", "tenant_id"),
        Index("idx_config_type", "config_type"),
        Index("idx_config_active", "is_active"),
    )


class ChatSession(Base):
    """Chat session management for multi-tenant AI conversations"""

    __tablename__ = "chat_sessions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), ForeignKey("tenants.id"), nullable=False)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)

    # Session details
    title = Column(String(255), default="New Chat")
    description = Column(Text)

    # AI Configuration
    ai_model = Column(String(100), default="gemini-2.5-flash-lite")
    ai_temperature = Column(DECIMAL(3, 2), default=0.7)
    ai_max_tokens = Column(Integer, default=2000)
    system_prompt = Column(Text)

    # Session metadata
    status = Column(Enum(ChatStatus), default=ChatStatus.ACTIVE)
    message_count = Column(Integer, default=0)
    total_tokens_used = Column(Integer, default=0)

    # Sharing and collaboration
    is_shared = Column(Boolean, default=False)
    shared_with = Column(JSON, default=list)  # List of user IDs

    # Timestamps
    started_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    last_message_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    archived_at = Column(DateTime)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    tenant = relationship("Tenant", back_populates="chat_sessions")
    user = relationship("User", back_populates="chat_sessions")
    messages = relationship(
        "Message",
        back_populates="chat_session",
        cascade="all, delete-orphan",
        order_by="Message.created_at",
    )

    # Indexes
    __table_args__ = (
        Index("idx_chat_tenant", "tenant_id"),
        Index("idx_chat_user", "user_id"),
        Index("idx_chat_status", "status"),
        Index("idx_chat_active", "tenant_id", "user_id", "status"),
        Index("idx_chat_shared", "is_shared"),
        Index("idx_chat_recent", "last_message_at"),
    )


class Message(Base):
    """Individual messages within chat sessions"""

    __tablename__ = "messages"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    chat_session_id = Column(String(36), ForeignKey("chat_sessions.id"), nullable=False)
    user_id = Column(String(36), ForeignKey("users.id"))  # Nullable for AI messages

    # Message content
    content = Column(Text, nullable=False)
    message_type = Column(Enum(MessageType), default=MessageType.TEXT)

    # AI-specific fields
    is_ai_response = Column(Boolean, default=False)
    ai_model_used = Column(String(100))
    ai_tokens_used = Column(Integer, default=0)
    ai_processing_time = Column(DECIMAL(5, 3))  # In seconds

    # File attachments
    attachments = Column(JSON, default=list)  # List of file metadata

    # Message metadata
    parent_message_id = Column(String(36), ForeignKey("messages.id"))  # For threading
    edit_count = Column(Integer, default=0)
    edited_at = Column(DateTime)

    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    chat_session = relationship("ChatSession", back_populates="messages")
    user = relationship("User", back_populates="messages")
    parent_message = relationship("Message", remote_side=[id])
    replies = relationship("Message", cascade="all, delete-orphan")

    # Indexes
    __table_args__ = (
        Index("idx_message_session", "chat_session_id"),
        Index("idx_message_user", "user_id"),
        Index("idx_message_type", "message_type"),
        Index("idx_message_ai", "is_ai_response"),
        Index("idx_message_created", "created_at"),
        Index("idx_message_thread", "parent_message_id"),
    )


class APIKey(Base):
    """API key management for external access"""

    __tablename__ = "api_keys"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), ForeignKey("tenants.id"), nullable=False)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)

    # Key details
    key_name = Column(String(100), nullable=False)
    key_hash = Column(String(255), nullable=False)  # Hashed API key
    key_prefix = Column(String(10), nullable=False)  # For identification

    # Permissions and limits
    permissions = Column(JSON, default=list)  # List of allowed endpoints
    rate_limit_per_hour = Column(Integer, default=1000)
    monthly_quota = Column(Integer, default=10000)
    current_month_usage = Column(Integer, default=0)

    # Status
    is_active = Column(Boolean, default=True)
    last_used_at = Column(DateTime)
    expires_at = Column(DateTime)

    # Metadata
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    tenant = relationship("Tenant")
    user = relationship("User")

    # Indexes and constraints
    __table_args__ = (
        UniqueConstraint("tenant_id", "key_name", name="uq_tenant_key_name"),
        Index("idx_api_key_tenant", "tenant_id"),
        Index("idx_api_key_user", "user_id"),
        Index("idx_api_key_hash", "key_hash"),
        Index("idx_api_key_active", "is_active"),
    )


class AuditLog(Base):
    """Audit logging for security and compliance"""

    __tablename__ = "audit_logs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), ForeignKey("tenants.id"))
    user_id = Column(String(36), ForeignKey("users.id"))

    # Event details
    event_type = Column(
        String(100), nullable=False
    )  # login, logout, config_change, etc.
    event_category = Column(
        String(50), nullable=False
    )  # security, configuration, chat, etc.
    description = Column(Text, nullable=False)

    # Request details
    ip_address = Column(String(45))  # IPv6 compatible
    user_agent = Column(Text)
    request_id = Column(String(36))

    # Additional metadata
    event_metadata = Column(JSON, default=dict)
    severity = Column(String(20), default="info")  # info, warning, error, critical

    # Timestamp
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    tenant = relationship("Tenant")
    user = relationship("User")

    # Indexes
    __table_args__ = (
        Index("idx_audit_tenant", "tenant_id"),
        Index("idx_audit_user", "user_id"),
        Index("idx_audit_event", "event_type"),
        Index("idx_audit_category", "event_category"),
        Index("idx_audit_created", "created_at"),
        Index("idx_audit_severity", "severity"),
    )


# Legacy compatibility - maintain existing ClientConfiguration for backward compatibility
class ClientConfiguration(Base):
    """Legacy client configuration model - maintained for backward compatibility"""

    __tablename__ = "client_configurations"

    client_id = Column(String(50), primary_key=True)
    config_data = Column(Text, nullable=False)
    version = Column(String(20), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    is_active = Column(Boolean, default=True)

    # Migration helper - will be removed in future versions
    migrated_to_tenant_id = Column(String(36), ForeignKey("tenants.id"))

    __table_args__ = (
        Index("idx_client_config_active", "is_active"),
        Index("idx_client_config_migrated", "migrated_to_tenant_id"),
    )
