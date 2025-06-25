#!/bin/bash

# Start both backend and frontend servers
echo "🚀 Starting Full RAG Application Stack..."

# Make scripts executable
chmod +x start_backend.sh
chmod +x start_frontend.sh

# Function to handle cleanup
cleanup() {
    echo ""
    echo "🛑 Shutting down servers..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit 0
}

# Set up signal handlers
trap cleanup INT TERM

echo "🔧 Starting backend server..."
./start_backend.sh &
BACKEND_PID=$!

# Wait a moment for backend to start
echo "⏳ Waiting for backend to initialize..."
sleep 5

echo "⚛️  Starting frontend server..."
./start_frontend.sh &
FRONTEND_PID=$!

echo ""
echo "✅ Full RAG Application is starting up!"
echo "📖 Backend API: http://localhost:8000"
echo "📖 API Docs: http://localhost:8000/docs"
echo "🌐 Frontend App: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop both servers"

# Wait for processes
wait $BACKEND_PID $FRONTEND_PID 