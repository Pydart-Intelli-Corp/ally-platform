#!/usr/bin/env python3
"""
Stamp the alembic version for Azure MySQL database
"""
import pymysql
import ssl
import os

def stamp_alembic_version():
    """Stamp the alembic_version table with the fresh_001 migration"""
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
                
                # Clear and set the fresh_001 version
                cursor.execute("DELETE FROM alembic_version")
                cursor.execute("INSERT INTO alembic_version (version_num) VALUES ('fresh_001')")
                connection.commit()
                print("Stamped alembic version with: fresh_001")
                
            else:
                print("Creating alembic_version table and stamping")
                cursor.execute("CREATE TABLE alembic_version (version_num VARCHAR(32) NOT NULL)")
                cursor.execute("INSERT INTO alembic_version (version_num) VALUES ('fresh_001')")
                connection.commit()
                print("Created alembic_version table and stamped with: fresh_001")
                
            # Verify final state
            cursor.execute("SELECT * FROM alembic_version")
            versions = cursor.fetchall()
            print(f"Final versions in database: {versions}")
                
        connection.close()
        print("Database stamp completed successfully!")
        return True
        
    except Exception as e:
        print(f"Error stamping migration: {e}")
        return False

if __name__ == "__main__":
    success = stamp_alembic_version()
    exit(0 if success else 1)
