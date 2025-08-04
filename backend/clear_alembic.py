#!/usr/bin/env python3
"""
Direct Azure MySQL connection to clear alembic version
"""
import pymysql
import ssl
import os

def clear_alembic_version():
    """Clear the alembic_version table directly"""
    try:
        # SSL context for Azure MySQL
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_REQUIRED
        ssl_context.load_verify_locations('/scripts/DigiCertGlobalRootCA.crt.pem')
        
        # Connect to Azure MySQL
        connection = pymysql.connect(
            host='psrazuredb.mysql.database.azure.com',
            port=3306,
            user='psrcloud',
            password='Access@LRC2404',
            database='ally-db',
            ssl=ssl_context,
            ssl_disabled=False
        )
        
        print("Connected to Azure MySQL successfully!")
        
        with connection.cursor() as cursor:
            # Check if alembic_version table exists
            cursor.execute("SHOW TABLES LIKE 'alembic_version'")
            result = cursor.fetchall()
            
            if result:
                print("Found alembic_version table")
                
                # Get current versions
                cursor.execute("SELECT * FROM alembic_version")
                versions = cursor.fetchall()
                print(f"Current versions: {versions}")
                
                # Clear the table
                cursor.execute("DELETE FROM alembic_version")
                connection.commit()
                print("Cleared alembic_version table successfully!")
                
            else:
                print("No alembic_version table found")
                
        connection.close()
        print("Database cleanup completed!")
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    success = clear_alembic_version()
    exit(0 if success else 1)
