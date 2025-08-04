#!/usr/bin/env python3
"""
Reset Alembic migration state for Azure MySQL database
"""
import os
import sys
from sqlalchemy import create_engine, text
from urllib.parse import quote_plus

def reset_alembic_version():
    """Reset the alembic_version table to clean state"""
    try:
        # Use the same SSL configuration as in the application
        DATABASE_URL = os.getenv('DATABASE_URL')
        if not DATABASE_URL:
            print("ERROR: DATABASE_URL environment variable not set")
            return False
            
        # Fix SSL certificate path for this context
        if '/app/DigiCertGlobalRootCA.crt.pem' in DATABASE_URL:
            DATABASE_URL = DATABASE_URL.replace('/app/DigiCertGlobalRootCA.crt.pem', '/scripts/DigiCertGlobalRootCA.crt.pem')
            
        print(f"Connecting to database...")
        print(f"URL: {DATABASE_URL.replace('Access%40LRC2404', '****')}")
        
        engine = create_engine(DATABASE_URL)
        
        with engine.connect() as conn:
            # Check if alembic_version table exists
            result = conn.execute(text("SHOW TABLES LIKE 'alembic_version'"))
            tables = result.fetchall()
            
            if len(tables) > 0:
                print("Found alembic_version table")
                
                # Get current versions
                result = conn.execute(text("SELECT * FROM alembic_version"))
                versions = result.fetchall()
                print(f"Current versions in database: {versions}")
                
                # Clear the table
                conn.execute(text("DELETE FROM alembic_version"))
                conn.commit()
                print("Cleared alembic_version table")
                
                # Insert the current migration head
                conn.execute(text("INSERT INTO alembic_version (version_num) VALUES ('4afe63dc1d41')"))
                conn.commit()
                print("Set alembic version to: 4afe63dc1d41")
                
            else:
                print("No alembic_version table found - will be created by migration")
                
            # Verify final state
            result = conn.execute(text("SELECT * FROM alembic_version"))
            versions = result.fetchall()
            print(f"Final versions in database: {versions}")
            
        print("Migration reset completed successfully!")
        return True
        
    except Exception as e:
        print(f"Error resetting migrations: {e}")
        return False

if __name__ == "__main__":
    success = reset_alembic_version()
    sys.exit(0 if success else 1)
