from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import asyncio
import json
import sys
import os
from datetime import datetime
import uuid
from dotenv import load_dotenv

# Load environment variables from .env file in project root
env_path = os.path.join(os.path.dirname(__file__), '..', '..', '.env')
load_dotenv(env_path)

# Add the parent directory to the path to import tradingagents
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG

app = FastAPI(title="TradingAgents API", version="1.0.0")
# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                # Remove dead connections
                self.active_connections.remove(connection)

manager = ConnectionManager()

# Pydantic models
class AnalysisRequest(BaseModel):
    ticker: str
    analysis_date: str
    analysts: List[str] = ["market", "social", "news", "fundamentals"]
    research_depth: int = 1
    llm_provider: str = "google"
    backend_url: str = "https://generativelanguage.googleapis.com/v1"
    shallow_thinker: str = "gemini-2.0-flash"
    deep_thinker: str = "gemini-2.0-flash"

class AgentStatus(BaseModel):
    agent_name: str
    status: str  # pending, in_progress, completed, error
    team: str
    output: Optional[str] = None
    timestamp: str

class AnalysisProgress(BaseModel):
    session_id: str
    ticker: str
    analysis_date: str
    current_agent: Optional[str]
    agent_statuses: Dict[str, AgentStatus]
    reports: Dict[str, str]
    final_decision: Optional[str] = None
    is_complete: bool = False

# Global storage for analysis sessions
analysis_sessions: Dict[str, AnalysisProgress] = {}

