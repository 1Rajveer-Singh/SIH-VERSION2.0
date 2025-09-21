# PowerShell script to start both Frontend and Backend services

Write-Host "🚀 Starting AI-Based Rockfall Prediction System..." -ForegroundColor Green

# Start Backend
Write-Host "📡 Starting Backend API Server..." -ForegroundColor Yellow
cd backend
Start-Process -FilePath "python" -ArgumentList "main.py" -WindowStyle Normal
Write-Host "✅ Backend started - http://localhost:8000" -ForegroundColor Green

# Wait a moment for backend to start
Start-Sleep -Seconds 3

# Start Frontend
Write-Host "🎨 Starting Frontend Development Server..." -ForegroundColor Yellow
cd ..\frontend
Start-Process -FilePath "npm" -ArgumentList "run", "dev" -WindowStyle Normal
Write-Host "✅ Frontend started - http://localhost:3000" -ForegroundColor Green

Write-Host ""
Write-Host "🌟 System Ready!" -ForegroundColor Magenta
Write-Host "📊 Frontend: http://localhost:3000" -ForegroundColor Cyan
Write-Host "🔗 Backend API: http://localhost:8000" -ForegroundColor Cyan
Write-Host "📚 API Docs: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "Use Ctrl+C in each terminal window to stop services" -ForegroundColor Yellow