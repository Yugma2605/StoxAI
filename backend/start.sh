#!/bin/bash

# TradingAgents Backend Startup Script

echo "🚀 Starting TradingAgents Backend..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.10+ and try again."
    exit 1
fi

# Check if we're in the right directory
if [ ! -f "main.py" ]; then
    echo "❌ main.py not found. Please run this script from the backend directory."
    exit 1
fi

# Check for .env file
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Creating from template..."
    cp env.example .env
    echo "   Please edit .env file with your API keys"
    echo ""
fi

# Load environment variables from .env file
if [ -f ".env" ]; then
    echo "✅ Loading environment variables from .env file"
    export $(cat .env | grep -v '^#' | xargs)
else
    echo "❌ .env file not found"
    exit 1
fi

# Install dependencies if requirements.txt exists
if [ -f "requirements.txt" ]; then
    echo "📦 Installing Python dependencies..."
    pip install -r requirements.txt
fi

# Create results directory if it doesn't exist
mkdir -p results

# Start the server
echo "🌟 Starting FastAPI server..."
echo "🔗 API will be available at: http://localhost:8000"
echo "📚 API Documentation: http://localhost:8000/docs"
echo "🔌 WebSocket endpoint: ws://localhost:8000/ws/{session_id}"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python main.py
