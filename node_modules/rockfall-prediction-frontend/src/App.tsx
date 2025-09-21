import React from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuth } from './contexts/AuthContext'
import LandingPage from './pages/LandingPage'
import LoginPage from './pages/LoginPage'
import HomePage from './pages/HomePage'
import ModernHomePage from './pages/ModernHomePage'
import ProfilePage from './pages/ProfilePage'
import DashboardPage from './pages/DashboardPage'
import PredictionsPage from './pages/PredictionsPage'
import ReportPage from './pages/ReportPage'
import SitesPage from './pages/SitesPage'
import DeviceManagerPage from './pages/DeviceManagerPage'
import SettingsPage from './pages/SettingsPage'
import HelpPage from './pages/HelpPage'
import ServicesPage from './pages/ServicesPage'
import LoadingSpinner from './components/LoadingSpinner'

function App() {
  const { state } = useAuth()

  if (state.isLoading) {
    return <LoadingSpinner />
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Routes>
        <Route 
          path="/" 
          element={!state.isAuthenticated ? <LandingPage /> : <Navigate to="/dashboard" />} 
        />
        <Route 
          path="/login" 
          element={!state.isAuthenticated ? <LoginPage /> : <Navigate to="/dashboard" />} 
        />
        <Route 
          path="/home" 
          element={state.isAuthenticated ? <ModernHomePage /> : <Navigate to="/" />} 
        />
        <Route 
          path="/profile" 
          element={state.isAuthenticated ? <ProfilePage /> : <Navigate to="/" />} 
        />
        <Route 
          path="/dashboard" 
          element={state.isAuthenticated ? <DashboardPage /> : <Navigate to="/" />} 
        />
        <Route 
          path="/predictions" 
          element={state.isAuthenticated ? <PredictionsPage /> : <Navigate to="/" />} 
        />
        <Route 
          path="/reports" 
          element={state.isAuthenticated ? <ReportPage /> : <Navigate to="/" />} 
        />
        <Route 
          path="/sites" 
          element={state.isAuthenticated ? <SitesPage /> : <Navigate to="/" />} 
        />
        <Route 
          path="/devices" 
          element={state.isAuthenticated ? <DeviceManagerPage /> : <Navigate to="/" />} 
        />
        <Route 
          path="/settings" 
          element={state.isAuthenticated ? <SettingsPage /> : <Navigate to="/" />} 
        />
        <Route 
          path="/help" 
          element={state.isAuthenticated ? <HelpPage /> : <Navigate to="/" />} 
        />
        <Route 
          path="/services" 
          element={state.isAuthenticated ? <ServicesPage /> : <Navigate to="/" />} 
        />
      </Routes>
    </div>
  )
}

export default App