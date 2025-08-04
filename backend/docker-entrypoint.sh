#!/bin/bash

# Docker entrypoint script for backend
# This script runs database migrations before starting the application

set -e

echo "🚀 Starting Ally Platform Backend..."

# Wait for database to be ready
echo "⏳ Waiting for Azure MySQL database to be ready..."
while ! python -c "
import pymysql
import ssl
import os
import time
try:
    # Create SSL context for Azure MySQL
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    connection = pymysql.connect(
        host=os.environ.get('MYSQL_HOST', 'psrazuredb.mysql.database.azure.com'),
        port=int(os.environ.get('MYSQL_PORT', 3306)),
        user=os.environ.get('MYSQL_USER', 'psrcloud'),
        password=os.environ.get('MYSQL_PASSWORD', 'Access@LRC2404'),
        database=os.environ.get('MYSQL_DATABASE', 'ally-db'),
        ssl=ssl_context,
        connect_timeout=10
    )
    connection.close()
    print('Azure MySQL database is ready!')
except Exception as e:
    print(f'Database not ready: {e}')
    exit(1)
"; do
  echo "Azure MySQL database is not ready yet, waiting..."
  sleep 5
done

echo "✅ Azure MySQL database is ready!"

# Run database migrations
echo "📋 Running database migrations on Azure MySQL..."
cd /app
export PYTHONPATH=/app

# Check if there are multiple heads and create a merge if needed
echo "Checking for multiple migration heads..."
HEADS_OUTPUT=$(alembic heads 2>&1 || echo "")
if echo "$HEADS_OUTPUT" | grep -q "Multiple head revisions"; then
    echo "Multiple heads detected, creating merge migration..."
    alembic merge heads -m "merge_heads"
    echo "Merge migration created, upgrading..."
fi

# Try to upgrade, handling both single and multiple head scenarios
echo "Upgrading to head..."
if ! alembic upgrade head 2>&1; then
    echo "Direct upgrade failed, trying to upgrade to heads..."
    alembic upgrade heads 2>/dev/null || {
        echo "Multiple heads upgrade failed, trying individual heads..."
        alembic heads --verbose
        echo "Please check migration structure manually"
        exit 1
    }
fi

echo "✅ Database migrations completed!"

# Start the application
echo "🎉 Starting FastAPI application..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
