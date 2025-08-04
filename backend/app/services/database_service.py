"""
Database Service Layer for Ally Platform
Provides high-level database operations and business logic for all models.
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, desc, func

from ..core.database import get_database_session
from ..models import (
    Tenant,
    User,
    Configuration,
    ChatSession,
    Message,
    APIKey,
    AuditLog,
    UserRole,
    ChatStatus,
    MessageType,
    ConfigurationType,
)

logger = logging.getLogger(__name__)


class TenantService:
    """Service layer for tenant management"""

    @staticmethod
    def create_tenant(
        name: str,
        domain: str,
        subdomain: str,
        subscription_plan: str = "basic",
        db: Session = None,
    ) -> Tenant:
        """Create a new tenant"""
        if db is None:
            db = next(get_database_session())

        try:
            tenant = Tenant(
                name=name,
                domain=domain,
                subdomain=subdomain,
                subscription_plan=subscription_plan,
            )
            db.add(tenant)
            db.commit()
            db.refresh(tenant)

            logger.info(f"Created tenant: {tenant.name} ({tenant.id})")
            return tenant

        except Exception as e:
            db.rollback()
            logger.error(f"Failed to create tenant: {e}")
            raise

    @staticmethod
    def get_tenant_by_domain(domain: str, db: Session = None) -> Optional[Tenant]:
        """Get tenant by domain"""
        if db is None:
            db = next(get_database_session())

        return (
            db.query(Tenant)
            .filter(and_(Tenant.domain == domain, Tenant.is_active == True))
            .first()
        )

    @staticmethod
    def get_tenant_by_subdomain(subdomain: str, db: Session = None) -> Optional[Tenant]:
        """Get tenant by subdomain"""
        if db is None:
            db = next(get_database_session())

        return (
            db.query(Tenant)
            .filter(and_(Tenant.subdomain == subdomain, Tenant.is_active == True))
            .first()
        )

    @staticmethod
    def update_tenant_usage(
        tenant_id: str, ai_requests: int = 0, storage_mb: int = 0, db: Session = None
    ):
        """Update tenant usage statistics"""
        if db is None:
            db = next(get_database_session())

        # This would be implemented with proper usage tracking tables
        # For now, it's a placeholder for usage monitoring
        pass


class UserService:
    """Service layer for user management"""

    @staticmethod
    def create_user(
        tenant_id: str,
        email: str,
        username: str,
        password_hash: str,
        first_name: str = None,
        last_name: str = None,
        role: UserRole = UserRole.USER,
        db: Session = None,
    ) -> User:
        """Create a new user"""
        if db is None:
            db = next(get_database_session())

        try:
            user = User(
                tenant_id=tenant_id,
                email=email,
                username=username,
                password_hash=password_hash,
                first_name=first_name,
                last_name=last_name,
                role=role,
            )
            db.add(user)
            db.commit()
            db.refresh(user)

            logger.info(f"Created user: {user.email} for tenant {tenant_id}")
            return user

        except Exception as e:
            db.rollback()
            logger.error(f"Failed to create user: {e}")
            raise

    @staticmethod
    def get_user_by_email(
        tenant_id: str, email: str, db: Session = None
    ) -> Optional[User]:
        """Get user by email within tenant"""
        if db is None:
            db = next(get_database_session())

        return (
            db.query(User)
            .filter(
                and_(
                    User.tenant_id == tenant_id,
                    User.email == email,
                    User.is_active == True,
                )
            )
            .first()
        )

    @staticmethod
    def update_last_login(user_id: str, db: Session = None):
        """Update user's last login timestamp"""
        if db is None:
            db = next(get_database_session())

        user = db.query(User).filter(User.id == user_id).first()
        if user:
            user.last_login_at = datetime.now(timezone.utc)
            user.last_activity_at = datetime.now(timezone.utc)
            db.commit()


