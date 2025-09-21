import api from './api'

export interface Site {
  id: string
  name: string
  location: {
    lat: number
    lng: number
    elevation: number
  }
  area_hectares: number
  description: string
  safety_protocols: string[]
  emergency_contacts: Array<{
    name: string
    role: string
    phone: string
    email: string
  }>
  status: string
  created_at: string
  updated_at: string
}

export interface SiteCreate {
  name: string
  location: {
    lat: number
    lng: number
    elevation: number
  }
  area_hectares: number
  description: string
  safety_protocols: string[]
  emergency_contacts: Array<{
    name: string
    role: string
    phone: string
    email: string
  }>
}

export interface SiteUpdate {
  name?: string
  location?: {
    lat: number
    lng: number
    elevation: number
  }
  area_hectares?: number
  description?: string
  safety_protocols?: string[]
  emergency_contacts?: Array<{
    name: string
    role: string
    phone: string
    email: string
  }>
  status?: string
}

export const sitesService = {
  async getSites(): Promise<Site[]> {
    const response = await api.get('/sites')
    return response.data
  },

  async getSite(id: string): Promise<Site> {
    const response = await api.get(`/sites/${id}`)
    return response.data
  },

  async createSite(data: SiteCreate): Promise<Site> {
    const response = await api.post('/sites', data)
    return response.data
  },

  async updateSite(id: string, data: SiteUpdate): Promise<Site> {
    const response = await api.put(`/sites/${id}`, data)
    return response.data
  },

  async deleteSite(id: string): Promise<void> {
    await api.delete(`/sites/${id}`)
  },

  async getSiteStatistics(id: string) {
    const response = await api.get(`/sites/${id}/statistics`)
    return response.data
  }
}

export default sitesService