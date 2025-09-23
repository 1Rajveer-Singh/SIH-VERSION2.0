# Docker Setup Script for AI-Based Rockfall Prediction System
# Run this script in PowerShell as Administrator

Write-Host "🐳 Docker Setup for Rockfall Prediction System" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan

# Check if Docker is installed
function Test-Docker {
    try {
        $dockerVersion = docker --version
        Write-Host "✅ Docker is installed: $dockerVersion" -ForegroundColor Green
        return $true
    }
    catch {
        Write-Host "❌ Docker is not installed or not running" -ForegroundColor Red
        Write-Host "Please install Docker Desktop from: https://www.docker.com/products/docker-desktop" -ForegroundColor Yellow
        return $false
    }
}

# Check if Docker Compose is available
function Test-DockerCompose {
    try {
        $composeVersion = docker-compose --version
        Write-Host "✅ Docker Compose is available: $composeVersion" -ForegroundColor Green
        return $true
    }
    catch {
        Write-Host "❌ Docker Compose is not available" -ForegroundColor Red
        return $false
    }
}

# Setup environment variables
function Setup-Environment {
    Write-Host "🔧 Setting up environment variables..." -ForegroundColor Yellow
    
    # Create .env file for production
    $envContent = @"
# Database Configuration
MONGO_ROOT_USERNAME=admin
MONGO_ROOT_PASSWORD=rockfall123
MONGO_DATABASE=rockfall_prediction

# Redis Configuration
REDIS_PASSWORD=redis123

# JWT Configuration
JWT_SECRET_KEY=your-super-secret-jwt-key-change-in-production

# CORS Origins (comma-separated)
CORS_ORIGINS=http://localhost:3000,http://localhost:80

# External Service Keys (Add your keys here)
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_token
SENDGRID_API_KEY=your_sendgrid_key

# AWS Configuration
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_S3_BUCKET=your_s3_bucket_name
"@

    $envContent | Out-File -FilePath ".env" -Encoding UTF8
    Write-Host "✅ Environment file created (.env)" -ForegroundColor Green
}

# Main setup function
function Start-DockerSetup {
    Write-Host "🚀 Starting Docker setup..." -ForegroundColor Cyan
    
    # Stop any running containers
    Write-Host "🛑 Stopping existing containers..." -ForegroundColor Yellow
    docker-compose down 2>$null
    
    # Remove old images (optional)
    $removeImages = Read-Host "Do you want to remove old Docker images? (y/N)"
    if ($removeImages -eq "y" -or $removeImages -eq "Y") {
        Write-Host "🗑️ Removing old Docker images..." -ForegroundColor Yellow
        docker system prune -f
    }
    
    Write-Host "📋 Available Docker setups:" -ForegroundColor Cyan
    Write-Host "1. 📊 MongoDB Only (Database)"
    Write-Host "2. 🔧 Development Environment (All services)"
    Write-Host "3. 🚀 Production Environment (Full stack)"
    Write-Host "4. 🧪 Test Environment"
    
    $choice = Read-Host "Select setup option (1-4)"
    
    switch ($choice) {
        "1" {
            Write-Host "🏃 Starting MongoDB only..." -ForegroundColor Green
            docker-compose -f docker-compose.mongodb.yml up -d
        }
        "2" {
            Write-Host "🏃 Starting Development Environment..." -ForegroundColor Green
            Setup-Environment
            docker-compose -f deployment/docker-compose.dev.yml up -d --build
        }
        "3" {
            Write-Host "🏃 Starting Production Environment..." -ForegroundColor Green
            Setup-Environment
            docker-compose -f deployment/docker-compose.yml up -d --build
        }
        "4" {
            Write-Host "🏃 Starting Test Environment..." -ForegroundColor Green
            docker-compose -f deployment/docker-compose.dev.yml up -d --build
        }
        default {
            Write-Host "❌ Invalid option. Starting MongoDB only..." -ForegroundColor Red
            docker-compose -f docker-compose.mongodb.yml up -d
        }
    }
}

# Service status check
function Check-Services {
    Write-Host "🔍 Checking service status..." -ForegroundColor Yellow
    docker-compose ps
    
    Write-Host "`n📋 Service URLs:" -ForegroundColor Cyan
    Write-Host "🌐 Frontend: http://localhost:3000" -ForegroundColor Green
    Write-Host "🔧 Backend API: http://localhost:8000" -ForegroundColor Green
    Write-Host "📊 API Docs: http://localhost:8000/docs" -ForegroundColor Green
    Write-Host "🗄️ MongoDB: mongodb://localhost:27017" -ForegroundColor Green
    Write-Host "📱 Mongo Express: http://localhost:8081" -ForegroundColor Green
    Write-Host "🔄 Redis: redis://localhost:6379" -ForegroundColor Green
}

# Show logs
function Show-Logs {
    $service = Read-Host "Enter service name (mongodb/backend/frontend/redis) or press Enter for all"
    if ([string]::IsNullOrEmpty($service)) {
        docker-compose logs -f
    } else {
        docker-compose logs -f $service
    }
}

# Cleanup function
function Stop-Services {
    Write-Host "🛑 Stopping all services..." -ForegroundColor Yellow
    docker-compose down
    
    $removeVolumes = Read-Host "Do you want to remove volumes (data will be lost)? (y/N)"
    if ($removeVolumes -eq "y" -or $removeVolumes -eq "Y") {
        docker-compose down -v
        Write-Host "🗑️ Volumes removed" -ForegroundColor Red
    }
}

# Main execution
if (-not (Test-Docker)) {
    exit 1
}

if (-not (Test-DockerCompose)) {
    exit 1
}

# Change to project directory
Set-Location $PSScriptRoot

Write-Host "`n🎯 Docker Setup Menu:" -ForegroundColor Cyan
Write-Host "1. 🚀 Start Services"
Write-Host "2. 🔍 Check Status"
Write-Host "3. 📋 Show Logs"
Write-Host "4. 🛑 Stop Services"
Write-Host "5. 🔄 Restart Services"
Write-Host "6. 🧹 Clean Up"

$menuChoice = Read-Host "Select option (1-6)"

switch ($menuChoice) {
    "1" { Start-DockerSetup; Check-Services }
    "2" { Check-Services }
    "3" { Show-Logs }
    "4" { Stop-Services }
    "5" { 
        Write-Host "🔄 Restarting services..." -ForegroundColor Yellow
        docker-compose restart
        Check-Services
    }
    "6" {
        Stop-Services
        docker system prune -f
        Write-Host "🧹 Cleanup completed" -ForegroundColor Green
    }
    default {
        Write-Host "❌ Invalid option. Starting default setup..." -ForegroundColor Red
        Start-DockerSetup
    }
}

Write-Host "`n✅ Docker setup completed!" -ForegroundColor Green
Write-Host "💡 Use 'docker-compose logs -f' to monitor services" -ForegroundColor Yellow
Write-Host "💡 Use 'docker-compose down' to stop services" -ForegroundColor Yellow