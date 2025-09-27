import React, { useState } from 'react'
import { Device, DeviceType } from '../types/devices'

interface DeviceMonitoringProps {
  devices: Device[]
}

export const DeviceMonitoring: React.FC<DeviceMonitoringProps> = ({ devices }) => {
  const [showDetails, setShowDetails] = useState(false)

  const getHealthScore = () => {
    const totalDevices = devices.length
    if (totalDevices === 0) return 100

    const healthyDevices = devices.filter(d => 
      d.status === 'online' && 
      d.enabled
    ).length

    return Math.round((healthyDevices / totalDevices) * 100)
  }

  const getAlerts = () => {
    const alerts = []

    // Error alerts
    const errorDevices = devices.filter(d => d.status === 'error')
    if (errorDevices.length > 0) {
      alerts.push({
        type: 'error',
        message: `${errorDevices.length} device(s) with errors`,
        devices: errorDevices.map(d => d.name)
      })
    }

    // Offline alerts
    const offlineDevices = devices.filter(d => d.status === 'offline' && d.enabled)
    if (offlineDevices.length > 0) {
      alerts.push({
        type: 'error',
        message: `${offlineDevices.length} enabled device(s) offline`,
        devices: offlineDevices.map(d => d.name)
      })
    }

    return alerts
  }

  const healthScore = getHealthScore()
  const alerts = getAlerts()

  const getHealthColor = (score: number) => {
    if (score >= 80) return 'text-green-600 bg-green-100'
    if (score >= 60) return 'text-yellow-600 bg-yellow-100'
    return 'text-red-600 bg-red-100'
  }

  return (
    <div className="backdrop-blur-lg bg-white/60 border border-white/50 rounded-2xl p-6 shadow-xl mb-8">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-bold text-gray-800">System Health Monitoring</h3>
        <button
          onClick={() => setShowDetails(!showDetails)}
          className="text-blue-600 hover:text-blue-800 font-medium text-sm transition-colors"
        >
          {showDetails ? 'Hide Details' : 'Show Details'}
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Health Score */}
        <div className="text-center">
          <div className={`inline-flex items-center justify-center w-20 h-20 rounded-full text-2xl font-bold ${getHealthColor(healthScore)}`}>
            {healthScore}%
          </div>
          <p className="text-sm text-gray-600 mt-2 font-medium">System Health</p>
        </div>

        {/* Quick Stats */}
        <div className="space-y-2">
          <div className="flex justify-between text-sm">
            <span className="text-gray-600">Active Devices:</span>
            <span className="font-semibold text-green-600">{devices.filter(d => d.status === 'online').length}</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-gray-600">Issues Detected:</span>
            <span className="font-semibold text-red-600">{alerts.length}</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-gray-600">Data Collection:</span>
            <span className="font-semibold text-blue-600">
              {devices.filter(d => d.lastReading).length}/{devices.length}
            </span>
          </div>
        </div>

        {/* Status Indicators */}
        <div className="space-y-2">
          {alerts.slice(0, 3).map((alert, index) => (
            <div key={index} className={`flex items-center space-x-2 text-xs p-2 rounded-lg ${
              alert.type === 'error' ? 'bg-red-50 text-red-700' : 'bg-yellow-50 text-yellow-700'
            }`}>
              <span>{alert.type === 'error' ? '🚨' : '⚠️'}</span>
              <span className="font-medium">{alert.message}</span>
            </div>
          ))}
          {alerts.length > 3 && (
            <div className="text-xs text-gray-500 text-center">
              +{alerts.length - 3} more alerts
            </div>
          )}
        </div>
      </div>

      {/* Detailed Alerts */}
      {showDetails && alerts.length > 0 && (
        <div className="mt-6 pt-6 border-t border-gray-200">
          <h4 className="text-sm font-semibold text-gray-700 mb-3">Detailed Alerts</h4>
          <div className="space-y-3">
            {alerts.map((alert, index) => (
              <div key={index} className={`p-3 rounded-lg border ${
                alert.type === 'error' 
                  ? 'bg-red-50 border-red-200' 
                  : 'bg-yellow-50 border-yellow-200'
              }`}>
                <div className={`font-medium text-sm mb-1 ${
                  alert.type === 'error' ? 'text-red-800' : 'text-yellow-800'
                }`}>
                  {alert.message}
                </div>
                <div className="text-xs text-gray-600">
                  Affected devices: {alert.devices.join(', ')}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

export const RefreshButton: React.FC<{
  onRefreshAll: () => void
  isLoading?: boolean
}> = ({ onRefreshAll, isLoading = false }) => {
  return (
    <button
      onClick={onRefreshAll}
      disabled={isLoading}
      className="bg-gradient-to-r from-blue-500 via-blue-600 to-blue-700 hover:from-blue-600 hover:via-blue-700 hover:to-blue-800 disabled:from-gray-400 disabled:via-gray-500 disabled:to-gray-600 text-white px-6 py-3 rounded-2xl font-bold transition-all duration-500 hover:scale-105 hover:shadow-2xl shadow-lg transform flex items-center space-x-2"
    >
      <svg 
        className={`w-5 h-5 ${isLoading ? 'animate-spin' : ''}`} 
        fill="none" 
        stroke="currentColor" 
        viewBox="0 0 24 24"
      >
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
      </svg>
      <span>{isLoading ? 'Refreshing...' : 'Refresh All'}</span>
    </button>
  )
}