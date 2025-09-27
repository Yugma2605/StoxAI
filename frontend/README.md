# TradingAgents Frontend

A modern React frontend for the TradingAgents multi-agent LLM financial trading framework.

## Features

- **Real-time Agent Monitoring**: Watch AI agents work in real-time with live status updates
- **Interactive Dashboard**: Modern, responsive interface with agent team visualization
- **Report Viewer**: Comprehensive analysis reports with markdown rendering
- **WebSocket Integration**: Live updates during analysis execution
- **Agent Status Tracking**: Visual progress indicators for each agent team
- **Responsive Design**: Works on desktop, tablet, and mobile devices

## Tech Stack

- **React 18**: Modern React with hooks and functional components
- **Tailwind CSS**: Utility-first CSS framework for styling
- **React Router**: Client-side routing
- **Axios**: HTTP client for API requests
- **React Markdown**: Markdown rendering for reports
- **Lucide React**: Beautiful icon library
- **Framer Motion**: Smooth animations and transitions
- **React Hot Toast**: Toast notifications

## Getting Started

### Prerequisites

- Node.js 16+ and npm
- Python 3.10+ (for backend)
- TradingAgents backend running on port 8000

### Installation

1. Install dependencies:
```bash
npm install
```

2. Install Tailwind CSS:
```bash
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
```

3. Start the development server:
```bash
npm start
```

The app will open at `http://localhost:3000`.

### Backend Setup

Make sure the TradingAgents backend is running:

```bash
cd backend
pip install -r requirements.txt
python main.py
```

## Project Structure

```
frontend/
├── public/
│   └── index.html
├── src/
│   ├── components/
│   │   ├── Dashboard.js          # Main dashboard
│   │   ├── AnalysisForm.js       # Analysis configuration
│   │   ├── AnalysisPage.js       # Analysis page
│   │   ├── AgentMonitor.js      # Real-time agent monitoring
│   │   └── ReportsViewer.js      # Report viewing interface
│   ├── App.js                    # Main app component
│   ├── index.js                  # React entry point
│   └── index.css                 # Global styles
├── package.json
├── tailwind.config.js
└── README.md
```

## Components

### Dashboard
- Welcome screen with feature overview
- Agent team descriptions
- Analysis workflow visualization
- Quick start button

### AnalysisForm
- Ticker symbol input
- Analysis date selection
- Analyst team selection
- Research depth configuration
- LLM provider settings

### AgentMonitor
- Real-time agent status updates
- WebSocket connection management
- Agent team progress tracking
- Individual agent details
- Live report generation

### ReportsViewer
- Comprehensive report display
- Markdown rendering
- Report download functionality
- Agent output summaries
- Analysis status tracking

## API Integration

The frontend communicates with the TradingAgents backend via:

- **REST API**: For starting analysis and fetching data
- **WebSocket**: For real-time updates during analysis
- **Proxy**: Development proxy to backend (configured in package.json)

## Styling

The app uses Tailwind CSS with custom components and utilities:

- **Custom Colors**: Primary, success, warning, danger color palettes
- **Component Classes**: Reusable button, card, and status styles
- **Responsive Design**: Mobile-first approach with breakpoints
- **Animations**: Smooth transitions and loading states

## Development

### Available Scripts

- `npm start`: Start development server
- `npm build`: Build for production
- `npm test`: Run tests
- `npm eject`: Eject from Create React App

### Code Style

- **Functional Components**: Use React hooks
- **PropTypes**: Type checking for props
- **ESLint**: Code linting and formatting
- **Prettier**: Code formatting

## Deployment

### Build for Production

```bash
npm run build
```

### Environment Variables

Create a `.env` file for environment-specific configuration:

```
REACT_APP_API_URL=http://localhost:8000
REACT_APP_WS_URL=ws://localhost:8000
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is part of the TradingAgents framework. See the main repository for license information.

