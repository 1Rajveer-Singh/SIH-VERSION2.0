@echo off
echo.
echo 🐳 Docker Quick Setup for Rockfall Prediction System
echo ================================================
echo.

cd /d "%~dp0"

echo 📋 Quick Setup Options:
echo 1. Start MongoDB only
echo 2. Start Full Development Environment  
echo 3. Start Production Environment
echo 4. Check Service Status
echo 5. Stop All Services
echo.

set /p choice="Select option (1-5): "

if "%choice%"=="1" (
    echo 🏃 Starting MongoDB...
    docker-compose -f docker-compose.mongodb.yml up -d
    goto :status
)

if "%choice%"=="2" (
    echo 🏃 Starting Development Environment...
    docker-compose -f deployment\docker-compose.dev.yml up -d --build
    goto :status
)

if "%choice%"=="3" (
    echo 🏃 Starting Production Environment...
    docker-compose -f deployment\docker-compose.yml up -d --build
    goto :status
)

if "%choice%"=="4" (
    goto :status
)

if "%choice%"=="5" (
    echo 🛑 Stopping all services...
    docker-compose down
    docker-compose -f docker-compose.mongodb.yml down
    docker-compose -f deployment\docker-compose.dev.yml down
    docker-compose -f deployment\docker-compose.yml down
    echo ✅ All services stopped
    goto :end
)

:status
echo.
echo 🔍 Service Status:
docker-compose ps
echo.
echo 📋 Service URLs:
echo 🌐 Frontend: http://localhost:3000
echo 🔧 Backend API: http://localhost:8000
echo 📊 API Docs: http://localhost:8000/docs
echo 🗄️ MongoDB: mongodb://localhost:27017
echo 📱 Mongo Express: http://localhost:8081
echo.

:end
echo.
echo 💡 Tip: Use 'docker-compose logs -f' to view logs
echo 💡 Tip: Use 'docker-compose down' to stop services
pause