import React, { useState, useRef } from 'react'
import { useAuth } from '../contexts/AuthContext'

interface UserProfile {
  id: string
  full_name: string
  username: string
  email: string
  role: string
  phone?: string
  department?: string
  location?: string
  bio?: string
  avatar?: string
  status: 'active' | 'away' | 'busy' | 'offline'
  joined_date: Date
  last_login: Date
}

function ProfilePage() {
  const { state } = useAuth()
  const [isEditing, setIsEditing] = useState(false)
  const [activeTab, setActiveTab] = useState('overview')
  const fileInputRef = useRef<HTMLInputElement>(null)
  
  // Mock user profile data
  const [userProfile, setUserProfile] = useState<UserProfile>({
    id: state.user?.id || '1',
    full_name: state.user?.full_name || 'Dr. Sarah Chen',
    username: state.user?.username || 'sarah.chen',
    email: state.user?.email || 'sarah.chen@rockfall.com',
    role: state.user?.role || 'admin',
    phone: '+1 (555) 123-4567',
    department: 'Geological Engineering',
    location: 'Vancouver, BC, Canada',
    bio: 'Senior Geological Engineer with 15+ years of experience in rockfall prediction and mining safety systems. Specialized in AI-driven risk assessment and predictive modeling.',
    avatar: undefined,
    status: 'active',
    joined_date: new Date('2020-03-15'),
    last_login: new Date()
  })

  const [editForm, setEditForm] = useState({
    full_name: userProfile.full_name,
    phone: userProfile.phone || '',
    department: userProfile.department || '',
    location: userProfile.location || '',
    bio: userProfile.bio || '',
    status: userProfile.status
  })

  const getRoleDisplayName = (role: string) => {
    const roleMap: { [key: string]: string } = {
      'admin': 'System Administrator',
      'geologist': 'Geologist',
      'engineer': 'Engineer',
      'operator': 'Site Operator',
      'viewer': 'Viewer'
    }
    return roleMap[role] || role
  }

  const getStatusColor = (status: string) => {
    const statusColors: { [key: string]: string } = {
      'active': 'bg-green-500',
      'away': 'bg-yellow-500',
      'busy': 'bg-red-500',
      'offline': 'bg-gray-500'
    }
    return statusColors[status] || 'bg-gray-500'
  }

  const handleSaveProfile = () => {
    setUserProfile(prev => ({
      ...prev,
      full_name: editForm.full_name,
      phone: editForm.phone,
      department: editForm.department,
      location: editForm.location,
      bio: editForm.bio,
      status: editForm.status
    }))
    setIsEditing(false)
  }

  const handleAvatarClick = () => {
    fileInputRef.current?.click()
  }

  const handleAvatarChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      const reader = new FileReader()
      reader.onload = (e) => {
        setUserProfile(prev => ({
          ...prev,
          avatar: e.target?.result as string
        }))
      }
      reader.readAsDataURL(file)
    }
  }

  return (
    <div className="min-h-screen bg-white relative">
      <div className="absolute inset-0 bg-gradient-to-br from-blue-50/20 via-purple-50/10 to-cyan-50/20"></div>
      <div className="relative z-10">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          {/* Profile Header */}
          <div className="mb-6">
            <div className="backdrop-blur-lg bg-white/40 border border-white/50 rounded-3xl shadow-xl overflow-hidden mb-6">
              <div className="bg-gradient-to-r from-blue-600 via-purple-600 to-cyan-600 px-6 py-12 relative overflow-hidden">
                <div className="absolute inset-0 bg-gradient-to-r from-blue-600/90 via-purple-600/90 to-cyan-600/90"></div>
                <div className="relative z-10 flex items-center space-x-8">
                  {/* Avatar */}
                  <div className="relative group">
                    <div 
                      className="w-32 h-32 rounded-full bg-white/20 backdrop-blur-sm border-4 border-white/30 flex items-center justify-center cursor-pointer group-hover:scale-105 transition-all duration-300 overflow-hidden"
                      onClick={handleAvatarClick}
                    >
                      {userProfile.avatar ? (
                        <img 
                          src={userProfile.avatar} 
                          alt="Profile Avatar" 
                          className="w-full h-full object-cover"
                        />
                      ) : (
                        <span className="text-5xl text-white/80">👤</span>
                      )}
                    </div>
                    <div className="absolute inset-0 rounded-full bg-black/20 opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex items-center justify-center">
                      <span className="text-white text-sm font-medium">Change Photo</span>
                    </div>
                    <input
                      ref={fileInputRef}
                      type="file"
                      accept="image/*"
                      onChange={handleAvatarChange}
                      className="hidden"
                    />
                  </div>

                  {/* User Info */}
                  <div className="flex-1">
                    <div className="flex items-center space-x-4 mb-4">
                      <h1 className="text-4xl font-bold text-white">{userProfile.full_name}</h1>
                      <div className={`w-4 h-4 rounded-full ${getStatusColor(userProfile.status)} border-2 border-white`}></div>
                    </div>
                    <div className="space-y-2">
                      <p className="text-white/90 text-lg">@{userProfile.username}</p>
                      <p className="text-white/80">{userProfile.email}</p>
                      <div className="flex items-center space-x-4 text-white/70">
                        <span>{getRoleDisplayName(userProfile.role)}</span>
                        <span>•</span>
                        <span>{userProfile.department}</span>
                        <span>•</span>
                        <span>{userProfile.location}</span>
                      </div>
                    </div>
                    <div className="mt-6 flex space-x-4">
                      <button
                        onClick={() => setIsEditing(!isEditing)}
                        className="bg-white/20 backdrop-blur-sm text-white px-6 py-2 rounded-2xl border border-white/30 hover:bg-white/30 transition-all duration-300 font-medium"
                      >
                        {isEditing ? 'Cancel Edit' : 'Edit Profile'}
                      </button>
                      <button className="bg-white/20 backdrop-blur-sm text-white px-6 py-2 rounded-2xl border border-white/30 hover:bg-white/30 transition-all duration-300 font-medium">
                        Download Report
                      </button>
                    </div>
                  </div>
                </div>
              </div>

              {/* Navigation Tabs */}
              <div className="px-6 py-4 bg-white/20 backdrop-blur-sm border-t border-white/20">
                <nav className="flex space-x-4">
                  {[
                    { id: 'overview', label: 'Overview', icon: '👤' },
                    { id: 'activity', label: 'Activity', icon: '📊' },
                    { id: 'settings', label: 'Settings', icon: '⚙️' }
                  ].map((tab) => (
                    <button
                      key={tab.id}
                      onClick={() => setActiveTab(tab.id)}
                      className={`group flex items-center space-x-3 px-4 py-2 rounded-2xl font-semibold transition-all duration-300 hover:scale-105 ${
                        activeTab === tab.id
                          ? 'bg-white/30 text-white shadow-lg border border-white/30'
                          : 'text-white/70 hover:text-white hover:bg-white/20 border border-white/10'
                      }`}
                    >
                      <span className="group-hover:scale-110 transition-transform duration-300">{tab.icon}</span>
                      <span>{tab.label}</span>
                    </button>
                  ))}
                </nav>
              </div>
            </div>
          </div>

          {/* Tab Content */}
          {activeTab === 'overview' && (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Profile Information */}
              <div className="lg:col-span-2 space-y-6">
                <div className="backdrop-blur-lg bg-white/40 border border-white/50 rounded-3xl shadow-xl p-5">
                  <div className="flex items-center mb-4">
                    <div className="p-3 bg-gradient-to-r from-blue-500 to-purple-500 rounded-2xl mr-4">
                      <span className="text-2xl">👤</span>
                    </div>
                    <div>
                      <h2 className="text-xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                        Profile Information
                      </h2>
                      <p className="text-gray-600">Manage your personal details</p>
                    </div>
                  </div>
                  
                  {isEditing ? (
                    <div className="space-y-6">
                      <div>
                        <label className="block text-sm font-semibold text-gray-700 mb-3 uppercase tracking-wider">Full Name</label>
                        <input
                          type="text"
                          value={editForm.full_name}
                          onChange={(e) => setEditForm(prev => ({ ...prev, full_name: e.target.value }))}
                          className="w-full px-4 py-3 backdrop-blur-sm bg-white/50 border border-white/30 rounded-2xl focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-transparent transition-all duration-300 text-gray-800"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-semibold text-gray-700 mb-3 uppercase tracking-wider">Phone</label>
                        <input
                          type="tel"
                          value={editForm.phone}
                          onChange={(e) => setEditForm(prev => ({ ...prev, phone: e.target.value }))}
                          className="w-full px-4 py-3 backdrop-blur-sm bg-white/50 border border-white/30 rounded-2xl focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-transparent transition-all duration-300 text-gray-800"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-semibold text-gray-700 mb-3 uppercase tracking-wider">Department</label>
                        <input
                          type="text"
                          value={editForm.department}
                          onChange={(e) => setEditForm(prev => ({ ...prev, department: e.target.value }))}
                          className="w-full px-4 py-3 backdrop-blur-sm bg-white/50 border border-white/30 rounded-2xl focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-transparent transition-all duration-300 text-gray-800"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-semibold text-gray-700 mb-3 uppercase tracking-wider">Location</label>
                        <input
                          type="text"
                          value={editForm.location}
                          onChange={(e) => setEditForm(prev => ({ ...prev, location: e.target.value }))}
                          className="w-full px-4 py-3 backdrop-blur-sm bg-white/50 border border-white/30 rounded-2xl focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-transparent transition-all duration-300 text-gray-800"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">Bio</label>
                        <textarea
                          value={editForm.bio}
                          onChange={(e) => setEditForm(prev => ({ ...prev, bio: e.target.value }))}
                          rows={4}
                          className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">Status</label>
                        <select
                          value={editForm.status}
                          onChange={(e) => setEditForm(prev => ({ ...prev, status: e.target.value as any }))}
                          className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        >
                          <option value="active">Active</option>
                          <option value="away">Away</option>
                          <option value="busy">Busy</option>
                          <option value="offline">Offline</option>
                        </select>
                      </div>
                      <div className="flex space-x-3 pt-4">
                        <button
                          onClick={handleSaveProfile}
                          className="bg-blue-600 text-white px-6 py-2 rounded-xl hover:bg-blue-700 transition-colors font-medium"
                        >
                          Save Changes
                        </button>
                        <button
                          onClick={() => setIsEditing(false)}
                          className="bg-gray-100 text-gray-700 px-6 py-2 rounded-xl hover:bg-gray-200 transition-colors font-medium"
                        >
                          Cancel
                        </button>
                      </div>
                    </div>
                  ) : (
                    <div className="space-y-4">
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                          <label className="block text-sm font-medium text-gray-500">Full Name</label>
                          <p className="text-gray-900 font-medium">{userProfile.full_name}</p>
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-gray-500">Username</label>
                          <p className="text-gray-900 font-medium">@{userProfile.username}</p>
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-gray-500">Email</label>
                          <p className="text-gray-900 font-medium">{userProfile.email}</p>
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-gray-500">Phone</label>
                          <p className="text-gray-900 font-medium">{userProfile.phone || 'Not provided'}</p>
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-gray-500">Department</label>
                          <p className="text-gray-900 font-medium">{userProfile.department || 'Not specified'}</p>
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-gray-500">Location</label>
                          <p className="text-gray-900 font-medium">{userProfile.location || 'Not specified'}</p>
                        </div>
                      </div>
                      {userProfile.bio && (
                        <div className="pt-4 border-t border-gray-100">
                          <label className="block text-sm font-medium text-gray-500 mb-2">Bio</label>
                          <p className="text-gray-700 leading-relaxed">{userProfile.bio}</p>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              </div>

              {/* Sidebar */}
              <div className="space-y-4">
                {/* Quick Stats */}
                <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-4">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Stats</h3>
                  <div className="space-y-3">
                    <div className="flex justify-between">
                      <span className="text-gray-600">Reports Generated</span>
                      <span className="font-semibold text-gray-900">47</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Sites Monitored</span>
                      <span className="font-semibold text-gray-900">12</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Predictions Made</span>
                      <span className="font-semibold text-gray-900">234</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Last Login</span>
                      <span className="font-semibold text-gray-900">Today</span>
                    </div>
                  </div>
                </div>

                {/* Role & Permissions */}
                <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-4">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Role & Permissions</h3>
                  <div className="space-y-3">
                    <div className="flex items-center space-x-3">
                      <div className="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center">
                        🛡️
                      </div>
                      <div>
                        <p className="font-medium text-gray-900">{getRoleDisplayName(userProfile.role)}</p>
                        <p className="text-sm text-gray-600">Full system access</p>
                      </div>
                    </div>
                    <div className="text-sm text-gray-600 space-y-1 pl-11">
                      <p>✅ View all sites and reports</p>
                      <p>✅ Manage users and permissions</p>
                      <p>✅ Configure system settings</p>
                      <p>✅ Generate and export reports</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'activity' && (
            <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-4">
              <h2 className="text-lg font-semibold text-gray-900 mb-3">Recent Activity</h2>
              <div className="space-y-4">
                {[
                  { action: 'Generated weekly risk assessment report', time: '2 hours ago', icon: '📊' },
                  { action: 'Updated sensor configuration for Site Alpha-7', time: '5 hours ago', icon: '🔧' },
                  { action: 'Reviewed high-risk alert for geological instability', time: '1 day ago', icon: '🚨' },
                  { action: 'Completed ML model calibration', time: '2 days ago', icon: '🤖' }
                ].map((activity, index) => (
                  <div key={index} className="flex items-center space-x-4 p-3 rounded-xl hover:bg-gray-50">
                    <div className="text-2xl">{activity.icon}</div>
                    <div className="flex-1">
                      <p className="text-gray-900">{activity.action}</p>
                      <p className="text-sm text-gray-500">{activity.time}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {activeTab === 'settings' && (
            <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-4">
              <h2 className="text-lg font-semibold text-gray-900 mb-3">Account Settings</h2>
              <div className="space-y-6">
                <div className="flex items-center justify-between py-4 border-b border-gray-100">
                  <div>
                    <h3 className="font-medium text-gray-900">Email Notifications</h3>
                    <p className="text-sm text-gray-600">Receive alerts and updates via email</p>
                  </div>
                  <button className="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm">
                    Configure
                  </button>
                </div>
                <div className="flex items-center justify-between py-4 border-b border-gray-100">
                  <div>
                    <h3 className="font-medium text-gray-900">Two-Factor Authentication</h3>
                    <p className="text-sm text-gray-600">Add an extra layer of security</p>
                  </div>
                  <button className="bg-green-600 text-white px-4 py-2 rounded-lg text-sm">
                    Enable
                  </button>
                </div>
                <div className="flex items-center justify-between py-4">
                  <div>
                    <h3 className="font-medium text-gray-900">Change Password</h3>
                    <p className="text-sm text-gray-600">Update your account password</p>
                  </div>
                  <button className="bg-gray-600 text-white px-4 py-2 rounded-lg text-sm">
                    Update
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default ProfilePage