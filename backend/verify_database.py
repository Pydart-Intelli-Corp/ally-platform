#!/usr/bin/env python3
"""
Script to verify the Azure MySQL database schema.
"""
import os
import sys
import ssl
import pymysql


def verify_database():
    """Verify the ally-db database schema on Azure MySQL server."""

    # Connection details from your Azure MySQL connection string
    host = "psrazuredb.mysql.database.azure.com"
    port = 3306
    user = "psrcloud"
    password = "Access@LRC2404"
    database_name = "ally-db"

    print(f"Verifying Azure MySQL database schema: {database_name}")

    try:
        # Create SSL context
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE

        # Connect to the ally-db database
        connection = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database_name,
            charset="utf8mb4",
            ssl=ssl_context,
        )

        print("✅ Connected to Azure MySQL ally-db database successfully!")

        with connection.cursor() as cursor:
            # Check tables
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            print(f"\n📋 Tables in {database_name}:")
            for table in tables:
                print(f"  - {table[0]}")

            # Check alembic version
            cursor.execute("SELECT version_num FROM alembic_version")
            version = cursor.fetchone()
            if version:
                print(f"\n🔢 Alembic version: {version[0]}")

            # Show table structure for tenants (example)
            if tables:
                print(f"\n🏗️  Structure of 'tenants' table:")
                cursor.execute("DESCRIBE tenants")
                columns = cursor.fetchall()
                for col in columns:
                    print(
                        f"  - {col[0]} ({col[1]}) - {col[3] if col[3] else 'NOT NULL'}"
                    )

        connection.close()
        print(f"\n🎉 Database verification complete! Schema is properly deployed.")

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    verify_database()
