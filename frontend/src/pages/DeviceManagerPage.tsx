import React, { useState, useEffect, useCallback } from 'react'
import Navbar from '../components/Navbar'
import { 
  Plus, 
  Settings, 
  Wifi, 
  WifiOff, 
  Battery, 
  Signal, 
  Trash2, 
  Edit, 
  Power, 
  PowerOff,
  TestTube,
  RefreshCw,
  AlertTriangle,
  CheckCircle,
  XCircle,
  Lock,
  Unlock,
  MapPin,
  Activity,
  Calendar
} from 'lucide-react'

interface Device {
  id: string
  device_id: string
  name: string
  type: 'seismic_sensor' | 'weather_station' | 'camera' | 'accelerometer' | 'tiltmeter' | 'pore_pressure' | 'displacement' | 'temperature' | 'rainfall'
  site_id: string
  site_name?: string
  zone_id?: string
  location?: {
    latitude: number
    longitude: number
    elevation?: number
  }
  status: 'online' | 'offline' | 'maintenance' | 'error' | 'testing'
  last_reading?: string
  battery_level?: number
  signal_strength?: number
  api_endpoint?: string
  api_key?: string
  connection_type: 'wifi' | 'cellular' | 'ethernet' | 'lora' | 'satellite'
  configuration: {
    sampling_rate: number
    sensitivity: number
    alert_threshold: number
    data_format: 'json' | 'xml' | 'csv'
    units: Record<string, string>
  }
  enabled: boolean
  last_test?: string
  test_results?: {
    connectivity: boolean
    data_quality: boolean
    response_time: number
    error_count: number
  }
  created_at: string
  updated_at?: string
  created_by?: string
}

interface SensorReading {
  timestamp: string
  device_id: string
  readings: Record<string, number>
  quality_score?: number
  anomaly_detected: boolean
  units: Record<string, string>
}

interface DeviceTest {
  device_id: string
  test_type: 'connectivity' | 'data_quality' | 'full_system'
  status: 'running' | 'passed' | 'failed'
  started_at: string
  completed_at?: string
  results?: {
    connectivity: boolean
    data_quality: boolean
    response_time: number
    error_messages: string[]
  }
}

