@echo off
echo 🚀 Starting TradingAgents Backend...

REM Check if .env file exists
if not exist ".env" (
    echo ⚠️  .env file not found. Creating from template...
    copy env.example .env
    echo    Please edit .env file with your API keys
    echo.
    pause
    exit /b 1
)

echo ✅ Loading environment variables from .env file

REM Install dependencies if requirements.txt exists
if exist "requirements.txt" (
    echo 📦 Installing Python dependencies...
    pip install -r requirements.txt
)

REM Create results directory if it doesn't exist
if not exist "results" mkdir results

REM Start the server
echo 🌟 Starting FastAPI server...
echo 🔗 API will be available at: http://localhost:8000
echo 📚 API Documentation: http://localhost:8000/docs
echo 🔌 WebSocket endpoint: ws://localhost:8000/ws/{session_id}
echo.
echo Press Ctrl+C to stop the server
echo.

python main.py




