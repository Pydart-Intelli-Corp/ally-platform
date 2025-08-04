#!/usr/bin/env python3
"""
Check what databases exist and stamp the alembic version
"""
import pymysql
import ssl
import os

def check_databases_and_stamp():
    """Check available databases and stamp the correct one"""
    try:
        # SSL context for Azure MySQL
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_REQUIRED
        ssl_context.load_verify_locations('/scripts/DigiCertGlobalRootCA.crt.pem')
        
        # Connect to Azure MySQL without specifying database
        connection = pymysql.connect(
            host='psrazuredb.mysql.database.azure.com',
            port=3306,
            user='psrcloud',
            password='Access@LRC2404',
            ssl=ssl_context,
            ssl_disabled=False
        )
        
        print("Connected to Azure MySQL successfully!")
        
        with connection.cursor() as cursor:
            # Show all databases
            cursor.execute("SHOW DATABASES")
            databases = cursor.fetchall()
            print(f"Available databases: {databases}")
            
            # Create ally-db database if it doesn't exist
            cursor.execute("CREATE DATABASE IF NOT EXISTS `ally-db`")
            connection.commit()
            print("Created/verified ally-db database exists")
            
            # Try to use ally-db
            try:
                cursor.execute("USE `ally-db`")
                print("Successfully selected ally-db database")
                
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
                
            except Exception as db_error:
                print(f"Error with ally-db database: {db_error}")
                return False
                
        connection.close()
        print("Database stamp completed successfully!")
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    success = check_databases_and_stamp()
    exit(0 if success else 1)
