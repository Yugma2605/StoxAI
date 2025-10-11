from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, BackgroundTasks
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
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
print(sys.path)
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG
from trading.tradingService import trading_service, TradeRequest

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
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        dead: List[WebSocket] = []
        for connection in list(self.active_connections):  # iterate over a snapshot
            try:
                await connection.send_text(message)
            except Exception:
                dead.append(connection)
        # prune dead connections after iteration
        for d in dead:
            self.disconnect(d)

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

async def cleanup_old_sessions():
    """Clean up old analysis sessions to prevent resource conflicts"""
    try:
        # Remove completed sessions older than 1 hour
        current_time = datetime.now()
        sessions_to_remove = []
        
        for session_id, session in analysis_sessions.items():
            if session.is_complete:
                # Check if session is older than 1 hour
                session_time = datetime.fromisoformat(session.agent_statuses.get('Market Analyst', {}).get('timestamp', current_time.isoformat()))
                if (current_time - session_time).total_seconds() > 3600:  # 1 hour
                    sessions_to_remove.append(session_id)
        
        for session_id in sessions_to_remove:
            del analysis_sessions[session_id]
            print(f"Cleaned up old session: {session_id}")
            
    except Exception as e:
        print(f"Error during session cleanup: {e}")
        # Continue execution even if cleanup fails

