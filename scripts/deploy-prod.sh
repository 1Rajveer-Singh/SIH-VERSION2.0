#!/bin/bash
# Production Deployment Script

set -e

echo "🚀 Starting production deployment..."

# Check if required files exist
if [ ! -f .env.prod ]; then
    echo "❌ Error: .env.prod file not found"
    echo "📝 Please copy .env.prod.example to .env.prod and configure it"
    exit 1
fi

# Load environment variables
source .env.prod

# Validate critical environment variables
if [ -z "$MONGO_ROOT_PASSWORD" ] || [ "$MONGO_ROOT_PASSWORD" = "your_secure_mongodb_password_here" ]; then
    echo "❌ Error: Please set a secure MONGO_ROOT_PASSWORD in .env.prod"
    exit 1
fi

if [ -z "$SECRET_KEY" ] || [ "$SECRET_KEY" = "your_very_secure_secret_key_here_min_32_chars" ]; then
    echo "❌ Error: Please set a secure SECRET_KEY in .env.prod"
    exit 1
fi

# Create necessary directories
mkdir -p ssl
mkdir -p logs
mkdir -p backups
mkdir -p monitoring/prometheus
mkdir -p monitoring/grafana/provisioning
mkdir -p nginx/conf.d

# Build and start services
echo "🏗️  Building Docker images..."
docker-compose -f docker-compose.prod.yml build --no-cache

echo "📦 Pulling latest images..."
docker-compose -f docker-compose.prod.yml pull

echo "🗃️  Creating volumes and networks..."
docker-compose -f docker-compose.prod.yml up --no-start

echo "🚀 Starting services..."
docker-compose -f docker-compose.prod.yml up -d

# Wait for services to be healthy
echo "⏳ Waiting for services to start..."
sleep 30

# Check service health
echo "🏥 Checking service health..."
docker-compose -f docker-compose.prod.yml ps

# Run database initialization if needed
echo "🗄️  Initializing database..."
docker-compose -f docker-compose.prod.yml exec -T backend python -c "
import asyncio
import sys
sys.path.append('/app')
from backend.database import create_collections
asyncio.run(create_collections())
print('Database collections created successfully')
"

# Import demo data if data directory exists
if [ -d "./data" ]; then
    echo "📊 Importing demo data..."
    docker-compose -f docker-compose.prod.yml exec -T backend python data/simple_import.py
fi

# Create initial admin user if needed
echo "👤 Creating admin user..."
docker-compose -f docker-compose.prod.yml exec -T backend python -c "
import asyncio
import sys
sys.path.append('/app')
from backend.auth import create_user
from backend.database import get_database

async def create_admin():
    db = await get_database()
    user_exists = await db.users.find_one({'username': 'admin'})
    if not user_exists:
        await create_user(
            username='admin',
            email='admin@example.com',
            password='admin123',
            role='admin'
        )
        print('Admin user created successfully')
    else:
        print('Admin user already exists')

asyncio.run(create_admin())
"

echo "✅ Production deployment completed!"
echo ""
echo "🌐 Access points:"
echo "   Frontend:      http://localhost:3001"
echo "   Backend API:   http://localhost:8000"
echo "   API Docs:      http://localhost:8000/docs"
echo "   Monitoring:    http://localhost:3000 (Grafana)"
echo "   Metrics:       http://localhost:9090 (Prometheus)"
echo ""
echo "🔐 Default credentials:"
echo "   Admin user:    admin / admin123"
echo "   Grafana:       admin / ${GRAFANA_PASSWORD}"
echo ""
echo "📝 Next steps:"
echo "   1. Configure SSL certificates in ./ssl/"
echo "   2. Set up domain DNS to point to this server"
echo "   3. Configure firewall rules"
echo "   4. Set up monitoring alerts"
echo "   5. Schedule regular backups"