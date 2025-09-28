import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  ArrowLeft, 
  Play, 
  Settings, 
  Brain, 
  Calendar, 
  TrendingUp,
  CheckCircle,
  Clock,
  AlertCircle
} from 'lucide-react';
import toast from 'react-hot-toast';

const AnalysisPage = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    ticker: 'AAPL',
    analysis_date: new Date().toISOString().split('T')[0],
    analysts: ['market', 'social', 'news', 'fundamentals'],
    research_depth: 1,
    llm_provider: 'google',
    backend_url: 'https://generativelanguage.googleapis.com/v1',
    shallow_thinker: 'gemini-2.0-flash',
    deep_thinker: 'gemini-2.0-flash'
  });
  const [isLoading, setIsLoading] = useState(false);
  const [recentSessions, setRecentSessions] = useState([]);

  const analystOptions = [
    { value: 'market', label: 'Market Analyst', description: 'Technical analysis and market trends' },
    { value: 'social', label: 'Social Analyst', description: 'Social media sentiment analysis' },
    { value: 'news', label: 'News Analyst', description: 'Global news and macroeconomic factors' },
    { value: 'fundamentals', label: 'Fundamentals Analyst', description: 'Financial statements and company fundamentals' }
  ];

  const llmProviders = [
    { value: 'google', label: 'Google Gemini', description: 'Gemini models via Google AI (Only supported option)' }
  ];

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleAnalystToggle = (analyst) => {
    setFormData(prev => ({
      ...prev,
      analysts: prev.analysts.includes(analyst)
        ? prev.analysts.filter(a => a !== analyst)
        : [...prev.analysts, analyst]
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      const response = await fetch(`${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/start-analysis`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        throw new Error('Failed to start analysis');
      }

      const result = await response.json();
      toast.success('Analysis started successfully!');
      navigate(`/monitor/${result.session_id}`);
    } catch (error) {
      toast.error(`Failed to start analysis: ${error.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  const fetchRecentSessions = async () => {
    try {
      // This would typically fetch from a sessions endpoint
      // For now, we'll use localStorage to simulate recent sessions
      const sessions = JSON.parse(localStorage.getItem('recentSessions') || '[]');
      setRecentSessions(sessions);
    } catch (error) {
      console.error('Error fetching recent sessions:', error);
    }
  };

  useEffect(() => {
    fetchRecentSessions();
  }, []);

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
                <h1 className="text-xl font-bold text-gray-900">Start New Analysis</h1>
                <p className="text-sm text-gray-600">Configure your trading analysis parameters</p>
              </div>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Analysis Form */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8">
              <form onSubmit={handleSubmit} className="space-y-8">
                {/* Basic Configuration */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Ticker Symbol
                    </label>
                    <div className="relative">
                      <TrendingUp className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                      <input
                        type="text"
                        value={formData.ticker}
                        onChange={(e) => handleInputChange('ticker', e.target.value.toUpperCase())}
                        className="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                        placeholder="e.g., AAPL, MSFT, GOOGL"
                        required
                      />
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Analysis Date
                    </label>
                    <div className="relative">
                      <Calendar className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                      <input
                        type="date"
                        value={formData.analysis_date}
                        onChange={(e) => handleInputChange('analysis_date', e.target.value)}
                        max={new Date().toISOString().split('T')[0]}
                        className="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                        required
                      />
                    </div>
                  </div>
                </div>

                {/* Analyst Selection */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-4">
                    Select Analysts
                  </label>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {analystOptions.map((analyst) => (
                      <div
                        key={analyst.value}
                        className={`p-4 border-2 rounded-lg cursor-pointer transition-all ${
                          formData.analysts.includes(analyst.value)
                            ? 'border-primary-500 bg-primary-50'
                            : 'border-gray-200 hover:border-gray-300'
                        }`}
                        onClick={() => handleAnalystToggle(analyst.value)}
                      >
                        <div className="flex items-center space-x-3">
                          <input
                            type="checkbox"
                            checked={formData.analysts.includes(analyst.value)}
                            onChange={() => handleAnalystToggle(analyst.value)}
                            className="w-4 h-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
                          />
                          <div>
                            <h4 className="font-medium text-gray-900">{analyst.label}</h4>
                            <p className="text-sm text-gray-600">{analyst.description}</p>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Research Depth */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Research Depth: {formData.research_depth} round{formData.research_depth !== 1 ? 's' : ''}
                  </label>
                  <input
                    type="range"
                    min="1"
                    max="3"
                    value={formData.research_depth}
                    onChange={(e) => handleInputChange('research_depth', parseInt(e.target.value))}
                    className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                  />
                  <div className="flex justify-between text-xs text-gray-500 mt-1">
                    <span>Quick (1 round)</span>
                    <span>Balanced (2 rounds)</span>
                    <span>Deep (3 rounds)</span>
                  </div>
                </div>

                {/* LLM Configuration */}
                <div className="border-t border-gray-200 pt-6">
                  <div className="flex items-center space-x-2 mb-4">
                    <Settings className="w-5 h-5 text-gray-600" />
                    <h3 className="text-lg font-medium text-gray-900">LLM Configuration</h3>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        LLM Provider
                      </label>
                      <select
                        value={formData.llm_provider}
                        onChange={(e) => handleInputChange('llm_provider', e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                      >
                        {llmProviders.map((provider) => (
                          <option key={provider.value} value={provider.value}>
                            {provider.label}
                          </option>
                        ))}
                      </select>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Backend URL
                      </label>
                      <input
                        type="url"
                        value={formData.backend_url}
                        onChange={(e) => handleInputChange('backend_url', e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                        placeholder="https://api.openai.com/v1"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Quick Thinking Model
                      </label>
                      <input
                        type="text"
                        value={formData.shallow_thinker}
                        onChange={(e) => handleInputChange('shallow_thinker', e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                        placeholder="gpt-4o-mini"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Deep Thinking Model
                      </label>
                      <input
                        type="text"
                        value={formData.deep_thinker}
                        onChange={(e) => handleInputChange('deep_thinker', e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                        placeholder="o4-mini"
                      />
                    </div>
                  </div>
                </div>

                {/* Submit Button */}
                <div className="flex justify-end space-x-4 pt-6 border-t border-gray-200">
                  <button
                    type="button"
                    onClick={() => navigate('/')}
                    className="btn-secondary"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={isLoading || formData.analysts.length === 0}
                    className="btn-primary flex items-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {isLoading ? (
                      <>
                        <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                        <span>Starting Analysis...</span>
                      </>
                    ) : (
                      <>
                        <Play className="w-4 h-4" />
                        <span>Start Analysis</span>
                      </>
                    )}
                  </button>
                </div>
              </form>
            </div>
          </div>

          {/* Recent Sessions */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Sessions</h3>
              {recentSessions.length > 0 ? (
                <div className="space-y-3">
                  {recentSessions.slice(0, 5).map((session, index) => (
                    <div
                      key={index}
                      className="p-3 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer"
                      onClick={() => navigate(`/monitor/${session.id}`)}
                    >
                      <div className="flex items-center justify-between">
                        <div>
                          <h4 className="font-medium text-gray-900">{session.ticker}</h4>
                          <p className="text-sm text-gray-600">{session.date}</p>
                        </div>
                        <div className="flex items-center space-x-1">
                          {session.status === 'completed' ? (
                            <CheckCircle className="w-4 h-4 text-success-600" />
                          ) : session.status === 'error' ? (
                            <AlertCircle className="w-4 h-4 text-danger-600" />
                          ) : (
                            <Clock className="w-4 h-4 text-warning-600" />
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center text-gray-500 py-8">
                  <Brain className="w-12 h-12 mx-auto mb-4 text-gray-300" />
                  <p>No recent sessions</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default AnalysisPage;
