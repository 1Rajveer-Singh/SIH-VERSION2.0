#!/bin/bash
# Start Both Frontend and Backend Services

echo "🚀 Starting AI-Based Rockfall Prediction System..."

# Function to cleanup background processes
cleanup() {
    echo "🔄 Shutting down services..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit 0
}

# Trap SIGINT (Ctrl+C) to cleanup
trap cleanup SIGINT

# Start Backend
echo "📡 Starting Backend API Server..."
cd backend
python main.py &
BACKEND_PID=$!
echo "✅ Backend started (PID: $BACKEND_PID) - http://localhost:8000"

# Wait a moment for backend to start
sleep 3

# Start Frontend
echo "🎨 Starting Frontend Development Server..."
cd ../frontend
npm run dev &
FRONTEND_PID=$!
echo "✅ Frontend started (PID: $FRONTEND_PID) - http://localhost:3000"

echo ""
echo "🌟 System Ready!"
echo "📊 Frontend: http://localhost:3000"
echo "🔗 Backend API: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID