import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  TrendingUp, 
  Brain, 
  Users, 
  BarChart3, 
  Play, 
  Settings,
  Activity,
  Shield,
  Target
} from 'lucide-react';
import AnalysisForm from './AnalysisForm';

const Dashboard = () => {
  const [showAnalysisForm, setShowAnalysisForm] = useState(false);

  const features = [
    {
      icon: <Brain className="w-8 h-8 text-primary-600" />,
      title: "Multi-Agent Analysis",
      description: "Specialized AI agents analyze market data, sentiment, news, and fundamentals",
      color: "bg-primary-50 border-primary-200"
    },
    {
      icon: <Users className="w-8 h-8 text-success-600" />,
      title: "Research Teams",
      description: "Bull and bear researchers debate investment strategies with risk management",
      color: "bg-success-50 border-success-200"
    },
    {
      icon: <Activity className="w-8 h-8 text-warning-600" />,
      title: "Real-time Monitoring",
      description: "Watch agents work in real-time with live status updates and progress tracking",
      color: "bg-warning-50 border-warning-200"
    },
    {
      icon: <Shield className="w-8 h-8 text-danger-600" />,
      title: "Risk Management",
      description: "Comprehensive risk assessment with multiple analyst perspectives",
      color: "bg-danger-50 border-danger-200"
    },
    {
      icon: <BarChart3 className="w-8 h-8 text-purple-600" />,
      title: "Technical Analysis",
      description: "Advanced technical indicators and market trend analysis",
      color: "bg-purple-50 border-purple-200"
    },
    {
      icon: <Target className="w-8 h-8 text-indigo-600" />,
      title: "Trading Decisions",
      description: "Final trading recommendations with detailed reasoning and confidence levels",
      color: "bg-indigo-50 border-indigo-200"
    }
  ];

  const agentTeams = [
    {
      name: "Analyst Team",
      agents: ["Market Analyst", "Social Analyst", "News Analyst", "Fundamentals Analyst"],
      description: "Comprehensive market analysis across multiple data sources",
      color: "bg-blue-500"
    },
    {
      name: "Research Team", 
      agents: ["Bull Researcher", "Bear Researcher", "Research Manager"],
      description: "Balanced investment research with debate and consensus building",
      color: "bg-green-500"
    },
    {
      name: "Trading Team",
      agents: ["Trader"],
      description: "Strategic trading plan development based on research insights",
      color: "bg-yellow-500"
    },
    {
      name: "Risk Management",
      agents: ["Risky Analyst", "Neutral Analyst", "Safe Analyst"],
      description: "Multi-perspective risk assessment and portfolio management",
      color: "bg-red-500"
    },
    {
      name: "Portfolio Management",
      agents: ["Portfolio Manager"],
      description: "Final decision making with comprehensive risk evaluation",
      color: "bg-purple-500"
    }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center space-x-3">
              <div className="bg-gradient-primary p-2 rounded-lg">
                <TrendingUp className="w-8 h-8 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Stox.ai</h1>
                <p className="text-sm text-gray-600">Multi-Agent LLM Financial Trading Framework</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <button
                onClick={() => setShowAnalysisForm(true)}
                className="btn-primary flex items-center space-x-2"
              >
                <Play className="w-4 h-4" />
                <span>Start Analysis</span>
              </button>
              <button className="btn-secondary flex items-center space-x-2">
                <Settings className="w-4 h-4" />
                <span>Settings</span>
              </button>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Hero Section */}
        <div className="text-center mb-12">
          <h2 className="text-4xl font-bold text-gray-900 mb-4">
            AI-Powered Trading Analysis
          </h2>
          <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
            Deploy specialized AI agents to analyze financial markets, debate investment strategies, 
            and make informed trading decisions with comprehensive risk management.
          </p>
          <div className="flex justify-center space-x-4">
            <button
              onClick={() => setShowAnalysisForm(true)}
              className="btn-primary text-lg px-8 py-3"
            >
              Start New Analysis
            </button>
            <button className="btn-secondary text-lg px-8 py-3">
              View Documentation
            </button>
          </div>
        </div>

        {/* Features Grid */}
        <div className="mb-16">
          <h3 className="text-2xl font-bold text-gray-900 text-center mb-8">
            Key Features
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {features.map((feature, index) => (
              <div
                key={index}
                className={`card card-hover border-2 ${feature.color}`}
              >
                <div className="flex items-start space-x-4">
                  {feature.icon}
                  <div>
                    <h4 className="text-lg font-semibold text-gray-900 mb-2">
                      {feature.title}
                    </h4>
                    <p className="text-gray-600">
                      {feature.description}
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Agent Teams */}
        <div className="mb-16">
          <h3 className="text-2xl font-bold text-gray-900 text-center mb-8">
            Agent Teams
          </h3>
          <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
            {agentTeams.map((team, index) => (
              <div key={index} className="card">
                <div className="flex items-center space-x-3 mb-4">
                  <div className={`w-3 h-3 rounded-full ${team.color}`}></div>
                  <h4 className="text-lg font-semibold text-gray-900">
                    {team.name}
                  </h4>
                </div>
                <p className="text-gray-600 mb-4">
                  {team.description}
                </p>
                <div className="space-y-2">
                  {team.agents.map((agent, agentIndex) => (
                    <div
                      key={agentIndex}
                      className="flex items-center space-x-2 text-sm text-gray-600"
                    >
                      <div className="w-2 h-2 bg-gray-400 rounded-full"></div>
                      <span>{agent}</span>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Workflow */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8">
          <h3 className="text-2xl font-bold text-gray-900 text-center mb-8">
            Analysis Workflow
          </h3>
          <div className="flex flex-col lg:flex-row items-center justify-between space-y-4 lg:space-y-0 lg:space-x-8">
            {[
              { step: 1, title: "Analyst Team", description: "Market, Social, News, Fundamentals" },
              { step: 2, title: "Research Team", description: "Bull vs Bear Debate" },
              { step: 3, title: "Trading Team", description: "Strategic Planning" },
              { step: 4, title: "Risk Management", description: "Multi-perspective Assessment" },
              { step: 5, title: "Portfolio Manager", description: "Final Decision" }
            ].map((step, index) => (
              <div key={index} className="flex flex-col items-center text-center">
                <div className="w-12 h-12 bg-primary-600 text-white rounded-full flex items-center justify-center font-bold text-lg mb-3">
                  {step.step}
                </div>
                <h4 className="font-semibold text-gray-900 mb-1">{step.title}</h4>
                <p className="text-sm text-gray-600">{step.description}</p>
                {index < 4 && (
                  <div className="hidden lg:block absolute top-6 left-full w-8 h-0.5 bg-gray-300 transform translate-x-4"></div>
                )}
              </div>
            ))}
          </div>
        </div>
      </main>

      {/* Analysis Form Modal */}
      {showAnalysisForm && (
        <AnalysisForm onClose={() => setShowAnalysisForm(false)} />
      )}
    </div>
  );
};

export default Dashboard;
