import React, { useState, useEffect } from 'react'
import Navbar from '../components/Navbar'

interface Device {
  id: string
  device_id: string
  name: string
  type: 'seismic_sensor' | 'weather_station' | 'camera' | 'accelerometer' | 'tiltmeter'
  site_id: string
  site_name?: string
  zone_id?: string
  location?: {
    latitude: number
    longitude: number
    elevation?: number
  }
  status: 'online' | 'offline' | 'maintenance' | 'error'
  last_reading?: string
  battery_level?: number
  signal_strength?: number
  configuration: {
    sampling_rate: number
    sensitivity: number
    alert_threshold: number
  }
  created_at: string
  updated_at?: string
}

interface SensorReading {
  timestamp: string
  readings: Record<string, number>
  quality_score?: number
  anomaly_detected: boolean
}

function DevicesPage() {
  const [devices, setDevices] = useState<Device[]>([])
  const [selectedDevice, setSelectedDevice] = useState<Device | null>(null)
  const [readings, setReadings] = useState<SensorReading[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [showCalibrationModal, setShowCalibrationModal] = useState(false)
  const [calibrating, setCalibrating] = useState(false)

  // Mock data for demonstration
  useEffect(() => {
    loadDevices()
  }, [])

  const loadDevices = async () => {
    try {
      setLoading(true)
      setError(null)
      
      // Mock data - in real app this would call the API
      const mockDevices: Device[] = [
        {
          id: 'dev-001',
          device_id: 'SEIS_001',
          name: 'Seismic Sensor Alpha',
          type: 'seismic_sensor',
          site_id: 'site-001',
          site_name: 'Colorado Mining District - Sector A',
          zone_id: 'zone-1',
          location: { latitude: 39.7392, longitude: -104.9903, elevation: 1609 },
          status: 'online',
          last_reading: '2024-09-21T10:30:00Z',
          battery_level: 87,
          signal_strength: 92,
          configuration: {
            sampling_rate: 100,
            sensitivity: 0.05,
            alert_threshold: 0.8
          },
          created_at: '2023-01-15T10:00:00Z',
          updated_at: '2024-09-21T10:30:00Z'
        },
        {
          id: 'dev-002',
          device_id: 'WEATHER_001',
          name: 'Weather Station Beta',
          type: 'weather_station',
          site_id: 'site-001',
          site_name: 'Colorado Mining District - Sector A',
          zone_id: 'zone-2',
          location: { latitude: 39.7395, longitude: -104.9905, elevation: 1620 },
          status: 'online',
          last_reading: '2024-09-21T10:25:00Z',
          battery_level: 94,
          signal_strength: 88,
          configuration: {
            sampling_rate: 60,
            sensitivity: 1.0,
            alert_threshold: 0.9
          },
          created_at: '2023-02-01T08:00:00Z',
          updated_at: '2024-09-21T10:25:00Z'
        },
        {
          id: 'dev-003',
          device_id: 'CAM_001',
          name: 'Security Camera Gamma',
          type: 'camera',
          site_id: 'site-002',
          site_name: 'Nevada Gold Fields - Sector B',
          zone_id: 'zone-4',
          location: { latitude: 39.1612, longitude: -119.7674, elevation: 1372 },
          status: 'maintenance',
          last_reading: '2024-09-20T15:45:00Z',
          battery_level: 23,
          signal_strength: 76,
          configuration: {
            sampling_rate: 30,
            sensitivity: 0.7,
            alert_threshold: 0.6
          },
          created_at: '2023-03-15T14:00:00Z',
          updated_at: '2024-09-20T15:45:00Z'
        },
        {
          id: 'dev-004',
          device_id: 'ACCEL_001',
          name: 'Accelerometer Delta',
          type: 'accelerometer',
          site_id: 'site-001',
          site_name: 'Colorado Mining District - Sector A',
          zone_id: 'zone-3',
          status: 'error',
          last_reading: '2024-09-19T22:10:00Z',
          battery_level: 0,
          signal_strength: 0,
          configuration: {
            sampling_rate: 200,
            sensitivity: 0.01,
            alert_threshold: 1.5
          },
          created_at: '2023-04-01T09:00:00Z',
          updated_at: '2024-09-19T22:10:00Z'
        },
        {
          id: 'dev-005',
          device_id: 'TILT_001',
          name: 'Tiltmeter Epsilon',
          type: 'tiltmeter',
          site_id: 'site-002',
          site_name: 'Nevada Gold Fields - Sector B',
          zone_id: 'zone-5',
          status: 'online',
          last_reading: '2024-09-21T10:28:00Z',
          battery_level: 78,
          signal_strength: 91,
          configuration: {
            sampling_rate: 10,
            sensitivity: 0.001,
            alert_threshold: 0.5
          },
          created_at: '2023-05-10T11:00:00Z',
          updated_at: '2024-09-21T10:28:00Z'
        }
      ]
      
      setDevices(mockDevices)
    } catch (err) {
      console.error('Error loading devices:', err)
      setError('Failed to load devices')
    } finally {
      setLoading(false)
    }
  }

  const calibrateDevice = async (deviceId: string) => {
    try {
      setCalibrating(true)
      // Mock API call
      await new Promise(resolve => setTimeout(resolve, 3000))
      
      // Update device status
      setDevices(devices.map(device => 
        device.id === deviceId 
          ? { ...device, status: 'online' as const, updated_at: new Date().toISOString() }
          : device
      ))
      
      setShowCalibrationModal(false)
      alert('Device calibration completed successfully!')
    } catch (err) {
      setError('Failed to calibrate device')
    } finally {
      setCalibrating(false)
    }
  }

  const restartDevice = async (deviceId: string) => {
    try {
      // Mock API call
      await new Promise(resolve => setTimeout(resolve, 2000))
      
      // Update device status
      setDevices(devices.map(device => 
        device.id === deviceId 
          ? { ...device, status: 'online' as const, updated_at: new Date().toISOString() }
          : device
      ))
      
      alert('Device restarted successfully!')
    } catch (err) {
      setError('Failed to restart device')
    }
  }

  const loadDeviceReadings = async (device: Device) => {
    try {
      // Mock sensor readings
      const mockReadings: SensorReading[] = [
        {
          timestamp: '2024-09-21T10:30:00Z',
          readings: { vibration: 0.45, temperature: 18.5, humidity: 62 },
          quality_score: 0.95,
          anomaly_detected: false
        },
        {
          timestamp: '2024-09-21T10:25:00Z',
          readings: { vibration: 0.52, temperature: 18.3, humidity: 63 },
          quality_score: 0.92,
          anomaly_detected: false
        },
        {
          timestamp: '2024-09-21T10:20:00Z',
          readings: { vibration: 0.38, temperature: 18.7, humidity: 61 },
          quality_score: 0.98,
          anomaly_detected: false
        },
        {
          timestamp: '2024-09-21T10:15:00Z',
          readings: { vibration: 1.25, temperature: 18.2, humidity: 64 },
          quality_score: 0.87,
          anomaly_detected: true
        }
      ]
      setReadings(mockReadings)
    } catch (err) {
      console.error('Error loading readings:', err)
    }
  }

  const getDeviceTypeIcon = (type: string) => {
    switch (type) {
      case 'seismic_sensor': return '🌊'
      case 'weather_station': return '🌤️'
      case 'camera': return '📹'
      case 'accelerometer': return '📱'
      case 'tiltmeter': return '📐'
      default: return '📡'
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'online': return 'bg-green-100 text-green-800 border-green-200'
      case 'offline': return 'bg-gray-100 text-gray-800 border-gray-200'
      case 'maintenance': return 'bg-yellow-100 text-yellow-800 border-yellow-200'
      case 'error': return 'bg-red-100 text-red-800 border-red-200'
      default: return 'bg-gray-100 text-gray-800 border-gray-200'
    }
  }

  const getBatteryColor = (level?: number) => {
    if (!level) return 'text-gray-500'
    if (level > 60) return 'text-green-600'
    if (level > 30) return 'text-yellow-600'
    return 'text-red-600'
  }

  const getSignalColor = (strength?: number) => {
    if (!strength) return 'text-gray-500'
    if (strength > 80) return 'text-green-600'
    if (strength > 50) return 'text-yellow-600'
    return 'text-red-600'
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-white relative">
        <div className="absolute inset-0 bg-gradient-to-br from-blue-50/30 via-purple-50/20 to-cyan-50/30"></div>
        <Navbar />
        <div className="relative z-10 flex items-center justify-center py-12">
          <div className="backdrop-blur-lg bg-white/20 border border-white/30 rounded-3xl p-12 shadow-2xl">
            <div className="animate-spin rounded-full h-16 w-16 border-4 border-transparent border-t-blue-600 border-r-purple-600 mx-auto"></div>
            <div className="mt-4 text-lg font-semibold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent text-center">
              Loading Devices...
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-white relative">
      <div className="absolute inset-0 bg-gradient-to-br from-blue-50/20 via-purple-50/10 to-cyan-50/20"></div>
      <div className="relative z-10">
        <Navbar />

        {/* Header */}
        <div className="backdrop-blur-lg bg-white/30 border-b border-white/40 shadow-xl">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="py-8">
            <div className="flex items-center justify-between">
              <div className="backdrop-blur-lg bg-white/30 border border-white/40 rounded-2xl p-6 shadow-xl">
                <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 via-purple-600 to-cyan-600 bg-clip-text text-transparent flex items-center">
                  📱 Device Management
                </h1>
                <p className="mt-2 text-gray-600 font-medium">
                  Monitor and control all mining site devices and sensors
                </p>
              </div>
              <button
                onClick={loadDevices}
                className="group bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white px-6 py-3 rounded-2xl font-semibold transition-all duration-300 hover:scale-105 shadow-lg"
              >
                <span className="mr-2 group-hover:rotate-180 transition-transform duration-500">🔄</span>
                Refresh Devices
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Error Display */}
        {error && (
          <div className="backdrop-blur-lg bg-red-50/80 border border-red-200/50 rounded-2xl p-6 shadow-xl mb-8">
            <div className="text-red-700 font-medium">{error}</div>
            <button 
              onClick={() => setError(null)}
              className="mt-2 text-red-800 underline hover:text-red-900 font-medium"
            >
              Dismiss
            </button>
          </div>
        )}

        {/* Device Overview Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="group backdrop-blur-lg bg-white/40 border border-white/50 p-5 rounded-3xl shadow-xl hover:shadow-2xl hover:scale-105 transform transition-all duration-300">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="w-10 h-10 bg-gradient-to-br from-blue-400/20 to-blue-600/20 rounded-2xl flex items-center justify-center backdrop-blur-sm border border-blue-200/30 group-hover:scale-110 transition-transform duration-300">
                  <span className="text-lg">📱</span>
                </div>
              </div>
              <div className="ml-3">
                <h3 className="text-xs font-semibold text-gray-700 uppercase tracking-wider">Total Devices</h3>
                <p className="text-2xl font-bold text-blue-600 mt-1">{devices.length}</p>
              </div>
            </div>
          </div>
          
          <div className="group backdrop-blur-lg bg-white/40 border border-white/50 p-5 rounded-3xl shadow-xl hover:shadow-2xl hover:scale-105 transform transition-all duration-300">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="w-10 h-10 bg-gradient-to-br from-green-400/20 to-green-600/20 rounded-2xl flex items-center justify-center backdrop-blur-sm border border-green-200/30 group-hover:scale-110 transition-transform duration-300">
                  <span className="text-lg">✅</span>
                </div>
              </div>
              <div className="ml-3">
                <h3 className="text-xs font-semibold text-gray-700 uppercase tracking-wider">Online</h3>
                <p className="text-2xl font-bold text-green-600 mt-1">
                  {devices.filter(d => d.status === 'online').length}
                </p>
              </div>
            </div>
          </div>

          <div className="group backdrop-blur-lg bg-white/40 border border-white/50 p-5 rounded-3xl shadow-xl hover:shadow-2xl hover:scale-105 transform transition-all duration-300">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="w-10 h-10 bg-gradient-to-br from-red-400/20 to-red-600/20 rounded-2xl flex items-center justify-center backdrop-blur-sm border border-red-200/30 group-hover:scale-110 transition-transform duration-300">
                  <span className="text-lg">⚠️</span>
                </div>
              </div>
              <div className="ml-3">
                <h3 className="text-xs font-semibold text-gray-700 uppercase tracking-wider">Issues</h3>
                <p className="text-2xl font-bold text-red-600 mt-1">
                  {devices.filter(d => d.status === 'error' || d.status === 'offline').length}
                </p>
              </div>
            </div>
          </div>

          <div className="group backdrop-blur-lg bg-white/40 border border-white/50 p-5 rounded-3xl shadow-xl hover:shadow-2xl hover:scale-105 transform transition-all duration-300">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="w-10 h-10 bg-gradient-to-br from-yellow-400/20 to-yellow-600/20 rounded-2xl flex items-center justify-center backdrop-blur-sm border border-yellow-200/30 group-hover:scale-110 transition-transform duration-300">
                  <span className="text-lg">🔧</span>
                </div>
              </div>
              <div className="ml-3">
                <h3 className="text-xs font-semibold text-gray-700 uppercase tracking-wider">Maintenance</h3>
                <p className="text-2xl font-bold text-yellow-600 mt-1">
                  {devices.filter(d => d.status === 'maintenance').length}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Devices Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-8">
          {devices.map((device) => (
            <div key={device.id} className="group backdrop-blur-lg bg-white/40 border border-white/50 rounded-3xl shadow-xl hover:shadow-2xl hover:scale-102 transform transition-all duration-300">
              <div className="p-6">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center">
                    <div className="text-2xl mr-3 group-hover:scale-110 transition-transform duration-300">
                      {getDeviceTypeIcon(device.type)}
                    </div>
                    <div>
                      <h3 className="text-lg font-bold text-gray-800 group-hover:text-gray-900">
                        {device.name}
                      </h3>
                      <p className="text-sm text-gray-600 mt-1 font-medium">
                        {device.device_id} • {device.type.replace('_', ' ')}
                      </p>
                    </div>
                  </div>
                  <span className={`px-3 py-1 rounded-2xl text-xs font-semibold border backdrop-blur-sm transition-all duration-300 group-hover:scale-105 ${getStatusColor(device.status)}`}>
                    {device.status}
                  </span>
                </div>

                {/* Site and Location Info */}
                <div className="mb-4">
                  <p className="text-sm text-gray-700 font-medium">
                    📍 {device.site_name}
                    {device.zone_id && ` • Zone ${device.zone_id}`}
                  </p>
                  {device.location && (
                    <p className="text-xs text-gray-600 mt-1">
                      {device.location.latitude.toFixed(4)}, {device.location.longitude.toFixed(4)}
                    </p>
                  )}
                </div>

                {/* Device Metrics */}
                <div className="grid grid-cols-2 gap-3 mb-4">
                  <div className="backdrop-blur-sm bg-white/30 rounded-xl p-2 border border-white/40">
                    <p className="text-xs text-gray-600 font-medium uppercase tracking-wider">Battery Level</p>
                    <p className={`text-sm font-bold mt-1 ${getBatteryColor(device.battery_level)}`}>
                      {device.battery_level ? `${device.battery_level}%` : 'N/A'}
                    </p>
                  </div>
                  <div className="backdrop-blur-sm bg-white/30 rounded-xl p-3 border border-white/40">
                    <p className="text-xs text-gray-600 font-medium uppercase tracking-wider">Signal Strength</p>
                    <p className={`text-sm font-bold mt-1 ${getSignalColor(device.signal_strength)}`}>
                      {device.signal_strength ? `${device.signal_strength}%` : 'N/A'}
                    </p>
                  </div>
                </div>

                {/* Last Reading */}
                {device.last_reading && (
                  <div className="mb-4">
                    <p className="text-xs text-gray-600 font-medium uppercase tracking-wider">Last Reading</p>
                    <p className="text-sm text-gray-700 font-medium mt-1">
                      {new Date(device.last_reading).toLocaleString()}
                    </p>
                  </div>
                )}

                {/* Configuration Summary */}
                <div className="mb-4 backdrop-blur-sm bg-white/30 rounded-2xl p-3 border border-white/40">
                  <p className="text-xs text-gray-600 font-medium uppercase tracking-wider mb-2">Configuration</p>
                  <div className="text-xs text-gray-700 space-y-1">
                    <div className="flex justify-between font-medium">
                      <span>Sampling Rate:</span>
                      <span className="text-blue-600">{device.configuration.sampling_rate}Hz</span>
                    </div>
                    <div className="flex justify-between font-medium">
                      <span>Sensitivity:</span>
                      <span className="text-purple-600">{device.configuration.sensitivity}</span>
                    </div>
                    <div className="flex justify-between font-medium">
                      <span>Alert Threshold:</span>
                      <span className="text-orange-600">{device.configuration.alert_threshold}</span>
                    </div>
                  </div>
                </div>

                {/* Action Buttons */}
                <div className="flex space-x-3">
                  <button
                    onClick={() => {
                      setSelectedDevice(device)
                      loadDeviceReadings(device)
                    }}
                    className="group flex-1 backdrop-blur-sm bg-blue-50/80 hover:bg-blue-100/80 text-blue-700 px-4 py-3 rounded-2xl text-sm font-semibold transition-all duration-300 hover:scale-105 border border-blue-200/50"
                  >
                    <span className="mr-2 group-hover:scale-110 transition-transform duration-300">📊</span>
                    View Data
                  </button>
                  <button
                    onClick={() => {
                      setSelectedDevice(device)
                      setShowCalibrationModal(true)
                    }}
                    className="group backdrop-blur-sm bg-green-50/80 hover:bg-green-100/80 text-green-700 px-4 py-3 rounded-2xl text-sm font-semibold transition-all duration-300 hover:scale-105 border border-green-200/50"
                  >
                    <span className="mr-2 group-hover:rotate-12 transition-transform duration-300">🔧</span>
                    Calibrate
                  </button>
                  <button
                    onClick={() => restartDevice(device.id)}
                    disabled={device.status === 'online'}
                    className="group backdrop-blur-sm bg-orange-50/80 hover:bg-orange-100/80 text-orange-700 px-4 py-3 rounded-2xl text-sm font-semibold transition-all duration-300 hover:scale-105 border border-orange-200/50 disabled:opacity-50"
                  >
                    <span className="mr-2 group-hover:rotate-180 transition-transform duration-500">🔄</span>
                    Restart
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Device Details Modal */}
        {selectedDevice && !showCalibrationModal && (
          <div className="fixed inset-0 bg-black/20 backdrop-blur-sm overflow-y-auto h-full w-full z-50" onClick={() => setSelectedDevice(null)}>
            <div className="relative top-20 mx-auto p-8 w-3/4 max-w-4xl backdrop-blur-lg bg-white/30 border border-white/50 rounded-3xl shadow-2xl" onClick={e => e.stopPropagation()}>
              <div className="mt-3">
                <h3 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent mb-6 flex items-center">
                  <span className="mr-3 text-3xl">{getDeviceTypeIcon(selectedDevice.type)}</span>
                  {selectedDevice.name} - Live Data
                </h3>
                
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                  {/* Device Info */}
                  <div className="backdrop-blur-sm bg-white/20 rounded-2xl p-6 border border-white/40">
                    <h4 className="font-bold text-gray-800 mb-4 text-lg">Device Information</h4>
                    <div className="space-y-3 text-sm">
                      <p className="flex justify-between"><span className="font-semibold text-gray-700">Device ID:</span> <span className="text-gray-800">{selectedDevice.device_id}</span></p>
                      <p className="flex justify-between"><span className="font-semibold text-gray-700">Type:</span> <span className="text-gray-800">{selectedDevice.type.replace('_', ' ')}</span></p>
                      <p className="flex items-center justify-between"><span className="font-semibold text-gray-700">Status:</span> 
                        <span className={`px-3 py-1 rounded-xl text-xs font-semibold backdrop-blur-sm border ${getStatusColor(selectedDevice.status)}`}>
                          {selectedDevice.status}
                        </span>
                      </p>
                      <p className="flex justify-between"><span className="font-semibold text-gray-700">Site:</span> <span className="text-gray-800">{selectedDevice.site_name}</span></p>
                      {selectedDevice.zone_id && <p className="flex justify-between"><span className="font-semibold text-gray-700">Zone:</span> <span className="text-gray-800">{selectedDevice.zone_id}</span></p>}
                      {selectedDevice.location && (
                        <p className="flex justify-between"><span className="font-semibold text-gray-700">Location:</span> <span className="text-gray-800">{selectedDevice.location.latitude}, {selectedDevice.location.longitude}</span></p>
                      )}
                    </div>
                  </div>

                  {/* Recent Readings */}
                  <div className="backdrop-blur-sm bg-white/20 rounded-2xl p-6 border border-white/40">
                    <h4 className="font-bold text-gray-800 mb-4 text-lg">Recent Readings</h4>
                    {readings.length > 0 ? (
                      <div className="space-y-4">
                        {readings.slice(0, 4).map((reading, index) => (
                          <div key={index} className={`border rounded p-3 ${reading.anomaly_detected ? 'border-red-200 bg-red-50' : 'border-gray-200'}`}>
                            <div className="flex items-center justify-between mb-2">
                              <span className="text-xs text-gray-500">
                                {new Date(reading.timestamp).toLocaleString()}
                              </span>
                              {reading.anomaly_detected && (
                                <span className="text-xs bg-red-100 text-red-800 px-2 py-1 rounded">
                                  Anomaly Detected
                                </span>
                              )}
                            </div>
                            <div className="text-sm">
                              {Object.entries(reading.readings).map(([key, value]) => (
                                <div key={key} className="flex justify-between">
                                  <span className="capitalize">{key}:</span>
                                  <span className="font-medium">{value}</span>
                                </div>
                              ))}
                              {reading.quality_score && (
                                <div className="flex justify-between">
                                  <span>Quality Score:</span>
                                  <span className="font-medium">{Math.round(reading.quality_score * 100)}%</span>
                                </div>
                              )}
                            </div>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <p className="text-gray-500">No recent readings available</p>
                    )}
                  </div>
                </div>

                <div className="flex justify-end mt-6 space-x-3">
                  <button
                    onClick={() => setSelectedDevice(null)}
                    className="px-4 py-2 bg-gray-300 text-gray-700 rounded-md hover:bg-gray-400 transition-colors"
                  >
                    Close
                  </button>
                  <button
                    onClick={() => setShowCalibrationModal(true)}
                    className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors"
                  >
                    🔧 Calibrate Device
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Calibration Modal */}
        {showCalibrationModal && selectedDevice && (
          <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50" onClick={() => setShowCalibrationModal(false)}>
            <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white" onClick={e => e.stopPropagation()}>
              <div className="mt-3">
                <h3 className="text-lg font-bold text-gray-900 mb-4">
                  🔧 Calibrate Device - {selectedDevice.name}
                </h3>
                
                <p className="text-sm text-gray-600 mb-6">
                  This will start the automatic calibration process for the selected device. 
                  The device may be temporarily offline during calibration.
                </p>

                <div className="bg-yellow-50 border border-yellow-200 rounded p-4 mb-6">
                  <div className="flex">
                    <div className="flex-shrink-0">
                      <span className="text-yellow-600">⚠️</span>
                    </div>
                    <div className="ml-3">
                      <p className="text-sm text-yellow-800">
                        <strong>Warning:</strong> Calibration will take approximately 2-3 minutes. 
                        Ensure the device area is clear of personnel and equipment.
                      </p>
                    </div>
                  </div>
                </div>

                <div className="flex justify-end space-x-3">
                  <button
                    onClick={() => setShowCalibrationModal(false)}
                    disabled={calibrating}
                    className="px-4 py-2 bg-gray-300 text-gray-700 rounded-md hover:bg-gray-400 disabled:opacity-50 transition-colors"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={() => calibrateDevice(selectedDevice.id)}
                    disabled={calibrating}
                    className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:bg-gray-400 transition-colors"
                  >
                    {calibrating ? (
                      <div className="flex items-center">
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                        Calibrating...
                      </div>
                    ) : (
                      'Start Calibration'
                    )}
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
      </div>
    </div>
  )
}

export default DevicesPage
