import { api } from './api'

export interface Prediction {
  id: string
  site_id: string
  zone_id?: string
  timestamp: string
  risk_level: string
  probability: number
  confidence: number
  prediction_model_version: string
  contributing_factors: ContributingFactor[]
  recommendations: string[]
}

export interface ContributingFactor {
  factor: string
  weight: number
  description: string
}

export interface MLAnalysisRequest {
  site_id: string
  zone_id?: string
  include_recommendations: boolean
  analysis_depth: 'basic' | 'detailed' | 'comprehensive'
}

export interface MLAnalysisResult {
  prediction: Prediction
  analysis_metadata: {
    processing_time_ms: number
    data_points_analyzed: number
    model_version: string
  }
}

export interface PredictionFilter {
  site_id?: string
  risk_level?: string
  start_date?: string
  end_date?: string
  min_confidence?: number
  limit?: number
}

export const predictionsAPI = {
  async getPredictions(filters?: PredictionFilter): Promise<Prediction[]> {
    const params = new URLSearchParams()
    if (filters?.site_id) params.append('site_id', filters.site_id)
    if (filters?.risk_level) params.append('risk_level', filters.risk_level)
    if (filters?.start_date) params.append('start_date', filters.start_date)
    if (filters?.end_date) params.append('end_date', filters.end_date)
    if (filters?.min_confidence) params.append('min_confidence', filters.min_confidence.toString())
    if (filters?.limit) params.append('limit', filters.limit.toString())
    
    const response = await api.get(`/predictions?${params.toString()}`)
    return response.data
  },

  async getPrediction(predictionId: string): Promise<Prediction> {
    const response = await api.get(`/predictions/${predictionId}`)
    return response.data
  },

  async runMLAnalysis(request: MLAnalysisRequest): Promise<MLAnalysisResult> {
    const response = await api.post('/predictions/analyze', request)
    return response.data
  },

  async getSitePredictions(siteId: string): Promise<Prediction[]> {
    const response = await api.get(`/predictions/site/${siteId}`)
    return response.data
  }
}