import React, { useState, useEffect } from 'react'
import Navbar from '../components/Navbar'

interface ServiceStatus {
  name: string
  status: 'operational' | 'degraded' | 'outage'
  description: string
  uptime: string
  lastIncident?: string
}

interface SystemMetric {
  name: string
  value: string
  status: 'good' | 'warning' | 'critical'
  description: string
}

function ServicesPage() {
  const [services, setServices] = useState<ServiceStatus[]>([])
  const [metrics, setMetrics] = useState<SystemMetric[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadServiceData()
  }, [])

  const loadServiceData = async () => {
    // Simulate loading delay
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    setServices([
      {
        name: 'Prediction Engine',
        status: 'operational',
        description: 'AI-powered rockfall prediction service',
        uptime: '99.9%',
      },
      {
        name: 'Sensor Network',
        status: 'operational',
        description: 'Real-time sensor data collection',
        uptime: '99.7%',
      },
      {
        name: 'Database Service',
        status: 'operational',
        description: 'MongoDB data storage and retrieval',
        uptime: '99.8%',
      },
      {
        name: 'Alert System',
        status: 'degraded',
        description: 'Email and SMS notification service',
        uptime: '97.2%',
        lastIncident: '2 hours ago - Delayed notifications'
      },
      {
        name: 'Drone Integration',
        status: 'operational',
        description: 'Automated drone data processing',
        uptime: '98.9%',
      },
      {
        name: 'Report Generator',
        status: 'operational',
        description: 'PDF, CSV, and Excel report generation',
        uptime: '99.5%',
      }
    ])

    setMetrics([
      {
        name: 'API Response Time',
        value: '120ms',
        status: 'good',
        description: 'Average response time for API calls'
      },
      {
        name: 'Data Processing Rate',
        value: '1,245 records/min',
        status: 'good',
        description: 'Sensor data processing throughput'
      },
      {
        name: 'Prediction Accuracy',
        value: '94.2%',
        status: 'good',
        description: 'Historical prediction accuracy rate'
      },
      {
        name: 'Active Sensors',
        value: '127/134',
        status: 'warning',
        description: 'Currently active monitoring sensors'
      },
      {
        name: 'Storage Usage',
        value: '68%',
        status: 'good',
        description: 'Database storage utilization'
      },
      {
        name: 'Alert Delivery Time',
        value: '2.1s',
        status: 'warning',
        description: 'Average time to deliver critical alerts'
      }
    ])

    setLoading(false)
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'operational':
      case 'good':
        return 'text-green-600 bg-green-100'
      case 'degraded':
      case 'warning':
        return 'text-yellow-600 bg-yellow-100'
      case 'outage':
      case 'critical':
        return 'text-red-600 bg-red-100'
      default:
        return 'text-gray-600 bg-gray-100'
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'operational':
      case 'good':
        return '✅'
      case 'degraded':
      case 'warning':
        return '⚠️'
      case 'outage':
      case 'critical':
        return '❌'
      default:
        return '❓'
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Navbar />
        <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
          <div className="flex justify-center items-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          </div>
        </div>
      </div>
    )
  }

  const overallStatus = services.some(s => s.status === 'outage') ? 'outage' :
                       services.some(s => s.status === 'degraded') ? 'degraded' : 'operational'

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      
      <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          {/* Header */}
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900">System Services</h1>
            <p className="mt-2 text-gray-600">
              Monitor the status and performance of all system components
            </p>
          </div>

          {/* Overall Status */}
          <div className="bg-white rounded-lg shadow p-6 mb-6">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-xl font-semibold text-gray-900">Overall System Status</h2>
                <p className="text-gray-600">Current operational status of all services</p>
              </div>
              <div className="flex items-center space-x-2">
                <span className="text-2xl">{getStatusIcon(overallStatus)}</span>
                <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(overallStatus)}`}>
                  {overallStatus.charAt(0).toUpperCase() + overallStatus.slice(1)}
                </span>
              </div>
            </div>
          </div>

          {/* Services Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
            {services.map((service, index) => (
              <div key={index} className="bg-white rounded-lg shadow p-6">
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900">{service.name}</h3>
                    <p className="text-sm text-gray-600">{service.description}</p>
                  </div>
                  <span className="text-xl">{getStatusIcon(service.status)}</span>
                </div>
                
                <div className="space-y-2">
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-gray-500">Status:</span>
                    <span className={`px-2 py-1 rounded text-xs font-medium ${getStatusColor(service.status)}`}>
                      {service.status.charAt(0).toUpperCase() + service.status.slice(1)}
                    </span>
                  </div>
                  
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-gray-500">Uptime:</span>
                    <span className="text-sm font-medium text-gray-900">{service.uptime}</span>
                  </div>
                  
                  {service.lastIncident && (
                    <div className="text-xs text-yellow-600 mt-2 p-2 bg-yellow-50 rounded">
                      Last incident: {service.lastIncident}
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>

          {/* System Metrics */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-6">System Metrics</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {metrics.map((metric, index) => (
                <div key={index} className="border border-gray-200 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="text-sm font-medium text-gray-900">{metric.name}</h3>
                    <span className="text-lg">{getStatusIcon(metric.status)}</span>
                  </div>
                  <div className="text-2xl font-bold text-gray-900 mb-1">{metric.value}</div>
                  <p className="text-sm text-gray-600">{metric.description}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Service Actions */}
          <div className="bg-white rounded-lg shadow p-6 mt-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Service Management</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <button className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors">
                🔄 Refresh Status
              </button>
              <button className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors">
                🧪 Run Health Check
              </button>
              <button className="bg-yellow-600 hover:bg-yellow-700 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors">
                📊 View Logs
              </button>
              <button className="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors">
                📈 Performance Report
              </button>
            </div>
          </div>

          {/* Recent Activity */}
          <div className="bg-white rounded-lg shadow p-6 mt-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Recent Activity</h2>
            <div className="space-y-3">
              <div className="flex items-center space-x-3 text-sm">
                <span className="text-green-600">✅</span>
                <span className="text-gray-500">2 minutes ago</span>
                <span className="text-gray-900">Prediction Engine completed health check</span>
              </div>
              <div className="flex items-center space-x-3 text-sm">
                <span className="text-yellow-600">⚠️</span>
                <span className="text-gray-500">15 minutes ago</span>
                <span className="text-gray-900">Alert System experiencing delays</span>
              </div>
              <div className="flex items-center space-x-3 text-sm">
                <span className="text-green-600">✅</span>
                <span className="text-gray-500">1 hour ago</span>
                <span className="text-gray-900">Database backup completed successfully</span>
              </div>
              <div className="flex items-center space-x-3 text-sm">
                <span className="text-green-600">✅</span>
                <span className="text-gray-500">3 hours ago</span>
                <span className="text-gray-900">Sensor Network calibration completed</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default ServicesPage