class ConfigurationService:
    """Service layer for configuration management"""

    @staticmethod
    def save_configuration(
        tenant_id: str,
        config_type: ConfigurationType,
        config_key: str,
        config_value: Dict[str, Any],
        created_by: str = None,
        db: Session = None,
    ) -> Configuration:
        """Save or update configuration"""
        if db is None:
            db = next(get_database_session())

        try:
            # Check if configuration exists
            existing = (
                db.query(Configuration)
                .filter(
                    and_(
                        Configuration.tenant_id == tenant_id,
                        Configuration.config_type == config_type,
                        Configuration.config_key == config_key,
                    )
                )
                .first()
            )

            if existing:
                # Update existing
                existing.config_value = config_value
                existing.updated_at = datetime.now(timezone.utc)
                configuration = existing
            else:
                # Create new
                configuration = Configuration(
                    tenant_id=tenant_id,
                    config_type=config_type,
                    config_key=config_key,
                    config_value=config_value,
                    created_by=created_by,
                )
                db.add(configuration)

            db.commit()
            db.refresh(configuration)

            logger.info(
                f"Saved configuration: {config_type.value}/{config_key} for tenant {tenant_id}"
            )
            return configuration

        except Exception as e:
            db.rollback()
            logger.error(f"Failed to save configuration: {e}")
            raise

    @staticmethod
    def get_configuration(
        tenant_id: str,
        config_type: ConfigurationType,
        config_key: str,
        db: Session = None,
    ) -> Optional[Configuration]:
        """Get configuration by type and key"""
        if db is None:
            db = next(get_database_session())

        return (
            db.query(Configuration)
            .filter(
                and_(
                    Configuration.tenant_id == tenant_id,
                    Configuration.config_type == config_type,
                    Configuration.config_key == config_key,
                    Configuration.is_active == True,
                )
            )
            .first()
        )

    @staticmethod
    def get_all_configurations(
        tenant_id: str, db: Session = None
    ) -> List[Configuration]:
        """Get all configurations for a tenant"""
        if db is None:
            db = next(get_database_session())

        return (
            db.query(Configuration)
            .filter(
                and_(
                    Configuration.tenant_id == tenant_id,
                    Configuration.is_active == True,
                )
            )
            .all()
        )


