#!/bin/bash

# Build and run script for Ally Platform

set -e

echo "🚀 Building Ally Platform Docker containers..."

# Build all containers
echo "📦 Building containers (this may take a few minutes)..."
docker-compose build --no-cache

echo "✅ Build completed!"

# Start services
echo "🎯 Starting services..."
docker-compose up -d

echo "⏳ Waiting for services to be healthy..."

# Wait for services to be healthy
timeout=300
counter=0

while [ $counter -lt $timeout ]; do
    if docker-compose ps | grep -q "Up (healthy)"; then
        echo "✅ Services are running and healthy!"
        
        echo ""
        echo "🎉 Ally Platform is ready!"
        echo "📖 Frontend: http://localhost:3000"
        echo "🔧 Backend API: http://localhost:8000"
        echo "📊 API Documentation: http://localhost:8000/docs"
        echo "🗄️ Database: Azure MySQL (psrazuredb.mysql.database.azure.com)"
        echo ""
        echo "📋 To view logs: docker-compose logs -f"
        echo "🛑 To stop: docker-compose down"
        
        exit 0
    fi
    
    sleep 5
    counter=$((counter + 5))
    echo "⏳ Still waiting... ($counter/$timeout seconds)"
done

echo "❌ Timeout waiting for services to be healthy"
echo "📋 Checking service status:"
docker-compose ps
echo ""
echo "📋 Backend logs:"
docker-compose logs backend
exit 1
