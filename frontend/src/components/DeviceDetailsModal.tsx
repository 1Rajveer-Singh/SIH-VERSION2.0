import React from 'react'
import { Device, deviceTypeConfigs } from '../types/devices'

interface DeviceDetailsModalProps {
  device: Device | null
  isOpen: boolean
  onClose: () => void
}

export const DeviceDetailsModal: React.FC<DeviceDetailsModalProps> = ({
  device,
  isOpen,
  onClose
}) => {
  if (!isOpen || !device) return null

  const config = deviceTypeConfigs[device.type]

  const getStatusColor = (status: Device['status']) => {
    switch (status) {
      case 'online': return 'text-green-600 bg-green-100 border-green-200'
      case 'offline': return 'text-gray-600 bg-gray-100 border-gray-200'
      case 'maintenance': return 'text-yellow-600 bg-yellow-100 border-yellow-200'
      case 'error': return 'text-red-600 bg-red-100 border-red-200'
      default: return 'text-gray-600 bg-gray-100 border-gray-200'
    }
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString()
  }

  const formatLastReading = (timestamp?: string) => {
    if (!timestamp) return 'No data available'
    const date = new Date(timestamp)
    const now = new Date()
    const diffMs = now.getTime() - date.getTime()
    const diffMins = Math.floor(diffMs / (1000 * 60))
    
    if (diffMins < 1) return 'Just now'
    if (diffMins < 60) return `${diffMins} minutes ago`
    if (diffMins < 1440) return `${Math.floor(diffMins / 60)} hours ago`
    return `${Math.floor(diffMins / 1440)} days ago`
  }

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4" onClick={onClose}>
      <div 
        className="bg-gradient-to-br from-white/95 via-white/90 to-white/85 backdrop-blur-xl rounded-3xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto border-2 border-white/30"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="relative p-8 bg-gradient-to-r from-blue-600/10 via-purple-600/10 to-cyan-600/10 rounded-t-3xl border-b border-white/30">
          <button
            onClick={onClose}
            className="absolute top-6 right-6 w-10 h-10 bg-white/20 hover:bg-white/30 rounded-full flex items-center justify-center text-gray-600 hover:text-gray-800 transition-all duration-300 backdrop-blur-sm"
          >
            ✕
          </button>
          
          <div className="flex items-center space-x-6">
            <div className={`w-24 h-24 bg-gradient-to-br from-${config.color}-400/30 via-${config.color}-500/20 to-${config.color}-600/30 rounded-3xl flex items-center justify-center backdrop-blur-sm border-2 border-${config.color}-200/40 shadow-xl`}>
              <span className="text-4xl">{config.icon}</span>
            </div>
            <div>
              <h2 className="text-3xl font-bold bg-gradient-to-r from-gray-800 via-gray-900 to-black bg-clip-text text-transparent mb-2">
                {device.name}
              </h2>
              <p className="text-lg text-gray-700 font-semibold mb-1">{config.category}</p>
              <div className={`inline-flex items-center px-4 py-2 rounded-full text-sm font-bold ${getStatusColor(device.status)} border shadow-sm`}>
                {device.status.toUpperCase()}
              </div>
            </div>
          </div>
        </div>

        {/* Content */}
        <div className="p-8 space-y-8">
          {/* Device Purpose & Working */}
          <div className="bg-gradient-to-br from-blue-50/80 to-blue-100/60 rounded-2xl p-6 border border-blue-200/50 backdrop-blur-sm">
            <h3 className="text-xl font-bold text-blue-900 mb-3 flex items-center">
              <span className="mr-3">🎯</span>
              Device Purpose & Working
            </h3>
            <p className="text-blue-800 leading-relaxed">{device.description}</p>
            <div className="mt-4 text-sm text-blue-700">
              <strong>Notes:</strong> {device.notes || 'No additional notes available'}
            </div>
          </div>

          {/* Device Information Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Basic Information */}
            <div className="bg-gradient-to-br from-purple-50/80 to-purple-100/60 rounded-2xl p-6 border border-purple-200/50 backdrop-blur-sm">
              <h3 className="text-lg font-bold text-purple-900 mb-4 flex items-center">
                <span className="mr-3">📋</span>
                Basic Information
              </h3>
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-purple-700 font-medium">Device ID:</span>
                  <span className="text-purple-900 font-semibold">{device.id}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-purple-700 font-medium">Type:</span>
                  <span className="text-purple-900 font-semibold">{device.type}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-purple-700 font-medium">Category:</span>
                  <span className="text-purple-900 font-semibold">{device.category}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-purple-700 font-medium">Enabled:</span>
                  <span className={`font-semibold ${device.enabled ? 'text-green-600' : 'text-red-600'}`}>
                    {device.enabled ? 'Yes' : 'No'}
                  </span>
                </div>
              </div>
            </div>

            {/* Status & Performance */}
            <div className="bg-gradient-to-br from-green-50/80 to-green-100/60 rounded-2xl p-6 border border-green-200/50 backdrop-blur-sm">
              <h3 className="text-lg font-bold text-green-900 mb-4 flex items-center">
                <span className="mr-3">📊</span>
                Status & Performance
              </h3>
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-green-700 font-medium">Last Reading:</span>
                  <span className="text-green-900 font-semibold">{formatLastReading(device.lastReading)}</span>
                </div>

              </div>
            </div>
          </div>

          {/* Location Information */}
          {device.location && (
            <div className="bg-gradient-to-br from-orange-50/80 to-orange-100/60 rounded-2xl p-6 border border-orange-200/50 backdrop-blur-sm">
              <h3 className="text-lg font-bold text-orange-900 mb-4 flex items-center">
                <span className="mr-3">📍</span>
                Location Information
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="text-center">
                  <span className="text-orange-700 font-medium block">Latitude</span>
                  <span className="text-orange-900 font-bold text-lg">{device.location.latitude.toFixed(6)}</span>
                </div>
                <div className="text-center">
                  <span className="text-orange-700 font-medium block">Longitude</span>
                  <span className="text-orange-900 font-bold text-lg">{device.location.longitude.toFixed(6)}</span>
                </div>
                {device.location.elevation && (
                  <div className="text-center">
                    <span className="text-orange-700 font-medium block">Elevation</span>
                    <span className="text-orange-900 font-bold text-lg">{device.location.elevation}m</span>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Measurement Fields */}
          <div className="bg-gradient-to-br from-cyan-50/80 to-cyan-100/60 rounded-2xl p-6 border border-cyan-200/50 backdrop-blur-sm">
            <h3 className="text-lg font-bold text-cyan-900 mb-4 flex items-center">
              <span className="mr-3">🔬</span>
              Measurement Fields
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {device.fields.map((field, index) => (
                <div key={index} className="bg-white/60 rounded-xl p-4 border border-cyan-200/30 backdrop-blur-sm">
                  <div className="flex justify-between items-start mb-2">
                    <h4 className="text-cyan-900 font-bold capitalize">{field.name}</h4>
                    {field.required && (
                      <span className="text-xs bg-red-100 text-red-600 px-2 py-1 rounded-full font-semibold">Required</span>
                    )}
                  </div>
                  <p className="text-cyan-800 text-sm mb-2">{field.description}</p>
                  <div className="flex justify-between text-xs">
                    <span className="text-cyan-700">Unit: <strong>{field.unit || 'N/A'}</strong></span>
                    <span className="text-cyan-700">Type: <strong>{field.type}</strong></span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Configuration & API */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Configuration */}
            <div className="bg-gradient-to-br from-indigo-50/80 to-indigo-100/60 rounded-2xl p-6 border border-indigo-200/50 backdrop-blur-sm">
              <h3 className="text-lg font-bold text-indigo-900 mb-4 flex items-center">
                <span className="mr-3">⚙️</span>
                Configuration
              </h3>
              <div className="space-y-3">
                {Object.entries(device.configuration).map(([key, value]) => (
                  <div key={key} className="flex justify-between items-center">
                    <span className="text-indigo-700 font-medium capitalize">{key.replace(/([A-Z])/g, ' $1')}:</span>
                    <span className="text-indigo-900 font-semibold">{value?.toString() || 'N/A'}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* API & CSV Information */}
            <div className="bg-gradient-to-br from-pink-50/80 to-pink-100/60 rounded-2xl p-6 border border-pink-200/50 backdrop-blur-sm">
              <h3 className="text-lg font-bold text-pink-900 mb-4 flex items-center">
                <span className="mr-3">🔗</span>
                API & Data Import
              </h3>
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-pink-700 font-medium">CSV Import:</span>
                  <span className={`font-semibold ${device.csvImportEnabled ? 'text-green-600' : 'text-red-600'}`}>
                    {device.csvImportEnabled ? 'Enabled' : 'Disabled'}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-pink-700 font-medium">API Endpoint:</span>
                  <span className="text-pink-900 font-semibold text-xs bg-white/60 px-2 py-1 rounded">
                    {device.apiEndpoint || 'Not configured'}
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* Timeline */}
          <div className="bg-gradient-to-br from-gray-50/80 to-gray-100/60 rounded-2xl p-6 border border-gray-200/50 backdrop-blur-sm">
            <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center">
              <span className="mr-3">⏰</span>
              Timeline
            </h3>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-gray-700 font-medium">Created:</span>
                <span className="text-gray-900 font-semibold">{formatDate(device.createdAt)}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-700 font-medium">Last Updated:</span>
                <span className="text-gray-900 font-semibold">{formatDate(device.updatedAt)}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}