class ChatService:
    """Service layer for chat management"""

    @staticmethod
    def create_chat_session(
        tenant_id: str,
        user_id: str,
        title: str = "New Chat",
        ai_model: str = "gemini-2.5-flash-lite",
        db: Session = None,
    ) -> ChatSession:
        """Create a new chat session"""
        if db is None:
            db = next(get_database_session())

        try:
            chat_session = ChatSession(
                tenant_id=tenant_id, user_id=user_id, title=title, ai_model=ai_model
            )
            db.add(chat_session)
            db.commit()
            db.refresh(chat_session)

            logger.info(f"Created chat session: {chat_session.id} for user {user_id}")
            return chat_session

        except Exception as e:
            db.rollback()
            logger.error(f"Failed to create chat session: {e}")
            raise

    @staticmethod
    def add_message(
        chat_session_id: str,
        content: str,
        user_id: str = None,
        is_ai_response: bool = False,
        message_type: MessageType = MessageType.TEXT,
        ai_model_used: str = None,
        ai_tokens_used: int = 0,
        db: Session = None,
    ) -> Message:
        """Add a message to a chat session"""
        if db is None:
            db = next(get_database_session())

        try:
            message = Message(
                chat_session_id=chat_session_id,
                user_id=user_id,
                content=content,
                message_type=message_type,
                is_ai_response=is_ai_response,
                ai_model_used=ai_model_used,
                ai_tokens_used=ai_tokens_used,
            )
            db.add(message)

            # Update chat session statistics
            chat_session = (
                db.query(ChatSession).filter(ChatSession.id == chat_session_id).first()
            )
            if chat_session:
                chat_session.message_count += 1
                chat_session.total_tokens_used += ai_tokens_used
                chat_session.last_message_at = datetime.now(timezone.utc)

            db.commit()
            db.refresh(message)

            logger.info(f"Added message to chat session: {chat_session_id}")
            return message

        except Exception as e:
            db.rollback()
            logger.error(f"Failed to add message: {e}")
            raise

    @staticmethod
    def get_chat_sessions(
        tenant_id: str,
        user_id: str,
        status: ChatStatus = ChatStatus.ACTIVE,
        limit: int = 50,
        offset: int = 0,
        db: Session = None,
    ) -> List[ChatSession]:
        """Get chat sessions for a user"""
        if db is None:
            db = next(get_database_session())

        return (
            db.query(ChatSession)
            .filter(
                and_(
                    ChatSession.tenant_id == tenant_id,
                    ChatSession.user_id == user_id,
                    ChatSession.status == status,
                )
            )
            .order_by(desc(ChatSession.last_message_at))
            .offset(offset)
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_chat_messages(
        chat_session_id: str, limit: int = 100, offset: int = 0, db: Session = None
    ) -> List[Message]:
        """Get messages for a chat session"""
        if db is None:
            db = next(get_database_session())

        return (
            db.query(Message)
            .filter(Message.chat_session_id == chat_session_id)
            .order_by(Message.created_at)
            .offset(offset)
            .limit(limit)
            .all()
        )


class AuditService:
    """Service layer for audit logging"""

    @staticmethod
    def log_event(
        event_type: str,
        event_category: str,
        description: str,
        tenant_id: str = None,
        user_id: str = None,
        ip_address: str = None,
        user_agent: str = None,
        metadata: Dict[str, Any] = None,
        severity: str = "info",
        db: Session = None,
    ) -> AuditLog:
        """Log an audit event"""
        if db is None:
            db = next(get_database_session())

        try:
            audit_log = AuditLog(
                tenant_id=tenant_id,
                user_id=user_id,
                event_type=event_type,
                event_category=event_category,
                description=description,
                ip_address=ip_address,
                user_agent=user_agent,
                metadata=metadata or {},
                severity=severity,
            )
            db.add(audit_log)
            db.commit()

            return audit_log

        except Exception as e:
            db.rollback()
            logger.error(f"Failed to log audit event: {e}")
            raise

    @staticmethod
    def get_audit_logs(
        tenant_id: str = None,
        user_id: str = None,
        event_type: str = None,
        limit: int = 100,
        offset: int = 0,
        db: Session = None,
    ) -> List[AuditLog]:
        """Get audit logs with filters"""
        if db is None:
            db = next(get_database_session())

        query = db.query(AuditLog)

        if tenant_id:
            query = query.filter(AuditLog.tenant_id == tenant_id)
        if user_id:
            query = query.filter(AuditLog.user_id == user_id)
        if event_type:
            query = query.filter(AuditLog.event_type == event_type)

        return (
            query.order_by(desc(AuditLog.created_at)).offset(offset).limit(limit).all()
        )


# Convenience functions for common operations
def get_or_create_tenant(domain: str, name: str = None, db: Session = None) -> Tenant:
    """Get existing tenant or create new one"""
    tenant = TenantService.get_tenant_by_domain(domain, db)
    if not tenant:
        subdomain = domain.split(".")[0] if "." in domain else domain
        tenant = TenantService.create_tenant(
            name=name or domain, domain=domain, subdomain=subdomain, db=db
        )
    return tenant


def migrate_legacy_config(client_id: str, db: Session = None) -> Optional[str]:
    """Migrate legacy client configuration to new tenant system"""
    if db is None:
        db = next(get_database_session())

    from ..config_manager import ClientConfiguration

    # Find legacy configuration
    legacy_config = (
        db.query(ClientConfiguration)
        .filter(ClientConfiguration.client_id == client_id)
        .first()
    )

    if not legacy_config or legacy_config.migrated_to_tenant_id:
        return legacy_config.migrated_to_tenant_id if legacy_config else None

    try:
        # Create tenant for legacy client
        tenant = TenantService.create_tenant(
            name=f"Migrated Client: {client_id}",
            domain=f"{client_id}.ally-platform.com",
            subdomain=client_id,
            db=db,
        )

        # Mark as migrated
        legacy_config.migrated_to_tenant_id = tenant.id
        db.commit()

        logger.info(f"Migrated legacy client {client_id} to tenant {tenant.id}")
        return tenant.id

    except Exception as e:
        db.rollback()
        logger.error(f"Failed to migrate legacy client {client_id}: {e}")
        raise
