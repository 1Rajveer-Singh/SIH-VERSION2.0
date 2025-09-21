import api from './api'

export interface RiskLevel {
  level: string
  probability: number
  confidence: number
}

export interface PredictionRequest {
  site_id: string
  sensor_ids: string[]
  prediction_type: string
  time_horizon: number
}

export interface Prediction {
  id: string
  site_id: string
  sensor_ids: string[]
  prediction_type: string
  timestamp: string
  risk_level: RiskLevel
  factors: Record<string, number>
  recommendations: string[]
  validity_period: number
}

export interface ModelPerformance {
  accuracy: number
  precision: number
  recall: number
  f1_score: number
  last_trained: string
}

export const predictionsService = {
  async createPrediction(data: PredictionRequest): Promise<Prediction> {
    const response = await api.post('/predictions', data)
    return response.data
  },

  async getPredictions(
    siteId?: string,
    riskLevel?: string,
    hours: number = 24
  ): Promise<Prediction[]> {
    const params = new URLSearchParams()
    if (siteId) params.append('site_id', siteId)
    if (riskLevel) params.append('risk_level', riskLevel)
    params.append('hours', hours.toString())
    
    const response = await api.get(`/predictions?${params.toString()}`)
    return response.data
  },

  async getPrediction(id: string): Promise<Prediction> {
    const response = await api.get(`/predictions/${id}`)
    return response.data
  },

  async createBatchPredictions(requests: PredictionRequest[]) {
    const response = await api.post('/predictions/batch', requests)
    return response.data
  },

  async getModelPerformance(modelType?: string) {
    const params = modelType ? `?model_type=${modelType}` : ''
    const response = await api.get(`/predictions/model/performance${params}`)
    return response.data
  },

  async getPredictionTrends(siteId?: string, days: number = 7) {
    const params = new URLSearchParams()
    if (siteId) params.append('site_id', siteId)
    params.append('days', days.toString())
    
    const response = await api.get(`/predictions/analytics/trends?${params.toString()}`)
    return response.data
  },

  async triggerModelRetraining(modelType: string) {
    const response = await api.post(`/predictions/retrain?model_type=${modelType}`)
    return response.data
  }
}

export default predictionsService