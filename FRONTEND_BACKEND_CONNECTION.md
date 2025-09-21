# Frontend-Backend Connection Guide

## 🎉 SUCCESS! Your application is now running!

### 🔗 Connection Status
✅ **Backend API Server**: Running on http://localhost:8000  
✅ **Frontend Application**: Running on http://localhost:3000  
✅ **API Documentation**: Available at http://localhost:8000/docs  
✅ **CORS Configuration**: Properly configured for frontend communication  
✅ **Environment Variables**: Set up for both development environments  

### 🌐 Application URLs

| Service | URL | Description |
|---------|-----|-------------|
| **Frontend** | http://localhost:3000 | React TypeScript application |
| **Backend API** | http://localhost:8000 | FastAPI REST API |
| **API Docs** | http://localhost:8000/docs | Interactive Swagger documentation |
| **Health Check** | http://localhost:8000/health | API health status endpoint |

### 🔧 Configuration Details

#### Backend Configuration:
- **Framework**: FastAPI with Uvicorn
- **Port**: 8000
- **CORS Origins**: `["http://localhost:3000", "http://localhost:8080"]`
- **API Prefix**: `/api/v1`
- **Environment**: Development mode with auto-reload

#### Frontend Configuration:
- **Framework**: React + TypeScript + Vite
- **Port**: 3000
- **API Base URL**: `http://localhost:8000/api/v1`
- **Environment**: Development mode with hot reload

### 🚀 How to Start the Application

#### Option 1: Manual Start (Current Method)
```powershell
# Terminal 1 - Backend
cd backend
python main.py

# Terminal 2 - Frontend  
cd frontend
npm run dev
```

#### Option 2: Use Startup Scripts
```powershell
# PowerShell script
.\start-dev.ps1

# Or Bash script (if using WSL/Git Bash)
./start-dev.sh
```

### 🔍 Testing the Connection

The connection between frontend and backend has been verified:

1. **Backend Health Check**: ✅ Responding correctly
   ```json
   {
     "status": "healthy",
     "timestamp": "2025-09-21T10:42:46.838195",
     "service": "rockfall-prediction-api", 
     "version": "1.0.0"
   }
   ```

2. **Frontend-Backend Communication**: ✅ Configured
   - API service properly configured with axios
   - CORS middleware allows frontend requests
   - JWT authentication setup for protected endpoints

### 📡 API Endpoints Available

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/` | Root endpoint |
| GET | `/api/v1/status` | API status |
| POST | `/api/v1/auth/login` | User authentication |
| GET | `/api/v1/users` | User management |
| GET | `/api/v1/sites` | Site management |
| GET | `/api/v1/sensors` | Sensor data |
| GET | `/api/v1/predictions` | ML predictions |
| GET | `/api/v1/alerts` | Alert management |

### 🛠️ Development Workflow

1. **Both servers auto-reload** when you make changes
2. **Frontend hot reload** updates the browser automatically
3. **Backend auto-reload** restarts the API server on code changes
4. **API documentation** updates automatically at `/docs`

### 🔐 Authentication Flow

The application includes JWT-based authentication:
1. Frontend sends login credentials to `/api/v1/auth/login`
2. Backend returns JWT token
3. Frontend stores token in localStorage
4. Subsequent API calls include `Authorization: Bearer <token>` header
5. Invalid tokens redirect to login page

### 📊 Features Ready to Use

- **User Authentication & Authorization**
- **Site Management Dashboard**
- **Real-time Sensor Monitoring**
- **ML-powered Rockfall Predictions**
- **Alert System & Notifications**
- **Interactive Data Visualizations**

### 🐛 Troubleshooting

If you encounter issues:

1. **Backend not starting**:
   - Check if Python dependencies are installed: `pip install -r requirements.txt`
   - Verify Python version: `python --version` (should be 3.11+)

2. **Frontend not starting**:
   - Check Node.js dependencies: `npm install`
   - Verify Node.js version: `node --version` (should be 18+)

3. **CORS errors**:
   - Verify frontend URL in backend CORS configuration
   - Check browser console for specific error messages

4. **API connection issues**:
   - Verify backend is running on port 8000
   - Check environment variables in `.env.development` files

### 🎯 Next Steps

Your application is now perfectly connected and ready for development! You can:
- Start building new features
- Test the existing functionality
- Deploy to production when ready
- Add new API endpoints and frontend components

**Happy coding! 🚀**