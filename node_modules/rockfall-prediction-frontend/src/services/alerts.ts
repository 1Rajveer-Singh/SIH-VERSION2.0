import api from './api'

export type AlertSeverity = 'low' | 'medium' | 'high' | 'critical'
export type AlertStatus = 'active' | 'acknowledged' | 'resolved' | 'dismissed'
export type AlertType = 'prediction' | 'sensor_malfunction' | 'threshold_exceeded' | 'system_error' | 'maintenance_due'

export interface Alert {
  id: string
  site_id: string
  title: string
  message: string
  severity: AlertSeverity
  alert_type: AlertType
  status: AlertStatus
  created_at: string
  updated_at: string
  acknowledged_by?: string
  acknowledged_at?: string
  resolved_at?: string
  resolution_notes?: string
  sensor_ids: string[]
  prediction_id?: string
}

export interface AlertCreate {
  site_id: string
  title: string
  message: string
  severity: AlertSeverity
  alert_type: AlertType
  sensor_ids?: string[]
  prediction_id?: string
}

export interface AlertUpdate {
  status?: AlertStatus
  acknowledged_by?: string
  resolution_notes?: string
}

export interface NotificationChannel {
  type: string
  enabled: boolean
  config: Record<string, any>
}

export interface NotificationPreferences {
  user_id: string
  channels: NotificationChannel[]
  severity_filter: AlertSeverity[]
  site_filters: string[]
}

export const alertsService = {
  async getAlerts(
    siteId?: string,
    severity?: AlertSeverity,
    status?: AlertStatus,
    alertType?: AlertType,
    hours: number = 24
  ): Promise<Alert[]> {
    const params = new URLSearchParams()
    if (siteId) params.append('site_id', siteId)
    if (severity) params.append('severity', severity)
    if (status) params.append('status', status)
    if (alertType) params.append('alert_type', alertType)
    params.append('hours', hours.toString())
    
    const response = await api.get(`/api/alerts?${params.toString()}`)
    return response.data
  },

  async getAlert(id: string): Promise<Alert> {
    const response = await api.get(`/api/alerts/${id}`)
    return response.data
  },

  async createAlert(data: AlertCreate): Promise<Alert> {
    const response = await api.post('/api/alerts', data)
    return response.data
  },

  async updateAlert(id: string, data: AlertUpdate): Promise<Alert> {
    const response = await api.put(`/api/alerts/${id}`, data)
    return response.data
  },

  async deleteAlert(id: string): Promise<void> {
    await api.delete(`/api/alerts/${id}`)
  },

  async getAlertsSummary(siteId?: string, days: number = 7) {
    const params = new URLSearchParams()
    if (siteId) params.append('site_id', siteId)
    params.append('days', days.toString())
    
    const response = await api.get(`/api/alerts/analytics/summary?${params.toString()}`)
    return response.data
  },

  async setNotificationPreferences(preferences: NotificationPreferences): Promise<NotificationPreferences> {
    const response = await api.post('/api/alerts/notifications/preferences', preferences)
    return response.data
  },

  async getNotificationPreferences(): Promise<NotificationPreferences> {
    const response = await api.get('/api/alerts/notifications/preferences')
    return response.data
  },

  async testNotification(severity: AlertSeverity) {
    const response = await api.post('/api/alerts/test-notification', { severity })
    return response.data
  },

  async bulkAcknowledgeAlerts(alertIds: string[]) {
    const response = await api.post('/api/alerts/bulk-acknowledge', { alert_ids: alertIds })
    return response.data
  }
}

export default alertsService