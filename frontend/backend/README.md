# TradingAgents Backend API

FastAPI backend for the TradingAgents multi-agent LLM financial trading framework.

## Features

- **REST API**: RESTful endpoints for analysis management
- **WebSocket Support**: Real-time updates during analysis execution
- **Session Management**: Track analysis sessions and progress
- **Agent Status Tracking**: Monitor individual agent progress
- **Report Generation**: Generate and serve analysis reports
- **CORS Support**: Cross-origin resource sharing for frontend integration

## Tech Stack

- **FastAPI**: Modern, fast web framework for building APIs
- **WebSockets**: Real-time bidirectional communication
- **Pydantic**: Data validation and serialization
- **TradingAgents**: Core multi-agent trading framework
- **Uvicorn**: ASGI server for production deployment

## Getting Started

### Prerequisites

- Python 3.10+
- TradingAgents framework installed
- OpenAI API key (or other LLM provider)
- FinnHub API key

### Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set environment variables:
```bash
export OPENAI_API_KEY=your_openai_api_key
export FINNHUB_API_KEY=your_finnhub_api_key
```

3. Start the server:
```bash
python main.py
```

The API will be available at `http://localhost:8000`.

## API Endpoints

### REST Endpoints

#### `GET /`
- **Description**: API health check
- **Response**: `{"message": "TradingAgents API is running"}`

#### `GET /health`
- **Description**: Detailed health status
- **Response**: `{"status": "healthy", "timestamp": "2024-01-01T00:00:00"}`

#### `POST /start-analysis`
- **Description**: Start a new trading analysis
- **Request Body**:
```json
{
  "ticker": "AAPL",
  "analysis_date": "2024-01-01",
  "analysts": ["market", "social", "news", "fundamentals"],
  "research_depth": 1,
  "llm_provider": "openai",
  "backend_url": "https://api.openai.com/v1",
  "shallow_thinker": "gpt-4o-mini",
  "deep_thinker": "o4-mini"
}
```
- **Response**: `{"session_id": "uuid", "status": "started"}`

#### `GET /analysis/{session_id}`
- **Description**: Get analysis progress
- **Response**: Analysis progress object with agent statuses

#### `GET /analysis/{session_id}/reports`
- **Description**: Get all analysis reports
- **Response**: Reports and agent outputs

#### `DELETE /analysis/{session_id}`
- **Description**: Delete analysis session
- **Response**: `{"message": "Session deleted"}`

### WebSocket Endpoints

#### `WS /ws/{session_id}`
- **Description**: Real-time updates for analysis session
- **Messages**:
  - `progress_update`: Agent status updates
  - `analysis_complete`: Analysis finished
  - `analysis_error`: Analysis failed

## Data Models

### AnalysisRequest
```python
{
  "ticker": str,
  "analysis_date": str,
  "analysts": List[str],
  "research_depth": int,
  "llm_provider": str,
  "backend_url": str,
  "shallow_thinker": str,
  "deep_thinker": str
}
```

### AgentStatus
```python
{
  "agent_name": str,
  "status": str,  # pending, in_progress, completed, error
  "team": str,
  "output": Optional[str],
  "timestamp": str
}
```

### AnalysisProgress
```python
{
  "session_id": str,
  "ticker": str,
  "analysis_date": str,
  "current_agent": Optional[str],
  "agent_statuses": Dict[str, AgentStatus],
  "reports": Dict[str, str],
  "final_decision": Optional[str],
  "is_complete": bool
}
```

## WebSocket Message Types

### Progress Update
```json
{
  "type": "progress_update",
  "session_id": "uuid",
  "progress": {
    "session_id": "uuid",
    "ticker": "AAPL",
    "agent_statuses": {...},
    "reports": {...}
  }
}
```

### Analysis Complete
```json
{
  "type": "analysis_complete",
  "session_id": "uuid",
  "final_decision": "BUY/HOLD/SELL recommendation"
}
```

### Analysis Error
```json
{
  "type": "analysis_error",
  "session_id": "uuid",
  "error": "Error message"
}
```

## Configuration

### Environment Variables

- `OPENAI_API_KEY`: OpenAI API key for LLM access
- `FINNHUB_API_KEY`: FinnHub API key for financial data
- `TRADINGAGENTS_RESULTS_DIR`: Directory for analysis results

### TradingAgents Configuration

The backend uses the TradingAgents framework with configurable parameters:

- **LLM Providers**: OpenAI, Anthropic, Google
- **Models**: Configurable quick and deep thinking models
- **Research Depth**: Number of debate rounds (1-3)
- **Online Tools**: Enable/disable real-time data fetching

## Error Handling

The API includes comprehensive error handling:

- **HTTP Errors**: Proper status codes and error messages
- **WebSocket Errors**: Connection management and reconnection
- **Analysis Errors**: Graceful handling of analysis failures
- **Validation Errors**: Input validation with detailed messages

## Development

### Running in Development

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### API Documentation

FastAPI automatically generates interactive API documentation:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## Production Deployment

### Using Uvicorn

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Using Gunicorn

```bash
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
```

### Docker Deployment

```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Monitoring

### Health Checks

- **GET /health**: Basic health status
- **WebSocket Status**: Connection monitoring
- **Analysis Status**: Session tracking

### Logging

The API includes structured logging for:

- **Request/Response**: HTTP request logging
- **WebSocket Events**: Connection and message logging
- **Analysis Progress**: Agent status updates
- **Errors**: Detailed error logging

## Security

### CORS Configuration

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### API Key Management

- Environment variable storage
- Secure API key handling
- No key exposure in logs

## Performance

### Optimization Features

- **Async Processing**: Non-blocking analysis execution
- **WebSocket Efficiency**: Minimal message overhead
- **Session Management**: Efficient memory usage
- **Connection Pooling**: Database connection optimization

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is part of the TradingAgents framework. See the main repository for license information.