@app.get("/")
async def root():
    return {"message": "TradingAgents API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """Handles WebSocket connections for real-time updates."""
    print(f"🔌 WebSocket connection attempt for session: {session_id}")
    await manager.connect(websocket)
    print(f"✅ WebSocket connected for session: {session_id}")

    try:
        while True:
            msg = await websocket.receive_text()  # optional ping/pong
            print(f"🔁 WebSocket message received: {msg}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"⚠️ WebSocket error: {e}")
        manager.disconnect(websocket)

@app.post("/start-analysis")
async def start_analysis(request: AnalysisRequest, background_tasks: BackgroundTasks):
    """Start a new trading analysis session"""
    session_id = str(uuid.uuid4())
    print(f"🟢 Created session {session_id} for {request.ticker}")
    # Create placeholder progress so /analysis/:id works immediately
    progress = AnalysisProgress(
        session_id=session_id,
        ticker=request.ticker,
        analysis_date=request.analysis_date,
        current_agent=None,
        agent_statuses={},
        reports={},
        is_complete=False
    )
    analysis_sessions[session_id] = progress
    print(f"🟢 Created session {session_id} for {request.ticker} - ", analysis_sessions.keys())

    # ✅ Return response immediately
    response = {"session_id": session_id, "status": "started"}
    asyncio.create_task(initialize_analysis(request, session_id))
    return response


async def initialize_analysis(request: AnalysisRequest, session_id: str):
    """Heavy initialization work runs in background"""
    try:
        await cleanup_old_sessions()
        config = DEFAULT_CONFIG.copy()
        config["max_debate_rounds"] = request.research_depth
        config["max_risk_discuss_rounds"] = request.research_depth
        config["quick_think_llm"] = request.shallow_thinker
        config["deep_think_llm"] = request.deep_thinker
        config["backend_url"] = request.backend_url
        config["llm_provider"] = request.llm_provider.lower()
        config["online_tools"] = True

        print(f"Initializing TradingAgentsGraph for session {session_id}")
        graph = TradingAgentsGraph(
            selected_analysts=request.analysts,
            config=config,
            debug=True
        )

        # Initialize team statuses
        teams = {
            "Analyst Team": ["Market Analyst", "Social Analyst", "News Analyst", "Fundamentals Analyst"],
            "Research Team": ["Bull Researcher", "Bear Researcher", "Research Manager"],
            "Trading Team": ["Trader"],
            "Risk Management": ["Risky Analyst", "Neutral Analyst", "Safe Analyst"],
            "Portfolio Management": ["Portfolio Manager"]
        }

        for team, agents in teams.items():
            for agent in agents:
                initial_status = "in_progress" if team == "Analyst Team" else "pending"
                analysis_sessions[session_id].agent_statuses[agent] = AgentStatus(
                    agent_name=agent,
                    status=initial_status,
                    team=team,
                    timestamp=datetime.now().isoformat()
                )

        # Broadcast initial progress
        await manager.broadcast(json.dumps({
            "type": "progress_update",
            "session_id": session_id,
            "progress": analysis_sessions[session_id].model_dump()
        }))

        # Start async processing
        asyncio.create_task(run_analysis_async(session_id, graph, request))

    except Exception as e:
        print(f"❌ Error during initialization for session {session_id}: {e}")

async def run_analysis_async(session_id: str, graph: TradingAgentsGraph, request: AnalysisRequest):
    try:
        print(f"Starting analysis for session {session_id}")
        progress = analysis_sessions[session_id]

        init_agent_state = graph.propagator.create_initial_state(
            request.ticker, request.analysis_date
        )
        args = graph.propagator.get_graph_args()

        await manager.broadcast(json.dumps({
            "type": "analysis_started",
            "session_id": session_id,
            "message": "Analysis started - initializing agents..."
        }))

        print(f"Starting graph stream for session {session_id}")

        loop = asyncio.get_running_loop()
        queue: asyncio.Queue = asyncio.Queue()

        def stream_chunks_to_queue():
            """Blocking: run in thread, pushing chunks to async queue."""
            try:
                for chunk in graph.graph.stream(init_agent_state, **args):
                    asyncio.run_coroutine_threadsafe(queue.put(chunk), loop)
            finally:
                asyncio.run_coroutine_threadsafe(queue.put(None), loop)

        # ✅ Launch producer thread
        asyncio.create_task(asyncio.to_thread(stream_chunks_to_queue))

        # ✅ Consumer loop
        while True:
            chunk = await queue.get()
            if chunk is None:
                break
            try:
                await update_progress_from_chunk(session_id, chunk)
            except Exception as inner_e:
                print(f"Error processing chunk in session {session_id}: {inner_e}")
                await manager.broadcast(json.dumps({
                    "type": "progress_update_error",
                    "session_id": session_id,
                    "error": str(inner_e)
                }))

        progress.is_complete = True
        await manager.broadcast(json.dumps({
            "type": "analysis_complete",
            "session_id": session_id,
            "final_decision": progress.final_decision
        }))

    except Exception as e:
        print(f"Error in analysis for session {session_id}: {e}")
        import traceback
        print(traceback.format_exc())


async def update_progress_from_chunk(session_id: str, chunk: Dict[str, Any]):
    """Update progress based on analysis chunk"""
    try:
        progress = analysis_sessions.get(session_id)
        if not progress:
            print(f"No progress found for session {session_id}")
            return

        # Track which agents are currently active based on chunk content
        current_agent = None
        agent_activity = []
        
        print(f"Processing chunk for session {session_id}: {list(chunk.keys())}")

        # Map report keys -> (report title, agent name to mark complete)
        report_mappings = {
            "market_report": ("Market Analysis", "Market Analyst"),
            "sentiment_report": ("Social Sentiment", "Social Analyst"),
            "news_report": ("News Analysis", "News Analyst"),
            "fundamentals_report": ("Fundamentals Analysis", "Fundamentals Analyst"),
            "investment_plan": ("Research Team Decision", "Research Manager"),
            "trader_investment_plan": ("Trading Plan", "Trader"),
            "final_trade_decision": ("Final Decision", "Portfolio Manager"),
        }

        # Handle high-level reports and mark agents as completed
        for key, (title, agent_name) in report_mappings.items():
            if key in chunk and chunk[key]:
                progress.reports[title] = chunk[key]
                if agent_name in progress.agent_statuses:
                    progress.agent_statuses[agent_name].status = "completed"
                    progress.agent_statuses[agent_name].output = chunk[key]
                    progress.agent_statuses[agent_name].timestamp = datetime.now().isoformat()
                    agent_activity.append(f"{agent_name} completed: {title}")

        # Analyst team granular updates (kept for backwards compatibility if the graph sends these fields)
        if chunk.get("market_report"):
            progress.agent_statuses["Market Analyst"].status = "completed"
            progress.agent_statuses["Market Analyst"].output = chunk["market_report"]
            progress.agent_statuses["Market Analyst"].timestamp = datetime.now().isoformat()
            current_agent = "Market Analyst"

        if chunk.get("sentiment_report"):
            progress.agent_statuses["Social Analyst"].status = "completed"
            progress.agent_statuses["Social Analyst"].output = chunk["sentiment_report"]
            progress.agent_statuses["Social Analyst"].timestamp = datetime.now().isoformat()
            current_agent = "Social Analyst"

        if chunk.get("news_report"):
            progress.agent_statuses["News Analyst"].status = "completed"
            progress.agent_statuses["News Analyst"].output = chunk["news_report"]
            progress.agent_statuses["News Analyst"].timestamp = datetime.now().isoformat()
            current_agent = "News Analyst"

        if chunk.get("fundamentals_report"):
            progress.agent_statuses["Fundamentals Analyst"].status = "completed"
            progress.agent_statuses["Fundamentals Analyst"].output = chunk["fundamentals_report"]
            progress.agent_statuses["Fundamentals Analyst"].timestamp = datetime.now().isoformat()
            current_agent = "Fundamentals Analyst"

        # Research team
        if chunk.get("investment_debate_state"):
            debate_state = chunk["investment_debate_state"]
            if debate_state.get("bull_history"):
                progress.agent_statuses["Bull Researcher"].status = "completed"
                progress.agent_statuses["Bull Researcher"].output = debate_state["bull_history"]
                progress.agent_statuses["Bull Researcher"].timestamp = datetime.now().isoformat()
                current_agent = "Bull Researcher"
            if debate_state.get("bear_history"):
                progress.agent_statuses["Bear Researcher"].status = "completed"
                progress.agent_statuses["Bear Researcher"].output = debate_state["bear_history"]
                progress.agent_statuses["Bear Researcher"].timestamp = datetime.now().isoformat()
                current_agent = "Bear Researcher"
            if debate_state.get("judge_decision"):
                progress.agent_statuses["Research Manager"].status = "completed"
                progress.agent_statuses["Research Manager"].output = debate_state["judge_decision"]
                progress.agent_statuses["Research Manager"].timestamp = datetime.now().isoformat()
                current_agent = "Research Manager"

        # Trader
        if chunk.get("trader_investment_plan"):
            progress.agent_statuses["Trader"].status = "completed"
            progress.agent_statuses["Trader"].output = chunk["trader_investment_plan"]
            progress.agent_statuses["Trader"].timestamp = datetime.now().isoformat()
            current_agent = "Trader"

        # Risk management
        if chunk.get("risk_debate_state"):
            risk_state = chunk["risk_debate_state"]
            if risk_state.get("current_risky_response"):
                progress.agent_statuses["Risky Analyst"].status = "completed"
                progress.agent_statuses["Risky Analyst"].output = risk_state["current_risky_response"]
                progress.agent_statuses["Risky Analyst"].timestamp = datetime.now().isoformat()
                current_agent = "Risky Analyst"
            if risk_state.get("current_safe_response"):
                progress.agent_statuses["Safe Analyst"].status = "completed"
                progress.agent_statuses["Safe Analyst"].output = risk_state["current_safe_response"]
                progress.agent_statuses["Safe Analyst"].timestamp = datetime.now().isoformat()
                current_agent = "Safe Analyst"
            if risk_state.get("current_neutral_response"):
                progress.agent_statuses["Neutral Analyst"].status = "completed"
                progress.agent_statuses["Neutral Analyst"].output = risk_state["current_neutral_response"]
                progress.agent_statuses["Neutral Analyst"].timestamp = datetime.now().isoformat()
                current_agent = "Neutral Analyst"
            if risk_state.get("judge_decision"):
                progress.agent_statuses["Portfolio Manager"].status = "completed"
                progress.agent_statuses["Portfolio Manager"].output = risk_state["judge_decision"]
                progress.agent_statuses["Portfolio Manager"].timestamp = datetime.now().isoformat()
                progress.final_decision = risk_state["judge_decision"]
                current_agent = "Portfolio Manager"

        # Update current agent
        progress.current_agent = current_agent

        # Send individual agent completion updates
        for activity in agent_activity:
            print(f"✅ {activity}")
            # Extract output more safely
            output = None
            try:
                # Find the corresponding report key for this activity
                for key, (title, agent_name) in report_mappings.items():
                    if agent_name in activity and key in chunk:
                        output = chunk[key]
                        break
            except Exception as e:
                print(f"Error extracting output for activity {activity}: {e}")
                output = None
                
            await manager.broadcast(json.dumps({
                "type": "agent_completed",
                "session_id": session_id,
                "message": activity,
                "agent": current_agent,
                "output": output
            }))

        # Send current agent status
        if current_agent:
            print(f"🔍 {current_agent} is currently working on session {session_id}")
            await manager.broadcast(json.dumps({
                "type": "agent_active",
                "session_id": session_id,
                "current_agent": current_agent,
                "message": f"{current_agent} is working..."
            }))

        # Broadcast full progress update
        await manager.broadcast(json.dumps({
            "type": "progress_update",
            "session_id": session_id,
            "progress": progress.model_dump()
        }))
        
    except Exception as e:
        print(f"Error in update_progress_from_chunk for session {session_id}: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        
        # Send error notification but don't crash the analysis
        await manager.broadcast(json.dumps({
            "type": "progress_update_error",
            "session_id": session_id,
            "error": f"Chunk processing error: {str(e)}"
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

@app.post("/cleanup-sessions")
async def cleanup_sessions():
    """Manually trigger session cleanup"""
    await cleanup_old_sessions()
    return {"message": "Session cleanup completed", "active_sessions": len(analysis_sessions)}

@app.get("/debug/sessions")
async def debug_sessions():
    """Debug endpoint to check session status"""
    return {
        "active_sessions": len(analysis_sessions),
        "sessions": {
            session_id: {
                "ticker": session.ticker,
                "is_complete": session.is_complete,
                "current_agent": session.current_agent,
                "agent_count": len(session.agent_statuses)
            }
            for session_id, session in analysis_sessions.items()
        }
    }

@app.post("/trade/buy")
async def buy_stock(trade: TradeRequest):
    return trading_service.buy(trade)

@app.post("/trade/sell")
async def sell_stock(trade: TradeRequest):
    return trading_service.sell(trade)

@app.get("/trade/portfolio")
async def get_portfolio():
    return trading_service.get_portfolio()



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
