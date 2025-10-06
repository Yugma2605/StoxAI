import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { 
  ArrowLeft, 
  Activity, 
  CheckCircle, 
  Clock, 
  AlertCircle,
  Brain,
  Users,
  Shield,
  Target,
  TrendingUp,
  BarChart3,
  FileText,
  Eye
} from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import toast from 'react-hot-toast';

const AgentMonitor = () => {
  const { sessionId } = useParams();
  const navigate = useNavigate();
  const [analysisData, setAnalysisData] = useState(null);
  const [isConnected, setIsConnected] = useState(false);
  const [selectedAgent, setSelectedAgent] = useState(null);
  const [activityFeed, setActivityFeed] = useState([]);
  const wsRef = useRef(null);
  const reconnectTimeoutRef = useRef(null);

  const agentIcons = {
    'Market Analyst': <BarChart3 className="w-5 h-5" />,
    'Social Analyst': <Users className="w-5 h-5" />,
    'News Analyst': <FileText className="w-5 h-5" />,
    'Fundamentals Analyst': <TrendingUp className="w-5 h-5" />,
    'Bull Researcher': <TrendingUp className="w-5 h-5" />,
    'Bear Researcher': <TrendingUp className="w-5 h-5" />,
    'Research Manager': <Brain className="w-5 h-5" />,
    'Trader': <Target className="w-5 h-5" />,
    'Risky Analyst': <Shield className="w-5 h-5" />,
    'Neutral Analyst': <Shield className="w-5 h-5" />,
    'Safe Analyst': <Shield className="w-5 h-5" />,
    'Portfolio Manager': <Target className="w-5 h-5" />
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-5 h-5 text-success-600" />;
      case 'in_progress':
        return <Activity className="w-5 h-5 text-primary-600 animate-pulse" />;
      case 'error':
        return <AlertCircle className="w-5 h-5 text-danger-600" />;
      case 'pending':
        return <Clock className="w-5 h-5 text-gray-400" />;
      default:
        return <Clock className="w-5 h-5 text-gray-400" />;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed':
        return 'status-completed';
      case 'in_progress':
        return 'status-in-progress';
      case 'error':
        return 'status-error';
      default:
        return 'status-pending';
    }
  };

  const connectWebSocket = useCallback(() => {
    console.log("---------------------------",analysisData);
    // if(!analysisData) return;
    console.log(`🔌 Connecting WebSocket to session: ${sessionId}`);
    
    try {
      const wsUrl = process.env.REACT_APP_WS_URL || 'ws://localhost:8000';
      const ws = new WebSocket(`${wsUrl}/ws/${sessionId}`);
      
      ws.onopen = () => {
        console.log(`🔌 WebSocket connected to session: ${sessionId}`);
        setIsConnected(true);
        if (reconnectTimeoutRef.current) {
          clearTimeout(reconnectTimeoutRef.current);
        }
        // Send initial ping to establish connection
        ws.send(JSON.stringify({ type: 'pong', timestamp: new Date().toISOString() }));
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          console.log('📨 WebSocket message received:', data.type);
          
          // Handle ping messages
          if (data.type === 'ping') {
            console.log('🏓 Received ping, sending pong');
            ws.send(JSON.stringify({ type: 'pong', timestamp: new Date().toISOString() }));
            return;
          }
          
          handleWebSocketMessage(data);
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };

      ws.onclose = (event) => {
        console.log(`🔌 WebSocket disconnected: ${event.code} - ${event.reason}`);
        setIsConnected(false);
        
        // Only attempt to reconnect if it's not a normal closure and not a temporary session
        if (event.code !== 1000 && !sessionId.startsWith('temp-')) {
          console.log(`🔄 Attempting to reconnect WebSocket in 5 seconds... (code: ${event.code})`);
          reconnectTimeoutRef.current = setTimeout(() => {
            console.log('🔄 Reconnecting WebSocket...');
            connectWebSocket();
          }, 5000); // Increased delay to 5 seconds
        } else if (event.code === 1000) {
          console.log('✅ WebSocket closed normally');
        } else if (event.code === 1008) {
          console.log('❌ Session not found, will retry connection');
          // Retry after a longer delay for session not found
          reconnectTimeoutRef.current = setTimeout(() => {
            console.log('🔄 Retrying WebSocket connection after session not found...');
            connectWebSocket();
          }, 10000); // 10 second delay for session not found
        }
      };

      ws.onerror = (error) => {
        console.error('❌ WebSocket error:', error);
        setIsConnected(false);
        // Don't show error toast for temporary sessions
        if (!sessionId.startsWith('temp-')) {
          toast.error('WebSocket connection error');
        }
      };

      wsRef.current = ws;
    } catch (error) {
      console.error('Error connecting WebSocket:', error);
      setIsConnected(false);
      toast.error('Failed to connect to WebSocket');
    }
  }, [sessionId]);

  const handleWebSocketMessage = (data) => {
    const timestamp = new Date().toLocaleTimeString();
    console.log(`📨 Processing WebSocket message: ${data.type}`, data);
    
    switch (data.type) {
      case 'analysis_started':
        toast.success('Analysis started! Agents are initializing...');
        setActivityFeed(prev => [...prev, {
          id: Date.now(),
          type: 'info',
          message: 'Analysis started - initializing agents...',
          timestamp,
          agent: null
        }]);
        break;
      case 'agent_active':
        // Update the current agent status to in_progress
        setAnalysisData(prev => ({
          ...prev,
          current_agent: data.current_agent,
          agent_statuses: {
            ...prev.agent_statuses,
            [data.current_agent]: {
              ...prev.agent_statuses[data.current_agent],
              status: 'in_progress',
              timestamp: new Date().toISOString()
            }
          }
        }));
        // toast(`${data.current_agent} is working...`, { duration: 2000 });
        setActivityFeed(prev => [...prev, {
          id: Date.now(),
          type: 'active',
          message: `${data.current_agent} is working...`,
          timestamp,
          agent: data.current_agent
        }]);
        break;
      case 'agent_completed':
        // Update the agent status to completed and add output
        setAnalysisData(prev => ({
          ...prev,
          agent_statuses: {
            ...prev.agent_statuses,
            [data.agent]: {
              ...prev.agent_statuses[data.agent],
              status: 'completed',
              output: data.output,
              timestamp: new Date().toISOString()
            }
          }
        }));
        // toast.success(`${data.message}`, { duration: 3000 });
        setActivityFeed(prev => [...prev, {
          id: Date.now(),
          type: 'completed',
          message: data.message,
          timestamp,
          agent: data.agent,
          output: data.output
        }]);
        break;
      case 'temp_session':
        // Handle temporary session message
        console.log('Temporary session detected:', data.message);
        break;
      case 'connection_established':
        console.log('✅ WebSocket connection established:', data.session_id);
        toast.success('Connected to analysis session');
        break;
      case 'progress_update':
        setAnalysisData(data.progress);
        break;
      case 'analysis_complete':
        setAnalysisData(prev => ({
          ...prev,
          is_complete: true,
          final_decision: data.final_decision
        }));
        // toast.success('Analysis completed!');
        setActivityFeed(prev => [...prev, {
          id: Date.now(),
          type: 'success',
          message: 'Analysis completed successfully!',
          timestamp,
          agent: null
        }]);
        break;
      case 'analysis_error':
        toast.error(`Analysis failed: ${data.error}`);
        setActivityFeed(prev => [...prev, {
          id: Date.now(),
          type: 'error',
          message: `Analysis failed: ${data.error}`,
          timestamp,
          agent: null
        }]);
        break;
      case 'progress_update_error':
        toast.error(`Progress update error: ${data.error}`);
        setActivityFeed(prev => [...prev, {
          id: Date.now(),
          type: 'error',
          message: `Progress update error: ${data.error}`,
          timestamp,
          agent: null
        }]);
        break;
    }
  };

  const fetchAnalysisData = useCallback(async () => {
    try {
      console.log(`📡 Fetching analysis data for session: ${sessionId}`);
      const response = await fetch(`${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/analysis/${sessionId}`);
      if (response.ok) {
        const data = await response.json();
        console.log("📊 Analysis data received:", data);
        setAnalysisData(data);
      } else if (response.status === 404) {
        console.warn('Session not found, will retry...');
        toast.error('Session not found. Waiting for agents to initialize...');
        setTimeout(fetchAnalysisData, 3000);
      } else {
        throw new Error('Failed to fetch analysis data');
      }
    } catch (error) {
      console.error('Error fetching analysis data:', error);
      toast.error('Failed to fetch analysis data');
      // If it's a network error or session not found, redirect to dashboard
      if (error.message.includes('Failed to fetch') || error.message.includes('404')) {
        navigate('/');
      }
    }
  }, [sessionId, navigate]);

  useEffect(() => {
    console.log(`🎯 AgentMonitor mounted with sessionId: ${sessionId}`);
    
    // Fetch data first
    fetchAnalysisData();
    
    // Add a small delay before connecting WebSocket to ensure session is ready
    const connectTimeout = setTimeout(() => {
      console.log(`⏰ Connecting WebSocket after delay for session: ${sessionId}`);
      connectWebSocket();
    }, 1000); // 1 second delay

    return () => {
      clearTimeout(connectTimeout);
      if (wsRef.current) {
        wsRef.current.close();
      }
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
    };
  }, [sessionId, fetchAnalysisData, connectWebSocket]);

  // No need for complex URL change detection since we're using React Router navigation

  const getProgressPercentage = () => {
    if (!analysisData?.agent_statuses) return 0;
    
    const totalAgents = Object.keys(analysisData.agent_statuses).length;
    const completedAgents = Object.values(analysisData.agent_statuses)
      .filter(agent => agent.status === 'completed').length;
    
    return Math.round((completedAgents / totalAgents) * 100);
  };

  const getTeamAgents = (teamName) => {
    if (!analysisData?.agent_statuses) return [];
    
    const teamMappings = {
      'Analyst Team': ['Market Analyst', 'Social Analyst', 'News Analyst', 'Fundamentals Analyst'],
      'Research Team': ['Bull Researcher', 'Bear Researcher', 'Research Manager'],
      'Trading Team': ['Trader'],
      'Risk Management': ['Risky Analyst', 'Neutral Analyst', 'Safe Analyst'],
      'Portfolio Management': ['Portfolio Manager']
    };
    
    return teamMappings[teamName]?.map(agentName => ({
      name: agentName,
      ...analysisData.agent_statuses[agentName]
    })) || [];
  };

  if (!analysisData) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="w-8 h-8 border-4 border-primary-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600">Loading analysis data...</p>
          <p className="text-sm text-gray-500 mt-2">Connecting to agents...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between py-4">
            <div className="flex items-center space-x-4">
              <button
                onClick={() => navigate('/')}
                className="text-gray-400 hover:text-gray-600 transition-colors"
              >
                <ArrowLeft className="w-6 h-6" />
              </button>
              <div>
                <h1 className="text-xl font-bold text-gray-900">
                  Analysis Monitor: {analysisData.ticker}
                </h1>
                <p className="text-sm text-gray-600">
                  {analysisData.analysis_date} • Session: {sessionId.slice(0, 8)}...
                </p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <div className={`w-3 h-3 rounded-full ${isConnected ? 'bg-success-500' : 'bg-danger-500'}`}></div>
                <span className="text-sm text-gray-600">
                  {isConnected ? 'Connected' : 'Disconnected'}
                </span>
              </div>
              <button
                onClick={() => navigate(`/reports/${sessionId}`)}
                className="btn-secondary flex items-center space-x-2"
              >
                <Eye className="w-4 h-4" />
                <span>View Reports</span>
              </button>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Progress Overview */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-8">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-900">Analysis Progress</h2>
            <span className="text-sm text-gray-600">
              {getProgressPercentage()}% Complete
            </span>
          </div>
          <div className="progress-bar">
            <div 
              className="progress-fill"
              style={{ width: `${getProgressPercentage()}%` }}
            ></div>
          </div>
          {analysisData.current_agent && !analysisData.is_complete && (
            <div className="mt-4 p-4 bg-primary-50 border border-primary-200 rounded-lg">
              <div className="flex items-center space-x-2">
                <Activity className="w-5 h-5 text-primary-600 animate-pulse" />
                <span className="font-medium text-primary-800">
                  {analysisData.current_agent} is currently working...
                </span>
              </div>
            </div>
          )}
          {analysisData.is_complete && (
            <div className="mt-4 p-4 bg-success-50 border border-success-200 rounded-lg">
              <div className="flex items-center space-x-2">
                <CheckCircle className="w-5 h-5 text-success-600" />
                <span className="font-medium text-success-800">Analysis Complete!</span>
              </div>
            </div>
          )}
        </div>

        {/* <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-8">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Real-time Activity</h2>
          <div className="max-h-64 overflow-y-auto space-y-3">
            {activityFeed.length === 0 ? (
              <div className="text-center text-gray-500 py-8">
                <Activity className="w-8 h-8 mx-auto mb-2 text-gray-300 animate-pulse" />
                <p>Waiting for agent activity...</p>
                <p className="text-sm text-gray-400 mt-1">Agents will start working shortly</p>
              </div>
            ) : (
              activityFeed.slice(-10).reverse().map((activity) => (
                <div key={activity.id} className="flex items-start space-x-3 p-3 rounded-lg bg-gray-50">
                  <div className={`w-2 h-2 rounded-full mt-2 ${
                    activity.type === 'completed' ? 'bg-success-500' :
                    activity.type === 'active' ? 'bg-primary-500' :
                    activity.type === 'error' ? 'bg-danger-500' :
                    'bg-gray-400'
                  }`}></div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between">
                      <p className="text-sm font-medium text-gray-900">{activity.message}</p>
                      <span className="text-xs text-gray-500">{activity.timestamp}</span>
                    </div>
                    {activity.agent && (
                      <p className="text-xs text-gray-600 mt-1">
                        Agent: {activity.agent}
                      </p>
                    )}
                    {activity.output && (
                      <div className="mt-2 p-2 bg-white rounded border text-xs text-gray-700 max-h-20 overflow-y-auto">
                        {activity.output.substring(0, 200)}...
                      </div>
                    )}
                  </div>
                </div>
              ))
            )}
          </div>
        </div> */}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Agent Teams */}
          <div className="lg:col-span-2 space-y-6">
            {[
              'Analyst Team',
              'Research Team', 
              'Trading Team',
              'Risk Management',
              'Portfolio Management'
            ].map((teamName) => {
              const teamAgents = getTeamAgents(teamName);
              if (teamAgents.length === 0) return null;

              return (
                <div key={teamName} className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">{teamName}</h3>
                  <div className="space-y-3">
                    {teamAgents.map((agent) => (
                      console.log(agent),
                      <div
                        key={agent.name}
                        className={`p-4 rounded-lg border-2 cursor-pointer transition-all ${
                          selectedAgent?.name === agent.name
                            ? 'border-primary-500 bg-primary-50'
                            : 'border-gray-200 hover:border-gray-300'
                        }`}
                        onClick={() => setSelectedAgent(agent)}
                      >
                        <div className="flex items-center justify-between">
                          <div className="flex items-center space-x-3">
                            {agentIcons[agent.name]}
                            <div>
                              <h4 className="font-medium text-gray-900">{agent.name}</h4>
                              <p className="text-sm text-gray-600">
                                {agent.team}
                              </p>
                            </div>
                          </div>
                          <div className="flex items-center space-x-2">
                          <span className={`px-2 py-1 rounded-full text-xs font-medium border ${getStatusColor(agent.status)}`}>
                            {(agent.status || "pending").replace("_", " ")}
                          </span>
                          {getStatusIcon(agent.status)}

                          </div>
                        </div>
                        {agent.output && (
                          <div className="mt-3 pt-3 border-t border-gray-200">
                            <p className="text-sm text-gray-600 line-clamp-2">
                              {agent.output.substring(0, 200)}...
                            </p>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              );
            })}
          </div>

          {/* Agent Details */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 sticky top-8">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Agent Details</h3>
              {selectedAgent ? (
                console.log("Selected Agent:", selectedAgent),
                <div className="space-y-4">
                  <div className="flex items-center space-x-3">
                    {agentIcons[selectedAgent.name]}
                    <div>
                      <h4 className="font-medium text-gray-900">{selectedAgent.name}</h4>
                      <p className="text-sm text-gray-600">{selectedAgent.team}</p>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-2">
                  <span className={`px-2 py-1 rounded-full text-xs font-medium border ${getStatusColor(selectedAgent.status)}`}>
                    {(selectedAgent.status || "pending").replace("_", " ")}
                  </span>
                  {getStatusIcon(selectedAgent.status)}

                  </div>

                  {selectedAgent.output && (
                    <div className="mt-4">
                      <h5 className="font-medium text-gray-900 mb-2">Output</h5>
                      <div className="max-h-96 overflow-y-auto">
                        <ReactMarkdown className="markdown-content">
                          {selectedAgent.output}
                        </ReactMarkdown>
                      </div>
                    </div>
                  )}

                  <div className="text-xs text-gray-500">
                    Last updated: {new Date(selectedAgent.timestamp).toLocaleString()}
                  </div>
                </div>
              ) : (
                <div className="text-center text-gray-500">
                  <Brain className="w-12 h-12 mx-auto mb-4 text-gray-300" />
                  <p>Select an agent to view details</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default AgentMonitor;
