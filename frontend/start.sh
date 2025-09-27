#!/bin/bash

# TradingAgents Frontend Startup Script

echo "🚀 Starting TradingAgents Frontend..."

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 16+ and try again."
    exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed. Please install npm and try again."
    exit 1
fi

# Check if we're in the right directory
if [ ! -f "package.json" ]; then
    echo "❌ package.json not found. Please run this script from the frontend directory."
    exit 1
fi

# Install dependencies if node_modules doesn't exist
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
fi

# Install Tailwind CSS if not already installed
if [ ! -f "tailwind.config.js" ]; then
    echo "🎨 Setting up Tailwind CSS..."
    npm install -D tailwindcss postcss autoprefixer
    npx tailwindcss init -p
fi

# Start the development server
echo "🌟 Starting React development server..."
echo "📱 Frontend will be available at: http://localhost:3000"
echo "🔗 Backend should be running at: http://localhost:8000"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

npm start


