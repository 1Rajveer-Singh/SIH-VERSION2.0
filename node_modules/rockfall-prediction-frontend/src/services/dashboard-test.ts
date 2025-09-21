import { api } from './api'

export interface DashboardStats {
  total_sites: number
  total_devices: number
  active_devices: number
  total_predictions: number
  recent_predictions: number
  active_alerts: number
  current_risk_level: string
  prediction_accuracy: number
  devices_online: number
  devices_total: number
  high_risk_sites?: number
  predictions_today?: number
  system_uptime?: string
}

export interface PredictionSummary {
  id: string
  site_id: string
  site_name?: string
  zone_id?: string
  risk_level: string
  probability: number
  confidence: number
  timestamp: string
  recommendations: string[]
}

export interface RecentAlert {
  id: string
  type: string
  severity: string
  message: string
  site_id?: string
  site_name?: string
  timestamp: string
  status: string
}

export interface SiteStatus {
  id: string
  name: string
  status: string
  current_risk_level?: string
  devices_count: number
  active_alerts: number
}

// Test API for debugging (no auth required)
export const testDashboardAPI = {
  async getStats(): Promise<DashboardStats> {
    const response = await api.get('/test/dashboard/stats')
    return response.data
  },

  async getPredictionSummary(): Promise<PredictionSummary[]> {
    const response = await api.get('/test/dashboard/predictions')
    return response.data
  },

  async getRecentAlerts(): Promise<RecentAlert[]> {
    const response = await api.get('/test/dashboard/alerts')
    return response.data
  }
}

// Production API (requires auth)
export const dashboardAPI = {
  async getStats(): Promise<DashboardStats> {
    const response = await api.get('/api/dashboard/stats')
    return response.data
  },

  async getPredictionSummary(): Promise<PredictionSummary[]> {
    const response = await api.get('/api/dashboard/predictions')
    return response.data
  },

  async getRecentAlerts(): Promise<RecentAlert[]> {
    const response = await api.get('/api/dashboard/alerts')
    return response.data
  },

  async runImmediatePrediction(siteId: string): Promise<PredictionSummary> {
    const response = await api.post('/api/dashboard/predictions/run', { site_id: siteId })
    return response.data
  }
}