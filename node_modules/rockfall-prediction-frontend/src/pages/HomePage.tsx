import React, { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { authApi } from '../services/api'

interface Notification {
  id: string
  type: 'alert' | 'info' | 'warning' | 'success'
  title: string
  message: string
  timestamp: Date
  isRead: boolean
}

interface QuickStat {
  label: string
  value: string
  change: string
  trend: 'up' | 'down' | 'stable'
  icon: string
}

function HomePage() {
  const { state, logout } = useAuth()
  const navigate = useNavigate()
  const [notifications, setNotifications] = useState<Notification[]>([])
  const [showNotifications, setShowNotifications] = useState(false)
  const [showProfile, setShowProfile] = useState(false)
  const [quickStats, setQuickStats] = useState<QuickStat[]>([])
  const [connectionStatus, setConnectionStatus] = useState<'connected' | 'disconnected' | 'checking'>('checking')

  useEffect(() => {
    loadHomeData()
    checkBackendConnection()
    
    // Check connection every 30 seconds
    const connectionInterval = setInterval(checkBackendConnection, 30000)
    
    return () => clearInterval(connectionInterval)
  }, [])

  const checkBackendConnection = async () => {
    try {
      const isConnected = await authApi.testConnection()
      setConnectionStatus(isConnected ? 'connected' : 'disconnected')
    } catch (error) {
      console.error('Connection check failed:', error)
      setConnectionStatus('disconnected')
    }
  }

  const loadHomeData = async () => {
    // Mock notifications
    setNotifications([
      {
        id: '1',
        type: 'alert',
        title: 'High Risk Alert',
        message: 'Site-001 showing elevated rockfall risk indicators',
        timestamp: new Date(),
        isRead: false
      },
      {
        id: '2',
        type: 'warning',
        title: 'Sensor Maintenance',
        message: 'TEMP_001 requires calibration within 48 hours',
        timestamp: new Date(Date.now() - 3600000),
        isRead: false
      },
      {
        id: '3',
        type: 'info',
        title: 'System Update',
        message: 'New ML model v2.3 deployed successfully',
        timestamp: new Date(Date.now() - 7200000),
        isRead: true
      }
    ])

    // Mock quick stats
    setQuickStats([
      { label: 'Active Sites', value: '12', change: '+2', trend: 'up', icon: '🏔️' },
      { label: 'Online Sensors', value: '48/52', change: '-1', trend: 'down', icon: '📡' },
      { label: 'Risk Level', value: 'Medium', change: 'stable', trend: 'stable', icon: '⚠️' },
      { label: 'Predictions Today', value: '23', change: '+5', trend: 'up', icon: '🔮' }
    ])
  }

  const markNotificationAsRead = (notificationId: string) => {
    setNotifications(prev => 
      prev.map(notif => 
        notif.id === notificationId ? { ...notif, isRead: true } : notif
      )
    )
  }

  const unreadCount = notifications.filter(n => !n.isRead).length

  const getNotificationIcon = (type: string) => {
    switch (type) {
      case 'alert': return '🚨'
      case 'warning': return '⚠️'
      case 'info': return 'ℹ️'
      case 'success': return '✅'
      default: return '📢'
    }
  }

  const getNotificationColor = (type: string) => {
    switch (type) {
      case 'alert': return 'border-red-200 bg-red-50'
      case 'warning': return 'border-yellow-200 bg-yellow-50'
      case 'info': return 'border-blue-200 bg-blue-50'
      case 'success': return 'border-green-200 bg-green-50'
      default: return 'border-gray-200 bg-gray-50'
    }
  }

  return (
    <div className="min-h-screen bg-white">
      {/* Background Effects */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-blue-500/5 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-purple-500/5 rounded-full blur-3xl animate-pulse animation-delay-2000"></div>
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-gradient-to-r from-cyan-500/3 to-purple-500/3 rounded-full blur-3xl animation-delay-4000"></div>
      </div>

      {/* Header Navigation */}
      <header className="relative z-10 bg-white/95 backdrop-blur-lg shadow-lg border-b border-gray-100 sticky top-0">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-20">
            {/* Logo and Title */}
            <div className="flex items-center space-x-4">
              <div className="w-12 h-12 bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl flex items-center justify-center">
                <span className="text-white text-xl font-bold">🏔️</span>
              </div>
              <h1 className="text-2xl font-bold bg-gradient-to-r from-gray-900 via-blue-800 to-purple-800 bg-clip-text text-transparent">
                GeoTech Predictor
              </h1>
              
              {/* Connection Status */}
              <div className={`flex items-center space-x-2 text-sm px-3 py-2 rounded-full shadow-sm ${
                connectionStatus === 'connected' ? 'bg-green-50 text-green-700 border border-green-200' : 
                connectionStatus === 'disconnected' ? 'bg-red-50 text-red-700 border border-red-200' : 'bg-yellow-50 text-yellow-700 border border-yellow-200'
              }`}>
                <div className={`w-3 h-3 rounded-full ${
                  connectionStatus === 'connected' ? 'bg-green-500 animate-pulse' : 
                  connectionStatus === 'disconnected' ? 'bg-red-500' : 'bg-yellow-500 animate-pulse'
                }`}></div>
                <span className="font-medium">
                  {connectionStatus === 'connected' && 'System Online'}
                  {connectionStatus === 'disconnected' && 'System Offline'}
                  {connectionStatus === 'checking' && 'Connecting...'}
                </span>
              </div>
            </div>

            {/* Navigation Items */}
            <nav className="hidden md:flex items-center space-x-2">
              <Link
                to="/dashboard"
                className="text-gray-600 hover:text-gray-900 hover:bg-gray-50 px-4 py-3 rounded-xl text-sm font-medium transition-all duration-300 hover:scale-105 flex items-center space-x-2"
              >
                <span>📊</span>
                <span>Dashboard</span>
              </Link>
              <Link
                to="/predictions"
                className="text-gray-600 hover:text-gray-900 hover:bg-gray-50 px-4 py-3 rounded-xl text-sm font-medium transition-all duration-300 hover:scale-105 flex items-center space-x-2"
              >
                <span>🔬</span>
                <span>Predictions</span>
              </Link>
              <Link
                to="/devices"
                className="text-gray-600 hover:text-gray-900 hover:bg-gray-50 px-4 py-3 rounded-xl text-sm font-medium transition-all duration-300 hover:scale-105 flex items-center space-x-2"
              >
                <span>📡</span>
                <span>Devices</span>
              </Link>
              <Link
                to="/sites"
                className="text-gray-600 hover:text-gray-900 hover:bg-gray-50 px-4 py-3 rounded-xl text-sm font-medium transition-all duration-300 hover:scale-105 flex items-center space-x-2"
              >
                <span>🗺️</span>
                <span>Sites</span>
              </Link>
            </nav>

            {/* Right side items */}
            <div className="flex items-center space-x-4">
              {/* Notifications */}
              <div className="relative">
                <button
                  onClick={() => setShowNotifications(!showNotifications)}
                  className="relative p-3 text-gray-600 hover:text-gray-900 hover:bg-gray-50 rounded-xl transition-all duration-300 hover:scale-105"
                >
                  <span className="text-xl">🔔</span>
                  {unreadCount > 0 && (
                    <span className="absolute -top-1 -right-1 bg-gradient-to-r from-red-500 to-pink-500 text-white text-xs rounded-full h-6 w-6 flex items-center justify-center font-semibold shadow-lg">
                      {unreadCount}
                    </span>
                  )}
                </button>

                {/* Notifications Dropdown */}
                {showNotifications && (
                  <div className="absolute right-0 mt-2 w-96 bg-white/95 backdrop-blur-xl rounded-2xl shadow-2xl border border-gray-200/50 z-50 overflow-hidden">
                    <div className="px-6 py-4 border-b border-gray-100/50 bg-gradient-to-r from-blue-50/50 to-purple-50/50">
                      <h3 className="text-lg font-semibold text-gray-800 flex items-center">
                        <span className="text-xl mr-2">🔔</span>
                        Notifications
                      </h3>
                    </div>
                    <div className="max-h-96 overflow-y-auto">
                      {notifications.length > 0 ? (
                        notifications.map((notification) => (
                          <div
                            key={notification.id}
                            className={`px-6 py-4 border-b border-gray-100/50 last:border-b-0 cursor-pointer hover:bg-gray-50/70 transition-all duration-300 ${
                              !notification.isRead ? 'bg-blue-50/50' : ''
                            }`}
                            onClick={() => markNotificationAsRead(notification.id)}
                          >
                            <div className="flex items-start space-x-3">
                              <div className="w-10 h-10 rounded-xl bg-gradient-to-r from-blue-500 to-purple-500 flex items-center justify-center text-white shadow-lg">
                                <span className="text-lg">{getNotificationIcon(notification.type)}</span>
                              </div>
                              <div className="flex-1 min-w-0">
                                <p className="text-sm font-semibold text-gray-900">
                                  {notification.title}
                                </p>
                                <p className="text-sm text-gray-600 mt-1">
                                  {notification.message}
                                </p>
                                <p className="text-xs text-gray-500 mt-1">
                                  {notification.timestamp.toLocaleString()}
                                </p>
                              </div>
                              {!notification.isRead && (
                                <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                              )}
                            </div>
                          </div>
                        ))
                      ) : (
                        <div className="px-4 py-8 text-center text-gray-500">
                          No notifications
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </div>

              {/* Profile */}
              <div className="relative">
                <button
                  onClick={() => setShowProfile(!showProfile)}
                  className="flex items-center space-x-3 text-gray-600 hover:text-gray-900 hover:bg-gray-50 px-3 py-2 rounded-xl transition-all duration-300 hover:scale-105"
                >
                  <div className="w-10 h-10 bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl flex items-center justify-center text-white text-sm font-bold shadow-lg">
                    {state.user?.email?.charAt(0).toUpperCase() || 'U'}
                  </div>
                  <span className="hidden md:block text-sm font-medium">
                    {state.user?.email || 'User'}
                  </span>
                </button>

                {/* Profile Dropdown */}
                {showProfile && (
                  <div className="absolute right-0 mt-2 w-64 bg-white/95 backdrop-blur-xl rounded-2xl shadow-2xl border border-gray-200/50 z-50 overflow-hidden">
                    <div className="px-6 py-4 border-b border-gray-100/50 bg-gradient-to-r from-blue-50/50 to-purple-50/50">
                      <div className="flex items-center space-x-3">
                        <div className="w-12 h-12 bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl flex items-center justify-center text-white font-bold shadow-lg">
                          {state.user?.email?.charAt(0).toUpperCase() || 'U'}
                        </div>
                        <div>
                          <p className="text-sm font-semibold text-gray-900">
                            {state.user?.email || 'User'}
                          </p>
                          <p className="text-xs text-gray-600">System Administrator</p>
                        </div>
                      </div>
                    </div>
                    <Link
                      to="/settings"
                      className="block px-6 py-3 text-sm text-gray-700 hover:bg-gray-50/70 transition-all duration-300 flex items-center space-x-3"
                    >
                      <span className="text-lg">⚙️</span>
                      <span>Settings</span>
                    </Link>
                    <Link
                      to="/help"
                      className="block px-6 py-3 text-sm text-gray-700 hover:bg-gray-50/70 transition-all duration-300 flex items-center space-x-3"
                    >
                      <span className="text-lg">❓</span>
                      <span>Help & Support</span>
                    </Link>
                    <button
                      onClick={logout}
                      className="block w-full text-left px-6 py-3 text-sm text-gray-700 hover:bg-red-50/70 transition-all duration-300 border-t border-gray-100/50 flex items-center space-x-3"
                    >
                      <span className="text-lg">🚪</span>
                      <span>Logout</span>
                    </button>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="relative z-10 max-w-7xl mx-auto py-8 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          {/* Welcome Section */}
          <div className="mb-12">
            <div className="text-center">
              <h2 className="text-5xl font-bold bg-gradient-to-r from-gray-900 via-blue-800 to-purple-800 bg-clip-text text-transparent mb-4">
                Welcome back, {state.user?.email?.split('@')[0] || 'User'}! 👋
              </h2>
              <p className="text-xl text-gray-600 max-w-3xl mx-auto">
                Advanced AI-powered geological monitoring system at your command
              </p>
            </div>
          </div>

          {/* Backend Disconnection Warning */}
          {connectionStatus === 'disconnected' && (
            <div className="mb-8 p-6 bg-gradient-to-r from-red-50 to-pink-50 border border-red-200/50 rounded-2xl shadow-lg">
              <div className="flex items-center space-x-4">
                <div className="w-12 h-12 bg-gradient-to-r from-red-500 to-pink-500 rounded-xl flex items-center justify-center shadow-lg">
                  <span className="text-white text-xl">⚠️</span>
                </div>
                <div className="flex-1">
                  <h3 className="text-red-800 font-bold text-lg">System Connection Issue</h3>
                  <p className="text-red-600 mt-1">
                    Backend services are temporarily unavailable. Some features may be limited. 
                    Our team is working to restore full connectivity.
                  </p>
                </div>
                <button
                  onClick={checkBackendConnection}
                  className="px-6 py-3 bg-gradient-to-r from-red-500 to-pink-500 hover:from-red-600 hover:to-pink-600 text-white text-sm font-semibold rounded-xl transition-all duration-300 hover:scale-105 shadow-lg"
                >
                  Retry Connection
                </button>
              </div>
            </div>
          )}

          {/* Quick Stats */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 mb-12">
            {quickStats.map((stat, index) => (
              <div key={index} className="group bg-white/70 backdrop-blur-xl rounded-2xl shadow-lg hover:shadow-2xl border border-gray-200/50 p-5 transition-all duration-300 hover:scale-105">
                <div className="flex items-center justify-between mb-3">
                  <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-purple-500 rounded-2xl flex items-center justify-center text-white text-lg shadow-lg group-hover:scale-110 transition-transform duration-300">
                    {stat.icon}
                  </div>
                  <div className={`px-3 py-1 rounded-full text-xs font-semibold ${
                    stat.trend === 'up' ? 'bg-green-100 text-green-700 border border-green-200' :
                    stat.trend === 'down' ? 'bg-red-100 text-red-700 border border-red-200' : 'bg-gray-100 text-gray-700 border border-gray-200'
                  }`}>
                    {stat.trend === 'up' ? '📈' : stat.trend === 'down' ? '📉' : '📊'} {stat.change}
                  </div>
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-600 mb-1">{stat.label}</p>
                  <p className="text-2xl font-bold bg-gradient-to-r from-gray-900 to-gray-700 bg-clip-text text-transparent">{stat.value}</p>
                </div>
              </div>
            ))}
          </div>

          {/* Quick Actions */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 mb-12">
            <Link
              to="/predictions"
              className="group bg-white/70 backdrop-blur-xl rounded-2xl shadow-lg hover:shadow-2xl border border-gray-200/50 p-5 transition-all duration-300 hover:scale-105"
            >
              <div className="flex flex-col items-center text-center space-y-3">
                <div className="w-16 h-16 bg-gradient-to-r from-blue-500 to-cyan-500 rounded-2xl flex items-center justify-center group-hover:scale-110 transition-transform duration-300 shadow-lg">
                  <span className="text-2xl text-white">🔬</span>
                </div>
                <div>
                  <h3 className="text-lg font-bold text-gray-900 mb-1">Quantum Analysis</h3>
                  <p className="text-sm text-gray-600">Launch advanced AI prediction engine</p>
                </div>
              </div>
            </Link>

            <Link
              to="/dashboard"
              className="group bg-white/70 backdrop-blur-xl rounded-2xl shadow-lg hover:shadow-2xl border border-gray-200/50 p-5 transition-all duration-300 hover:scale-105"
            >
              <div className="flex flex-col items-center text-center space-y-3">
                <div className="w-16 h-16 bg-gradient-to-r from-green-500 to-emerald-500 rounded-2xl flex items-center justify-center group-hover:scale-110 transition-transform duration-300 shadow-lg">
                  <span className="text-2xl text-white">📊</span>
                </div>
                <div>
                  <h3 className="text-lg font-bold text-gray-900 mb-1">Control Center</h3>
                  <p className="text-sm text-gray-600">Real-time system monitoring</p>
                </div>
              </div>
            </Link>

            <Link
              to="/devices"
              className="group bg-white/70 backdrop-blur-xl rounded-2xl shadow-lg hover:shadow-2xl border border-gray-200/50 p-5 transition-all duration-300 hover:scale-105"
            >
              <div className="flex flex-col items-center text-center space-y-3">
                <div className="w-16 h-16 bg-gradient-to-r from-purple-500 to-pink-500 rounded-2xl flex items-center justify-center group-hover:scale-110 transition-transform duration-300 shadow-lg">
                  <span className="text-2xl text-white">📡</span>
                </div>
                <div>
                  <h3 className="text-lg font-bold text-gray-900 mb-1">Device Hub</h3>
                  <p className="text-sm text-gray-600">Sensor network management</p>
                </div>
              </div>
            </Link>
          </div>

          {/* Recent Activity */}
          <div className="bg-white/70 backdrop-blur-xl rounded-2xl shadow-lg border border-gray-200/50 p-6">
            <h3 className="text-xl font-bold text-gray-900 mb-4 flex items-center">
              <span className="text-xl mr-3">🕒</span>
              System Activity Feed
            </h3>
            <div className="space-y-6">
              <div className="flex items-center space-x-4 p-4 bg-blue-50/50 rounded-xl border border-blue-200/50">
                <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-cyan-500 rounded-xl flex items-center justify-center">
                  <span className="text-white text-lg">🎯</span>
                </div>
                <div className="flex-1">
                  <p className="text-sm font-semibold text-gray-900">
                    New prediction analysis completed for Site-001
                  </p>
                  <p className="text-xs text-gray-600 mt-1">Advanced AI processing finished • 2 minutes ago</p>
                </div>
                <span className="px-3 py-1 bg-orange-100 text-orange-800 text-xs font-semibold rounded-full border border-orange-200">⚠️ Medium Risk</span>
              </div>
              
              <div className="flex items-center space-x-3 pb-3 border-b">
                <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                <div className="flex-1">
                  <p className="text-sm font-medium text-gray-900">
                    Sensor SEIS_001 came back online
                  </p>
                  <p className="text-xs text-gray-600">15 minutes ago</p>
                </div>
                <span className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded">Resolved</span>
              </div>
              
              <div className="flex items-center space-x-3 pb-3 border-b">
                <div className="w-2 h-2 bg-red-500 rounded-full"></div>
                <div className="flex-1">
                  <p className="text-sm font-medium text-gray-900">
                    Alert: High pore pressure detected at Zone-3
                  </p>
                  <p className="text-xs text-gray-600">1 hour ago</p>
                </div>
                <span className="px-2 py-1 bg-red-100 text-red-800 text-xs rounded">Critical</span>
              </div>
              
              <div className="flex items-center space-x-3">
                <div className="w-2 h-2 bg-purple-500 rounded-full"></div>
                <div className="flex-1">
                  <p className="text-sm font-medium text-gray-900">
                    System maintenance completed
                  </p>
                  <p className="text-xs text-gray-600">3 hours ago</p>
                </div>
                <span className="px-2 py-1 bg-purple-100 text-purple-800 text-xs rounded">Maintenance</span>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}

export default HomePage