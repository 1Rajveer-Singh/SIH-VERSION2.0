import React from 'react'
import { Outlet, Link, useLocation } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'

function MainLayout() {
  const { state, logout } = useAuth()
  const location = useLocation()

  const navigation = [
    { name: 'Dashboard', href: '/dashboard', icon: '📊', current: location.pathname === '/dashboard' },
    { name: 'Mining Sites', href: '/sites', icon: '🏔️', current: location.pathname === '/sites' },
    { name: 'Device Manager', href: '/devices', icon: '📱', current: location.pathname === '/devices' },
    { name: 'Predictions', href: '/predictions', icon: '🤖', current: location.pathname === '/predictions' },
    { name: 'Reports', href: '/reports', icon: '📈', current: location.pathname === '/reports' },
    { name: 'Settings', href: '/settings', icon: '⚙️', current: location.pathname === '/settings' },
  ]

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Top Navigation */}
      <nav className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-semibold text-gray-900 mr-8">
                🏔️ Rockfall Prediction System
              </h1>
              
              {/* Navigation Links */}
              <div className="hidden md:flex space-x-1">
                {navigation.map((item) => (
                  <Link
                    key={item.name}
                    to={item.href}
                    className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                      item.current
                        ? 'bg-blue-100 text-blue-700'
                        : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                    }`}
                  >
                    <span className="mr-2">{item.icon}</span>
                    {item.name}
                  </Link>
                ))}
              </div>
            </div>
            
            {/* User Menu */}
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <div className="w-3 h-3 rounded-full bg-green-400"></div>
                <span className="text-sm text-gray-600 hidden sm:block">System Online</span>
              </div>
              
              <div className="flex items-center space-x-2">
                <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                  <span className="text-sm font-medium text-blue-600">
                    {(state.user?.full_name || state.user?.username || 'U').charAt(0).toUpperCase()}
                  </span>
                </div>
                <span className="text-sm text-gray-700 hidden sm:block">
                  {state.user?.full_name || state.user?.username}
                </span>
              </div>
              
              <button
                onClick={logout}
                className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-md text-sm font-medium"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
        
        {/* Mobile Navigation */}
        <div className="md:hidden border-t">
          <div className="px-2 pt-2 pb-3 space-y-1">
            {navigation.map((item) => (
              <Link
                key={item.name}
                to={item.href}
                className={`block px-3 py-2 rounded-md text-base font-medium ${
                  item.current
                    ? 'bg-blue-100 text-blue-700'
                    : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                }`}
              >
                <span className="mr-2">{item.icon}</span>
                {item.name}
              </Link>
            ))}
          </div>
        </div>
      </nav>

      {/* Page Content */}
      <main className="flex-1">
        <Outlet />
      </main>
    </div>
  )
}

export default MainLayout