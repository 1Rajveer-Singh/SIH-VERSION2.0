import React, { useState, useEffect } from 'react'
import { useAuth } from '../contexts/AuthContext'
import Navbar from '../components/Navbar'

interface SystemSetting {
  key: string
  value: any
  description: string
  data_type: string
}

interface UserProfile {
  email: string
  full_name: string
  username: string
  role: string
  notifications_enabled: boolean
  email_alerts: boolean
  sms_alerts: boolean
}

function SettingsPage() {
  const { state } = useAuth()
  const [activeTab, setActiveTab] = useState<'profile' | 'notifications' | 'system'>('profile')
  const [systemSettings, setSystemSettings] = useState<SystemSetting[]>([])
  const [userProfile, setUserProfile] = useState<UserProfile>({
    email: state.user?.email || '',
    full_name: state.user?.full_name || '',
    username: state.user?.username || '',
    role: state.user?.role || '',
    notifications_enabled: true,
    email_alerts: true,
    sms_alerts: false
  })
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState('')

  useEffect(() => {
    loadSystemSettings()
  }, [])

  const loadSystemSettings = async () => {
    // Mock system settings
    setSystemSettings([
      {
        key: 'prediction_threshold_low',
        value: 0.3,
        description: 'Low risk threshold for predictions',
        data_type: 'float'
      },
      {
        key: 'prediction_threshold_medium',
        value: 0.6,
        description: 'Medium risk threshold for predictions',
        data_type: 'float'
      },
      {
        key: 'prediction_threshold_high',
        value: 0.8,
        description: 'High risk threshold for predictions',
        data_type: 'float'
      },
      {
        key: 'alert_email_enabled',
        value: true,
        description: 'Enable email alerts system-wide',
        data_type: 'bool'
      },
      {
        key: 'data_retention_days',
        value: 365,
        description: 'Data retention period in days',
        data_type: 'int'
      }
    ])
  }

  const handleProfileSave = async () => {
    setLoading(true)
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000))
      setMessage('Profile updated successfully!')
      setTimeout(() => setMessage(''), 3000)
    } catch (error) {
      setMessage('Error updating profile')
    }
    setLoading(false)
  }

  const handleSystemSettingSave = async (key: string, value: any) => {
    setLoading(true)
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 500))
      setSystemSettings(prev => 
        prev.map(setting => 
          setting.key === key ? { ...setting, value } : setting
        )
      )
      setMessage('System setting updated successfully!')
      setTimeout(() => setMessage(''), 3000)
    } catch (error) {
      setMessage('Error updating system setting')
    }
    setLoading(false)
  }

  return (
    <div className="min-h-screen bg-white relative">
      <div className="absolute inset-0 bg-gradient-to-br from-blue-50/20 via-purple-50/10 to-cyan-50/20"></div>
      <div className="relative z-10">
        <Navbar />
        
        <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
          <div className="px-4 py-4 sm:px-0">
            <div className="backdrop-blur-lg bg-white/30 border border-white/40 rounded-2xl p-5 shadow-xl mb-6">
              <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-600 via-purple-600 to-cyan-600 bg-clip-text text-transparent mb-4">
                ⚙️ Settings
              </h1>
              
              {/* Tab Navigation */}
              <nav className="flex space-x-4">
                <button
                  onClick={() => setActiveTab('profile')}
                  className={`group py-2 px-4 rounded-2xl font-semibold text-sm transition-all duration-300 hover:scale-105 ${
                    activeTab === 'profile'
                      ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-lg'
                      : 'backdrop-blur-sm bg-white/30 text-gray-700 hover:bg-white/50 border border-white/40'
                  }`}
                >
                  <span className={`mr-2 ${activeTab === 'profile' ? '' : 'group-hover:scale-110'} transition-transform duration-300`}>👤</span>
                  Profile
                </button>
                <button
                  onClick={() => setActiveTab('notifications')}
                  className={`group py-2 px-4 rounded-2xl font-semibold text-sm transition-all duration-300 hover:scale-105 ${
                    activeTab === 'notifications'
                      ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-lg'
                      : 'backdrop-blur-sm bg-white/30 text-gray-700 hover:bg-white/50 border border-white/40'
                  }`}
                >
                  <span className={`mr-2 ${activeTab === 'notifications' ? '' : 'group-hover:scale-110'} transition-transform duration-300`}>🔔</span>
                  Notifications
                </button>
                {state.user?.role === 'admin' && (
                  <button
                    onClick={() => setActiveTab('system')}
                    className={`group py-2 px-4 rounded-2xl font-semibold text-sm transition-all duration-300 hover:scale-105 ${
                      activeTab === 'system'
                        ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-lg'
                        : 'backdrop-blur-sm bg-white/30 text-gray-700 hover:bg-white/50 border border-white/40'
                    }`}
                  >
                    <span className={`mr-2 ${activeTab === 'system' ? '' : 'group-hover:scale-110'} transition-transform duration-300`}>⚙️</span>
                    System
                  </button>
                )}
              </nav>
            </div>

            {/* Message */}
            {message && (
              <div className={`mt-6 p-6 rounded-2xl backdrop-blur-lg border shadow-xl ${
                message.includes('Error') 
                  ? 'bg-red-50/80 text-red-800 border-red-200/50' 
                  : 'bg-green-50/80 text-green-800 border-green-200/50'
              }`}>
                <div className="font-medium">{message}</div>
              </div>
            )}

            {/* Tab Content */}
            <div className="mt-6">
              {/* Profile Tab */}
              {activeTab === 'profile' && (
                <div className="backdrop-blur-lg bg-white/40 border border-white/50 rounded-3xl shadow-xl p-6">
                  <h2 className="text-xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent mb-4">
                    👤 Profile Information
                  </h2>
                  <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                    <div>
                      <label className="block text-sm font-semibold text-gray-700 mb-2 uppercase tracking-wider">Full Name</label>
                      <input
                        type="text"
                        value={userProfile.full_name}
                        onChange={(e) => setUserProfile(prev => ({ ...prev, full_name: e.target.value }))}
                        className="mt-1 block w-full border border-white/30 rounded-2xl shadow-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent backdrop-blur-sm bg-white/30 px-3 py-2 transition-all duration-300"
                      />
                    </div>
                    
                    <div>
                      <label className="block text-sm font-semibold text-gray-700 mb-2 uppercase tracking-wider">Username</label>
                      <input
                        type="text"
                        value={userProfile.username}
                        onChange={(e) => setUserProfile(prev => ({ ...prev, username: e.target.value }))}
                        className="mt-1 block w-full border border-white/30 rounded-2xl shadow-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent backdrop-blur-sm bg-white/30 px-3 py-2 transition-all duration-300"
                      />
                    </div>
                    
                    <div>
                      <label className="block text-sm font-semibold text-gray-700 mb-2 uppercase tracking-wider">Email</label>
                      <input
                        type="email"
                        value={userProfile.email}
                        onChange={(e) => setUserProfile(prev => ({ ...prev, email: e.target.value }))}
                        className="mt-1 block w-full border border-white/30 rounded-2xl shadow-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent backdrop-blur-sm bg-white/30 px-4 py-3 transition-all duration-300"
                      />
                    </div>
                    
                    <div>
                      <label className="block text-sm font-semibold text-gray-700 mb-2 uppercase tracking-wider">Role</label>
                      <input
                        type="text"
                        value={userProfile.role}
                        disabled
                        className="mt-1 block w-full border border-white/30 rounded-2xl shadow-lg backdrop-blur-sm bg-white/20 text-gray-600 px-4 py-3"
                      />
                    </div>
                  </div>
                  
                  <div className="mt-8">
                    <button
                      onClick={handleProfileSave}
                      disabled={loading}
                      className="group bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white px-8 py-3 rounded-2xl text-sm font-semibold disabled:opacity-50 transition-all duration-300 hover:scale-105 shadow-lg"
                    >
                      {loading ? (
                        <span className="flex items-center">
                          <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent mr-2"></div>
                          Saving...
                        </span>
                      ) : (
                        <span className="group-hover:scale-110 transition-transform duration-300">💾 Save Profile</span>
                      )}
                    </button>
                  </div>
                </div>
              )}

              {/* Notifications Tab */}
              {activeTab === 'notifications' && (
                <div className="backdrop-blur-lg bg-white/40 border border-white/50 rounded-3xl shadow-xl p-6">
                  <h2 className="text-xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent mb-4">
                    🔔 Notification Preferences
                  </h2>
                  <div className="space-y-4">
                    <div className="flex items-center justify-between p-3 backdrop-blur-sm bg-white/30 rounded-2xl border border-white/40">
                      <div>
                        <h3 className="text-sm font-bold text-gray-800">Enable Notifications</h3>
                        <p className="text-sm text-gray-600 mt-1">Receive system notifications</p>
                      </div>
                      <label className="flex items-center">
                        <input
                          type="checkbox"
                          checked={userProfile.notifications_enabled}
                          onChange={(e) => setUserProfile(prev => ({ ...prev, notifications_enabled: e.target.checked }))}
                          className="rounded-lg border-white/30 text-blue-600 shadow-lg focus:border-blue-300 focus:ring focus:ring-blue-200 focus:ring-opacity-50 w-5 h-5"
                        />
                      </label>
                    </div>
                    
                    <div className="flex items-center justify-between p-3 backdrop-blur-sm bg-white/30 rounded-2xl border border-white/40">
                      <div>
                        <h3 className="text-sm font-bold text-gray-800">Email Alerts</h3>
                        <p className="text-sm text-gray-600 mt-1">Receive alerts via email</p>
                      </div>
                      <label className="flex items-center">
                        <input
                          type="checkbox"
                          checked={userProfile.email_alerts}
                          onChange={(e) => setUserProfile(prev => ({ ...prev, email_alerts: e.target.checked }))}
                          className="rounded-lg border-white/30 text-blue-600 shadow-lg focus:border-blue-300 focus:ring focus:ring-blue-200 focus:ring-opacity-50 w-5 h-5"
                        />
                      </label>
                    </div>
                    
                    <div className="flex items-center justify-between p-4 backdrop-blur-sm bg-white/30 rounded-2xl border border-white/40">
                      <div>
                        <h3 className="text-sm font-bold text-gray-800">SMS Alerts</h3>
                        <p className="text-sm text-gray-600 mt-1">Receive alerts via SMS</p>
                      </div>
                      <label className="flex items-center">
                        <input
                          type="checkbox"
                          checked={userProfile.sms_alerts}
                          onChange={(e) => setUserProfile(prev => ({ ...prev, sms_alerts: e.target.checked }))}
                          className="rounded-lg border-white/30 text-blue-600 shadow-lg focus:border-blue-300 focus:ring focus:ring-blue-200 focus:ring-opacity-50 w-5 h-5"
                        />
                      </label>
                    </div>
                  </div>
                  
                  <div className="mt-8">
                    <button
                      onClick={handleProfileSave}
                      disabled={loading}
                      className="group bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white px-8 py-3 rounded-2xl text-sm font-semibold disabled:opacity-50 transition-all duration-300 hover:scale-105 shadow-lg"
                    >
                      {loading ? (
                        <span className="flex items-center">
                          <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent mr-2"></div>
                          Saving...
                        </span>
                      ) : (
                        <span className="group-hover:scale-110 transition-transform duration-300">🔔 Save Preferences</span>
                      )}
                    </button>
                  </div>
                </div>
            )}

            {/* System Tab (Admin Only) */}
            {activeTab === 'system' && state.user?.role === 'admin' && (
              <div className="backdrop-blur-sm bg-white/30 border border-white/20 rounded-3xl p-6 shadow-2xl">
                <div className="flex items-center mb-6">
                  <div className="p-2 bg-gradient-to-r from-purple-500 to-pink-500 rounded-2xl mr-3">
                    <span className="text-xl">⚙️</span>
                  </div>
                  <div>
                    <h2 className="text-xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">System Settings</h2>
                    <p className="text-gray-600 text-sm">Configure system-wide parameters and behavior</p>
                  </div>
                </div>
                
                <div className="space-y-4">
                  {systemSettings.map((setting) => (
                    <div key={setting.key} className="backdrop-blur-sm bg-white/40 border border-white/30 rounded-2xl p-4 hover:bg-white/50 transition-all duration-300 hover:scale-[1.01] hover:shadow-xl">
                      <div className="flex items-center justify-between">
                        <div className="flex-1">
                          <h3 className="text-base font-semibold text-gray-800 mb-1">{setting.key.replace(/_/g, ' ').toUpperCase()}</h3>
                          <p className="text-gray-600 text-sm">{setting.description}</p>
                        </div>
                        <div className="ml-4">
                          {setting.data_type === 'bool' ? (
                            <label className="relative inline-flex items-center cursor-pointer">
                              <input
                                type="checkbox"
                                checked={setting.value}
                                onChange={(e) => handleSystemSettingSave(setting.key, e.target.checked)}
                                className="sr-only peer"
                              />
                              <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-purple-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-purple-600"></div>
                            </label>
                          ) : (
                            <input
                              type={setting.data_type === 'int' ? 'number' : 'text'}
                              value={setting.value}
                              onChange={(e) => {
                                const value = setting.data_type === 'int' ? parseInt(e.target.value) : 
                                             setting.data_type === 'float' ? parseFloat(e.target.value) : e.target.value
                                handleSystemSettingSave(setting.key, value)
                              }}
                              className="backdrop-blur-sm bg-white/50 border border-white/30 rounded-xl px-4 py-2 w-32 text-gray-800 focus:outline-none focus:ring-2 focus:ring-purple-500/50 focus:border-transparent transition-all duration-300"
                            />
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
    </div>
  )
}

export default SettingsPage