import React, { useState, useEffect } from 'react'
import Navbar from '../components/Navbar'

interface MiningSite {
  id: string
  name: string
  description?: string
  location: {
    latitude: number
    longitude: number
    elevation?: number
  }
  zones: Array<{
    id: string
    name: string
    risk_level: string
  }>
  status: string
  emergency_contacts: Array<{
    name: string
    role: string
    phone: string
    email: string
  }>
  area_hectares?: number
  safety_protocols: string[]
  created_at: string
  updated_at?: string
  current_risk_level?: string
  devices_count: number
  active_alerts: number
}

interface SiteCreate {
  name: string
  description?: string
  location: {
    latitude: number
    longitude: number
    elevation?: number
  }
  area_hectares?: number
  safety_protocols: string[]
}

function SitesPage() {
  const [sites, setSites] = useState<MiningSite[]>([])
  const [selectedSite, setSelectedSite] = useState<MiningSite | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [showEmergencyModal, setShowEmergencyModal] = useState(false)
  
  const [newSite, setNewSite] = useState<SiteCreate>({
    name: '',
    description: '',
    location: {
      latitude: 0,
      longitude: 0,
      elevation: 0
    },
    area_hectares: 0,
    safety_protocols: []
  })

  // Mock data for demonstration
  useEffect(() => {
    loadSites()
  }, [])

  const loadSites = async () => {
    try {
      setLoading(true)
      setError(null)
      
      // Mock data - in real app this would call the API
      const mockSites: MiningSite[] = [
        {
          id: 'site-001',
          name: 'Colorado Mining District - Sector A',
          description: 'Primary extraction site with high-grade ore deposits',
          location: {
            latitude: 39.7392,
            longitude: -104.9903,
            elevation: 1609
          },
          zones: [
            { id: 'zone-1', name: 'North Face', risk_level: 'medium' },
            { id: 'zone-2', name: 'South Slope', risk_level: 'low' },
            { id: 'zone-3', name: 'East Ridge', risk_level: 'high' }
          ],
          status: 'active',
          emergency_contacts: [
            { name: 'John Smith', role: 'Site Manager', phone: '+1-555-0123', email: 'john.smith@mining.com' },
            { name: 'Sarah Johnson', role: 'Safety Officer', phone: '+1-555-0124', email: 'sarah.johnson@mining.com' }
          ],
          area_hectares: 125.5,
          safety_protocols: ['Hard hat required', 'Safety harness in Zone 3', 'Daily inspection logs'],
          created_at: '2023-01-15T10:00:00Z',
          updated_at: '2024-09-20T15:30:00Z',
          current_risk_level: 'medium',
          devices_count: 12,
          active_alerts: 2
        },
        {
          id: 'site-002',
          name: 'Nevada Gold Fields - Sector B',
          description: 'Secondary site with moderate production capacity',
          location: {
            latitude: 39.1612,
            longitude: -119.7674,
            elevation: 1372
          },
          zones: [
            { id: 'zone-4', name: 'West Wall', risk_level: 'low' },
            { id: 'zone-5', name: 'Central Pit', risk_level: 'medium' }
          ],
          status: 'active',
          emergency_contacts: [
            { name: 'Mike Davis', role: 'Site Manager', phone: '+1-555-0125', email: 'mike.davis@mining.com' }
          ],
          area_hectares: 83.2,
          safety_protocols: ['Equipment checks', 'Weather monitoring'],
          created_at: '2023-03-10T08:00:00Z',
          updated_at: '2024-09-19T11:20:00Z',
          current_risk_level: 'low',
          devices_count: 8,
          active_alerts: 0
        }
      ]
      
      setSites(mockSites)
    } catch (err) {
      console.error('Error loading sites:', err)
      setError('Failed to load sites')
    } finally {
      setLoading(false)
    }
  }

  const handleCreateSite = async () => {
    try {
      // In real app, this would call the API
      const newSiteData: MiningSite = {
        ...newSite,
        id: `site-${String(sites.length + 1).padStart(3, '0')}`,
        zones: [],
        status: 'active',
        emergency_contacts: [],
        created_at: new Date().toISOString(),
        devices_count: 0,
        active_alerts: 0
      }
      
      setSites([...sites, newSiteData])
      setShowCreateModal(false)
      setNewSite({
        name: '',
        description: '',
        location: { latitude: 0, longitude: 0, elevation: 0 },
        area_hectares: 0,
        safety_protocols: []
      })
    } catch (err) {
      setError('Failed to create site')
    }
  }

  const triggerEmergencyProtocol = async (siteId: string, emergencyType: string) => {
    try {
      // In real app, this would call the API
      alert(`Emergency protocol "${emergencyType}" triggered for site ${siteId}`)
      setShowEmergencyModal(false)
    } catch (err) {
      setError('Failed to trigger emergency protocol')
    }
  }

  const getRiskLevelColor = (level: string) => {
    switch (level?.toLowerCase()) {
      case 'high': return 'text-red-600 bg-red-50 border-red-200'
      case 'medium': return 'text-orange-600 bg-orange-50 border-orange-200'
      case 'low': return 'text-green-600 bg-green-50 border-green-200'
      default: return 'text-gray-600 bg-gray-50 border-gray-200'
    }
  }

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'active': return 'bg-green-100 text-green-800'
      case 'maintenance': return 'bg-yellow-100 text-yellow-800'
      case 'inactive': return 'bg-gray-100 text-gray-800'
      case 'emergency': return 'bg-red-100 text-red-800'
      default: return 'bg-gray-100 text-gray-800'
    }
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
              Loading Sites...
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
                    🏭 Mining Sites Management
                  </h1>
                  <p className="mt-2 text-gray-600 font-medium">
                    Monitor and manage all mining sites, zones, and safety protocols
                  </p>
                </div>
                <button
                  onClick={() => setShowCreateModal(true)}
                  className="group bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white px-6 py-3 rounded-2xl font-semibold transition-all duration-300 hover:scale-105 shadow-lg"
                >
                  <span className="mr-2 group-hover:scale-110 transition-transform duration-300">+</span>
                  Add New Site
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
              onClick={loadSites}
              className="mt-2 text-red-800 underline hover:text-red-900 font-medium"
            >
              Retry
            </button>
          </div>
        )}

        {/* Sites Overview Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          <div className="group backdrop-blur-lg bg-white/40 border border-white/50 p-5 rounded-3xl shadow-xl hover:shadow-2xl hover:scale-105 transform transition-all duration-300">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="w-10 h-10 bg-gradient-to-br from-blue-400/20 to-blue-600/20 rounded-2xl flex items-center justify-center backdrop-blur-sm border border-blue-200/30 group-hover:scale-110 transition-transform duration-300">
                  <span className="text-lg">🏭</span>
                </div>
              </div>
              <div className="ml-3">
                <h3 className="text-xs font-semibold text-gray-700 uppercase tracking-wider">Total Sites</h3>
                <p className="text-2xl font-bold text-blue-600 mt-1">{sites.length}</p>
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
                <h3 className="text-xs font-semibold text-gray-700 uppercase tracking-wider">Active Sites</h3>
                <p className="text-2xl font-bold text-green-600 mt-1">
                  {sites.filter(s => s.status === 'active').length}
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
                  {sites.reduce((sum, s) => sum + s.active_alerts, 0)}
                </p>
              </div>
            </div>
          </div>

          <div className="group backdrop-blur-lg bg-white/40 border border-white/50 p-5 rounded-3xl shadow-xl hover:shadow-2xl hover:scale-105 transform transition-all duration-300">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="w-10 h-10 bg-gradient-to-br from-purple-400/20 to-purple-600/20 rounded-2xl flex items-center justify-center backdrop-blur-sm border border-purple-200/30 group-hover:scale-110 transition-transform duration-300">
                  <span className="text-lg">📱</span>
                </div>
              </div>
              <div className="ml-3">
                <h3 className="text-xs font-semibold text-gray-700 uppercase tracking-wider">Total Devices</h3>
                <p className="text-2xl font-bold text-purple-600 mt-1">
                  {sites.reduce((sum, s) => sum + s.devices_count, 0)}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Sites Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
          {sites.map((site) => (
            <div key={site.id} className="group backdrop-blur-lg bg-white/40 border border-white/50 rounded-3xl shadow-xl hover:shadow-2xl hover:scale-102 transform transition-all duration-300">
              <div className="p-6">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <h3 className="text-lg font-bold text-gray-800 group-hover:text-gray-900 mb-2">
                      {site.name}
                    </h3>
                    <p className="text-sm text-gray-600 font-medium">
                      {site.description}
                    </p>
                  </div>
                  <span className={`px-3 py-1 rounded-2xl text-xs font-semibold backdrop-blur-sm border transition-all duration-300 group-hover:scale-105 ${getStatusColor(site.status)}`}>
                    {site.status}
                  </span>
                </div>

                {/* Location Info */}
                <div className="mb-4 backdrop-blur-sm bg-white/30 rounded-2xl p-3 border border-white/40">
                  <p className="text-sm text-gray-700 font-medium">
                    📍 {site.location.latitude.toFixed(4)}, {site.location.longitude.toFixed(4)}
                  </p>
                  {site.location.elevation && (
                    <p className="text-sm text-gray-700 font-medium mt-1">
                      ⛰️ {site.location.elevation}m elevation
                    </p>
                  )}
                  {site.area_hectares && (
                    <p className="text-sm text-gray-700 font-medium mt-1">
                      📏 {site.area_hectares} hectares
                    </p>
                  )}
                </div>

                {/* Risk Level */}
                {site.current_risk_level && (
                  <div className={`p-3 rounded-2xl border backdrop-blur-sm mb-4 transition-all duration-300 ${getRiskLevelColor(site.current_risk_level)}`}>
                    <div className="flex items-center justify-between">
                      <span className="font-semibold text-gray-700 text-sm">Current Risk Level</span>
                      <span className="font-bold text-base">{site.current_risk_level.toUpperCase()}</span>
                    </div>
                  </div>
                )}

                {/* Stats */}
                <div className="grid grid-cols-2 gap-3 mb-4">
                  <div className="text-center backdrop-blur-sm bg-white/30 rounded-2xl p-3 border border-white/40">
                    <p className="text-2xl font-bold text-blue-600">{site.devices_count}</p>
                    <p className="text-sm text-gray-600 font-medium mt-1">Devices</p>
                  </div>
                  <div className="text-center backdrop-blur-sm bg-white/30 rounded-2xl p-3 border border-white/40">
                    <p className="text-2xl font-bold text-red-600">{site.active_alerts}</p>
                    <p className="text-sm text-gray-600 font-medium mt-1">Alerts</p>
                  </div>
                </div>

                {/* Zones */}
                {site.zones.length > 0 && (
                  <div className="mb-4">
                    <h4 className="font-bold text-gray-800 mb-2 text-sm">Zones ({site.zones.length})</h4>
                    <div className="space-y-2">
                      {site.zones.slice(0, 3).map((zone) => (
                        <div key={zone.id} className="flex items-center justify-between text-sm backdrop-blur-sm bg-white/20 rounded-xl p-2 border border-white/30">
                          <span className="text-gray-700 font-medium">{zone.name}</span>
                          <span className={`px-3 py-1 rounded-xl text-xs font-semibold backdrop-blur-sm border
                            ${zone.risk_level === 'high' ? 'bg-red-100/80 text-red-800 border-red-200/50' : 
                              zone.risk_level === 'medium' ? 'bg-orange-100/80 text-orange-800 border-orange-200/50' : 
                              'bg-green-100/80 text-green-800 border-green-200/50'}`}>
                            {zone.risk_level}
                          </span>
                        </div>
                      ))}
                      {site.zones.length > 3 && (
                        <p className="text-xs text-gray-500 font-medium text-center mt-2">+{site.zones.length - 3} more zones</p>
                      )}
                    </div>
                  </div>
                )}

                {/* Action Buttons */}
                <div className="flex space-x-2">
                  <button
                    onClick={() => setSelectedSite(site)}
                    className="group flex-1 backdrop-blur-sm bg-blue-50/80 hover:bg-blue-100/80 text-blue-700 px-3 py-2 rounded-2xl text-sm font-semibold transition-all duration-300 hover:scale-105 border border-blue-200/50"
                  >
                    <span className="group-hover:scale-110 transition-transform duration-300">View Details</span>
                  </button>
                  <button
                    onClick={() => {
                      setSelectedSite(site)
                      setShowEmergencyModal(true)
                    }}
                    className="group backdrop-blur-sm bg-red-50/80 hover:bg-red-100/80 text-red-700 px-3 py-2 rounded-2xl text-sm font-semibold transition-all duration-300 hover:scale-105 border border-red-200/50"
                  >
                    <span className="mr-2 group-hover:animate-pulse">🚨</span>
                    Emergency
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Site Details Modal */}
        {selectedSite && !showEmergencyModal && (
          <div className="fixed inset-0 bg-black/20 backdrop-blur-sm overflow-y-auto h-full w-full z-50" onClick={() => setSelectedSite(null)}>
            <div className="relative top-20 mx-auto p-6 w-3/4 max-w-4xl backdrop-blur-lg bg-white/30 border border-white/50 rounded-3xl shadow-2xl" onClick={e => e.stopPropagation()}>
              <div className="mt-3">
                <h3 className="text-xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent mb-4">
                  {selectedSite.name} - Site Details
                </h3>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {/* Basic Info */}
                  <div className="backdrop-blur-sm bg-white/20 rounded-2xl p-4 border border-white/40">
                    <h4 className="font-bold text-gray-800 mb-3 text-base">Basic Information</h4>
                    <div className="space-y-2 text-sm">
                      <p><span className="font-medium">ID:</span> {selectedSite.id}</p>
                      <p><span className="font-medium">Status:</span> 
                        <span className={`ml-2 px-2 py-1 rounded text-xs ${getStatusColor(selectedSite.status)}`}>
                          {selectedSite.status}
                        </span>
                      </p>
                      <p><span className="font-medium">Location:</span> {selectedSite.location.latitude}, {selectedSite.location.longitude}</p>
                      {selectedSite.area_hectares && <p><span className="font-medium">Area:</span> {selectedSite.area_hectares} hectares</p>}
                      <p><span className="font-medium">Created:</span> {new Date(selectedSite.created_at).toLocaleDateString()}</p>
                    </div>
                  </div>

                  {/* Emergency Contacts */}
                  <div>
                    <h4 className="font-semibold text-gray-900 mb-2 text-base">Emergency Contacts</h4>
                    {selectedSite.emergency_contacts.length > 0 ? (
                      <div className="space-y-2">
                        {selectedSite.emergency_contacts.map((contact, index) => (
                          <div key={index} className="border border-gray-200 rounded p-2">
                            <p className="font-medium text-sm">{contact.name}</p>
                            <p className="text-xs text-gray-600">{contact.role}</p>
                            <p className="text-xs text-blue-600">{contact.phone}</p>
                            <p className="text-xs text-blue-600">{contact.email}</p>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <p className="text-gray-500">No emergency contacts configured</p>
                    )}
                  </div>

                  {/* Safety Protocols */}
                  <div>
                    <h4 className="font-semibold text-gray-900 mb-3">Safety Protocols</h4>
                    {selectedSite.safety_protocols.length > 0 ? (
                      <ul className="text-sm space-y-1">
                        {selectedSite.safety_protocols.map((protocol, index) => (
                          <li key={index} className="flex items-start">
                            <span className="text-green-600 mr-2">✓</span>
                            {protocol}
                          </li>
                        ))}
                      </ul>
                    ) : (
                      <p className="text-gray-500">No safety protocols defined</p>
                    )}
                  </div>

                  {/* Zones */}
                  <div>
                    <h4 className="font-semibold text-gray-900 mb-3">Zones</h4>
                    {selectedSite.zones.length > 0 ? (
                      <div className="space-y-2">
                        {selectedSite.zones.map((zone) => (
                          <div key={zone.id} className="flex items-center justify-between border border-gray-200 rounded p-2">
                            <span className="font-medium">{zone.name}</span>
                            <span className={`px-2 py-1 rounded text-xs font-medium 
                              ${zone.risk_level === 'high' ? 'bg-red-100 text-red-800' : 
                                zone.risk_level === 'medium' ? 'bg-orange-100 text-orange-800' : 
                                'bg-green-100 text-green-800'}`}>
                              {zone.risk_level}
                            </span>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <p className="text-gray-500">No zones defined</p>
                    )}
                  </div>
                </div>

                <div className="flex justify-end mt-6 space-x-3">
                  <button
                    onClick={() => setSelectedSite(null)}
                    className="px-4 py-2 bg-gray-300 text-gray-700 rounded-md hover:bg-gray-400 transition-colors"
                  >
                    Close
                  </button>
                  <button
                    onClick={() => setShowEmergencyModal(true)}
                    className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 transition-colors"
                  >
                    🚨 Trigger Emergency
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Emergency Protocol Modal */}
        {showEmergencyModal && selectedSite && (
          <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50" onClick={() => setShowEmergencyModal(false)}>
            <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white" onClick={e => e.stopPropagation()}>
              <div className="mt-3">
                <h3 className="text-lg font-bold text-gray-900 mb-4">
                  🚨 Emergency Protocol - {selectedSite.name}
                </h3>
                
                <p className="text-sm text-gray-600 mb-4">
                  Select the type of emergency protocol to activate:
                </p>

                <div className="space-y-3">
                  <button
                    onClick={() => triggerEmergencyProtocol(selectedSite.id, 'Rockfall Alert')}
                    className="w-full bg-red-600 hover:bg-red-700 text-white px-4 py-3 rounded-md font-medium transition-colors text-left"
                  >
                    ⚠️ Rockfall Alert
                    <p className="text-sm text-red-100">Immediate danger - evacuate affected zones</p>
                  </button>
                  
                  <button
                    onClick={() => triggerEmergencyProtocol(selectedSite.id, 'Equipment Failure')}
                    className="w-full bg-orange-600 hover:bg-orange-700 text-white px-4 py-3 rounded-md font-medium transition-colors text-left"
                  >
                    🔧 Equipment Failure
                    <p className="text-sm text-orange-100">Critical equipment malfunction</p>
                  </button>
                  
                  <button
                    onClick={() => triggerEmergencyProtocol(selectedSite.id, 'Medical Emergency')}
                    className="w-full bg-purple-600 hover:bg-purple-700 text-white px-4 py-3 rounded-md font-medium transition-colors text-left"
                  >
                    🏥 Medical Emergency
                    <p className="text-sm text-purple-100">Medical assistance required</p>
                  </button>
                  
                  <button
                    onClick={() => triggerEmergencyProtocol(selectedSite.id, 'Weather Alert')}
                    className="w-full bg-blue-600 hover:bg-blue-700 text-white px-4 py-3 rounded-md font-medium transition-colors text-left"
                  >
                    ⛈️ Weather Alert
                    <p className="text-sm text-blue-100">Severe weather conditions</p>
                  </button>
                </div>

                <div className="flex justify-end mt-6">
                  <button
                    onClick={() => setShowEmergencyModal(false)}
                    className="px-4 py-2 bg-gray-300 text-gray-700 rounded-md hover:bg-gray-400 transition-colors"
                  >
                    Cancel
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Create Site Modal */}
        {showCreateModal && (
          <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50" onClick={() => setShowCreateModal(false)}>
            <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white" onClick={e => e.stopPropagation()}>
              <div className="mt-3">
                <h3 className="text-lg font-bold text-gray-900 mb-4">
                  Create New Mining Site
                </h3>
                
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Site Name</label>
                    <input
                      type="text"
                      value={newSite.name}
                      onChange={(e) => setNewSite({...newSite, name: e.target.value})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="Enter site name"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Description</label>
                    <textarea
                      value={newSite.description}
                      onChange={(e) => setNewSite({...newSite, description: e.target.value})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      rows={3}
                      placeholder="Site description"
                    />
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Latitude</label>
                      <input
                        type="number"
                        step="0.0001"
                        value={newSite.location.latitude}
                        onChange={(e) => setNewSite({
                          ...newSite, 
                          location: {...newSite.location, latitude: parseFloat(e.target.value) || 0}
                        })}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Longitude</label>
                      <input
                        type="number"
                        step="0.0001"
                        value={newSite.location.longitude}
                        onChange={(e) => setNewSite({
                          ...newSite, 
                          location: {...newSite.location, longitude: parseFloat(e.target.value) || 0}
                        })}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      />
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Area (hectares)</label>
                    <input
                      type="number"
                      step="0.1"
                      value={newSite.area_hectares}
                      onChange={(e) => setNewSite({...newSite, area_hectares: parseFloat(e.target.value) || 0})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                </div>

                <div className="flex justify-end mt-6 space-x-3">
                  <button
                    onClick={() => setShowCreateModal(false)}
                    className="px-4 py-2 bg-gray-300 text-gray-700 rounded-md hover:bg-gray-400 transition-colors"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={handleCreateSite}
                    disabled={!newSite.name}
                    className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-400 transition-colors"
                  >
                    Create Site
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

export default SitesPage
