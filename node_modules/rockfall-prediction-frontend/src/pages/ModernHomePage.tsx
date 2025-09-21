import React, { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'

interface DashboardCard {
  id: string
  title: string
  value: string
  change: string
  trend: 'up' | 'down' | 'stable'
  icon: string
  color: string
}

interface RecentActivity {
  id: string
  type: 'prediction' | 'alert' | 'maintenance' | 'report'
  title: string
  message: string
  timestamp: Date
  priority: 'high' | 'medium' | 'low'
}

function HomePage() {
  const { state } = useAuth()
  const [dashboardCards, setDashboardCards] = useState<DashboardCard[]>([])
  const [recentActivity, setRecentActivity] = useState<RecentActivity[]>([])
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    loadDashboardData()
  }, [])

  const loadDashboardData = async () => {
    // Simulate loading
    setTimeout(() => {
      setDashboardCards([
        {
          id: '1',
          title: 'Active Sites',
          value: '24',
          change: '+2',
          trend: 'up',
          icon: '🏭',
          color: 'blue'
        },
        {
          id: '2',
          title: 'Risk Predictions',
          value: '156',
          change: '+12',
          trend: 'up',
          icon: '🤖',
          color: 'purple'
        },
        {
          id: '3',
          title: 'Active Sensors',
          value: '2,847',
          change: '-5',
          trend: 'down',
          icon: '📡',
          color: 'green'
        },
        {
          id: '4',
          title: 'High Risk Alerts',
          value: '3',
          change: '0',
          trend: 'stable',
          icon: '🚨',
          color: 'red'
        }
      ])

      setRecentActivity([
        {
          id: '1',
          type: 'alert',
          title: 'High Risk Detection',
          message: 'Site Alpha-7 shows 85% rockfall probability in next 24h',
          timestamp: new Date(Date.now() - 10 * 60 * 1000),
          priority: 'high'
        },
        {
          id: '2',
          type: 'prediction',
          title: 'ML Model Update',
          message: 'Predictive model updated with latest geological data',
          timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000),
          priority: 'medium'
        },
        {
          id: '3',
          type: 'maintenance',
          title: 'Sensor Calibration',
          message: 'Site Beta-3 sensors successfully recalibrated',
          timestamp: new Date(Date.now() - 4 * 60 * 60 * 1000),
          priority: 'low'
        },
        {
          id: '4',
          type: 'report',
          title: 'Weekly Report Generated',
          message: 'Risk assessment report for September 2025 completed',
          timestamp: new Date(Date.now() - 24 * 60 * 60 * 1000),
          priority: 'medium'
        }
      ])

      setIsLoading(false)
    }, 1000)
  }

  const getCardColorClasses = (color: string) => {
    const colors = {
      blue: 'from-blue-500 to-blue-600 text-white',
      purple: 'from-purple-500 to-purple-600 text-white',
      green: 'from-green-500 to-green-600 text-white',
      red: 'from-red-500 to-red-600 text-white'
    }
    return colors[color as keyof typeof colors] || colors.blue
  }

  const getActivityIcon = (type: string) => {
    const icons = {
      prediction: '🤖',
      alert: '🚨',
      maintenance: '🔧',
      report: '📊'
    }
    return icons[type as keyof typeof icons] || '📢'
  }

  const getPriorityColor = (priority: string) => {
    const colors = {
      high: 'bg-red-100 text-red-800',
      medium: 'bg-yellow-100 text-yellow-800',
      low: 'bg-green-100 text-green-800'
    }
    return colors[priority as keyof typeof colors] || colors.medium
  }

  const formatTimeAgo = (date: Date) => {
    const now = new Date()
    const diffInMinutes = Math.floor((now.getTime() - date.getTime()) / (1000 * 60))
    
    if (diffInMinutes < 1) return 'Just now'
    if (diffInMinutes < 60) return `${diffInMinutes}m ago`
    if (diffInMinutes < 1440) return `${Math.floor(diffInMinutes / 60)}h ago`
    return `${Math.floor(diffInMinutes / 1440)}d ago`
  }

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mb-4"></div>
          <p className="text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Welcome Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Welcome back, {state.user?.full_name || state.user?.username}! 👋
          </h1>
          <p className="text-gray-600">
            Here's what's happening with your rockfall prediction system today.
          </p>
        </div>

        {/* Dashboard Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {dashboardCards.map((card) => (
            <div
              key={card.id}
              className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden hover:shadow-lg transition-all duration-200"
            >
              <div className={`bg-gradient-to-r ${getCardColorClasses(card.color)} p-6`}>
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-white/80 text-sm font-medium">{card.title}</p>
                    <p className="text-3xl font-bold text-white mt-1">{card.value}</p>
                  </div>
                  <div className="text-3xl opacity-80">{card.icon}</div>
                </div>
              </div>
              <div className="p-4">
                <div className="flex items-center text-sm">
                  <span className={`inline-flex items-center ${
                    card.trend === 'up' ? 'text-green-600' : 
                    card.trend === 'down' ? 'text-red-600' : 'text-gray-600'
                  }`}>
                    {card.trend === 'up' && '↗️'}
                    {card.trend === 'down' && '↘️'}
                    {card.trend === 'stable' && '➡️'}
                    <span className="ml-1 font-medium">{card.change}</span>
                  </span>
                  <span className="text-gray-500 ml-1">from last week</span>
                </div>
              </div>
            </div>
          ))}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Recent Activity */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-semibold text-gray-900">Recent Activity</h2>
                <Link
                  to="/reports"
                  className="text-sm text-blue-600 hover:text-blue-700 font-medium"
                >
                  View all →
                </Link>
              </div>
              <div className="space-y-4">
                {recentActivity.map((activity) => (
                  <div
                    key={activity.id}
                    className="flex items-start space-x-4 p-4 rounded-xl hover:bg-gray-50 transition-colors"
                  >
                    <div className="flex-shrink-0 text-2xl">
                      {getActivityIcon(activity.type)}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between">
                        <h3 className="text-sm font-medium text-gray-900">
                          {activity.title}
                        </h3>
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getPriorityColor(activity.priority)}`}>
                          {activity.priority}
                        </span>
                      </div>
                      <p className="text-sm text-gray-600 mt-1">{activity.message}</p>
                      <p className="text-xs text-gray-400 mt-1">
                        {formatTimeAgo(activity.timestamp)}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Quick Actions */}
          <div className="space-y-6">
            {/* Quick Actions Card */}
            <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Quick Actions</h2>
              <div className="space-y-3">
                <Link
                  to="/predictions"
                  className="flex items-center p-3 rounded-xl hover:bg-blue-50 transition-colors group"
                >
                  <div className="flex-shrink-0 w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center group-hover:bg-blue-200 transition-colors">
                    <span className="text-lg">🤖</span>
                  </div>
                  <div className="ml-3">
                    <p className="text-sm font-medium text-gray-900">New Prediction</p>
                    <p className="text-xs text-gray-500">Run AI analysis</p>
                  </div>
                </Link>
                
                <Link
                  to="/sites"
                  className="flex items-center p-3 rounded-xl hover:bg-green-50 transition-colors group"
                >
                  <div className="flex-shrink-0 w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center group-hover:bg-green-200 transition-colors">
                    <span className="text-lg">🏭</span>
                  </div>
                  <div className="ml-3">
                    <p className="text-sm font-medium text-gray-900">Manage Sites</p>
                    <p className="text-xs text-gray-500">View all locations</p>
                  </div>
                </Link>
                
                <Link
                  to="/reports"
                  className="flex items-center p-3 rounded-xl hover:bg-purple-50 transition-colors group"
                >
                  <div className="flex-shrink-0 w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center group-hover:bg-purple-200 transition-colors">
                    <span className="text-lg">📊</span>
                  </div>
                  <div className="ml-3">
                    <p className="text-sm font-medium text-gray-900">Generate Report</p>
                    <p className="text-xs text-gray-500">Create analytics</p>
                  </div>
                </Link>
              </div>
            </div>

            {/* System Status Card */}
            <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">System Status</h2>
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">ML Engine</span>
                  <span className="flex items-center text-green-600">
                    <div className="w-2 h-2 bg-green-400 rounded-full mr-2"></div>
                    Online
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Data Pipeline</span>
                  <span className="flex items-center text-green-600">
                    <div className="w-2 h-2 bg-green-400 rounded-full mr-2"></div>
                    Running
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Sensor Network</span>
                  <span className="flex items-center text-yellow-600">
                    <div className="w-2 h-2 bg-yellow-400 rounded-full mr-2"></div>
                    Partial
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Alert System</span>
                  <span className="flex items-center text-green-600">
                    <div className="w-2 h-2 bg-green-400 rounded-full mr-2"></div>
                    Active
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default HomePage