@app.get("/")
async def root():
    return {"message": "TradingAgents API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.post("/start-analysis")
async def start_analysis(request: AnalysisRequest):
    """Start a new trading analysis session"""
    print("Starting analysiss", request)
    session_id = str(uuid.uuid4())
    
    # Create custom config
    config = DEFAULT_CONFIG.copy()
    config["max_debate_rounds"] = request.research_depth
    config["max_risk_discuss_rounds"] = request.research_depth
    config["quick_think_llm"] = request.shallow_thinker
    config["deep_think_llm"] = request.deep_thinker
    config["backend_url"] = request.backend_url
    config["llm_provider"] = request.llm_provider.lower()
    config["online_tools"] = True
    
    # Initialize the trading agents graph
    try:
        graph = TradingAgentsGraph(
            selected_analysts=request.analysts,
            config=config,
            debug=True
        )
        
        # Create initial progress tracking
        progress = AnalysisProgress(
            session_id=session_id,
            ticker=request.ticker,
            analysis_date=request.analysis_date,
            current_agent=None,
            agent_statuses={},
            reports={},
            is_complete=False
        )
        
        # Initialize agent statuses
        teams = {
            "Analyst Team": ["Market Analyst", "Social Analyst", "News Analyst", "Fundamentals Analyst"],
            "Research Team": ["Bull Researcher", "Bear Researcher", "Research Manager"],
            "Trading Team": ["Trader"],
            "Risk Management": ["Risky Analyst", "Neutral Analyst", "Safe Analyst"],
            "Portfolio Management": ["Portfolio Manager"]
        }
        
        for team, agents in teams.items():
            for agent in agents:
                progress.agent_statuses[agent] = AgentStatus(
                    agent_name=agent,
                    status="pending",
                    team=team,
                    timestamp=datetime.now().isoformat()
                )
        
        analysis_sessions[session_id] = progress
        
        # Start analysis in background
        asyncio.create_task(run_analysis_async(session_id, graph, request))
        
        return {"session_id": session_id, "status": "started"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start analysis: {str(e)}")

async def run_analysis_async(session_id: str, graph: TradingAgentsGraph, request: AnalysisRequest):
    """Run the analysis asynchronously and update progress"""
    try:
        progress = analysis_sessions[session_id]
        
        # Initialize state
        init_agent_state = graph.propagator.create_initial_state(
            request.ticker, request.analysis_date
        )
        args = graph.propagator.get_graph_args()
        
        # Stream the analysis
        for chunk in graph.graph.stream(init_agent_state, **args):
            print(f"Analysis chunk: {chunk}")  # Debug output
            if len(chunk.get("messages", [])) > 0:
                # Update progress based on chunk content
                await update_progress_from_chunk(session_id, chunk)
                
        # Mark as complete
        progress.is_complete = True
        await manager.broadcast(json.dumps({
            "type": "analysis_complete",
            "session_id": session_id,
            "final_decision": progress.final_decision
        }))
        
    except Exception as e:
        # Handle errors
        progress = analysis_sessions.get(session_id)
        if progress:
            progress.is_complete = True
            await manager.broadcast(json.dumps({
                "type": "analysis_error",
                "session_id": session_id,
                "error": str(e)
            }))

async def update_progress_from_chunk(session_id: str, chunk: Dict[str, Any]):
    """Update progress based on analysis chunk"""
    progress = analysis_sessions.get(session_id)
    if not progress:
        return
    
    print(f"Updating progress for session {session_id}: {chunk}")  # Debug output
    
    # Update reports
    report_mappings = {
        "market_report": "Market Analysis",
        "sentiment_report": "Social Sentiment", 
        "news_report": "News Analysis",
        "fundamentals_report": "Fundamentals Analysis",
        "investment_plan": "Research Team Decision",
        "trader_investment_plan": "Trading Plan",
        "final_trade_decision": "Final Decision"
    }
    
    for key, title in report_mappings.items():
        if key in chunk and chunk[key]:
            progress.reports[title] = chunk[key]
            progress.agent_statuses[key.replace("_report", "").replace("_", " ").title()].status = "completed"
    
    # Update agent statuses based on chunk content
    if "market_report" in chunk and chunk["market_report"]:
        progress.agent_statuses["Market Analyst"].status = "completed"
        progress.agent_statuses["Market Analyst"].output = chunk["market_report"]
    
    if "sentiment_report" in chunk and chunk["sentiment_report"]:
        progress.agent_statuses["Social Analyst"].status = "completed"
        progress.agent_statuses["Social Analyst"].output = chunk["sentiment_report"]
    
    if "news_report" in chunk and chunk["news_report"]:
        progress.agent_statuses["News Analyst"].status = "completed"
        progress.agent_statuses["News Analyst"].output = chunk["news_report"]
    
    if "fundamentals_report" in chunk and chunk["fundamentals_report"]:
        progress.agent_statuses["Fundamentals Analyst"].status = "completed"
        progress.agent_statuses["Fundamentals Analyst"].output = chunk["fundamentals_report"]
    
    # Handle research team
    if "investment_debate_state" in chunk and chunk["investment_debate_state"]:
        debate_state = chunk["investment_debate_state"]
        if "bull_history" in debate_state:
            progress.agent_statuses["Bull Researcher"].status = "completed"
            progress.agent_statuses["Bull Researcher"].output = debate_state["bull_history"]
        
        if "bear_history" in debate_state:
            progress.agent_statuses["Bear Researcher"].status = "completed"
            progress.agent_statuses["Bear Researcher"].output = debate_state["bear_history"]
        
        if "judge_decision" in debate_state:
            progress.agent_statuses["Research Manager"].status = "completed"
            progress.agent_statuses["Research Manager"].output = debate_state["judge_decision"]
    
    # Handle trader
    if "trader_investment_plan" in chunk and chunk["trader_investment_plan"]:
        progress.agent_statuses["Trader"].status = "completed"
        progress.agent_statuses["Trader"].output = chunk["trader_investment_plan"]
    
    # Handle risk management
    if "risk_debate_state" in chunk and chunk["risk_debate_state"]:
        risk_state = chunk["risk_debate_state"]
        if "current_risky_response" in risk_state:
            progress.agent_statuses["Risky Analyst"].status = "completed"
            progress.agent_statuses["Risky Analyst"].output = risk_state["current_risky_response"]
        
        if "current_safe_response" in risk_state:
            progress.agent_statuses["Safe Analyst"].status = "completed"
            progress.agent_statuses["Safe Analyst"].output = risk_state["current_safe_response"]
        
        if "current_neutral_response" in risk_state:
            progress.agent_statuses["Neutral Analyst"].status = "completed"
            progress.agent_statuses["Neutral Analyst"].output = risk_state["current_neutral_response"]
        
        if "judge_decision" in risk_state:
            progress.agent_statuses["Portfolio Manager"].status = "completed"
            progress.agent_statuses["Portfolio Manager"].output = risk_state["judge_decision"]
            progress.final_decision = risk_state["judge_decision"]
    
    # Broadcast update
    await manager.broadcast(json.dumps({
        "type": "progress_update",
        "session_id": session_id,
        "progress": progress.dict()
    }))

@app.get("/analysis/{session_id}")
async def get_analysis_progress(session_id: str):
    """Get current analysis progress"""
    if session_id not in analysis_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return analysis_sessions[session_id]

@app.get("/analysis/{session_id}/reports")
async def get_analysis_reports(session_id: str):
    """Get all reports from analysis"""
    if session_id not in analysis_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    progress = analysis_sessions[session_id]
    return {
        "session_id": session_id,
        "ticker": progress.ticker,
        "analysis_date": progress.analysis_date,
        "reports": progress.reports,
        "agent_outputs": {agent: status.output for agent, status in progress.agent_statuses.items() if status.output},
        "is_complete": progress.is_complete
    }

@app.delete("/analysis/{session_id}")
async def delete_analysis(session_id: str):
    """Delete analysis session"""
    if session_id in analysis_sessions:
        del analysis_sessions[session_id]
        return {"message": "Session deleted"}
    else:
        raise HTTPException(status_code=404, detail="Session not found")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
