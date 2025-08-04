#!/usr/bin/env python3
"""
Comprehensive codebase verification script for Ally Platform Phase 3
"""
import os
import sys
import traceback

# Set up environment
os.environ["ENVIRONMENT"] = "production"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_environment():
    """Test environment configuration"""
    print("🔍 Testing Environment Configuration...")
    try:
        from app.core.environment import env_config

        env = env_config.detect_environment()
        db_url = env_config.get_database_url()
        print(f"   ✅ Environment: {env}")
        print(f"   ✅ Database URL configured: {bool(db_url)}")
        return True
    except Exception as e:
        print(f"   ❌ Environment config failed: {e}")
        traceback.print_exc()
        return False


def test_models():
    """Test database models"""
    print("🔍 Testing Database Models...")
    try:
        from app.models import (
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

        models = [Tenant, User, Configuration, ChatSession, Message, APIKey, AuditLog]
        enums = [UserRole, ChatStatus, MessageType, ConfigurationType]
        print(f"   ✅ All {len(models)} models imported successfully")
        print(f"   ✅ All {len(enums)} enums imported successfully")
        return True
    except Exception as e:
        print(f"   ❌ Model import failed: {e}")
        traceback.print_exc()
        return False


def test_database_connection():
    """Test database connection"""
    print("🔍 Testing Database Connection...")
    try:
        import ssl
        import pymysql

        host = "psrazuredb.mysql.database.azure.com"
        port = 3306
        user = "psrcloud"
        password = "Access@LRC2404"
        database = "ally-db"

        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE

        connection = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database,
            charset="utf8mb4",
            ssl=ssl_context,
        )

        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = %s",
                (database,),
            )
            table_count = cursor.fetchone()[0]

            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()

            cursor.execute("SELECT version_num FROM alembic_version")
            version = cursor.fetchone()

        connection.close()

        print(f"   ✅ Connected to Azure MySQL successfully")
        print(f"   ✅ Database: {database}")
        print(f"   ✅ Tables found: {table_count}")
        print(f"   ✅ Alembic version: {version[0] if version else 'None'}")

        print("   📋 Tables:")
        for table in tables:
            print(f"      - {table[0]}")

        return True
    except Exception as e:
        print(f"   ❌ Database connection failed: {e}")
        traceback.print_exc()
        return False


def test_service_layer():
    """Test service layer"""
    print("🔍 Testing Service Layer...")
    try:
        from app.services.database_service import (
            TenantService,
            UserService,
            ConfigurationService,
            ChatService,
            AuditService,
        )

        services = [
            TenantService,
            UserService,
            ConfigurationService,
            ChatService,
            AuditService,
        ]
        print(f"   ✅ All {len(services)} service classes imported successfully")
        return True
    except Exception as e:
        print(f"   ❌ Service layer failed: {e}")
        traceback.print_exc()
        return False


def test_alembic_migrations():
    """Test Alembic migrations"""
    print("🔍 Testing Alembic Migrations...")
    try:
        versions_dir = "alembic/versions"
        migrations = [
            f
            for f in os.listdir(versions_dir)
            if f.endswith(".py") and not f.startswith("__")
        ]
        print(f"   ✅ Found {len(migrations)} migration files")
        for m in migrations:
            print(f"      - {m}")
        return True
    except Exception as e:
        print(f"   ❌ Migration check failed: {e}")
        traceback.print_exc()
        return False


def main():
    """Run all verification tests"""
    print("🎯 ALLY PLATFORM PHASE 3 - COMPREHENSIVE VERIFICATION")
    print("=" * 60)

    tests = [
        test_environment,
        test_models,
        test_database_connection,
        test_service_layer,
        test_alembic_migrations,
    ]

    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
            print()
        except Exception as e:
            print(f"   ❌ Test crashed: {e}")
            results.append(False)
            print()

    # Summary
    passed = sum(results)
    total = len(results)

    print("📊 VERIFICATION SUMMARY")
    print("=" * 60)
    print(f"✅ Tests passed: {passed}/{total}")
    print(f"❌ Tests failed: {total - passed}/{total}")

    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Phase 3 is fully operational.")
    else:
        print(f"\n⚠️  {total - passed} tests failed. See details above.")

    return passed == total


if __name__ == "__main__":
    main()
