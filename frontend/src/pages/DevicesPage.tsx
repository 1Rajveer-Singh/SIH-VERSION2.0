import React, { useState, useEffect } from 'react'
import Navbar from '../components/Navbar'
import { EnhancedDeviceCard } from '../components/EnhancedDeviceCard'
import { DeviceDetailsModal } from '../components/DeviceDetailsModal'
import { Device, DeviceType, deviceTypeConfigs } from '../types/devices'

const DevicesPage: React.FC = () => {
  const [devices, setDevices] = useState<Device[]>([])
  const [loading, setLoading] = useState(true)
  const [refreshLoading, setRefreshLoading] = useState(false)
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState<'all' | 'online' | 'offline' | 'maintenance' | 'error'>('all')
  const [selectedDevice, setSelectedDevice] = useState<Device | null>(null)
  const [showAddDevice, setShowAddDevice] = useState(false)

  // Mock data for demonstration
  const mockDevices: Device[] = [
    {
      id: '1',
      name: 'GBI-SAR Station Alpha',
      type: 'gb-insar',
      status: 'online',
      location: { latitude: 45.0792, longitude: 7.6729, elevation: 1200 },
      lastReading: new Date().toISOString(),
      category: 'Ground Radar',
      description: 'Ground-based radar monitoring wide-area slope displacement',
      enabled: true,
      configuration: { samplingRate: 100, threshold: 0.8, alertEnabled: true },
      csvImportEnabled: true,
      apiEndpoint: '/api/devices/gb-insar/001',
      notes: 'Continuous monitoring of Sector A slopes',
      fields: [] as any,
      createdAt: '2023-01-15T10:00:00Z',
      updatedAt: new Date().toISOString()
    },
    {
      id: '2',
      name: 'LiDAR Scanner Beta',
      type: 'lidar',
      status: 'online',
      location: { latitude: 45.0800, longitude: 7.6750, elevation: 1250 },
      lastReading: new Date().toISOString(),
      category: 'Optical Scanner',
      description: 'High-resolution 3D terrain mapping',
      enabled: true,
      configuration: { samplingRate: 50, threshold: 0.9, alertEnabled: true },
      csvImportEnabled: true,
      apiEndpoint: '/api/devices/lidar/002',
      notes: 'Terrain mapping for Zone B',
      fields: [] as any,
      createdAt: '2023-02-10T12:00:00Z',
      updatedAt: new Date().toISOString()
    },
    {
      id: '3',
      name: 'Inclinometer Gamma',
      type: 'borehole-inclinometer',
      status: 'online',
      location: { latitude: 45.0785, longitude: 7.6740, elevation: 1180 },
      lastReading: new Date().toISOString(),
      category: 'Subsurface Monitor',
      description: 'Deep subsurface displacement monitoring',
      enabled: true,
      configuration: { samplingRate: 200, threshold: 0.7, alertEnabled: true },
      csvImportEnabled: true,
      apiEndpoint: '/api/devices/borehole/003',
      notes: 'Continuous subsurface monitoring active',
      fields: [] as any,
      createdAt: '2022-11-20T09:00:00Z',
      updatedAt: new Date().toISOString()
    },
    {
      id: '4',
      name: 'Piezometer Delta',
      type: 'piezometer',
      status: 'online',
      location: { latitude: 45.0795, longitude: 7.6735, elevation: 1150 },
      lastReading: new Date().toISOString(),
      category: 'Hydrological Monitor',
      description: 'Groundwater pressure and level monitoring',
      enabled: true,
      configuration: { samplingRate: 150, threshold: 0.6, alertEnabled: true },
      csvImportEnabled: true,
      apiEndpoint: '/api/devices/piezometer/004',
      notes: 'Monitoring groundwater conditions',
      fields: [] as any,
      createdAt: '2023-03-05T14:00:00Z',
      updatedAt: new Date().toISOString()
    },
    {
      id: '5',
      name: 'Weather Station Epsilon',
      type: 'weather-station',
      status: 'online',
      location: { latitude: 45.0788, longitude: 7.6755, elevation: 1300 },
      lastReading: new Date().toISOString(),
      category: 'Environmental Monitor',
      description: 'Comprehensive weather and environmental monitoring',
      enabled: true,
      configuration: { samplingRate: 60, threshold: 0.5, alertEnabled: true },
      csvImportEnabled: true,
      apiEndpoint: '/api/devices/weather/005',
      notes: 'Primary weather monitoring station',
      fields: [] as any,
      createdAt: '2023-01-30T11:00:00Z',
      updatedAt: new Date().toISOString()
    },
    {
      id: '6',
      name: 'Geophone Array Zeta',
      type: 'geophone',
      status: 'online',
      location: { latitude: 45.0803, longitude: 7.6720, elevation: 1220 },
      lastReading: new Date().toISOString(),
      category: 'Seismic Monitor',
      description: 'Ground vibration and seismic activity detection',
      enabled: true,
      configuration: { samplingRate: 1000, threshold: 0.9, alertEnabled: true },
      csvImportEnabled: true,
      apiEndpoint: '/api/devices/geophone/006',
      notes: 'Monitoring for rockfall precursors',
      fields: [] as any,
      createdAt: '2022-12-15T16:00:00Z',
      updatedAt: new Date().toISOString()
    },
    {
      id: '7',
      name: 'Drone Imagery Hub Eta',
      type: 'drone-imagery',
      status: 'online',
      location: { latitude: 45.0797, longitude: 7.6745, elevation: 1100 },
      lastReading: new Date().toISOString(),
      category: 'Aerial Survey',
      description: 'Automated drone imagery and crack detection',
      enabled: true,
      configuration: { samplingRate: 10, threshold: 0.8, alertEnabled: true },
      csvImportEnabled: true,
      apiEndpoint: '/api/devices/drone/007',
      notes: 'Active aerial monitoring and crack detection',
      fields: [] as any,
      createdAt: '2023-07-15T12:00:00Z',
      updatedAt: new Date().toISOString()
    }
  ]

  useEffect(() => {
    // Simulate loading
    setTimeout(() => {
      setDevices(mockDevices)
      setLoading(false)
    }, 1000)
  }, [])

  const filteredDevices = devices.filter(device => {
    const matchesSearch = device.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      device.type.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesStatus = statusFilter === 'all' || device.status === statusFilter
    return matchesSearch && matchesStatus
  })

  const handleRefresh = () => {
    setRefreshLoading(true)
    setTimeout(() => {
      setDevices([...mockDevices])
      setRefreshLoading(false)
    }, 1500)
  }

  const handleDeviceSelect = (device: Device) => {
    setSelectedDevice(device)
  }

  const handleDeleteDevice = (deviceId: string) => {
    setDevices(devices.filter(device => device.id !== deviceId))
  }

  const handleUpdateDevice = (updatedDevice: Device) => {
    setDevices(devices.map(device => 
      device.id === updatedDevice.id ? updatedDevice : device
    ))
  }

  const handleAddNewDevice = () => {
    setShowAddDevice(true)
  }

  const handleCreateDevice = (deviceData: any) => {
    const newDevice: Device = {
      id: (devices.length + 1).toString(),
      name: deviceData.name,
      type: deviceData.type,
      status: 'offline',
      location: { latitude: 0, longitude: 0, elevation: 0 },
      lastReading: new Date().toISOString(),
      category: deviceTypeConfigs[deviceData.type as DeviceType]?.category || 'Unknown',
      description: deviceData.description || '',
      enabled: false,
      configuration: { samplingRate: 100, threshold: 0.8, alertEnabled: true },
      csvImportEnabled: false,
      apiEndpoint: '',
      notes: '',
      fields: [] as any,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    }
    setDevices([...devices, newDevice])
    setShowAddDevice(false)
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-white">
        <Navbar />
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600"></div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-white">
      <Navbar />
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header with Refresh and Add Device Buttons */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-4xl font-bold text-gray-900 mb-2">
              Devices
            </h1>
            <p className="text-gray-600">Monitor and manage all field devices with advanced functionality</p>
          </div>
          <div className="flex space-x-4">
            <button
              onClick={handleRefresh}
              disabled={refreshLoading}
              className="flex items-center space-x-2 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
            >
              {refreshLoading ? (
                <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
              ) : (
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
              )}
              <span>Refresh</span>
            </button>
            
            <button
              onClick={handleAddNewDevice}
              className="flex items-center space-x-2 px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
              </svg>
              <span>Add New Device</span>
            </button>
          </div>
        </div>

        {/* Search and Filter Controls */}
        <div className="mb-8 space-y-4">
          <div className="flex flex-col lg:flex-row gap-4 items-center">
            {/* Search */}
            <div className="relative flex-1 max-w-md">
              <input
                type="text"
                placeholder="Search devices by name or type..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full bg-white border border-gray-300 rounded-lg px-4 py-3 text-gray-900 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-300 shadow-sm"
              />
              <svg className="absolute right-3 top-3.5 h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </div>

            {/* Status Filter */}
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value as any)}
              className="bg-white border border-gray-300 rounded-lg px-4 py-3 text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-300 shadow-sm"
            >
              <option value="all">All Status</option>
              <option value="online">Online</option>
              <option value="offline">Offline</option>
              <option value="maintenance">Maintenance</option>
            </select>
          </div>
        </div>

        {/* Device Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {filteredDevices.map((device) => (
            <EnhancedDeviceCard
              key={device.id}
              device={device}
              onShowDetails={handleDeviceSelect}
              onDeleteDevice={handleDeleteDevice}
              onUpdateDevice={handleUpdateDevice}
            />
          ))}
        </div>

        {/* No devices found */}
        {filteredDevices.length === 0 && (
          <div className="text-center py-16">
            <div className="bg-gray-50 rounded-lg p-12 border border-gray-200">
              <svg className="mx-auto h-16 w-16 text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9.75 9.75l4.5 4.5m0-4.5l-4.5 4.5M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">No devices found</h3>
              <p className="text-gray-600">Try adjusting your search or filter criteria to find devices</p>
            </div>
          </div>
        )}

        {/* Device Details Modal */}
        {selectedDevice && (
          <DeviceDetailsModal
            device={selectedDevice}
            isOpen={!!selectedDevice}
            onClose={() => setSelectedDevice(null)}
          />
        )}

        {/* Add New Device Modal */}
        {showAddDevice && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" onClick={() => setShowAddDevice(false)}>
            <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4" onClick={(e) => e.stopPropagation()}>
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-900">Add New Device</h3>
                <button
                  onClick={() => setShowAddDevice(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
              
              <form onSubmit={(e) => {
                e.preventDefault()
                const formData = new FormData(e.currentTarget)
                const deviceData = {
                  name: formData.get('name'),
                  type: formData.get('type'),
                  description: formData.get('description')
                }
                handleCreateDevice(deviceData)
              }}>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Device Name</label>
                    <input
                      type="text"
                      name="name"
                      required
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="Enter device name"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Device Type</label>
                    <select
                      name="type"
                      required
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="">Select device type</option>
                      <option value="gb-insar">GB-InSAR</option>
                      <option value="lidar">LiDAR</option>
                      <option value="borehole-inclinometer">Borehole Inclinometer</option>
                      <option value="piezometer">Piezometer</option>
                      <option value="weather-station">Weather Station</option>
                      <option value="geophone">Geophone</option>
                      <option value="drone-imagery">Drone Imagery</option>
                    </select>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
                    <textarea
                      name="description"
                      rows={3}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="Enter device description"
                    />
                  </div>
                </div>
                
                <div className="flex justify-end space-x-3 mt-6">
                  <button
                    type="button"
                    onClick={() => setShowAddDevice(false)}
                    className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-md"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-md"
                  >
                    Create Device
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default DevicesPage