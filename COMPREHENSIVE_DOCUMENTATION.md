# AI-Based Rockfall Prediction & Alert System - Documentation

## 🌟 Complete System Documentation

This document provides comprehensive documentation for the AI-Based Rockfall Prediction & Alert System, a production-ready mining safety solution.

## 📋 Table of Contents

1. [System Overview](#system-overview)
2. [Architecture Documentation](#architecture-documentation)
3. [API Documentation](#api-documentation)
4. [Deployment Guide](#deployment-guide)
5. [User Manual](#user-manual)
6. [Developer Guide](#developer-guide)
7. [Testing Guide](#testing-guide)
8. [Troubleshooting](#troubleshooting)

---

## System Overview

### Project Description
A comprehensive, production-ready AI system for mining safety that predicts and alerts about rockfall incidents using machine learning, real-time sensor monitoring, and advanced geospatial analysis.

### Key Features
- **Real-time Sensor Monitoring**: Continuous data collection from mining sensors
- **AI-Powered Predictions**: PyTorch-based ML models (LSTM, CNN, Ensemble)
- **Multi-Channel Alerts**: Email, SMS, webhook notifications with escalation
- **Interactive Dashboard**: Real-time React frontend with data visualization
- **Geospatial Analysis**: DEM processing, drone imagery analysis
- **Explainable AI**: SHAP-based explanations for model predictions

### Technology Stack
- **Backend**: FastAPI, MongoDB, PyTorch, Celery
- **Frontend**: React, TypeScript, Tailwind CSS, Vite
- **DevOps**: Docker, Nginx, Prometheus, Grafana
- **Testing**: Pytest, Jest, React Testing Library

---

## Architecture Documentation

### System Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   React Client  │────│   Nginx Proxy    │────│  FastAPI Server │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                         │
                       ┌──────────────────┐             │
                       │   ML Services    │─────────────┤
                       └──────────────────┘             │
                                                         │
┌─────────────────┐    ┌──────────────────┐             │
│   Notifications │────│   Celery Queue   │─────────────┤
└─────────────────┘    └──────────────────┘             │
                                                         │
                       ┌──────────────────┐             │
                       │   MongoDB Atlas  │─────────────┘
                       └──────────────────┘
```

### Component Architecture

#### Backend Components
- **API Layer**: FastAPI with automatic OpenAPI documentation
- **Authentication**: JWT-based with role-based access control
- **Database Layer**: MongoDB with async Motor driver
- **ML Services**: PyTorch models with SHAP explanations
- **Notification System**: Multi-channel alert processing
- **Task Queue**: Celery for background processing

#### Frontend Components
- **Dashboard**: Real-time monitoring interface
- **Alert Management**: Alert configuration and history
- **User Management**: Authentication and authorization
- **Data Visualization**: Charts and geospatial displays
- **Settings**: System configuration interface

### Database Schema

#### Collections
1. **users**: User authentication and profiles
2. **sites**: Mining site information and metadata
3. **sensors**: Sensor device configurations
4. **sensor_readings**: Time-series sensor data
5. **predictions**: ML model predictions and results
6. **alerts**: Alert configurations and history
7. **notifications**: Notification logs and status

#### Indexing Strategy
- **Time-series indices**: Optimized for sensor data queries
- **Geospatial indices**: 2dsphere indices for location queries
- **Compound indices**: Multi-field indices for complex queries
- **TTL indices**: Automatic data expiration for logs

---

## API Documentation

### Authentication Endpoints

#### POST /auth/login
Login with username/email and password.

**Request Body:**
```json
{
  "username": "user@example.com",
  "password": "secure_password"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 3600,
  "user": {
    "id": "507f1f77bcf86cd799439011",
    "username": "user@example.com",
    "role": "engineer"
  }
}
```

#### POST /auth/refresh
Refresh access token using refresh token.

#### POST /auth/logout
Logout and invalidate tokens.

### User Management Endpoints

#### GET /users/
Get all users (admin only).

**Query Parameters:**
- `page`: Page number (default: 1)
- `size`: Page size (default: 50)
- `role`: Filter by role

**Response:**
```json
{
  "items": [
    {
      "id": "507f1f77bcf86cd799439011",
      "username": "engineer1",
      "email": "engineer1@company.com",
      "role": "engineer",
      "full_name": "John Engineer",
      "is_active": true,
      "created_at": "2024-01-15T10:30:00Z"
    }
  ],
  "total": 25,
  "page": 1,
  "size": 50,
  "pages": 1
}
```

#### POST /users/
Create new user (admin only).

#### GET /users/{user_id}
Get user by ID.

#### PUT /users/{user_id}
Update user information.

#### DELETE /users/{user_id}
Delete user (admin only).

### Site Management Endpoints

#### GET /sites/
Get all mining sites.

**Response:**
```json
{
  "items": [
    {
      "id": "507f1f77bcf86cd799439012",
      "name": "North Pit Alpha",
      "location": {
        "type": "Point",
        "coordinates": [-112.074036, 39.585889]
      },
      "description": "Primary extraction site",
      "status": "active",
      "created_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

#### POST /sites/
Create new mining site.

#### GET /sites/{site_id}
Get site details including sensors and recent data.

#### PUT /sites/{site_id}
Update site information.

### Sensor Endpoints

#### GET /sensors/
Get all sensors with filtering options.

**Query Parameters:**
- `site_id`: Filter by site
- `sensor_type`: Filter by sensor type
- `status`: Filter by status

#### POST /sensors/
Register new sensor.

**Request Body:**
```json
{
  "device_id": "ACCEL_001",
  "site_id": "507f1f77bcf86cd799439012",
  "sensor_type": "accelerometer",
  "location": {
    "type": "Point",
    "coordinates": [-112.074036, 39.585889]
  },
  "installation_date": "2024-01-15T10:30:00Z"
}
```

#### POST /sensors/{sensor_id}/readings
Submit sensor readings (bulk).

**Request Body:**
```json
{
  "readings": [
    {
      "timestamp": "2024-01-15T10:30:00Z",
      "values": {
        "x_acceleration": 0.05,
        "y_acceleration": 0.03,
        "z_acceleration": 9.81
      },
      "metadata": {
        "battery_level": 0.85,
        "signal_strength": -65
      }
    }
  ]
}
```

### Prediction Endpoints

#### GET /predictions/
Get prediction history with filtering.

**Query Parameters:**
- `site_id`: Filter by site
- `risk_level`: Filter by risk level
- `start_date`: Start date filter
- `end_date`: End date filter

#### POST /predictions/generate
Generate new prediction for site.

**Request Body:**
```json
{
  "site_id": "507f1f77bcf86cd799439012",
  "model_type": "ensemble",
  "time_horizon": 24
}
```

**Response:**
```json
{
  "prediction_id": "507f1f77bcf86cd799439013",
  "site_id": "507f1f77bcf86cd799439012",
  "risk_probability": 0.75,
  "risk_class": "High",
  "confidence_score": 0.89,
  "explanation": {
    "top_factors": [
      "Increased seismic activity",
      "Weather conditions",
      "Historical patterns"
    ],
    "shap_values": {...}
  },
  "time_horizon": 24,
  "created_at": "2024-01-15T10:30:00Z"
}
```

### Alert Endpoints

#### GET /alerts/
Get alert configurations and history.

#### POST /alerts/
Create new alert rule.

**Request Body:**
```json
{
  "name": "High Risk Alert",
  "site_id": "507f1f77bcf86cd799439012",
  "conditions": {
    "risk_threshold": 0.7,
    "time_window": 60
  },
  "notification_channels": ["email", "sms"],
  "escalation_rules": [
    {
      "delay_minutes": 15,
      "channels": ["sms", "webhook"]
    }
  ]
}
```

---

## Deployment Guide

### Development Deployment

#### Prerequisites
- Python 3.11+
- Node.js 18+
- MongoDB 6.0+
- Redis 6.0+

#### Quick Start

1. **Environment Setup**
   ```bash
   # Copy environment configuration
   cp .env.dev.example .env
   
   # Edit .env with your settings
   nano .env
   ```

2. **Backend Setup**
   ```bash
   cd backend
   pip install -r requirements.txt
   uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
   ```

3. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

4. **Access Applications**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Production Deployment

#### Docker Deployment

1. **Prepare Environment**
   ```bash
   cp .env.prod.example .env
   # Configure production settings in .env
   ```

2. **Deploy with Docker Compose**
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

3. **Initialize Database**
   ```bash
   # Import demo data
   docker exec -it rockfall-backend python scripts/init_demo_data.py
   ```

#### Manual Production Setup

1. **System Dependencies**
   ```bash
   # Ubuntu/Debian
   sudo apt update
   sudo apt install python3.11 nodejs npm mongodb redis-server nginx
   
   # CentOS/RHEL
   sudo yum install python3.11 nodejs npm mongodb redis nginx
   ```

2. **Application Setup**
   ```bash
   # Backend
   cd backend
   pip install -r requirements.txt
   gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
   
   # Frontend
   cd frontend
   npm install
   npm run build
   ```

3. **Nginx Configuration**
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;
       
       location / {
           root /path/to/frontend/dist;
           try_files $uri $uri/ /index.html;
       }
       
       location /api {
           proxy_pass http://127.0.0.1:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

#### Environment Variables

**Required Variables:**
```bash
# Database
MONGODB_URL=mongodb://localhost:27017/rockfall_prediction
REDIS_URL=redis://localhost:6379/0

# Security
SECRET_KEY=your-super-secret-jwt-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# External Services
TWILIO_ACCOUNT_SID=your-twilio-sid
TWILIO_AUTH_TOKEN=your-twilio-token
SENDGRID_API_KEY=your-sendgrid-key

# Application
ENVIRONMENT=production
DEBUG=false
CORS_ORIGINS=https://your-domain.com
```

#### SSL Configuration

1. **Obtain SSL Certificate**
   ```bash
   # Using Let's Encrypt
   sudo certbot --nginx -d your-domain.com
   ```

2. **Update Nginx Configuration**
   ```nginx
   server {
       listen 443 ssl;
       ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
       ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
       # ... rest of configuration
   }
   ```

#### Monitoring Setup

1. **Prometheus Configuration**
   ```yaml
   # prometheus.yml
   global:
     scrape_interval: 15s
   
   scrape_configs:
     - job_name: 'rockfall-api'
       static_configs:
         - targets: ['localhost:8000']
   ```

2. **Grafana Dashboard**
   - Import provided dashboard JSON
   - Configure data source (Prometheus)
   - Set up alerting rules

---

## User Manual

### Getting Started

#### First Login
1. Navigate to the application URL
2. Use provided credentials to log in
3. Complete profile setup if required
4. Familiarize yourself with the dashboard

#### Dashboard Overview
The main dashboard provides:
- **Real-time Monitoring**: Current sensor status and readings
- **Risk Assessment**: Current risk levels for all sites
- **Recent Alerts**: Latest alerts and notifications
- **Quick Actions**: Common tasks and operations

### User Roles

#### Safety Officer
- **Permissions**: View all data, manage alerts, generate reports
- **Responsibilities**: Monitor safety conditions, respond to alerts
- **Key Features**: Alert management, incident reporting

#### Engineer
- **Permissions**: View site data, configure sensors, run predictions
- **Responsibilities**: Technical monitoring, system maintenance
- **Key Features**: Sensor management, data analysis

#### Manager
- **Permissions**: Full system access, user management, reporting
- **Responsibilities**: Oversight, decision making, compliance
- **Key Features**: User management, comprehensive reporting

#### Researcher
- **Permissions**: Read-only access to historical data
- **Responsibilities**: Analysis, research, reporting
- **Key Features**: Data export, historical analysis

### Features Guide

#### Site Management
1. **Adding New Site**
   - Navigate to Sites → Add New
   - Fill in site details and location
   - Configure default alert thresholds
   - Save and activate site

2. **Site Configuration**
   - Access site settings
   - Configure sensor placement
   - Set alert parameters
   - Define notification preferences

#### Sensor Management
1. **Sensor Registration**
   - Go to Sensors → Register New
   - Enter device ID and specifications
   - Set installation location
   - Configure reading intervals

2. **Sensor Monitoring**
   - View real-time sensor status
   - Check battery levels and connectivity
   - Review recent readings
   - Troubleshoot issues

#### Alert Configuration
1. **Creating Alert Rules**
   - Define trigger conditions
   - Set threshold values
   - Configure notification channels
   - Set up escalation procedures

2. **Managing Notifications**
   - Configure contact methods
   - Set availability schedules
   - Test notification channels
   - Review delivery logs

#### Data Analysis
1. **Historical Data Review**
   - Select time range and sites
   - Filter by sensor type or conditions
   - Export data for external analysis
   - Generate trend reports

2. **Prediction Analysis**
   - Run prediction models
   - Review confidence scores
   - Analyze contributing factors
   - Export prediction results

### Common Tasks

#### Daily Monitoring Checklist
- [ ] Check dashboard for active alerts
- [ ] Review overnight prediction reports
- [ ] Verify sensor connectivity status
- [ ] Check battery levels for wireless sensors
- [ ] Review weather impact assessments

#### Weekly Maintenance Tasks
- [ ] Generate weekly safety reports
- [ ] Review and update alert thresholds
- [ ] Check system performance metrics
- [ ] Validate notification channel functionality
- [ ] Update emergency contact information

#### Monthly Administrative Tasks
- [ ] User access review and updates
- [ ] System backup verification
- [ ] Performance optimization review
- [ ] Training schedule updates
- [ ] Compliance reporting

---

## Developer Guide

### Development Environment Setup

#### Prerequisites
```bash
# Required software
- Python 3.11+
- Node.js 18+
- Git
- Docker (optional)
- MongoDB Compass (recommended)
```

#### Initial Setup
```bash
# Clone repository
git clone <repository-url>
cd "Advance Prototype"

# Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-test.txt

# Frontend setup
cd ../frontend
npm install

# Environment configuration
cp .env.dev.example .env
# Edit .env with development settings
```

### Code Structure

#### Backend Architecture
```
backend/
├── app/
│   ├── api/                    # API endpoint definitions
│   │   └── v1/                 # API version 1
│   ├── core/                   # Core functionality
│   │   ├── auth.py            # Authentication logic
│   │   ├── config.py          # Configuration management
│   │   └── database.py        # Database connections
│   ├── models/                 # Pydantic models
│   │   ├── user.py            # User models
│   │   ├── sensor.py          # Sensor models
│   │   └── prediction.py      # Prediction models
│   ├── routers/               # API route handlers
│   │   ├── auth.py            # Authentication routes
│   │   ├── users.py           # User management routes
│   │   └── sensors.py         # Sensor routes
│   ├── services/              # Business logic
│   │   ├── ml/                # ML service modules
│   │   ├── notifications/     # Notification services
│   │   └── data/              # Data processing services
│   └── main.py                # FastAPI application
├── tests/                     # Test suite
│   ├── test_auth.py          # Authentication tests
│   ├── test_api.py           # API endpoint tests
│   └── conftest.py           # Test configuration
└── requirements.txt           # Python dependencies
```

#### Frontend Architecture
```
frontend/
├── src/
│   ├── components/            # Reusable React components
│   │   ├── common/           # Generic components
│   │   ├── dashboard/        # Dashboard components
│   │   └── forms/            # Form components
│   ├── pages/                # Page components
│   │   ├── Dashboard.tsx     # Main dashboard
│   │   ├── Login.tsx         # Authentication
│   │   └── Sites.tsx         # Site management
│   ├── hooks/                # Custom React hooks
│   │   ├── useAuth.ts        # Authentication hook
│   │   └── useApi.ts         # API interaction hook
│   ├── services/             # API service layer
│   │   ├── api.ts            # Base API configuration
│   │   ├── auth.ts           # Authentication service
│   │   └── sensors.ts        # Sensor API service
│   ├── types/                # TypeScript type definitions
│   │   ├── auth.ts           # Authentication types
│   │   └── sensors.ts        # Sensor types
│   └── App.tsx               # Main application component
├── tests/                    # Frontend tests
└── package.json              # Node.js dependencies
```

### Development Workflow

#### Branch Strategy
```bash
# Feature development
git checkout -b feature/new-prediction-model
# Work on feature
git commit -m "Add ensemble prediction model"
git push origin feature/new-prediction-model
# Create pull request
```

#### Code Quality Standards

**Backend Standards:**
```bash
# Code formatting
black app/ tests/
isort app/ tests/

# Linting
flake8 app/ tests/
mypy app/

# Testing
pytest tests/ --cov=app --cov-report=html
```

**Frontend Standards:**
```bash
# Code formatting
npm run format

# Linting
npm run lint

# Type checking
npm run type-check

# Testing
npm run test
```

#### Adding New Features

**Adding New API Endpoint:**
1. Define Pydantic models in `models/`
2. Create route handler in `routers/`
3. Add business logic in `services/`
4. Write tests in `tests/`
5. Update API documentation

**Adding New Frontend Component:**
1. Create component in appropriate directory
2. Define TypeScript interfaces
3. Implement component logic
4. Add component tests
5. Update Storybook documentation

### Testing Guidelines

#### Backend Testing
```python
# Example test structure
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_create_user():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/users/", json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpassword"
        })
    assert response.status_code == 201
    assert response.json()["username"] == "testuser"
```

#### Frontend Testing
```typescript
// Example component test
import { render, screen } from '@testing-library/react';
import { Dashboard } from '../pages/Dashboard';

test('renders dashboard with navigation', () => {
  render(<Dashboard />);
  const navElement = screen.getByRole('navigation');
  expect(navElement).toBeInTheDocument();
});
```

### Debugging Guide

#### Backend Debugging
```python
# Add debug logging
import logging
logger = logging.getLogger(__name__)

# In your code
logger.debug("Debug information")
logger.info("General information")
logger.warning("Warning message")
logger.error("Error message")

# Using debugger
import pdb; pdb.set_trace()  # Add breakpoint
```

#### Frontend Debugging
```typescript
// Console debugging
console.log('Debug info:', data);
console.warn('Warning:', warning);
console.error('Error:', error);

// React DevTools
// Install React Developer Tools browser extension

// TypeScript debugging
// Use debugger statement for breakpoints
debugger;
```

### Performance Optimization

#### Backend Optimization
- Use async/await for database operations
- Implement proper indexing strategies
- Use connection pooling
- Implement caching with Redis
- Profile with py-spy or similar tools

#### Frontend Optimization
- Use React.memo for expensive components
- Implement proper key props for lists
- Use lazy loading for routes
- Optimize bundle size with tree shaking
- Profile with React DevTools Profiler

---

## Testing Guide

### Test Strategy

#### Test Pyramid
```
    ┌─────────────────┐
    │   E2E Tests     │  ← Few, high-level integration
    │                 │
    ├─────────────────┤
    │ Integration     │  ← Some, API + DB integration
    │ Tests           │
    ├─────────────────┤
    │   Unit Tests    │  ← Many, fast, isolated
    │                 │
    └─────────────────┘
```

#### Test Categories

**Unit Tests:**
- Individual function testing
- Component isolation testing
- Mock external dependencies
- Fast execution (< 1s per test)

**Integration Tests:**
- API endpoint testing
- Database integration
- External service integration
- Service-to-service communication

**End-to-End Tests:**
- Complete user workflows
- Browser automation
- Real environment testing
- Performance validation

### Backend Testing

#### Test Configuration
```python
# conftest.py
import pytest
import asyncio
from httpx import AsyncClient
from app.main import app
from app.database import get_database

@pytest.fixture
async def client():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

@pytest.fixture
async def db():
    # Use test database
    test_db = get_test_database()
    yield test_db
    # Cleanup after test
    await test_db.drop_collection("test_collection")
```

#### Authentication Tests
```python
# test_auth.py
import pytest
from app.core.auth import get_password_hash, verify_password

class TestPasswordHashing:
    def test_password_hashing(self):
        password = "test_password_123"
        hashed = get_password_hash(password)
        
        assert hashed != password
        assert verify_password(password, hashed) is True
        assert verify_password("wrong_password", hashed) is False

@pytest.mark.asyncio
async def test_login_endpoint(client):
    response = await client.post("/auth/login", json={
        "username": "testuser",
        "password": "testpassword"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()
```

#### API Tests
```python
# test_sites.py
@pytest.mark.asyncio
async def test_create_site(client, auth_headers):
    site_data = {
        "name": "Test Site",
        "location": {
            "type": "Point",
            "coordinates": [-112.074036, 39.585889]
        },
        "description": "Test mining site"
    }
    
    response = await client.post(
        "/sites/", 
        json=site_data, 
        headers=auth_headers
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Site"
    assert "id" in data

@pytest.mark.asyncio
async def test_get_sites_pagination(client, auth_headers):
    response = await client.get(
        "/sites/?page=1&size=10", 
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "page" in data
```

#### ML Model Tests
```python
# test_ml_models.py
import torch
import pytest
from app.services.ml.lstm_model import LSTMPredictor

class TestLSTMModel:
    def test_model_initialization(self):
        model = LSTMPredictor(
            input_size=10,
            hidden_size=50,
            num_layers=2,
            output_size=1
        )
        assert model.input_size == 10
        assert model.hidden_size == 50

    def test_model_prediction(self):
        model = LSTMPredictor(10, 50, 2, 1)
        input_data = torch.randn(1, 24, 10)  # batch, sequence, features
        
        with torch.no_grad():
            output = model(input_data)
        
        assert output.shape == (1, 1)
        assert 0 <= output.item() <= 1  # Probability output
```

### Frontend Testing

#### Component Tests
```typescript
// Login.test.tsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { Login } from '../pages/Login';
import { AuthProvider } from '../contexts/AuthContext';

const MockedLogin = () => (
  <AuthProvider>
    <Login />
  </AuthProvider>
);

test('renders login form', () => {
  render(<MockedLogin />);
  
  expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
  expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
  expect(screen.getByRole('button', { name: /sign in/i })).toBeInTheDocument();
});

test('handles form submission', async () => {
  const mockLogin = jest.fn();
  jest.mock('../hooks/useAuth', () => ({
    useAuth: () => ({ login: mockLogin })
  }));

  render(<MockedLogin />);
  
  fireEvent.change(screen.getByLabelText(/email/i), {
    target: { value: 'test@example.com' }
  });
  fireEvent.change(screen.getByLabelText(/password/i), {
    target: { value: 'password123' }
  });
  
  fireEvent.click(screen.getByRole('button', { name: /sign in/i }));
  
  await waitFor(() => {
    expect(mockLogin).toHaveBeenCalledWith('test@example.com', 'password123');
  });
});
```

#### Hook Tests
```typescript
// useAuth.test.ts
import { renderHook, act } from '@testing-library/react';
import { useAuth } from '../hooks/useAuth';

test('useAuth hook manages authentication state', async () => {
  const { result } = renderHook(() => useAuth());
  
  expect(result.current.isAuthenticated).toBe(false);
  expect(result.current.user).toBe(null);
  
  await act(async () => {
    await result.current.login('test@example.com', 'password123');
  });
  
  expect(result.current.isAuthenticated).toBe(true);
  expect(result.current.user).toBeTruthy();
});
```

### Running Tests

#### Backend Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_auth.py

# Run specific test
pytest tests/test_auth.py::test_password_hashing

# Run with verbose output
pytest -v

# Run integration tests only
pytest -m integration

# Run unit tests only
pytest -m "not integration"
```

#### Frontend Tests
```bash
# Run all tests
npm test

# Run in watch mode
npm run test:watch

# Run with coverage
npm run test:coverage

# Run specific test file
npm test Login.test.tsx

# Run E2E tests
npm run e2e
```

#### E2E Tests with Playwright
```typescript
// tests/e2e/login.spec.ts
import { test, expect } from '@playwright/test';

test('user can login and access dashboard', async ({ page }) => {
  await page.goto('/login');
  
  await page.fill('[data-testid="email"]', 'test@example.com');
  await page.fill('[data-testid="password"]', 'password123');
  await page.click('[data-testid="login-button"]');
  
  await expect(page).toHaveURL('/dashboard');
  await expect(page.locator('[data-testid="dashboard-title"]')).toBeVisible();
});

test('displays error for invalid credentials', async ({ page }) => {
  await page.goto('/login');
  
  await page.fill('[data-testid="email"]', 'invalid@example.com');
  await page.fill('[data-testid="password"]', 'wrongpassword');
  await page.click('[data-testid="login-button"]');
  
  await expect(page.locator('[data-testid="error-message"]')).toBeVisible();
});
```

### Test Data Management

#### Backend Test Data
```python
# test_data.py
from factory import Factory, Faker, SubFactory
from app.models.user import User
from app.models.site import Site

class UserFactory(Factory):
    class Meta:
        model = User
    
    username = Faker('user_name')
    email = Faker('email')
    role = 'engineer'
    is_active = True

class SiteFactory(Factory):
    class Meta:
        model = Site
    
    name = Faker('company')
    description = Faker('text', max_nb_chars=200)
    location = {
        "type": "Point",
        "coordinates": [Faker('longitude'), Faker('latitude')]
    }
```

#### Frontend Test Data
```typescript
// testUtils.ts
export const mockUser = {
  id: '1',
  username: 'testuser',
  email: 'test@example.com',
  role: 'engineer',
  isActive: true
};

export const mockSite = {
  id: '1',
  name: 'Test Site',
  location: {
    type: 'Point',
    coordinates: [-112.074036, 39.585889]
  },
  description: 'Test mining site'
};

export const renderWithProviders = (ui: React.ReactElement) => {
  const Wrapper = ({ children }: { children: React.ReactNode }) => (
    <AuthProvider>
      <QueryClient>
        {children}
      </QueryClient>
    </AuthProvider>
  );
  
  return render(ui, { wrapper: Wrapper });
};
```

---

## Troubleshooting

### Common Issues

#### Backend Issues

**Issue: Database Connection Failed**
```
Error: Could not connect to MongoDB
```

**Solution:**
1. Verify MongoDB is running: `systemctl status mongod`
2. Check connection string in `.env` file
3. Verify network connectivity and firewall settings
4. Check MongoDB logs: `tail -f /var/log/mongodb/mongod.log`

**Issue: Authentication Token Expired**
```
Error: 401 Unauthorized - Token has expired
```

**Solution:**
1. Check token expiration settings in config
2. Implement automatic token refresh
3. Clear browser storage and re-login
4. Verify system clock synchronization

**Issue: ML Model Loading Error**
```
Error: Failed to load PyTorch model
```

**Solution:**
1. Verify model files exist in correct directory
2. Check PyTorch version compatibility
3. Ensure sufficient memory for model loading
4. Validate model file integrity

#### Frontend Issues

**Issue: CORS Error**
```
Error: CORS policy blocks request to API
```

**Solution:**
1. Configure CORS origins in backend settings
2. Use proxy in development mode
3. Verify API URL configuration
4. Check browser console for exact error

**Issue: Build Fails**
```
Error: TypeScript compilation failed
```

**Solution:**
1. Run type checking: `npm run type-check`
2. Fix TypeScript errors in code
3. Update type definitions if needed
4. Clear node_modules and reinstall: `rm -rf node_modules && npm install`

**Issue: Performance Issues**
```
Warning: Slow component rendering
```

**Solution:**
1. Use React DevTools Profiler to identify bottlenecks
2. Implement React.memo for expensive components
3. Optimize data fetching with proper caching
4. Use pagination for large datasets

#### Deployment Issues

**Issue: Docker Container Won't Start**
```
Error: Container exits immediately
```

**Solution:**
1. Check container logs: `docker logs <container-id>`
2. Verify environment variables are set
3. Check Dockerfile syntax and dependencies
4. Ensure proper file permissions

**Issue: High Memory Usage**
```
Warning: Container using excessive memory
```

**Solution:**
1. Monitor memory usage: `docker stats`
2. Optimize ML model loading
3. Implement proper garbage collection
4. Set memory limits in Docker configuration

**Issue: SSL Certificate Error**
```
Error: SSL certificate verification failed
```

**Solution:**
1. Verify certificate validity: `openssl x509 -in cert.pem -text`
2. Check certificate chain completeness
3. Verify domain name matches certificate
4. Update certificate if expired

### Performance Optimization

#### Database Performance
```javascript
// MongoDB indexing strategy
db.sensor_readings.createIndex({ 
  "device_id": 1, 
  "timestamp": -1 
});

db.sensor_readings.createIndex({ 
  "site_id": 1, 
  "sensor_type": 1, 
  "timestamp": -1 
});

// Location-based queries
db.sensors.createIndex({ 
  "location": "2dsphere" 
});
```

#### API Performance
```python
# Use async operations
@app.get("/sensors/{sensor_id}/readings")
async def get_sensor_readings(
    sensor_id: str,
    limit: int = 100,
    skip: int = 0
):
    readings = await db.sensor_readings.find(
        {"device_id": sensor_id}
    ).sort("timestamp", -1).skip(skip).limit(limit).to_list(length=limit)
    return readings

# Implement caching
from functools import lru_cache

@lru_cache(maxsize=128)
def get_site_config(site_id: str):
    # Expensive operation cached in memory
    return site_configuration
```

#### Frontend Performance
```typescript
// Component optimization
const ExpensiveComponent = React.memo(({ data }) => {
  const processedData = useMemo(() => 
    processLargeDataset(data), [data]
  );
  
  return <div>{processedData}</div>;
});

// Lazy loading
const Dashboard = lazy(() => import('./pages/Dashboard'));
const Reports = lazy(() => import('./pages/Reports'));

function App() {
  return (
    <Suspense fallback={<Loading />}>
      <Routes>
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/reports" element={<Reports />} />
      </Routes>
    </Suspense>
  );
}
```

### Monitoring and Alerting

#### Application Monitoring
```python
# Custom metrics with Prometheus
from prometheus_client import Counter, Histogram, generate_latest

REQUEST_COUNT = Counter('api_requests_total', 'API request count', ['method', 'endpoint'])
REQUEST_LATENCY = Histogram('api_request_duration_seconds', 'API request latency')

@app.middleware("http")
async def monitor_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    REQUEST_COUNT.labels(method=request.method, endpoint=request.url.path).inc()
    REQUEST_LATENCY.observe(process_time)
    
    return response
```

#### Log Analysis
```bash
# Useful log analysis commands
# Find error patterns
grep -E "(ERROR|CRITICAL)" /var/log/rockfall/app.log | head -20

# Monitor API response times
tail -f /var/log/nginx/access.log | grep -E "POST|GET" | awk '{print $NF}'

# Database connection issues
grep "connection" /var/log/mongodb/mongod.log
```

### Support Resources

#### Internal Documentation
- API Documentation: `/docs` endpoint
- Database Schema: `docs/database-schema.md`
- Configuration Guide: `docs/configuration.md`
- Deployment Guide: `docs/deployment.md`

#### External Resources
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [MongoDB Documentation](https://docs.mongodb.com/)
- [PyTorch Documentation](https://pytorch.org/docs/)

#### Getting Help
1. **Check Documentation**: Review relevant docs first
2. **Search Issues**: Look for similar problems in issue tracker
3. **Enable Debug Logging**: Add detailed logging to troubleshoot
4. **Create Minimal Reproduction**: Isolate the problem
5. **Contact Support**: Provide detailed error information

---

*This documentation is maintained by the development team and updated regularly. Last updated: September 2025*