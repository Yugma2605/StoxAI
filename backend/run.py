#!/usr/bin/env python3
"""
TradingAgents Backend Server
Run the FastAPI server with proper configuration
"""

import os
import sys
import uvicorn
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add the parent directory to the path to import tradingagents
current_dir = Path(__file__).parent
parent_dir = current_dir.parent.parent
sys.path.append(str(parent_dir))

def main():
    """Run the TradingAgents backend server"""
    
    # Set default environment variables if not set
    os.environ.setdefault('GOOGLE_API_KEY', '')
    os.environ.setdefault('FINNHUB_API_KEY', '')
    os.environ.setdefault('TRADINGAGENTS_RESULTS_DIR', './results')
    
    # Configuration
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 8000))
    workers = int(os.getenv('WORKERS', 1))
    reload = os.getenv('RELOAD', 'false').lower() == 'true'
    
    print(f"Starting TradingAgents Backend Server...")
    print(f"Host: {host}")
    print(f"Port: {port}")
    print(f"Workers: {workers}")
    print(f"Reload: {reload}")
    print(f"API Documentation: http://{host}:{port}/docs")
    print(f"WebSocket Endpoint: ws://{host}:{port}/ws/{{session_id}}")
    
    # Run the server
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        workers=workers if not reload else 1,
        reload=reload,
        log_level="info",
        access_log=True
    )

if __name__ == "__main__":
    main()
