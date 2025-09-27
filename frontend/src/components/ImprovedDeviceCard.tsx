import React from 'react'
import { Device, deviceTypeConfigs } from '../types/devices'

interface ImprovedDeviceCardProps {
  device: Device
  onShowDetails: (device: Device) => void
}

export const ImprovedDeviceCard: React.FC<ImprovedDeviceCardProps> = ({
  device,
  onShowDetails
}) => {
  const config = deviceTypeConfigs[device.type as keyof typeof deviceTypeConfigs]
  
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'online':
      case 'active': 
        return 'text-emerald-400 bg-emerald-400/20 border-emerald-400/30'
      case 'offline':
      case 'inactive': 
        return 'text-red-400 bg-red-400/20 border-red-400/30'
      case 'maintenance': 
        return 'text-yellow-400 bg-yellow-400/20 border-yellow-400/30'
      case 'error': 
        return 'text-orange-400 bg-orange-400/20 border-orange-400/30'
      default: 
        return 'text-gray-400 bg-gray-400/20 border-gray-400/30'
    }
  }





  return (
    <div className="group relative">
      {/* Main Card */}
      <div className="relative bg-gradient-to-br from-white/10 via-white/5 to-transparent backdrop-blur-xl border border-white/20 rounded-3xl p-6 transition-all duration-500 hover:scale-105 hover:shadow-2xl hover:shadow-blue-500/20 hover:border-blue-400/40 overflow-hidden">
        
        {/* Background Gradient Overlay */}
        <div className="absolute inset-0 bg-gradient-to-br from-blue-500/5 via-purple-500/5 to-cyan-500/5 rounded-3xl"></div>
        
        {/* Device Header */}
        <div className="relative z-10 flex items-start justify-between mb-4">
          <div className="flex items-center space-x-3">
            <div className="text-3xl p-2 rounded-2xl bg-gradient-to-br from-blue-500/20 to-purple-500/20 backdrop-blur-sm border border-white/20">
              {config.icon}
            </div>
            <div>
              <h3 className="font-bold text-white text-lg leading-tight">{device.name}</h3>
              <p className="text-sm text-slate-300 font-medium">{config.category}</p>
              <p className="text-xs text-slate-400 mt-1">{device.category}</p>
            </div>
          </div>
          
          {/* Status Badge */}
          <div className={`px-3 py-1 rounded-full text-xs font-bold border backdrop-blur-sm ${getStatusColor(device.status)}`}>
            {device.status.toUpperCase()}
          </div>
        </div>

        {/* Location Info */}
        <div className="relative z-10 mb-4">
          <div className="flex items-center text-sm text-slate-300">
            <svg className="w-4 h-4 mr-2 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
            <span className="font-medium">
              {device.location?.latitude.toFixed(4)}, {device.location?.longitude.toFixed(4)}
            </span>
            {device.location?.elevation && (
              <span className="ml-2 text-slate-400">({device.location.elevation}m)</span>
            )}
          </div>
        </div>

        {/* Performance Metrics Grid */}
        <div className="relative z-10 grid grid-cols-1 gap-4 mb-6">

        </div>

        {/* Last Reading */}
        <div className="relative z-10 mb-6">
          <div className="flex items-center justify-between text-sm">
            <span className="text-slate-400 font-medium">Last Reading</span>
            <span className="text-slate-200 font-semibold">
              {device.lastReading ? new Date(device.lastReading).toLocaleDateString('en', { 
                month: 'short', 
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
              }) : 'No data'}
            </span>
          </div>
        </div>

        {/* Action Button */}
        <div className="relative z-10">
          <button
            onClick={() => onShowDetails(device)}
            className="w-full bg-gradient-to-r from-blue-600/30 via-purple-600/30 to-cyan-600/30 hover:from-blue-600/50 hover:via-purple-600/50 hover:to-cyan-600/50 border border-blue-400/40 hover:border-blue-400/60 text-white font-bold py-3 px-6 rounded-2xl transition-all duration-300 hover:scale-[1.02] hover:shadow-lg hover:shadow-blue-500/25 backdrop-blur-sm"
          >
            <span className="flex items-center justify-center space-x-2">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
              </svg>
              <span>Show Details</span>
            </span>
          </button>
        </div>

        {/* Animated Border Effect */}
        <div className="absolute inset-0 rounded-3xl opacity-0 group-hover:opacity-100 transition-opacity duration-500">
          <div className="absolute inset-0 rounded-3xl bg-gradient-to-r from-blue-500/20 via-purple-500/20 to-cyan-500/20 animate-pulse"></div>
        </div>
      </div>
    </div>
  )
}