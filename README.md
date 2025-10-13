# TradingAgents Frontend

A modern web frontend for the TradingAgents multi-agent LLM financial trading framework. This frontend provides a real-time interface to monitor AI agents as they analyze financial markets and make trading decisions.

Demo Link - https://drive.google.com/file/d/1LgrRVt_63HtXJfonj01B1airvuPkHTBT/view?usp=sharing

## 🌟 Features

- **Real-time Agent Monitoring**: Watch AI agents work in real-time with live status updates
- **Interactive Dashboard**: Modern, responsive interface with agent team visualization  
- **Report Viewer**: Comprehensive analysis reports with markdown rendering
- **WebSocket Integration**: Live updates during analysis execution
- **Agent Status Tracking**: Visual progress indicators for each agent team
- **Responsive Design**: Works on desktop, tablet, and mobile devices

## 🏗️ Architecture

The frontend consists of two main components:

### Backend API (FastAPI)
- **REST API**: Endpoints for analysis management and data retrieval
- **WebSocket Support**: Real-time updates during analysis execution
- **Session Management**: Track analysis sessions and progress
- **Agent Status Tracking**: Monitor individual agent progress
- **Report Generation**: Generate and serve analysis reports

### Frontend (React)
- **React 18**: Modern React with hooks and functional components
- **Tailwind CSS**: Utility-first CSS framework for styling
- **React Router**: Client-side routing
- **WebSocket Integration**: Real-time communication with backend
- **Responsive Design**: Mobile-first approach

## 🚀 Quick Start

### Prerequisites

- Node.js 16+ and npm
- Python 3.10+ (for backend)
- Google API key (for Gemini models)
- FinnHub API key

### 1. Clone and Setup

```bash
# Clone the repository
git clone <repository-url>
cd TradingAgents

# Install TradingAgents dependencies
pip install -r requirements.txt
```

### 2. Start the Backend

```bash
# Navigate to backend directory
cd frontend/backend

# Set environment variables
export GOOGLE_API_KEY=your_google_api_key
export FINNHUB_API_KEY=your_finnhub_api_key

# Start the backend server
python main.py
```

The backend will be available at `http://localhost:8000`

### 3. Start the Frontend

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start the development server
npm start
```

The frontend will be available at `http://localhost:3000`

## 📁 Project Structure

```
frontend/
├── backend/                 # FastAPI backend
│   ├── main.py             # Main FastAPI application
│   ├── requirements.txt    # Python dependencies
│   ├── run.py             # Server runner script
│   └── start.sh           # Backend startup script
├── src/                    # React frontend
│   ├── components/        # React components
│   │   ├── Dashboard.js   # Main dashboard
│   │   ├── AnalysisForm.js # Analysis configuration
│   │   ├── AgentMonitor.js # Real-time monitoring
│   │   └── ReportsViewer.js # Report viewing
│   ├── App.js             # Main app component
│   └── index.js           # React entry point
├── public/                 # Static assets
├── package.json           # Node.js dependencies
├── tailwind.config.js     # Tailwind configuration
└── start.sh               # Frontend startup script
```

## 🎯 Usage

### 1. Start Analysis

1. Navigate to the dashboard
2. Click "Start Analysis" 
3. Configure your analysis parameters:
   - **Ticker Symbol**: Stock symbol to analyze (e.g., AAPL, MSFT)
   - **Analysis Date**: Date for the analysis
   - **Analysts**: Select which analyst teams to include
   - **Research Depth**: Number of debate rounds (1-3)
   - **LLM Configuration**: Choose models and providers

### 2. Monitor Progress

1. Watch agents work in real-time
2. See progress updates for each agent team:
   - **Analyst Team**: Market, Social, News, Fundamentals
   - **Research Team**: Bull vs Bear debate
   - **Trading Team**: Strategic planning
   - **Risk Management**: Multi-perspective assessment
   - **Portfolio Management**: Final decision

### 3. View Reports

1. Access comprehensive analysis reports
2. Download reports in markdown format
3. View individual agent outputs
4. Track analysis status and completion

## 🔧 Configuration

### Backend Configuration

Environment variables for the backend:

```bash
# Required
GOOGLE_API_KEY=your_google_api_key
FINNHUB_API_KEY=your_finnhub_api_key

# Optional
HOST=0.0.0.0
PORT=8000
WORKERS=1
RELOAD=false
TRADINGAGENTS_RESULTS_DIR=./results
```

### Frontend Configuration

Create a `.env` file in the frontend directory:

```bash
REACT_APP_API_URL=http://localhost:8000
REACT_APP_WS_URL=ws://localhost:8000
```

## 🎨 Customization

### Styling

The frontend uses Tailwind CSS with custom components:

- **Custom Colors**: Primary, success, warning, danger palettes
- **Component Classes**: Reusable button, card, and status styles
- **Responsive Design**: Mobile-first approach
- **Animations**: Smooth transitions and loading states

### Adding New Features

1. **New Components**: Add to `src/components/`
2. **API Integration**: Extend backend endpoints
3. **Styling**: Use Tailwind classes and custom CSS
4. **State Management**: Use React hooks and context

## 🚀 Deployment

### Development

```bash
# Backend
cd frontend/backend
python main.py

# Frontend  
cd frontend
npm start
```

### Production

```bash
# Build frontend
cd frontend
npm run build

# Serve with nginx or similar
# Backend can be deployed with gunicorn/uvicorn
```

### Docker

```dockerfile
# Backend Dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["python", "main.py"]

# Frontend Dockerfile  
FROM node:16-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "start"]
```

## 🔍 API Documentation

### REST Endpoints

- `GET /` - API health check
- `GET /health` - Detailed health status
- `POST /start-analysis` - Start new analysis
- `GET /analysis/{session_id}` - Get analysis progress
- `GET /analysis/{session_id}/reports` - Get analysis reports
- `DELETE /analysis/{session_id}` - Delete analysis session

### WebSocket

- `WS /ws/{session_id}` - Real-time updates

Full API documentation available at `http://localhost:8000/docs`

## 🧪 Testing

### Backend Testing

```bash
cd frontend/backend
python -m pytest tests/
```

### Frontend Testing

```bash
cd frontend
npm test
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request


## 🆘 Support

- **Documentation**: Check the API docs at `/docs`
- **Issues**: Report bugs and feature requests
- **Community**: Join the TradingAgents community

## 🔗 Links

- **API Documentation**: `http://localhost:8000/docs`
- **Frontend**: `http://localhost:3000`
- **Backend**: `http://localhost:8000`
