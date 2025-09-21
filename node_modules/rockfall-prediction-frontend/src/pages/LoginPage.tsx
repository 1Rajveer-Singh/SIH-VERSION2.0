import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { authApi, authUtils } from '../services/api';
import { useAuth } from '../contexts/AuthContext';

function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [connectionStatus, setConnectionStatus] = useState('checking');
  const navigate = useNavigate();
  const { login } = useAuth();

  useEffect(() => {
    const checkConnection = async () => {
      try {
        console.log('LoginPage: Checking backend connection...')
        const isConnected = await authApi.testConnection();
        console.log('LoginPage: Connection status:', isConnected)
        setConnectionStatus(isConnected ? 'connected' : 'disconnected');
      } catch (error) {
        console.error('LoginPage: Connection check error:', error)
        setConnectionStatus('disconnected');
      }
    };
    checkConnection();
  }, []);

  useEffect(() => {
    if (authUtils.isAuthenticated()) {
      navigate('/dashboard');
    }
  }, [navigate]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    try {
      await login(email, password);
      navigate('/dashboard');
    } catch (error: any) {
      if (error.response?.status === 401) {
        setError('Invalid email or password. Please check your credentials.');
      } else if (error.response?.status === 400) {
        setError('Account is inactive. Please contact administrator.');
      } else if (error.message?.includes('Network Error') || error.code === 'ECONNREFUSED') {
        setError('Cannot connect to server. Please make sure the backend is running.');
      } else {
        setError(error.response?.data?.detail || error.message || 'Login failed. Please try again.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-white flex items-center justify-center relative overflow-hidden">
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-blue-500/5 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-purple-500/5 rounded-full blur-3xl animate-pulse"></div>
      </div>

      <div className="relative z-10 w-full max-w-md px-6">
        <div className="bg-white/90 backdrop-blur-xl rounded-3xl border border-gray-200 p-8 shadow-2xl">
          <div className="text-center mb-8">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-r from-cyan-500 to-blue-600 rounded-2xl mb-4">
              <span className="text-2xl"></span>
            </div>
            <h1 className="text-3xl font-bold bg-gradient-to-r from-cyan-600 via-blue-600 to-purple-700 bg-clip-text text-transparent mb-2">
              GeoTech Portal
            </h1>
            <p className="text-gray-600">Access your quantum geological monitoring dashboard</p>
            
            <div className={`mt-4 flex items-center justify-center space-x-2 text-sm ${
              connectionStatus === 'connected' ? 'text-green-600' : 
              connectionStatus === 'disconnected' ? 'text-red-600' : 'text-yellow-600'
            }`}>
              <div className={`w-2 h-2 rounded-full ${
                connectionStatus === 'connected' ? 'bg-green-500 animate-pulse' : 
                connectionStatus === 'disconnected' ? 'bg-red-500' : 'bg-yellow-500 animate-pulse'
              }`}></div>
              <span>
                {connectionStatus === 'connected' && 'Backend Connected'}
                {connectionStatus === 'disconnected' && 'Backend Disconnected'}
                {connectionStatus === 'checking' && 'Checking Connection...'}
              </span>
              {connectionStatus === 'disconnected' && (
                <button
                  onClick={async () => {
                    setConnectionStatus('checking');
                    try {
                      const isConnected = await authApi.testConnection();
                      setConnectionStatus(isConnected ? 'connected' : 'disconnected');
                    } catch {
                      setConnectionStatus('disconnected');
                    }
                  }}
                  className="ml-2 px-2 py-1 text-xs bg-red-100 hover:bg-red-200 text-red-700 rounded transition-colors"
                >
                  Retry
                </button>
              )}
            </div>
          </div>

          {error && (
            <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-xl text-red-700 text-sm">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Email Address
              </label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full px-4 py-3 bg-gray-50 border border-gray-300 rounded-xl text-gray-900 placeholder-gray-500 focus:ring-2 focus:ring-cyan-500 focus:border-transparent"
                placeholder="admin@rockfall.com"
                required
                disabled={isLoading}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Password
              </label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full px-4 py-3 bg-gray-50 border border-gray-300 rounded-xl text-gray-900 placeholder-gray-500 focus:ring-2 focus:ring-cyan-500 focus:border-transparent"
                placeholder="Enter your password"
                required
                disabled={isLoading}
              />
            </div>

            <button
              type="submit"
              disabled={isLoading || connectionStatus === 'disconnected'}
              className={`w-full py-3 px-6 rounded-xl font-semibold transition-all duration-300 ${
                isLoading || connectionStatus === 'disconnected'
                  ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                  : 'bg-gradient-to-r from-cyan-500 via-blue-600 to-purple-600 text-white hover:from-cyan-400 hover:via-blue-500 hover:to-purple-500 hover:scale-105 shadow-lg shadow-blue-500/25'
              }`}
            >
              {isLoading ? (
                <div className="flex items-center justify-center space-x-2">
                  <div className="w-5 h-5 border-2 border-gray-400 border-t-transparent rounded-full animate-spin"></div>
                  <span>Authenticating...</span>
                </div>
              ) : connectionStatus === 'disconnected' ? (
                <span>Backend Disconnected</span>
              ) : (
                <div className="flex items-center justify-center space-x-2">
                  <span></span>
                  <span>Access Dashboard</span>
                </div>
              )}
            </button>
          </form>

          <div className="mt-6 p-4 bg-gray-50 rounded-xl border border-gray-200">
            <h3 className="text-sm font-semibold text-gray-700 mb-2">Demo Credentials</h3>
            <div className="text-xs text-gray-600 space-y-1">
              <div><strong>Admin:</strong> admin@rockfall.com / secret123</div>
              <div><strong>Operator:</strong> operator@rockfall.com / secret123</div>
            </div>
          </div>
        </div>

        <div className="mt-6 text-center text-xs text-gray-500">
          <p>Quantum Geological Monitoring System v2.0</p>
          <p>© 2025 GeoTech Solutions. All rights reserved.</p>
        </div>
      </div>
    </div>
  );
}

export default LoginPage;