function DeviceManagerPage() {
  const [devices, setDevices] = useState<Device[]>([])
  const [selectedDevice, setSelectedDevice] = useState<Device | null>(null)
  const [readings, setReadings] = useState<SensorReading[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)
  
  // Modal states
  const [showAddModal, setShowAddModal] = useState(false)
  const [showEditModal, setShowEditModal] = useState(false)
  const [showDeleteModal, setShowDeleteModal] = useState(false)
  const [showTestModal, setShowTestModal] = useState(false)
  
  // Form states
  const [deviceForm, setDeviceForm] = useState<Partial<Device>>({
    name: '',
    type: 'seismic_sensor',
    site_id: '',
    zone_id: '',
    api_endpoint: '',
    api_key: '',
    connection_type: 'wifi',
    configuration: {
      sampling_rate: 60,
      sensitivity: 1.0,
      alert_threshold: 0.8,
      data_format: 'json',
      units: {}
    },
    enabled: true
  })
  
  const [deletePassword, setDeletePassword] = useState('')
  const [testResults, setTestResults] = useState<DeviceTest | null>(null)
  const [testingDevice, setTestingDevice] = useState<string | null>(null)

  useEffect(() => {
    loadDevices()
  }, [])

  const loadDevices = async () => {
    try {
      setLoading(true)
      setError(null)
      
      // TODO: Replace with actual API call
      const response = await fetch('/api/devices')
      if (!response.ok) {
        throw new Error('Failed to load devices')
      }
      
      const devicesData = await response.json()
      setDevices(devicesData)
    } catch (err) {
      console.error('Error loading devices:', err)
      // Load mock data for development
      loadMockDevices()
    } finally {
      setLoading(false)
    }
  }

  const loadMockDevices = () => {
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
        api_endpoint: 'https://api.sensornetwork.com/seismic/001',
        api_key: 'sk_****_****_****',
        connection_type: 'wifi',
        configuration: {
          sampling_rate: 100,
          sensitivity: 0.05,
          alert_threshold: 0.8,
          data_format: 'json',
          units: { acceleration: 'g', frequency: 'Hz' }
        },
        enabled: true,
        last_test: '2024-09-21T09:00:00Z',
        test_results: {
          connectivity: true,
          data_quality: true,
          response_time: 120,
          error_count: 0
        },
        created_at: '2023-01-15T10:00:00Z',
        updated_at: '2024-09-21T10:30:00Z',
        created_by: 'admin'
      },
      {
        id: 'dev-002',
        device_id: 'PORE_001',
        name: 'Pore Pressure Monitor',
        type: 'pore_pressure',
        site_id: 'site-001',
        site_name: 'Colorado Mining District - Sector A',
        zone_id: 'zone-2',
        location: { latitude: 39.7395, longitude: -104.9905, elevation: 1620 },
        status: 'online',
        last_reading: '2024-09-21T10:25:00Z',
        battery_level: 94,
        signal_strength: 88,
        api_endpoint: 'https://api.hydrotech.com/pore-pressure/001',
        api_key: 'pp_****_****_****',
        connection_type: 'cellular',
        configuration: {
          sampling_rate: 60,
          sensitivity: 1.0,
          alert_threshold: 0.9,
          data_format: 'json',
          units: { pressure: 'kPa', temperature: 'C' }
        },
        enabled: true,
        last_test: '2024-09-21T08:30:00Z',
        test_results: {
          connectivity: true,
          data_quality: true,
          response_time: 89,
          error_count: 0
        },
        created_at: '2023-02-01T08:00:00Z',
        updated_at: '2024-09-21T10:25:00Z',
        created_by: 'admin'
      },
      {
        id: 'dev-003',
        device_id: 'DISP_001',
        name: 'Displacement Sensor',
        type: 'displacement',
        site_id: 'site-001',
        site_name: 'Colorado Mining District - Sector A',
        zone_id: 'zone-1',
        location: { latitude: 39.7390, longitude: -104.9900, elevation: 1615 },
        status: 'maintenance',
        last_reading: '2024-09-21T08:15:00Z',
        battery_level: 23,
        signal_strength: 76,
        api_endpoint: 'https://api.geotech.com/displacement/001',
        api_key: 'ds_****_****_****',
        connection_type: 'lora',
        configuration: {
          sampling_rate: 30,
          sensitivity: 0.1,
          alert_threshold: 0.7,
          data_format: 'json',
          units: { displacement: 'mm', angle: 'degrees' }
        },
        enabled: true,
        last_test: '2024-09-20T15:00:00Z',
        test_results: {
          connectivity: false,
          data_quality: false,
          response_time: 0,
          error_count: 3
        },
        created_at: '2023-03-10T12:00:00Z',
        updated_at: '2024-09-21T08:15:00Z',
        created_by: 'operator1'
      }
    ]
    setDevices(mockDevices)
  }

  const handleAddDevice = async () => {
    try {
      setError(null)
      
      const deviceData = {
        ...deviceForm,
        device_id: `${deviceForm.type?.toUpperCase()}_${Date.now()}`,
        id: `dev-${Date.now()}`,
        created_at: new Date().toISOString(),
        status: 'offline' as const,
        created_by: 'current_user' // TODO: Get from auth context
      }
      
      // TODO: Replace with actual API call
      const response = await fetch('/api/devices', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(deviceData)
      })
      
      if (!response.ok) {
        throw new Error('Failed to add device')
      }
      
      await loadDevices()
      setShowAddModal(false)
      setDeviceForm({
        name: '',
        type: 'seismic_sensor',
        site_id: '',
        zone_id: '',
        api_endpoint: '',
        api_key: '',
        connection_type: 'wifi',
        configuration: {
          sampling_rate: 60,
          sensitivity: 1.0,
          alert_threshold: 0.8,
          data_format: 'json',
          units: {}
        },
        enabled: true
      })
      setSuccess('Device added successfully')
      setTimeout(() => setSuccess(null), 3000)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to add device')
    }
  }

  const handleTestConnectivity = async (device: Device) => {
    try {
      setTestingDevice(device.id)
      setError(null)
      
      const testData: DeviceTest = {
        device_id: device.device_id,
        test_type: 'full_system',
        status: 'running',
        started_at: new Date().toISOString()
      }
      
      setTestResults(testData)
      setShowTestModal(true)
      
      // TODO: Replace with actual API call
      const response = await fetch(`/api/devices/${device.id}/test`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ test_type: 'full_system' })
      })
      
      if (!response.ok) {
        throw new Error('Failed to test device')
      }
      
      // Simulate test duration
      setTimeout(() => {
        const completedTest: DeviceTest = {
          ...testData,
          status: 'passed',
          completed_at: new Date().toISOString(),
          results: {
            connectivity: true,
            data_quality: true,
            response_time: Math.floor(Math.random() * 200) + 50,
            error_messages: []
          }
        }
        setTestResults(completedTest)
        setTestingDevice(null)
      }, 3000)
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to test device')
      setTestingDevice(null)
    }
  }

  const handleToggleDevice = async (device: Device) => {
    try {
      setError(null)
      
      const updatedDevice = {
        ...device,
        enabled: !device.enabled,
        status: !device.enabled ? 'online' : 'offline' as const,
        updated_at: new Date().toISOString()
      }
      
      // TODO: Replace with actual API call
      const response = await fetch(`/api/devices/${device.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(updatedDevice)
      })
      
      if (!response.ok) {
        throw new Error('Failed to update device')
      }
      
      await loadDevices()
      setSuccess(`Device ${device.enabled ? 'disabled' : 'enabled'} successfully`)
      setTimeout(() => setSuccess(null), 3000)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update device')
    }
  }

  const handleDeleteDevice = async () => {
    if (deletePassword !== 'admin@123') {
      setError('Incorrect admin password')
      return
    }
    
    if (!selectedDevice) return
    
    try {
      setError(null)
      
      // TODO: Replace with actual API call
      const response = await fetch(`/api/devices/${selectedDevice.id}`, {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ admin_password: deletePassword })
      })
      
      if (!response.ok) {
        throw new Error('Failed to delete device')
      }
      
      await loadDevices()
      setShowDeleteModal(false)
      setSelectedDevice(null)
      setDeletePassword('')
      setSuccess('Device deleted successfully')
      setTimeout(() => setSuccess(null), 3000)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete device')
    }
  }

  const getStatusIcon = (status: Device['status']) => {
    switch (status) {
      case 'online':
        return <CheckCircle className="h-5 w-5 text-green-500" />
      case 'offline':
        return <XCircle className="h-5 w-5 text-red-500" />
      case 'maintenance':
        return <Settings className="h-5 w-5 text-yellow-500" />
      case 'error':
        return <AlertTriangle className="h-5 w-5 text-red-600" />
      case 'testing':
        return <TestTube className="h-5 w-5 text-blue-500" />
      default:
        return <XCircle className="h-5 w-5 text-gray-400" />
    }
  }

  const getConnectionIcon = (type: Device['connection_type']) => {
    switch (type) {
      case 'wifi':
        return <Wifi className="h-4 w-4 text-blue-500" />
      case 'cellular':
        return <Signal className="h-4 w-4 text-green-500" />
      case 'ethernet':
        return <Activity className="h-4 w-4 text-gray-600" />
      case 'lora':
        return <Activity className="h-4 w-4 text-purple-500" />
      case 'satellite':
        return <Activity className="h-4 w-4 text-orange-500" />
      default:
        return <WifiOff className="h-4 w-4 text-gray-400" />
    }
  }

  const deviceTypes = [
    { value: 'seismic_sensor', label: 'Seismic Sensor' },
    { value: 'weather_station', label: 'Weather Station' },
    { value: 'camera', label: 'Camera' },
    { value: 'accelerometer', label: 'Accelerometer' },
    { value: 'tiltmeter', label: 'Tiltmeter' },
    { value: 'pore_pressure', label: 'Pore Pressure Monitor' },
    { value: 'displacement', label: 'Displacement Sensor' },
    { value: 'temperature', label: 'Temperature Sensor' },
    { value: 'rainfall', label: 'Rainfall Monitor' }
  ]

  const connectionTypes = [
    { value: 'wifi', label: 'WiFi' },
    { value: 'cellular', label: 'Cellular' },
    { value: 'ethernet', label: 'Ethernet' },
    { value: 'lora', label: 'LoRa' },
    { value: 'satellite', label: 'Satellite' }
  ]

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Device Manager</h1>
              <p className="text-gray-600 mt-2">Manage sensor devices, API connections, and monitoring</p>
            </div>
            <button
              onClick={() => setShowAddModal(true)}
              className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 flex items-center gap-2"
            >
              <Plus className="h-5 w-5" />
              Add Device
            </button>
          </div>
        </div>

        {/* Alerts */}
        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
            {error}
          </div>
        )}
        
        {success && (
          <div className="mb-6 bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-lg">
            {success}
          </div>
        )}

        {/* Device Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white p-6 rounded-lg shadow">
            <div className="flex items-center">
              <CheckCircle className="h-8 w-8 text-green-500" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Online</p>
                <p className="text-2xl font-semibold text-gray-900">
                  {devices.filter(d => d.status === 'online').length}
                </p>
              </div>
            </div>
          </div>
          
          <div className="bg-white p-6 rounded-lg shadow">
            <div className="flex items-center">
              <XCircle className="h-8 w-8 text-red-500" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Offline</p>
                <p className="text-2xl font-semibold text-gray-900">
                  {devices.filter(d => d.status === 'offline').length}
                </p>
              </div>
            </div>
          </div>
          
          <div className="bg-white p-6 rounded-lg shadow">
            <div className="flex items-center">
              <Settings className="h-8 w-8 text-yellow-500" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Maintenance</p>
                <p className="text-2xl font-semibold text-gray-900">
                  {devices.filter(d => d.status === 'maintenance').length}
                </p>
              </div>
            </div>
          </div>
          
          <div className="bg-white p-6 rounded-lg shadow">
            <div className="flex items-center">
              <Activity className="h-8 w-8 text-blue-500" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Total Devices</p>
                <p className="text-2xl font-semibold text-gray-900">{devices.length}</p>
              </div>
            </div>
          </div>
        </div>

        {/* Device List */}
        <div className="bg-white shadow rounded-lg overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-medium text-gray-900">Sensor Devices</h3>
          </div>
          
          {loading ? (
            <div className="flex justify-center items-center py-12">
              <RefreshCw className="h-8 w-8 animate-spin text-blue-500" />
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Device
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Location
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Connection
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Last Reading
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {devices.map((device) => (
                    <tr key={device.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <div className="flex-shrink-0 h-10 w-10">
                            <div className="h-10 w-10 rounded-full bg-blue-100 flex items-center justify-center">
                              <Activity className="h-5 w-5 text-blue-600" />
                            </div>
                          </div>
                          <div className="ml-4">
                            <div className="text-sm font-medium text-gray-900">{device.name}</div>
                            <div className="text-sm text-gray-500">{device.device_id}</div>
                            <div className="text-xs text-gray-400 capitalize">{device.type.replace('_', ' ')}</div>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center text-sm text-gray-900">
                          <MapPin className="h-4 w-4 text-gray-400 mr-1" />
                          {device.location ? 
                            `${device.location.latitude.toFixed(4)}, ${device.location.longitude.toFixed(4)}` :
                            'Not set'
                          }
                        </div>
                        {device.site_name && (
                          <div className="text-xs text-gray-500">{device.site_name}</div>
                        )}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          {getStatusIcon(device.status)}
                          <span className="ml-2 text-sm text-gray-900 capitalize">{device.status}</span>
                        </div>
                        <div className="flex items-center mt-1">
                          {device.enabled ? (
                            <Unlock className="h-3 w-3 text-green-500 mr-1" />
                          ) : (
                            <Lock className="h-3 w-3 text-red-500 mr-1" />
                          )}
                          <span className="text-xs text-gray-500">
                            {device.enabled ? 'Enabled' : 'Disabled'}
                          </span>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          {getConnectionIcon(device.connection_type)}
                          <span className="ml-2 text-sm text-gray-900 capitalize">
                            {device.connection_type}
                          </span>
                        </div>
                        <div className="flex items-center mt-1 space-x-4">
                          {device.battery_level && (
                            <div className="flex items-center">
                              <Battery className="h-3 w-3 text-gray-400 mr-1" />
                              <span className="text-xs text-gray-500">{device.battery_level}%</span>
                            </div>
                          )}
                          {device.signal_strength && (
                            <div className="flex items-center">
                              <Signal className="h-3 w-3 text-gray-400 mr-1" />
                              <span className="text-xs text-gray-500">{device.signal_strength}%</span>
                            </div>
                          )}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center text-sm text-gray-900">
                          <Calendar className="h-4 w-4 text-gray-400 mr-1" />
                          {device.last_reading ? 
                            new Date(device.last_reading).toLocaleString() :
                            'Never'
                          }
                        </div>
                        {device.last_test && (
                          <div className="text-xs text-gray-500">
                            Last test: {new Date(device.last_test).toLocaleString()}
                          </div>
                        )}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                        <div className="flex items-center space-x-2">
                          <button
                            onClick={() => handleTestConnectivity(device)}
                            disabled={testingDevice === device.id}
                            className="text-blue-600 hover:text-blue-900 disabled:opacity-50"
                            title="Test connectivity"
                          >
                            {testingDevice === device.id ? (
                              <RefreshCw className="h-4 w-4 animate-spin" />
                            ) : (
                              <TestTube className="h-4 w-4" />
                            )}
                          </button>
                          
                          <button
                            onClick={() => handleToggleDevice(device)}
                            className={`${device.enabled ? 'text-red-600 hover:text-red-900' : 'text-green-600 hover:text-green-900'}`}
                            title={device.enabled ? 'Disable device' : 'Enable device'}
                          >
                            {device.enabled ? (
                              <PowerOff className="h-4 w-4" />
                            ) : (
                              <Power className="h-4 w-4" />
                            )}
                          </button>
                          
                          <button
                            onClick={() => {
                              setSelectedDevice(device)
                              setDeviceForm(device)
                              setShowEditModal(true)
                            }}
                            className="text-indigo-600 hover:text-indigo-900"
                            title="Edit device"
                          >
                            <Edit className="h-4 w-4" />
                          </button>
                          
                          <button
                            onClick={() => {
                              setSelectedDevice(device)
                              setShowDeleteModal(true)
                            }}
                            className="text-red-600 hover:text-red-900"
                            title="Delete device"
                          >
                            <Trash2 className="h-4 w-4" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>

      {/* Add Device Modal */}
      {showAddModal && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-11/12 md:w-2/3 lg:w-1/2 shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Add New Device</h3>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Device Name</label>
                  <input
                    type="text"
                    value={deviceForm.name || ''}
                    onChange={(e) => setDeviceForm({...deviceForm, name: e.target.value})}
                    className="w-full border border-gray-300 rounded-md px-3 py-2"
                    placeholder="Enter device name"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Device Type</label>
                  <select
                    value={deviceForm.type || 'seismic_sensor'}
                    onChange={(e) => setDeviceForm({...deviceForm, type: e.target.value as Device['type']})}
                    className="w-full border border-gray-300 rounded-md px-3 py-2"
                  >
                    {deviceTypes.map(type => (
                      <option key={type.value} value={type.value}>{type.label}</option>
                    ))}
                  </select>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Site ID</label>
                  <input
                    type="text"
                    value={deviceForm.site_id || ''}
                    onChange={(e) => setDeviceForm({...deviceForm, site_id: e.target.value})}
                    className="w-full border border-gray-300 rounded-md px-3 py-2"
                    placeholder="site-001"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Zone ID</label>
                  <input
                    type="text"
                    value={deviceForm.zone_id || ''}
                    onChange={(e) => setDeviceForm({...deviceForm, zone_id: e.target.value})}
                    className="w-full border border-gray-300 rounded-md px-3 py-2"
                    placeholder="zone-1"
                  />
                </div>
                
                <div className="md:col-span-2">
                  <label className="block text-sm font-medium text-gray-700 mb-1">API Endpoint</label>
                  <input
                    type="url"
                    value={deviceForm.api_endpoint || ''}
                    onChange={(e) => setDeviceForm({...deviceForm, api_endpoint: e.target.value})}
                    className="w-full border border-gray-300 rounded-md px-3 py-2"
                    placeholder="https://api.example.com/sensor/data"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">API Key</label>
                  <input
                    type="password"
                    value={deviceForm.api_key || ''}
                    onChange={(e) => setDeviceForm({...deviceForm, api_key: e.target.value})}
                    className="w-full border border-gray-300 rounded-md px-3 py-2"
                    placeholder="Enter API key"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Connection Type</label>
                  <select
                    value={deviceForm.connection_type || 'wifi'}
                    onChange={(e) => setDeviceForm({...deviceForm, connection_type: e.target.value as Device['connection_type']})}
                    className="w-full border border-gray-300 rounded-md px-3 py-2"
                  >
                    {connectionTypes.map(type => (
                      <option key={type.value} value={type.value}>{type.label}</option>
                    ))}
                  </select>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Sampling Rate (seconds)</label>
                  <input
                    type="number"
                    value={deviceForm.configuration?.sampling_rate || 60}
                    onChange={(e) => setDeviceForm({
                      ...deviceForm, 
                      configuration: {
                        ...deviceForm.configuration!,
                        sampling_rate: parseInt(e.target.value)
                      }
                    })}
                    className="w-full border border-gray-300 rounded-md px-3 py-2"
                    min="1"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Alert Threshold</label>
                  <input
                    type="number"
                    step="0.1"
                    min="0"
                    max="1"
                    value={deviceForm.configuration?.alert_threshold || 0.8}
                    onChange={(e) => setDeviceForm({
                      ...deviceForm, 
                      configuration: {
                        ...deviceForm.configuration!,
                        alert_threshold: parseFloat(e.target.value)
                      }
                    })}
                    className="w-full border border-gray-300 rounded-md px-3 py-2"
                  />
                </div>
              </div>
              
              <div className="flex justify-end mt-6 space-x-3">
                <button
                  onClick={() => setShowAddModal(false)}
                  className="px-4 py-2 bg-gray-300 text-gray-700 rounded-md hover:bg-gray-400"
                >
                  Cancel
                </button>
                <button
                  onClick={handleAddDevice}
                  className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
                >
                  Add Device
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Delete Device Modal */}
      {showDeleteModal && selectedDevice && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Delete Device</h3>
              <p className="text-sm text-gray-600 mb-4">
                Are you sure you want to delete "{selectedDevice.name}"? This action cannot be undone.
              </p>
              
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Admin Password
                </label>
                <input
                  type="password"
                  value={deletePassword}
                  onChange={(e) => setDeletePassword(e.target.value)}
                  className="w-full border border-gray-300 rounded-md px-3 py-2"
                  placeholder="Enter admin password"
                />
              </div>
              
              <div className="flex justify-end space-x-3">
                <button
                  onClick={() => {
                    setShowDeleteModal(false)
                    setSelectedDevice(null)
                    setDeletePassword('')
                  }}
                  className="px-4 py-2 bg-gray-300 text-gray-700 rounded-md hover:bg-gray-400"
                >
                  Cancel
                </button>
                <button
                  onClick={handleDeleteDevice}
                  className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700"
                >
                  Delete
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Test Results Modal */}
      {showTestModal && testResults && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Device Test Results</h3>
              
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Status:</span>
                  <span className={`text-sm font-medium ${testResults.status === 'running' ? 'text-blue-600' : testResults.status === 'passed' ? 'text-green-600' : 'text-red-600'}`}>
                    {testResults.status === 'running' ? 'Testing...' : testResults.status.toUpperCase()}
                  </span>
                </div>
                
                {testResults.status === 'running' && (
                  <div className="flex items-center justify-center py-4">
                    <RefreshCw className="h-8 w-8 animate-spin text-blue-500" />
                  </div>
                )}
                
                {testResults.results && (
                  <div className="space-y-2">
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600">Connectivity:</span>
                      <span className={`text-sm font-medium ${testResults.results.connectivity ? 'text-green-600' : 'text-red-600'}`}>
                        {testResults.results.connectivity ? 'PASS' : 'FAIL'}
                      </span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600">Data Quality:</span>
                      <span className={`text-sm font-medium ${testResults.results.data_quality ? 'text-green-600' : 'text-red-600'}`}>
                        {testResults.results.data_quality ? 'PASS' : 'FAIL'}
                      </span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600">Response Time:</span>
                      <span className="text-sm font-medium text-gray-900">
                        {testResults.results.response_time}ms
                      </span>
                    </div>
                  </div>
                )}
              </div>
              
              <div className="flex justify-end mt-6">
                <button
                  onClick={() => setShowTestModal(false)}
                  className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default DeviceManagerPage