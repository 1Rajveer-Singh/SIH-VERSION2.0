# AI-Based Rockfall Prediction & Alert System - Project Structure

## 📁 Project Organization

```
Advance Prototype/
├── 📁 backend/                     # FastAPI backend application
│   ├── 📁 app/                     # Application modules
│   │   ├── 📁 api/                 # API endpoints
│   │   ├── 📁 core/                # Core configurations and utilities
│   │   ├── 📁 database/            # Database connections and utilities
│   │   ├── 📁 models/              # Pydantic models and schemas
│   │   ├── 📁 routers/             # FastAPI routers
│   │   └── 📁 services/            # Business logic services
│   ├── 📁 tests/                   # Backend tests
│   ├── 📄 main.py                  # FastAPI application entry point
│   ├── 📄 requirements.txt         # Python dependencies
│   ├── 📄 requirements-test.txt    # Test dependencies
│   ├── 📄 pytest.ini              # Pytest configuration
│   └── 📄 Dockerfile              # Backend container configuration
│
├── 📁 frontend/                    # React TypeScript frontend
│   ├── 📁 src/                     # Frontend source code
│   │   ├── 📁 components/          # React components
│   │   ├── 📁 contexts/            # React contexts
│   │   ├── 📁 pages/               # Page components
│   │   ├── 📁 services/            # API services
│   │   └── 📁 __tests__/           # Frontend tests
│   ├── 📄 package.json             # Node.js dependencies
│   ├── 📄 tsconfig.json            # TypeScript configuration
│   ├── 📄 vite.config.ts           # Vite build configuration
│   ├── 📄 tailwind.config.js       # Tailwind CSS configuration
│   └── 📄 Dockerfile              # Frontend container configuration
│
├── 📁 ml_models/                   # Machine Learning components
│   ├── 📄 rockfall_prediction.py   # ML prediction models
│   ├── 📄 explainable_ai.py        # AI explanability features
│   ├── 📄 preprocessing.py         # Data preprocessing utilities
│   └── 📄 requirements.txt         # ML-specific dependencies
│
├── 📁 notification_system/         # Alert and notification system
│   ├── 📄 notifications.py         # Notification handlers
│   ├── 📄 escalation.py           # Alert escalation logic
│   └── 📄 __init__.py             # Package initialization
│
├── 📁 data/                        # Data management
│   ├── 📁 data/                    # Raw data files (JSON)
│   ├── 📁 demo/                    # Demo data files
│   ├── 📄 generate_demo_data.py    # Demo data generation
│   └── 📄 import_demo_data.py      # Data import utilities
│
├── 📁 database/                    # Database management
│   ├── 📁 migrations/              # Database migrations
│   ├── 📁 schemas/                 # Database schemas
│   ├── 📄 init_database.py         # Database initialization
│   ├── 📄 seed_demo_data.py        # Database seeding
│   └── 📄 README.md               # Database setup guide
│
├── 📁 deployment/                  # Deployment configurations
│   ├── 📄 docker-compose.yml       # Base docker compose
│   ├── 📄 docker-compose.dev.yml   # Development environment
│   ├── 📄 docker-compose.prod.yml  # Production environment
│   └── 📄 .env.example            # Environment template
│
├── 📁 config/                      # Configuration files
│   ├── 📄 .env.dev.example         # Development environment template
│   └── 📄 .env.prod.example        # Production environment template
│
├── 📁 scripts/                     # Utility scripts
│   ├── 📄 setup-dev.sh/.ps1        # Development setup scripts
│   ├── 📄 deploy-prod.sh/.ps1      # Production deployment scripts
│   ├── 📄 run-tests.sh/.ps1        # Test execution scripts
│   └── 📄 backup.sh               # Backup utilities
│
├── 📁 monitoring/                  # System monitoring
│   └── 📄 prometheus.yml          # Prometheus configuration
│
├── 📁 nginx/                       # Web server configuration
│   ├── 📁 conf.d/                 # Nginx configurations
│   └── 📄 nginx.conf              # Main nginx config
│
├── 📁 docs/                        # Project documentation
│
├── 📄 README.md                    # Project overview and setup
├── 📄 COMPREHENSIVE_DOCUMENTATION.md  # Detailed documentation
├── 📄 DEPLOYMENT.md                # Deployment guide
├── 📄 PROJECT_STRUCTURE.md         # This file - project organization
└── 📄 package.json                # Root package.json for workspaces
```

## 🧹 Cleanup Summary

The following duplicate and unnecessary files/folders have been removed:

### ❌ Removed Duplicates:
- `ml-models/` → Kept `ml_models/` (Python naming convention)
- `notifications/` → Kept `notification_system/` (more comprehensive)
- `demo_data/` → Consolidated with `data/demo/`
- `tests/` (root) → Kept `backend/tests/` (proper organization)
- `docker/` → Empty folder removed

### ❌ Removed Redundant Files:
- `backend/simple_main.py` → Kept comprehensive `main.py`
- `backend/simple_test.py` → Kept proper test structure
- `backend/test_api.py` → Consolidated into `tests/` folder
- `backend/app/main.py` → Kept root `main.py` (more comprehensive)
- `data/simple_import.py` → Kept full-featured import script
- All `__pycache__/` directories
- All `.pytest_cache/` directories

### 📁 Reorganized:
- Docker Compose files moved to `deployment/`
- Environment templates moved to `config/`
- Maintained clear separation of concerns

## 🚀 Benefits of This Structure

1. **Clear Separation**: Frontend, backend, ML, and infrastructure are clearly separated
2. **Scalability**: Each component can be developed and deployed independently
3. **Maintainability**: Related files are grouped together logically
4. **Docker-Ready**: Proper Dockerfile placement for containerization
5. **CI/CD Friendly**: Clear structure for automated deployment
6. **Development Friendly**: Easy to navigate and understand

## 📋 Quick Start

1. **Backend**: `cd backend && pip install -r requirements.txt`
2. **Frontend**: `cd frontend && npm install`
3. **Development**: Use `docker-compose -f deployment/docker-compose.dev.yml up`
4. **Production**: Use `docker-compose -f deployment/docker-compose.prod.yml up`

## 🔧 Configuration

- Copy environment templates from `config/` folder
- Customize for your environment (development/production)
- All deployment configurations are in `deployment/` folder