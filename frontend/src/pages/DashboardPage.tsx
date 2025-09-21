import React, { useState, useEffect } from 'react'
import { useAuth } from '../contexts/AuthContext'
import { testDashboardAPI, DashboardStats, PredictionSummary, RecentAlert } from '../services/dashboard-test'
import Navbar from '../components/Navbar'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
} from 'chart.js'
import { Line, Bar, Doughnut } from 'react-chartjs-2'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
)

function DashboardPage() {
  const { state, logout } = useAuth()
  const [stats, setStats] = useState<DashboardStats | null>(null)
  const [predictions, setPredictions] = useState<PredictionSummary[]>([])
  const [alerts, setAlerts] = useState<RecentAlert[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [timeFilter, setTimeFilter] = useState<'24h' | '7d' | '30d' | '90d'>('24h')
  const [riskFilter, setRiskFilter] = useState<'all' | 'high' | 'medium' | 'low'>('all')
  const [sensorHealth, setSensorHealth] = useState<any[]>([])
  const [eventTimeline, setEventTimeline] = useState<any[]>([])
  const [filteredPredictions, setFilteredPredictions] = useState<PredictionSummary[]>([])
  const [filteredAlerts, setFilteredAlerts] = useState<RecentAlert[]>([])
  const [showFilters, setShowFilters] = useState(false)

  // Chart data generation functions
  const generateRiskTrendData = () => {
    const labels = ['6h ago', '5h ago', '4h ago', '3h ago', '2h ago', '1h ago', 'Now']
    return {
      labels,
      datasets: [
        {
          label: 'High Risk',
          data: [12, 15, 18, 20, 22, 25, 28],
          borderColor: 'rgb(239, 68, 68)',
          backgroundColor: 'rgba(239, 68, 68, 0.1)',
          tension: 0.4
        },
        {
          label: 'Medium Risk',
          data: [25, 22, 28, 30, 35, 32, 38],
          borderColor: 'rgb(245, 158, 11)',
          backgroundColor: 'rgba(245, 158, 11, 0.1)',
          tension: 0.4
        },
        {
          label: 'Low Risk',
          data: [45, 48, 42, 38, 35, 40, 32],
          borderColor: 'rgb(34, 197, 94)',
          backgroundColor: 'rgba(34, 197, 94, 0.1)',
          tension: 0.4
        }
      ]
    }
  }

  const generateDeviceStatusData = () => {
    const online = sensorHealth.filter(s => s.status === 'online').length
    const offline = sensorHealth.filter(s => s.status === 'offline').length
    
    return {
      labels: ['Online', 'Offline', 'Maintenance'],
      datasets: [
        {
          data: [online, offline, 2],
          backgroundColor: [
            'rgba(34, 197, 94, 0.8)',
            'rgba(239, 68, 68, 0.8)',
            'rgba(245, 158, 11, 0.8)'
          ],
          borderColor: [
            'rgb(34, 197, 94)',
            'rgb(239, 68, 68)',
            'rgb(245, 158, 11)'
          ],
          borderWidth: 2
        }
      ]
    }
  }

  const generatePredictionAccuracyData = () => {
    const labels = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    return {
      labels,
      datasets: [
        {
          label: 'Prediction Accuracy (%)',
          data: [92, 95, 88, 94, 97, 91, 96],
          backgroundColor: 'rgba(147, 51, 234, 0.1)',
          borderColor: 'rgb(147, 51, 234)',
          borderWidth: 3,
          tension: 0.4
        },
        {
          label: 'Confidence Level (%)',
          data: [88, 90, 85, 89, 93, 87, 92],
          backgroundColor: 'rgba(59, 130, 246, 0.1)',
          borderColor: 'rgb(59, 130, 246)',
          borderWidth: 3,
          tension: 0.4
        }
      ]
    }
  }

  const generateAlertDistributionData = () => {
    const labels = ['Critical', 'High', 'Medium', 'Low', 'Info']
    return {
      labels,
      datasets: [
        {
          label: 'Alert Count',
          data: [3, 8, 15, 22, 12],
          backgroundColor: [
            'rgba(220, 38, 38, 0.8)',
            'rgba(239, 68, 68, 0.8)',
            'rgba(245, 158, 11, 0.8)',
            'rgba(34, 197, 94, 0.8)',
            'rgba(59, 130, 246, 0.8)'
          ],
          borderColor: [
            'rgb(220, 38, 38)',
            'rgb(239, 68, 68)',
            'rgb(245, 158, 11)',
            'rgb(34, 197, 94)',
            'rgb(59, 130, 246)'
          ],
          borderWidth: 1
        }
      ]
    }
  }

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top' as const,
        labels: {
          usePointStyle: true,
          padding: 20,
          font: {
            size: 12,
            weight: 'bold' as const
          }
        }
      }
    },
    scales: {
      y: {
        beginAtZero: true,
        grid: {
          color: 'rgba(0, 0, 0, 0.1)'
        },
        ticks: {
          font: {
            size: 11
          }
        }
      },
      x: {
        grid: {
          color: 'rgba(0, 0, 0, 0.1)'
        },
        ticks: {
          font: {
            size: 11
          }
        }
      }
    }
  }

  const doughnutOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'bottom' as const,
        labels: {
          usePointStyle: true,
          padding: 15,
          font: {
            size: 12,
            weight: 'bold' as const
          }
        }
      }
    }
  }

  useEffect(() => {
    loadDashboardData()
    // Refresh data every 30 seconds
    const interval = setInterval(loadDashboardData, 30000)
    return () => clearInterval(interval)
  }, [])

  useEffect(() => {
    applyFilters()
  }, [predictions, alerts, timeFilter, riskFilter])

  const applyFilters = () => {
    let filteredPreds = [...predictions]
    let filteredAlts = [...alerts]

    // Apply time filter
    const now = new Date()
    const timeThresholds = {
      '24h': 24 * 60 * 60 * 1000,
      '7d': 7 * 24 * 60 * 60 * 1000,
      '30d': 30 * 24 * 60 * 60 * 1000,
      '90d': 90 * 24 * 60 * 60 * 1000
    }
    
    const threshold = now.getTime() - timeThresholds[timeFilter]
    filteredPreds = filteredPreds.filter(p => new Date(p.timestamp).getTime() > threshold)
    filteredAlts = filteredAlts.filter(a => new Date(a.timestamp).getTime() > threshold)

    // Apply risk filter
    if (riskFilter !== 'all') {
      filteredPreds = filteredPreds.filter(p => p.risk_level.toLowerCase() === riskFilter)
    }

    setFilteredPredictions(filteredPreds)
    setFilteredAlerts(filteredAlts)
  }

  const loadDashboardData = async () => {
    try {
      setLoading(true)
      setError(null)
      
      const [statsData, predictionsData, alertsData] = await Promise.all([
        testDashboardAPI.getStats(),
        testDashboardAPI.getPredictionSummary(),
        testDashboardAPI.getRecentAlerts()
      ])

      setStats(statsData)
      setPredictions(predictionsData)
      setAlerts(alertsData)

      // Mock additional data for enhanced features
      setSensorHealth([
        { device_id: 'SEIS_001', status: 'online', health: 98, last_update: new Date() },
        { device_id: 'PORE_001', status: 'online', health: 95, last_update: new Date() },
        { device_id: 'TEMP_001', status: 'warning', health: 82, last_update: new Date() },
        { device_id: 'RAIN_001', status: 'offline', health: 0, last_update: new Date(Date.now() - 3600000) }
      ])

      setEventTimeline([
        { time: new Date(), type: 'prediction', message: 'High risk prediction generated for Site-001' },
        { time: new Date(Date.now() - 1800000), type: 'alert', message: 'Sensor PORE_001 detected pressure spike' },
        { time: new Date(Date.now() - 3600000), type: 'maintenance', message: 'TEMP_001 sensor maintenance completed' },
        { time: new Date(Date.now() - 7200000), type: 'prediction', message: 'Medium risk prediction for Site-002' }
      ])

    } catch (err) {
      console.error('Error loading dashboard data:', err)
      setError('Failed to load dashboard data')
    } finally {
      setLoading(false)
    }
  }

  const getRiskLevelColor = (level: string) => {
    switch (level.toLowerCase()) {
      case 'high': return 'text-red-600'
      case 'medium': return 'text-orange-600'
      case 'low': return 'text-green-600'
      default: return 'text-gray-600'
    }
  }

  const getSeverityColor = (severity: string) => {
    switch (severity.toLowerCase()) {
      case 'critical': return 'bg-red-100 text-red-800'
      case 'high': return 'bg-orange-100 text-orange-800'
      case 'medium': return 'bg-yellow-100 text-yellow-800'
      case 'low': return 'bg-green-100 text-green-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  if (loading && !stats) {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center relative">
        <div className="absolute inset-0 bg-gradient-to-br from-blue-50/30 via-purple-50/20 to-cyan-50/30"></div>
        <div className="relative backdrop-blur-lg bg-white/20 border border-white/30 rounded-3xl p-12 shadow-2xl">
          <div className="animate-spin rounded-full h-16 w-16 border-4 border-transparent border-t-blue-600 border-r-purple-600 mx-auto"></div>
          <div className="mt-4 text-lg font-semibold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent text-center">
            Loading Dashboard...
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-white relative">
      <div className="absolute inset-0 bg-gradient-to-br from-blue-50/20 via-purple-50/10 to-cyan-50/20"></div>
      <div className="relative z-10">
        {/* Navigation */}
        <Navbar />

        <main className="max-w-7xl mx-auto py-3 sm:px-6 lg:px-8">
          <div className="px-4 py-3 sm:px-0">
            {/* Header with Filters */}
            <div className="mb-4">
              <div className="flex flex-row items-center justify-end w-full">
                <div className="flex items-center space-x-4">
                  <button
                    onClick={() => setShowFilters(!showFilters)}
                    className="group inline-flex items-center px-6 py-3 border border-white/30 rounded-2xl shadow-lg text-sm font-medium text-gray-700 bg-white/40 backdrop-blur-lg hover:bg-white/60 hover:scale-105 transform transition-all duration-300"
                  >
                    <span className="mr-2 group-hover:rotate-12 transition-transform duration-300">🔍</span>
                    Filters
                  </button>
                  <button 
                    onClick={loadDashboardData}
                    className="group inline-flex items-center px-6 py-3 border border-transparent rounded-2xl shadow-lg text-sm font-medium text-white bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 hover:scale-105 transform transition-all duration-300"
                  >
                    <span className="mr-2 group-hover:rotate-180 transition-transform duration-500">🔄</span>
                    Refresh
                  </button>
                </div>
              </div>

              {/* Filter Panel */}
              {showFilters && (
                <div className="mt-3 backdrop-blur-lg bg-white/40 border border-white/50 rounded-2xl p-4 shadow-xl">
                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Time Range</label>
                      <select
                        value={timeFilter}
                        onChange={(e) => setTimeFilter(e.target.value as any)}
                        className="w-full border border-white/30 rounded-xl px-4 py-3 text-sm bg-white/50 backdrop-blur-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-300"
                      >
                        <option value="24h">Last 24 Hours</option>
                        <option value="7d">Last 7 Days</option>
                        <option value="30d">Last 30 Days</option>
                        <option value="90d">Last 90 Days</option>
                      </select>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Risk Level</label>
                      <select
                        value={riskFilter}
                        onChange={(e) => setRiskFilter(e.target.value as any)}
                        className="w-full border border-white/30 rounded-xl px-4 py-3 text-sm bg-white/50 backdrop-blur-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-300"
                      >
                        <option value="all">All Risk Levels</option>
                        <option value="high">High Risk Only</option>
                        <option value="medium">Medium Risk Only</option>
                        <option value="low">Low Risk Only</option>
                      </select>
                    </div>
                    <div className="flex items-end">
                      <div className="text-sm text-gray-600 font-medium backdrop-blur-lg bg-white/30 px-4 py-2 rounded-xl border border-white/40">
                        Showing {filteredPredictions.length} predictions, {filteredAlerts.length} alerts
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Error State */}
            {error && (
              <div className="backdrop-blur-lg bg-red-50/80 border border-red-200/50 rounded-2xl p-4 shadow-xl mb-3">
                <div className="text-red-700 font-medium">{error}</div>
                <button 
                  onClick={loadDashboardData}
                  className="mt-2 text-red-800 underline hover:text-red-900 font-medium"
                >
                  Retry
                </button>
              </div>
            )}

          {/* Stats Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-4">
            <div className="group backdrop-blur-lg bg-white/40 border border-white/50 p-5 rounded-3xl shadow-xl hover:shadow-2xl hover:scale-105 transform transition-all duration-300">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <div className="w-10 h-10 bg-gradient-to-br from-orange-400/20 to-orange-600/20 rounded-2xl flex items-center justify-center backdrop-blur-sm border border-orange-200/30 group-hover:scale-110 transition-transform duration-300">
                    <span className="text-lg">⚠️</span>
                  </div>
                </div>
                <div className="ml-3">
                  <h3 className="text-xs font-semibold text-gray-700 uppercase tracking-wider">Current Risk Level</h3>
                  <p className={`text-2xl font-bold mt-1 ${getRiskLevelColor(stats?.current_risk_level || 'unknown')}`}>
                    {stats?.current_risk_level || 'Loading...'}
                  </p>
                </div>
              </div>
            </div>

            <div className="group backdrop-blur-lg bg-white/40 border border-white/50 p-5 rounded-3xl shadow-xl hover:shadow-2xl hover:scale-105 transform transition-all duration-300">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <div className="w-10 h-10 bg-gradient-to-br from-red-400/20 to-red-600/20 rounded-2xl flex items-center justify-center backdrop-blur-sm border border-red-200/30 group-hover:scale-110 transition-transform duration-300">
                    <span className="text-lg">🚨</span>
                  </div>
                </div>
                <div className="ml-3">
                  <h3 className="text-xs font-semibold text-gray-700 uppercase tracking-wider">Active Alerts</h3>
                  <p className="text-2xl font-bold text-red-600 mt-1">
                    {stats?.active_alerts || '0'}
                  </p>
                </div>
              </div>
            </div>

            <div className="group backdrop-blur-lg bg-white/40 border border-white/50 p-5 rounded-3xl shadow-xl hover:shadow-2xl hover:scale-105 transform transition-all duration-300">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <div className="w-10 h-10 bg-gradient-to-br from-green-400/20 to-green-600/20 rounded-2xl flex items-center justify-center backdrop-blur-sm border border-green-200/30 group-hover:scale-110 transition-transform duration-300">
                    <span className="text-lg">📡</span>
                  </div>
                </div>
                <div className="ml-3">
                  <h3 className="text-xs font-semibold text-gray-700 uppercase tracking-wider">Devices Online</h3>
                  <p className="text-2xl font-bold text-green-600 mt-1">
                    {stats ? `${stats.active_devices}/${stats.total_devices}` : '0/0'}
                  </p>
                </div>
              </div>
            </div>

            <div className="group backdrop-blur-lg bg-white/40 border border-white/50 p-5 rounded-3xl shadow-xl hover:shadow-2xl hover:scale-105 transform transition-all duration-300">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <div className="w-10 h-10 bg-gradient-to-br from-blue-400/20 to-blue-600/20 rounded-2xl flex items-center justify-center backdrop-blur-sm border border-blue-200/30 group-hover:scale-110 transition-transform duration-300">
                    <span className="text-lg">📊</span>
                  </div>
                </div>
                <div className="ml-3">
                  <h3 className="text-xs font-semibold text-gray-700 uppercase tracking-wider">Prediction Accuracy</h3>
                  <p className="text-2xl font-bold text-blue-600 mt-1">
                    {stats?.prediction_accuracy ? `${stats.prediction_accuracy}%` : 'N/A'}
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Main Content Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-4">
            {/* Recent Predictions */}
            <div className="backdrop-blur-lg bg-white/40 border border-white/50 rounded-3xl shadow-xl p-4">
              <div className="flex items-center justify-between mb-2">
                <h2 className="text-lg font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                  📈 Latest Predictions
                </h2>
                <span className="text-sm text-gray-600 font-medium backdrop-blur-lg bg-white/30 px-3 py-1 rounded-xl border border-white/40">
                  {filteredPredictions.length} total
                </span>
              </div>
              <div className="space-y-2">
                {filteredPredictions.length > 0 ? filteredPredictions.slice(0, 5).map((prediction) => (
                  <div key={prediction.id} className="group flex items-center justify-between p-2 border-b border-white/20 last:border-b-0 hover:bg-white/20 rounded-2xl transition-all duration-300 hover:scale-102">
                    <div className="flex-1">
                      <p className="font-semibold text-gray-800 group-hover:text-gray-900">
                        {prediction.site_name || `Site ${prediction.site_id}`}
                        {prediction.zone_id && ` - Zone ${prediction.zone_id}`}
                      </p>
                      <p className="text-sm text-gray-600 mt-1">
                        {new Date(prediction.timestamp).toLocaleString()}
                      </p>
                      <p className="text-sm text-gray-500 mt-1">
                        Confidence: {Math.round(prediction.confidence * 100)}%
                      </p>
                    </div>
                    <div className="ml-4">
                      <span className={`px-4 py-2 rounded-2xl text-sm font-semibold backdrop-blur-sm border transition-all duration-300 group-hover:scale-105
                        ${prediction.risk_level.toLowerCase() === 'high' ? 'bg-red-100/80 text-red-800 border-red-200/50' : 
                          prediction.risk_level.toLowerCase() === 'medium' ? 'bg-orange-100/80 text-orange-800 border-orange-200/50' : 
                          'bg-green-100/80 text-green-800 border-green-200/50'}`}>
                        {prediction.risk_level}
                      </span>
                    </div>
                  </div>
                )) : (
                  <div className="text-center py-8">
                    <div className="w-16 h-16 bg-gradient-to-br from-gray-100 to-gray-200 rounded-2xl flex items-center justify-center mx-auto mb-4">
                      <span className="text-2xl">📊</span>
                    </div>
                    <p className="text-gray-500 font-medium">No predictions for selected filters</p>
                  </div>
                )}
              </div>
            </div>

            {/* Recent Alerts */}
            <div className="backdrop-blur-lg bg-white/40 border border-white/50 rounded-3xl shadow-xl p-4">
              <div className="flex items-center justify-between mb-2">
                <h2 className="text-lg font-bold bg-gradient-to-r from-red-600 to-orange-600 bg-clip-text text-transparent">
                  🚨 Active Alerts
                </h2>
                <span className="text-sm text-gray-600 font-medium backdrop-blur-lg bg-white/30 px-3 py-1 rounded-xl border border-white/40">
                  {filteredAlerts.length} active
                </span>
              </div>
              <div className="space-y-2">
                {filteredAlerts.length > 0 ? filteredAlerts.slice(0, 5).map((alert) => (
                  <div key={alert.id} className="group flex items-start space-x-3 p-2 border-b border-white/20 last:border-b-0 hover:bg-white/20 rounded-2xl transition-all duration-300 hover:scale-102">
                    <div className="flex-shrink-0">
                      <div className={`w-4 h-4 rounded-full mt-1 animate-pulse
                        ${alert.severity.toLowerCase() === 'critical' ? 'bg-red-500 shadow-lg shadow-red-500/50' : 
                          alert.severity.toLowerCase() === 'high' ? 'bg-orange-500 shadow-lg shadow-orange-500/50' : 
                          alert.severity.toLowerCase() === 'medium' ? 'bg-yellow-500 shadow-lg shadow-yellow-500/50' : 
                          'bg-green-500 shadow-lg shadow-green-500/50'}`}>
                      </div>
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-semibold text-gray-800 group-hover:text-gray-900">
                        {alert.message}
                      </p>
                      <p className="text-sm text-gray-600 mt-1">
                        {alert.site_name || alert.site_id} • {new Date(alert.timestamp).toLocaleString()}
                      </p>
                      <span className={`inline-flex px-3 py-1 rounded-2xl text-xs font-semibold mt-2 backdrop-blur-sm border transition-all duration-300 group-hover:scale-105 ${getSeverityColor(alert.severity)}`}>
                        {alert.severity}
                      </span>
                    </div>
                  </div>
                )) : (
                  <div className="text-center py-8">
                    <div className="w-16 h-16 bg-gradient-to-br from-gray-100 to-gray-200 rounded-2xl flex items-center justify-center mx-auto mb-4">
                      <span className="text-2xl">🔕</span>
                    </div>
                    <p className="text-gray-500 font-medium">No active alerts</p>
                  </div>
                )}
              </div>
            </div>

            {/* Sensor Health Monitoring */}
            <div className="backdrop-blur-lg bg-white/40 border border-white/50 rounded-3xl shadow-xl p-8">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-2xl font-bold bg-gradient-to-r from-green-600 to-blue-600 bg-clip-text text-transparent">
                  📡 Sensor Health
                </h2>
                <span className="text-sm text-gray-600 font-medium backdrop-blur-lg bg-white/30 px-3 py-1 rounded-xl border border-white/40">
                  {sensorHealth.filter(s => s.status === 'online').length}/{sensorHealth.length} online
                </span>
              </div>
              <div className="space-y-4">
                {sensorHealth.map((sensor) => (
                  <div key={sensor.device_id} className="group flex items-center justify-between p-4 border-b border-white/20 last:border-b-0 hover:bg-white/20 rounded-2xl transition-all duration-300">
                    <div className="flex-1">
                      <div className="flex items-center">
                        <div className={`w-4 h-4 rounded-full mr-4 animate-pulse shadow-lg
                          ${sensor.status === 'online' ? 'bg-green-500 shadow-green-500/50' : 
                            sensor.status === 'warning' ? 'bg-yellow-500 shadow-yellow-500/50' : 
                            'bg-red-500 shadow-red-500/50'}`}>
                        </div>
                        <div>
                          <p className="font-semibold text-gray-800 group-hover:text-gray-900">{sensor.device_id}</p>
                          <p className="text-sm text-gray-600 mt-1">
                            Health: {sensor.health}% • {sensor.status}
                          </p>
                        </div>
                      </div>
                    </div>
                    <div className="ml-4">
                      <div className="w-20 bg-white/30 rounded-full h-3 backdrop-blur-sm border border-white/40">
                        <div 
                          className={`h-3 rounded-full transition-all duration-500 ${
                            sensor.health > 90 ? 'bg-gradient-to-r from-green-400 to-green-600' :
                            sensor.health > 70 ? 'bg-gradient-to-r from-yellow-400 to-yellow-600' : 'bg-gradient-to-r from-red-400 to-red-600'
                          }`}
                          style={{width: `${sensor.health}%`}}
                        ></div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Event Timeline */}
          <div className="mt-8">
            <div className="backdrop-blur-lg bg-white/40 border border-white/50 rounded-3xl shadow-xl p-8">
              <h2 className="text-2xl font-bold bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent mb-6">
                🕒 Event Timeline
              </h2>
              <div className="space-y-4">
                {eventTimeline.slice(0, 10).map((event, index) => (
                  <div key={index} className="group flex items-start space-x-4 p-4 hover:bg-white/20 rounded-2xl transition-all duration-300">
                    <div className="flex-shrink-0">
                      <div className={`w-4 h-4 rounded-full mt-2 animate-pulse shadow-lg
                        ${event.type === 'prediction' ? 'bg-blue-500 shadow-blue-500/50' :
                          event.type === 'alert' ? 'bg-red-500 shadow-red-500/50' :
                          event.type === 'maintenance' ? 'bg-green-500 shadow-green-500/50' : 'bg-gray-500 shadow-gray-500/50'}`}>
                      </div>
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-semibold text-gray-800 group-hover:text-gray-900">
                        {event.message}
                      </p>
                      <p className="text-sm text-gray-600 mt-1">
                        {event.time.toLocaleString()} • {event.type}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Charts and Analytics */}
          <div className="mt-4">
            <div className="backdrop-blur-lg bg-white/40 border border-white/50 rounded-3xl shadow-xl p-4">
              <h2 className="text-lg font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent mb-3">
                📊 Analytics & Insights
              </h2>
              
              {/* Top Row Charts */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-4">
                {/* Risk Trend Chart */}
                <div className="backdrop-blur-sm bg-white/20 rounded-2xl border border-white/30 p-3">
                  <h3 className="text-md font-semibold text-gray-800 mb-2 flex items-center">
                    📈 Risk Level Trends
                    <span className="ml-2 text-sm text-gray-600 font-normal">(Last 6 hours)</span>
                  </h3>
                  <div className="h-48">
                    <Line data={generateRiskTrendData()} options={chartOptions} />
                  </div>
                </div>

                {/* Prediction Accuracy Chart */}
                <div className="backdrop-blur-sm bg-white/20 rounded-2xl border border-white/30 p-3">
                  <h3 className="text-md font-semibold text-gray-800 mb-2 flex items-center">
                    🎯 Prediction Performance
                    <span className="ml-2 text-sm text-gray-600 font-normal">(Last 7 days)</span>
                  </h3>
                  <div className="h-48">
                    <Line data={generatePredictionAccuracyData()} options={chartOptions} />
                  </div>
                </div>
              </div>

              {/* Bottom Row Charts */}
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
                {/* Device Status Pie Chart */}
                <div className="backdrop-blur-sm bg-white/20 rounded-2xl border border-white/30 p-3">
                  <h3 className="text-md font-semibold text-gray-800 mb-2 flex items-center">
                    🔧 Device Status
                  </h3>
                  <div className="h-40">
                    <Doughnut data={generateDeviceStatusData()} options={doughnutOptions} />
                  </div>
                </div>

                {/* Alert Distribution Chart */}
                <div className="backdrop-blur-sm bg-white/20 rounded-2xl border border-white/30 p-3">
                  <h3 className="text-md font-semibold text-gray-800 mb-2 flex items-center">
                    🚨 Alert Distribution
                    <span className="ml-2 text-sm text-gray-600 font-normal">(24h)</span>
                  </h3>
                  <div className="h-40">
                    <Bar data={generateAlertDistributionData()} options={{
                      ...chartOptions,
                      plugins: {
                        ...chartOptions.plugins,
                        legend: {
                          display: false
                        }
                      }
                    }} />
                  </div>
                </div>

                {/* Quick Metrics */}
                <div className="backdrop-blur-sm bg-white/20 rounded-2xl border border-white/30 p-3">
                  <h3 className="text-md font-semibold text-gray-800 mb-2">🎛️ Quick Metrics</h3>
                  <div className="space-y-2">
                    <div className="flex justify-between items-center">
                      <span className="text-sm font-medium text-gray-700">System Uptime</span>
                      <span className="text-sm font-bold text-green-600">99.8%</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm font-medium text-gray-700">Avg Response Time</span>
                      <span className="text-sm font-bold text-blue-600">45ms</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm font-medium text-gray-700">Data Processed</span>
                      <span className="text-sm font-bold text-purple-600">2.4GB</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm font-medium text-gray-700">Predictions Today</span>
                      <span className="text-sm font-bold text-orange-600">{stats?.recent_predictions || 0}</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm font-medium text-gray-700">Active Monitors</span>
                      <span className="text-sm font-bold text-cyan-600">{sensorHealth.filter(s => s.status === 'online').length}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* System Status */}
          <div className="mt-4">
            <div className="backdrop-blur-lg bg-white/40 border border-white/50 rounded-3xl shadow-xl p-4">
              <h2 className="text-lg font-bold bg-gradient-to-r from-cyan-600 to-blue-600 bg-clip-text text-transparent mb-3">
                System Overview
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="group text-center p-3 backdrop-blur-sm bg-white/20 rounded-2xl border border-white/30 hover:scale-105 transform transition-all duration-300">
                  <h3 className="text-xs font-semibold text-gray-700 uppercase tracking-wider mb-2">Mining Sites</h3>
                  <p className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-blue-800 bg-clip-text text-transparent">{stats?.total_sites || 0}</p>
                  <p className="text-xs text-gray-600 mt-1 font-medium">Total monitored sites</p>
                </div>
                <div className="group text-center p-3 backdrop-blur-sm bg-white/20 rounded-2xl border border-white/30 hover:scale-105 transform transition-all duration-300">
                  <h3 className="text-xs font-semibold text-gray-700 uppercase tracking-wider mb-2">Total Predictions</h3>
                  <p className="text-2xl font-bold bg-gradient-to-r from-purple-600 to-purple-800 bg-clip-text text-transparent">{stats?.total_predictions || 0}</p>
                  <p className="text-xs text-gray-600 mt-1 font-medium">Lifetime predictions</p>
                </div>
                <div className="group text-center p-3 backdrop-blur-sm bg-white/20 rounded-2xl border border-white/30 hover:scale-105 transform transition-all duration-300">
                  <h3 className="text-xs font-semibold text-gray-700 uppercase tracking-wider mb-2">Recent Activity</h3>
                  <p className="text-2xl font-bold bg-gradient-to-r from-green-600 to-green-800 bg-clip-text text-transparent">{stats?.recent_predictions || 0}</p>
                  <p className="text-xs text-gray-600">Predictions in last 24h</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
      </div>
    </div>
  )
}

export default DashboardPage