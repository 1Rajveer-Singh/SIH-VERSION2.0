import api from './api'

export interface SensorLocation {
  lat: number
  lng: number
  elevation: number
}

export interface Sensor {
  id: string
  site_id: string
  name: string
  location: SensorLocation
  sensor_types: string[]
  status: string
  last_reading: string | null
  installation_date: string
}

export interface SensorCreate {
  site_id: string
  name: string
  location: SensorLocation
  sensor_types: string[]
}

export interface SensorUpdate {
  name?: string
  location?: SensorLocation
  status?: string
}

export interface SensorReading {
  timestamp: string
  sensor_id: string
  readings: Record<string, number>
}

export const sensorsService = {
  async getSensors(siteId?: string, status?: string): Promise<Sensor[]> {
    const params = new URLSearchParams()
    if (siteId) params.append('site_id', siteId)
    if (status) params.append('status', status)
    
    const response = await api.get(`/sensors?${params.toString()}`)
    return response.data
  },

  async getSensor(id: string): Promise<Sensor> {
    const response = await api.get(`/sensors/${id}`)
    return response.data
  },

  async createSensor(data: SensorCreate): Promise<Sensor> {
    const response = await api.post('/sensors', data)
    return response.data
  },

  async updateSensor(id: string, data: SensorUpdate): Promise<Sensor> {
    const response = await api.put(`/sensors/${id}`, data)
    return response.data
  },

  async deleteSensor(id: string): Promise<void> {
    await api.delete(`/sensors/${id}`)
  },

  async getSensorReadings(id: string, hours: number = 24) {
    const response = await api.get(`/sensors/${id}/readings?hours=${hours}`)
    return response.data
  },

  async getSensorStatus(id: string) {
    const response = await api.get(`/sensors/${id}/status`)
    return response.data
  }
}

export default sensorsService