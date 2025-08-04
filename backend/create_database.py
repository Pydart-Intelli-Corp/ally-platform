#!/usr/bin/env python3
"""
Script to create the Azure MySQL database.
"""
import os
import sys
import ssl
from urllib.parse import quote_plus
import pymysql


def create_database():
    """Create the ally-db database on Azure MySQL server."""

    # Connection details from your Azure MySQL connection string
    host = "psrazuredb.mysql.database.azure.com"
    port = 3306
    user = "psrcloud"
    password = "Access@LRC2404"
    database_name = "ally-db"

    print(f"Connecting to Azure MySQL server: {host}")

    try:
        # Create SSL context
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE

        # Connect to MySQL server without specifying database
        connection = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            charset="utf8mb4",
            ssl=ssl_context,
        )

        print("✅ Connected to Azure MySQL server successfully!")

        with connection.cursor() as cursor:
            # Check if database exists
            cursor.execute("SHOW DATABASES LIKE %s", (database_name,))
            if cursor.fetchone():
                print(f"✅ Database '{database_name}' already exists!")
            else:
                # Create database
                cursor.execute(
                    f"CREATE DATABASE `{database_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
                )
                print(f"✅ Database '{database_name}' created successfully!")

            # Show all databases to confirm
            cursor.execute("SHOW DATABASES")
            databases = cursor.fetchall()
            print("\n📋 Available databases:")
            for db in databases:
                print(f"  - {db[0]}")

        connection.close()
        print(f"\n🎉 Database setup complete! You can now run migrations.")

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    create_database()

if __name__ == "__main__":
    create_database()
