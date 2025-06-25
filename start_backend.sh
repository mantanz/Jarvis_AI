#!/bin/bash

# Start the FastAPI backend server
echo "🚀 Starting FastAPI Backend Server..."

# Check if virtual environment exists, create if not
if [ ! -d "rag_env" ]; then
    echo "📦 Creating virtual environment..."
    python -m venv rag_env
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source rag_env/bin/activate

# Install/update dependencies
echo "📥 Installing Python dependencies..."
pip install -r requirements.txt

# Start the FastAPI server
echo "🌐 Starting FastAPI server on http://localhost:8000"
echo "📖 API Documentation will be available at http://localhost:8000/docs"
uvicorn main:app --host 0.0.0.0 --port 8000 --reload 