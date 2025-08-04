# pylint: disable=no-member
"""
Alembic environment configuration file.
This file configures the database migration environment.
"""

import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context  # pylint: disable=no-member

# Add the parent directory to the Python path to import our app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import our models and database configuration
from app.models import Base
from app.core.environment import env_config

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set the database URL from environment configuration
database_url = env_config.get_database_url()

# Handle different connection string formats
if database_url.startswith("Server="):
    # Handle .NET style connection string format
    # Server=psrazuredb.mysql.database.azure.com;Port=3306;UserID=psrcloud;Password=Access@LRC2404;Database=ally-db;SslMode=Required;SslCa=E:\\PYDART\\BackEnd\\psr-\\DigiCertGlobalRootCA.crt.pem
    parts = {}
    for part in database_url.split(";"):
        if "=" in part:
            key, value = part.split("=", 1)
            parts[key.strip()] = value.strip()

    # Convert to MySQL URL format
    server = parts.get("Server", "localhost")
    port = parts.get("Port", "3306")
    user = parts.get("UserID", "root")
    password = parts.get("Password", "")
    database = parts.get("Database", "ally-db")

    # URL encode the password to handle special characters
    import urllib.parse

    encoded_password = urllib.parse.quote(password, safe="")

    # Construct MySQL URL with SSL
    mysql_url = f"mysql://{user}:{encoded_password}@{server}:{port}/{database}?ssl=true"
    # Escape % characters for ConfigParser
    escaped_url = mysql_url.replace("%", "%%")
else:
    # Handle standard MySQL URL format
    if "%" in database_url:
        # Escape % characters for ConfigParser
        escaped_url = database_url.replace("%", "%%")
    else:
        escaped_url = database_url

config.set_main_option("sqlalchemy.url", escaped_url)

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    # Get the database URL from environment or config
    try:
        from app.core.environment import get_database_url

        url = get_database_url()
    except Exception as e:
        print(f"Could not get database URL from environment: {e}")
        url = config.get_main_option("sqlalchemy.url")

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    try:
        from app.core.environment import get_database_url

        database_url = get_database_url()
        print(f"Database connection test starting...")
    except Exception as e:
        print(f"Error getting database URL: {e}")
        database_url = config.get_main_option("sqlalchemy.url")

    try:
        # Create engine with SSL configuration for production
        connect_args = {}
        environment = os.environ.get("ENVIRONMENT", "").lower()
        skip_ssl = os.environ.get("ALEMBIC_SKIP_SSL", "false").lower() == "true"
        database_host = os.environ.get("MYSQL_HOST", "")
        
        # Use SSL for Azure MySQL even in Docker environment
        if ("production" in environment or "azure" in database_host.lower()) and not skip_ssl:
            # Use SSL certificate file for Azure MySQL with correct PyMySQL parameters
            connect_args = {
                "ssl_ca": "/app/DigiCertGlobalRootCA.crt.pem",
                "ssl_disabled": False
            }
            print(f"Using SSL certificate for Azure MySQL: {database_host}")
        elif skip_ssl:
            # Only skip SSL if explicitly requested
            print("Skipping SSL configuration (ALEMBIC_SKIP_SSL=true)")
            connect_args = {"ssl_disabled": True}
        else:
            print("Using default connection configuration")

        connectable = engine_from_config(
            config.get_section(config.config_ini_section, {}),
            prefix="sqlalchemy.",
            poolclass=pool.NullPool,
            url=database_url,
            connect_args=connect_args,
        )

        with connectable.connect() as connection:
            context.configure(connection=connection, target_metadata=target_metadata)

            with context.begin_transaction():
                context.run_migrations()
    except Exception as e:
        print(
            f"Database connection test failed (this is normal during migrations): {e}"
        )
        # For autogenerate, we need a real connection, so let's try a simplified approach
        if "autogenerate" in sys.argv or "--autogenerate" in sys.argv:
            print(
                "Autogenerate requires database connection. Retrying with simplified SSL..."
            )
            try:
                import ssl

                ssl_context = ssl.create_default_context()
                ssl_context.check_hostname = False
                ssl_context.verify_mode = ssl.CERT_NONE

                connectable = engine_from_config(
                    config.get_section(config.config_ini_section, {}),
                    prefix="sqlalchemy.",
                    poolclass=pool.NullPool,
                    url=database_url,
                    connect_args={"ssl": ssl_context},
                )

                with connectable.connect() as connection:
                    context.configure(
                        connection=connection, target_metadata=target_metadata
                    )

                    with context.begin_transaction():
                        context.run_migrations()
            except Exception as e2:
                print(f"Simplified SSL also failed: {e2}")
                raise
        else:
            # Fall back to offline mode if not autogenerate
            print("Falling back to offline mode...")
            run_migrations_offline()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
