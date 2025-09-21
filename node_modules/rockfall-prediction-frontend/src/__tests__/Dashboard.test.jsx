// Dashboard component tests
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import { AuthProvider } from '../contexts/AuthContext'
import Dashboard from '../components/Dashboard/Dashboard'

// Mock API services
vi.mock('../services/api', () => ({
  getSites: vi.fn(),
  getSensors: vi.fn(),
  getRecentAlerts: vi.fn(),
  getSystemStatus: vi.fn(),
}))

// Mock Chart.js
vi.mock('react-chartjs-2', () => ({
  Line: ({ data, options }) => (
    <div data-testid="line-chart">
      <div data-testid="chart-data">{JSON.stringify(data)}</div>
      <div data-testid="chart-options">{JSON.stringify(options)}</div>
    </div>
  ),
  Bar: ({ data, options }) => (
    <div data-testid="bar-chart">
      <div data-testid="chart-data">{JSON.stringify(data)}</div>
      <div data-testid="chart-options">{JSON.stringify(options)}</div>
    </div>
  ),
  Doughnut: ({ data, options }) => (
    <div data-testid="doughnut-chart">
      <div data-testid="chart-data">{JSON.stringify(data)}</div>
      <div data-testid="chart-options">{JSON.stringify(options)}</div>
    </div>
  ),
}))

const mockUser = {
  username: 'testuser',
  role: 'admin',
  permissions: ['read', 'write', 'admin']
}

const renderWithProviders = (component) => {
  return render(
    <BrowserRouter>
      <AuthProvider value={{ user: mockUser, isAuthenticated: true }}>
        {component}
      </AuthProvider>
    </BrowserRouter>
  )
}

describe('Dashboard Component', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    
    // Setup default mock returns
    const api = require('../services/api')
    api.getSites.mockResolvedValue({
      items: [
        {
          id: 'site-001',
          name: 'Test Site 1',
          status: 'active',
          location: { lat: 39.7392, lng: -104.9903 }
        },
        {
          id: 'site-002',
          name: 'Test Site 2',
          status: 'maintenance',
          location: { lat: 40.7589, lng: -111.8883 }
        }
      ],
      total: 2
    })
    
    api.getSensors.mockResolvedValue({
      items: [
        {
          id: 'sensor-001',
          name: 'Accelerometer 1',
          status: 'active',
          site_id: 'site-001'
        },
        {
          id: 'sensor-002',
          name: 'Inclinometer 1',
          status: 'offline',
          site_id: 'site-001'
        }
      ],
      total: 2
    })
    
    api.getRecentAlerts.mockResolvedValue({
      items: [
        {
          id: 'alert-001',
          title: 'High Vibration Detected',
          severity: 'high',
          status: 'active',
          created_at: '2024-01-15T12:00:00Z',
          site_id: 'site-001'
        }
      ],
      total: 1
    })
    
    api.getSystemStatus.mockResolvedValue({
      database: 'healthy',
      api: 'healthy',
      ml_models: 'healthy',
      notifications: 'healthy'
    })
  })

  it('renders dashboard layout', async () => {
    renderWithProviders(<Dashboard />)
    
    await waitFor(() => {
      expect(screen.getByText(/dashboard/i)).toBeInTheDocument()
      expect(screen.getByText(/system overview/i)).toBeInTheDocument()
    })
  })

  it('displays site statistics', async () => {
    renderWithProviders(<Dashboard />)
    
    await waitFor(() => {
      expect(screen.getByText('Total Sites')).toBeInTheDocument()
      expect(screen.getByText('2')).toBeInTheDocument()
      expect(screen.getByText('Active Sites')).toBeInTheDocument()
      expect(screen.getByText('1')).toBeInTheDocument()
    })
  })

  it('displays sensor statistics', async () => {
    renderWithProviders(<Dashboard />)
    
    await waitFor(() => {
      expect(screen.getByText('Total Sensors')).toBeInTheDocument()
      expect(screen.getByText('2')).toBeInTheDocument()
      expect(screen.getByText('Online Sensors')).toBeInTheDocument()
      expect(screen.getByText('1')).toBeInTheDocument()
    })
  })

  it('displays alert statistics', async () => {
    renderWithProviders(<Dashboard />)
    
    await waitFor(() => {
      expect(screen.getByText('Active Alerts')).toBeInTheDocument()
      expect(screen.getByText('1')).toBeInTheDocument()
    })
  })

  it('displays recent alerts', async () => {
    renderWithProviders(<Dashboard />)
    
    await waitFor(() => {
      expect(screen.getByText('Recent Alerts')).toBeInTheDocument()
      expect(screen.getByText('High Vibration Detected')).toBeInTheDocument()
    })
  })

  it('displays system status', async () => {
    renderWithProviders(<Dashboard />)
    
    await waitFor(() => {
      expect(screen.getByText('System Status')).toBeInTheDocument()
      expect(screen.getByText('Database')).toBeInTheDocument()
      expect(screen.getByText('API')).toBeInTheDocument()
      expect(screen.getByText('ML Models')).toBeInTheDocument()
      expect(screen.getByText('Notifications')).toBeInTheDocument()
    })
  })

  it('renders charts', async () => {
    renderWithProviders(<Dashboard />)
    
    await waitFor(() => {
      expect(screen.getByTestId('line-chart')).toBeInTheDocument()
      expect(screen.getByTestId('bar-chart')).toBeInTheDocument()
      expect(screen.getByTestId('doughnut-chart')).toBeInTheDocument()
    })
  })

  it('handles API errors gracefully', async () => {
    const api = require('../services/api')
    api.getSites.mockRejectedValue(new Error('API Error'))
    api.getSensors.mockRejectedValue(new Error('API Error'))
    api.getRecentAlerts.mockRejectedValue(new Error('API Error'))

    renderWithProviders(<Dashboard />)
    
    await waitFor(() => {
      expect(screen.getByText(/error loading dashboard data/i)).toBeInTheDocument()
    })
  })

  it('shows loading state initially', () => {
    const api = require('../services/api')
    api.getSites.mockImplementation(() => new Promise(() => {})) // Never resolves

    renderWithProviders(<Dashboard />)
    
    expect(screen.getByTestId('loading-spinner')).toBeInTheDocument()
  })

  it('refreshes data when refresh button is clicked', async () => {
    const api = require('../services/api')
    
    renderWithProviders(<Dashboard />)
    
    await waitFor(() => {
      expect(screen.getByText('Dashboard')).toBeInTheDocument()
    })

    const refreshButton = screen.getByRole('button', { name: /refresh/i })
    fireEvent.click(refreshButton)

    // APIs should be called again
    expect(api.getSites).toHaveBeenCalledTimes(2)
    expect(api.getSensors).toHaveBeenCalledTimes(2)
    expect(api.getRecentAlerts).toHaveBeenCalledTimes(2)
  })
})