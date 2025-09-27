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
    try {
      const wsUrl = process.env.REACT_APP_WS_URL || 'ws://localhost:8000';
      const ws = new WebSocket(`${wsUrl}/ws/${sessionId}`);
      
      ws.onopen = () => {
        console.log('WebSocket connected');
        setIsConnected(true);
        if (reconnectTimeoutRef.current) {
          clearTimeout(reconnectTimeoutRef.current);
        }
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          handleWebSocketMessage(data);
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };

      ws.onclose = () => {
        console.log('WebSocket disconnected');
        setIsConnected(false);
        // Attempt to reconnect after 3 seconds
        reconnectTimeoutRef.current = setTimeout(() => {
          connectWebSocket();
        }, 3000);
      };

      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        setIsConnected(false);
      };

      wsRef.current = ws;
    } catch (error) {
      console.error('Error connecting WebSocket:', error);
      setIsConnected(false);
    }
  }, [sessionId]);

  const handleWebSocketMessage = (data) => {
    switch (data.type) {
      case 'progress_update':
        setAnalysisData(data.progress);
        break;
      case 'analysis_complete':
        setAnalysisData(prev => ({
          ...prev,
          is_complete: true,
          final_decision: data.final_decision
        }));
        toast.success('Analysis completed!');
        break;
      case 'analysis_error':
        toast.error(`Analysis failed: ${data.error}`);
        break;
    }
  };

  const fetchAnalysisData = useCallback(async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/analysis/${sessionId}`);
      if (response.ok) {
        const data = await response.json();
        setAnalysisData(data);
      }
    } catch (error) {
      console.error('Error fetching analysis data:', error);
      toast.error('Failed to fetch analysis data');
    }
  }, [sessionId]);

  useEffect(() => {
    fetchAnalysisData();
    connectWebSocket();

    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
    };
  }, [sessionId, fetchAnalysisData, connectWebSocket]);

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
          {analysisData.is_complete && (
            <div className="mt-4 p-4 bg-success-50 border border-success-200 rounded-lg">
              <div className="flex items-center space-x-2">
                <CheckCircle className="w-5 h-5 text-success-600" />
                <span className="font-medium text-success-800">Analysis Complete!</span>
              </div>
            </div>
          )}
        </div>

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
                              {agent.status.replace('_', ' ')}
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
                      {selectedAgent.status.replace('_', ' ')}
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
