#!/bin/bash
# Development Environment Setup Script

set -e

echo "🛠️  Setting up development environment..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Error: Docker is not running"
    echo "Please start Docker and try again"
    exit 1
fi

# Create development environment file if it doesn't exist
if [ ! -f .env.dev ]; then
    echo "📝 Creating development environment file..."
    cp .env.dev.example .env.dev
    echo "✅ Created .env.dev from template"
fi

# Load environment variables
source .env.dev

# Stop any existing containers
echo "🛑 Stopping any existing containers..."
docker-compose -f docker-compose.dev.yml down -v || true

# Build and start development services
echo "🏗️  Building development images..."
docker-compose -f docker-compose.dev.yml build

echo "🚀 Starting development services..."
docker-compose -f docker-compose.dev.yml up -d

# Wait for services to start
echo "⏳ Waiting for services to start..."
sleep 20

# Check service status
echo "🏥 Checking service status..."
docker-compose -f docker-compose.dev.yml ps

# Import demo data
echo "📊 Importing demo data..."
sleep 10  # Give MongoDB more time to fully start

# Import data using Python script
echo "Running data import..."
docker-compose -f docker-compose.dev.yml exec -T backend-dev python /app/data/simple_import.py || {
    echo "⚠️  Demo data import failed, but services are running"
    echo "You can manually import data later using: npm run import-data"
}

echo "✅ Development environment setup completed!"
echo ""
echo "🌐 Development access points:"
echo "   Frontend:         http://localhost:3001"
echo "   Backend API:      http://localhost:8000" 
echo "   API Docs:         http://localhost:8000/docs"
echo "   MongoDB Admin:    http://localhost:8081 (admin/admin)"
echo "   Redis Admin:      http://localhost:8082"
echo ""
echo "🔐 Demo credentials:"
echo "   Username: admin     | Password: secret"
echo "   Username: operator  | Password: secret" 
echo "   Username: viewer    | Password: secret"
echo ""
echo "🛠️  Development commands:"
echo "   View logs:        docker-compose -f docker-compose.dev.yml logs -f"
echo "   Stop services:    docker-compose -f docker-compose.dev.yml down"
echo "   Restart services: docker-compose -f docker-compose.dev.yml restart"
echo "   Rebuild:          docker-compose -f docker-compose.dev.yml up --build"