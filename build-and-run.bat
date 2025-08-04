@echo off
echo 🚀 Building Ally Platform Docker containers...

REM Build all containers
echo 📦 Building containers (this may take a few minutes)...
docker-compose build --no-cache

if %ERRORLEVEL% neq 0 (
    echo ❌ Build failed!
    pause
    exit /b 1
)

echo ✅ Build completed!

REM Start services
echo 🎯 Starting services...
docker-compose up -d

if %ERRORLEVEL% neq 0 (
    echo ❌ Failed to start services!
    pause
    exit /b 1
)

echo ⏳ Waiting for services to be healthy...

REM Wait a bit for services to start
timeout /t 30 /nobreak >nul

echo ✅ Services should be running!
echo.
echo 🎉 Ally Platform is ready!
echo 📖 Frontend: http://localhost:3000
echo 🔧 Backend API: http://localhost:8000
echo 📊 API Documentation: http://localhost:8000/docs
echo 🗄️ Database: Azure MySQL (psrazuredb.mysql.database.azure.com)
echo.
echo 📋 To view logs: docker-compose logs -f
echo 🛑 To stop: docker-compose down

pause
