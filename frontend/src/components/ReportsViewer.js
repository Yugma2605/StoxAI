import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { 
  ArrowLeft, 
  Download, 
  Share2, 
  FileText,
  TrendingUp,
  BarChart3,
  Brain,
  Users,
  Shield,
  Target,
  Calendar,
  Clock,
  CheckCircle,
  AlertCircle
} from 'lucide-react';
import ReactMarkdown from 'react-markdown';

const ReportsViewer = () => {
  const { sessionId } = useParams();
  const navigate = useNavigate();
  const [reportData, setReportData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  const fetchReportData = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/reports/${sessionId}`);
      if (response.ok) {
        const data = await response.json();
        setReportData(data);
      } else {
        throw new Error('Failed to fetch report data');
      }
    } catch (error) {
      console.error('Error fetching report data:', error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchReportData();
  }, [sessionId]);

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="w-8 h-8 border-4 border-primary-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600">Loading report data...</p>
        </div>
      </div>
    );
  }

  if (!reportData) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <AlertCircle className="w-12 h-12 text-danger-600 mx-auto mb-4" />
          <h2 className="text-xl font-bold text-gray-900 mb-2">Report Not Found</h2>
          <p className="text-gray-600 mb-4">The requested report could not be found.</p>
          <button
            onClick={() => navigate('/')}
            className="btn-primary"
          >
            Return to Dashboard
          </button>
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
                  Analysis Report: {reportData.ticker}
                </h1>
                <p className="text-sm text-gray-600">
                  {reportData.analysis_date} • Session: {sessionId.slice(0, 8)}...
                </p>
              </div>
            </div>
            <div className="flex items-center space-x-3">
              <button className="btn-secondary flex items-center space-x-2">
                <Download className="w-4 h-4" />
                <span>Export</span>
              </button>
              <button className="btn-secondary flex items-center space-x-2">
                <Share2 className="w-4 h-4" />
                <span>Share</span>
              </button>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Analysis Report</h2>
          
          {reportData.final_decision ? (
            <div className="prose max-w-none">
              <ReactMarkdown>{reportData.final_decision}</ReactMarkdown>
            </div>
          ) : (
            <div className="text-center py-12">
              <Target className="w-12 h-12 text-gray-300 mx-auto mb-4" />
              <p className="text-gray-500">No final decision available yet.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ReportsViewer;


