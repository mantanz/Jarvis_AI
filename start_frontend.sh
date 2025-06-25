#!/bin/bash

# Start the React frontend development server
echo "⚛️  Starting React Frontend Development Server..."

# Check if node_modules exists, install if not
if [ ! -d "node_modules" ]; then
    echo "📦 Installing Node.js dependencies..."
    npm install
fi

# Set environment variable for API URL
export REACT_APP_API_URL=http://localhost:8000

# Start the React development server
echo "🌐 Starting React development server on http://localhost:3000"
echo "🔄 The app will automatically reload when you save changes"
npm start 