import api from './api'

// Training configuration interfaces matching backend models
export interface TrainingConfig {
  // Temporal features configuration
  temporal_features: {
    displacement: boolean
    velocity: boolean
    acceleration: boolean
    tilt: boolean
    strain: boolean
    pore_pressure: boolean
    rainfall: boolean
    temperature: boolean
    humidity: boolean
    wind_speed: boolean
    seismic_activity: boolean
    ground_temperature: boolean
  }

  // Spatial features configuration
  spatial_features: {
    drone_imagery: boolean
    lidar_scans: boolean
    geological_maps: boolean
    slope_analysis: boolean
    rock_mass_rating: boolean
    joint_orientation: boolean
    weathering_data: boolean
    vegetation_analysis: boolean
  }

  // Model architecture selection
  temporal_model: {
    type: 'LSTM' | 'GRU' | 'Transformer'
    layers: number
    hidden_size: number
    dropout: number
    bidirectional: boolean
  }

  spatial_model: {
    type: 'CNN' | 'PointNet' | 'ResNet'
    layers: number
    filters: number
    dropout: number
  }

  fusion_model: {
    type: 'MLP' | 'Attention' | 'Advanced'
    layers: number
    hidden_size: number
    dropout: number
  }

  // Training hyperparameters
  hyperparameters: {
    learning_rate: number
    batch_size: number
    epochs: number
    validation_split: number
    early_stopping_patience: number
    weight_decay: number
  }

  // Advanced options
  advanced_options: {
    ensemble_methods: boolean
    bayesian_uncertainty: boolean
    adversarial_training: boolean
    data_augmentation: boolean
    transfer_learning: boolean
    multi_task_learning: boolean
    automated_feature_selection: boolean
    hyperparameter_optimization: boolean
  }

  // Dataset and validation settings
  dataset: string
  cross_validation_folds: number
  test_split_ratio: number
}

export interface TrainingJob {
  job_id: string
  user_id: string
  config: TrainingConfig
  status: 'queued' | 'preparing' | 'training' | 'completed' | 'failed' | 'cancelled'
  progress: number
  current_epoch: number
  total_epochs: number
  created_at: string
  started_at?: string
  completed_at?: string
  updated_at?: string
  estimated_completion?: string
  logs: string[]
  metrics: TrainingMetrics[]
  error_message?: string
  performance_summary?: any
  model_paths?: any
}

export interface TrainingMetrics {
  epoch: number
  train_loss: number
  val_loss: number
  accuracy: number
  pr_auc: number
  lead_time_mae: number
  confidence_calibration: number
  temporal_loss: number
  spatial_loss: number
  fusion_loss: number
}

export interface TrainingStatusResponse {
  job_id: string
  status: string
  progress: number
  current_epoch: number
  total_epochs: number
  estimated_time_remaining?: number
  latest_metrics?: TrainingMetrics
  logs: string[]
  error_message?: string
}

export interface ModelPerformanceReport {
  job_id: string
  training_summary: {
    duration_minutes: number
    total_epochs: number
    final_metrics: any
    dataset_used: string
  }
  model_architecture: {
    temporal_model: any
    spatial_model: any
    fusion_model: any
    advanced_options: any
  }
  performance_metrics: any
  feature_importance: Record<string, number>
  validation_results: {
    cross_validation_score: number
    holdout_test_accuracy: number
    confidence_intervals: {
      accuracy: [number, number]
      precision: [number, number]
      recall: [number, number]
    }
  }
  recommendations: string[]
}

export interface ModelDeployment {
  deployment_id: string
  job_id: string
  name: string
  description: string
  deployed_at: string
  deployed_by: string
  status: string
  is_current: boolean
  performance_summary: any
}

// Training API service
export const trainingService = {
  // Start a new training job
  async startTraining(config: TrainingConfig): Promise<{ job_id: string; message: string; status: string }> {
    const response = await api.post('/training/train', config)
    return response.data
  },

  // Get training job status
  async getTrainingStatus(jobId: string): Promise<TrainingStatusResponse> {
    const response = await api.get(`/training/status/${jobId}`)
    return response.data
  },

  // Cancel a training job
  async cancelTraining(jobId: string): Promise<{ message: string }> {
    const response = await api.post(`/training/cancel/${jobId}`)
    return response.data
  },

  // Get user's training jobs
  async getUserTrainingJobs(limit: number = 50, skip: number = 0): Promise<TrainingJob[]> {
    const response = await api.get(`/training/jobs?limit=${limit}&skip=${skip}`)
    return response.data
  },

  // Get performance report for completed job
  async getPerformanceReport(jobId: string): Promise<ModelPerformanceReport> {
    const response = await api.get(`/training/report/${jobId}`)
    return response.data
  },

  // Deploy a trained model
  async deployModel(jobId: string, deploymentName: string, description: string, replaceCurrent: boolean = false): Promise<{ message: string; deployment_id: string; deployment_name: string }> {
    const response = await api.post(`/training/deploy/${jobId}`, {
      deployment_name: deploymentName,
      description: description,
      replace_current: replaceCurrent
    })
    return response.data
  },

  // Get model deployments
  async getDeployments(): Promise<ModelDeployment[]> {
    const response = await api.get('/training/deployments')
    return response.data
  },

  // Real-time status polling utility
  pollTrainingStatus(
    jobId: string, 
    onUpdate: (status: TrainingStatusResponse) => void,
    onComplete: (status: TrainingStatusResponse) => void,
    onError: (error: any) => void,
    intervalMs: number = 2000
  ): () => void {
    let isPolling = true
    
    const poll = async () => {
      try {
        if (!isPolling) return
        
        const status = await this.getTrainingStatus(jobId)
        onUpdate(status)
        
        if (status.status === 'completed' || status.status === 'failed' || status.status === 'cancelled') {
          isPolling = false
          onComplete(status)
          return
        }
        
        if (isPolling) {
          setTimeout(poll, intervalMs)
        }
      } catch (error) {
        isPolling = false
        onError(error)
      }
    }
    
    poll()
    
    // Return cleanup function
    return () => {
      isPolling = false
    }
  }
}

export default trainingService