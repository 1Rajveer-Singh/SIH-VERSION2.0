import React, { useState, useRef, useEffect } from 'react'
import { useAuth } from '../contexts/AuthContext'
import trainingService, { TrainingConfig as BackendTrainingConfig, TrainingStatusResponse } from '../services/training'

interface TrainingConfig {
  temporalModel: {
    type: 'LSTM' | 'GRU' | 'Temporal_Transformer'
    enabled: boolean
  }
  spatialModel: {
    type: 'CNN' | 'PointNet' | 'PointNet_Plus'
    enabled: boolean
  }
  fusionModel: {
    type: 'MLP' | 'Fusion_Network'
    enabled: boolean
  }
  advancedOptions: {
    ensembleMethods: boolean
    bayesianUncertainty: boolean
    gradientBoosting: boolean
  }
  outputTypes: {
    riskProbability: boolean
    leadTime: boolean
    confidenceScore: boolean
    uncertaintyEstimation: boolean
  }
  temporalFeatures: {
    displacement: boolean
    velocity: boolean
    porePressure: boolean
    rainfall: boolean
    blastVibrations: boolean
    seismicActivity: boolean
    groundwaterLevel: boolean
    soilMoisture: boolean
    crackPropagation: boolean
    stressFactors: boolean
  }
  spatialFeatures: {
    droneImagery: boolean
    crackDetection: boolean
    demChanges: boolean
    lidarPointClouds: boolean
    surfaceRoughness: boolean
    vegetationCoverage: boolean
  }
  trainingWindow: {
    value: number
    unit: 'hours' | 'days' | 'weeks'
  }
  predictionHorizon: {
    shortTerm: number
    longTerm: number
  }
  hyperparameters: {
    learningRate: number
    batchSize: number
    epochs: number
    dropoutRate: number
    sequenceLength: number
    hiddenDimensions: number
    attentionHeads: number
  }
  dataset: string
}

interface TrainingMetrics {
  epoch: number
  trainLoss: number
  valLoss: number
  accuracy: number
  prAuc: number
  leadTimeMae: number
  confidenceCalibration: number
}

interface TrainingStatus {
  isRunning: boolean
  currentEpoch: number
  totalEpochs: number
  status: 'idle' | 'preparing' | 'training' | 'completed' | 'failed' | 'cancelled'
  progress: number
  estimatedTimeRemaining: number
  logs: string[]
  metrics: TrainingMetrics[]
  error?: string
}

function ModelTrainingPage() {
  const { state } = useAuth()
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [trainingPassword, setTrainingPassword] = useState('')
  const [passwordError, setPasswordError] = useState('')
  const [sessionTimeout, setSessionTimeout] = useState<number | null>(null)
  const [currentJobId, setCurrentJobId] = useState<string | null>(null)
  const [pollingCleanup, setPollingCleanup] = useState<(() => void) | null>(null)
  
  // File import state
  const [importStatus, setImportStatus] = useState<string>('')
  const [importedData, setImportedData] = useState<any>(null)

  const [trainingConfig, setTrainingConfig] = useState<TrainingConfig>({
    temporalModel: {
      type: 'LSTM',
      enabled: true
    },
    spatialModel: {
      type: 'CNN',
      enabled: true
    },
    fusionModel: {
      type: 'MLP',
      enabled: true
    },
    advancedOptions: {
      ensembleMethods: false,
      bayesianUncertainty: true,
      gradientBoosting: false
    },
    outputTypes: {
      riskProbability: true,
      leadTime: true,
      confidenceScore: true,
      uncertaintyEstimation: false
    },
    temporalFeatures: {
      displacement: true,
      velocity: true,
      porePressure: true,
      rainfall: true,
      blastVibrations: false,
      seismicActivity: true,
      groundwaterLevel: false,
      soilMoisture: false,
      crackPropagation: true,
      stressFactors: false
    },
    spatialFeatures: {
      droneImagery: true,
      crackDetection: true,
      demChanges: true,
      lidarPointClouds: false,
      surfaceRoughness: false,
      vegetationCoverage: false
    },
    trainingWindow: {
      value: 7,
      unit: 'days'
    },
    predictionHorizon: {
      shortTerm: 24,
      longTerm: 48
    },
    hyperparameters: {
      learningRate: 0.001,
      batchSize: 32,
      epochs: 100,
      dropoutRate: 0.2,
      sequenceLength: 96,
      hiddenDimensions: 128,
      attentionHeads: 8
    },
    dataset: 'historical'
  })
  
  const [trainingStatus, setTrainingStatus] = useState<TrainingStatus>({
    isRunning: false,
    currentEpoch: 0,
    totalEpochs: 0,
    status: 'idle',
    progress: 0,
    estimatedTimeRemaining: 0,
    logs: [],
    metrics: []
  })

  // Authentication handlers
  const handlePasswordSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (trainingPassword === 'admintime') {
      setIsAuthenticated(true)
      setPasswordError('')
      setTrainingPassword('')
      
      // Set session timeout for 30 minutes
      const timeout = setTimeout(() => {
        handleLogout()
      }, 30 * 60 * 1000)
      setSessionTimeout(timeout)
    } else {
      setPasswordError('Invalid password. Access denied.')
      setTrainingPassword('')
    }
  }

  const handleLogout = () => {
    setIsAuthenticated(false)
    setTrainingPassword('')
    setPasswordError('')
    if (sessionTimeout) clearTimeout(sessionTimeout)
    setSessionTimeout(null)
  }

  // File import handler
  const handleFileImport = async (event: React.ChangeEvent<HTMLInputElement>, fileType: 'csv' | 'json') => {
    const file = event.target.files?.[0]
    if (!file) return

    try {
      setImportStatus('Reading file...')
      const text = await file.text()
      
      if (fileType === 'csv') {
        // Basic CSV parsing - you might want to use a proper CSV parser library
        const lines = text.split('\n')
        const headers = lines[0].split(',')
        const data = lines.slice(1).map(line => {
          const values = line.split(',')
          const row: any = {}
          headers.forEach((header, index) => {
            row[header.trim()] = values[index]?.trim()
          })
          return row
        })
        setImportedData({ type: 'csv', data, headers })
        setImportStatus(`✓ CSV file imported: ${data.length} rows, ${headers.length} columns`)
      } else if (fileType === 'json') {
        const data = JSON.parse(text)
        setImportedData({ type: 'json', data })
        setImportStatus(`✓ JSON file imported: ${JSON.stringify(data).length} bytes`)
      }
    } catch (error: any) {
      setImportStatus(`❌ Error: ${error.message}`)
    }
  }

  // Convert frontend training config to backend format
  const convertToBackendConfig = (frontendConfig: TrainingConfig): BackendTrainingConfig => {
    return {
      temporal_features: {
        displacement: frontendConfig.temporalFeatures.displacement,
        velocity: frontendConfig.temporalFeatures.velocity,
        acceleration: true, // Default enabled
        tilt: true, // Default enabled
        strain: true, // Default enabled
        pore_pressure: frontendConfig.temporalFeatures.porePressure,
        rainfall: frontendConfig.temporalFeatures.rainfall,
        temperature: true, // Default enabled
        humidity: true, // Default enabled
        wind_speed: true, // Default enabled
        seismic_activity: frontendConfig.temporalFeatures.seismicActivity,
        ground_temperature: frontendConfig.temporalFeatures.groundwaterLevel
      },
      spatial_features: {
        drone_imagery: frontendConfig.spatialFeatures.droneImagery,
        lidar_scans: frontendConfig.spatialFeatures.lidarPointClouds,
        geological_maps: true, // Default enabled
        slope_analysis: true, // Default enabled
        rock_mass_rating: true, // Default enabled
        joint_orientation: true, // Default enabled
        weathering_data: frontendConfig.spatialFeatures.surfaceRoughness,
        vegetation_analysis: frontendConfig.spatialFeatures.vegetationCoverage
      },
      temporal_model: {
        type: frontendConfig.temporalModel.type === 'Temporal_Transformer' ? 'Transformer' : frontendConfig.temporalModel.type,
        layers: 3,
        hidden_size: frontendConfig.hyperparameters.hiddenDimensions,
        dropout: frontendConfig.hyperparameters.dropoutRate,
        bidirectional: true
      },
      spatial_model: {
        type: frontendConfig.spatialModel.type === 'PointNet_Plus' ? 'ResNet' : frontendConfig.spatialModel.type,
        layers: 4,
        filters: 64,
        dropout: frontendConfig.hyperparameters.dropoutRate
      },
      fusion_model: {
        type: frontendConfig.fusionModel.type === 'Fusion_Network' ? 'Advanced' : frontendConfig.fusionModel.type,
        layers: 2,
        hidden_size: frontendConfig.hyperparameters.hiddenDimensions,
        dropout: frontendConfig.hyperparameters.dropoutRate
      },
      hyperparameters: {
        learning_rate: frontendConfig.hyperparameters.learningRate,
        batch_size: frontendConfig.hyperparameters.batchSize,
        epochs: frontendConfig.hyperparameters.epochs,
        validation_split: 0.2,
        early_stopping_patience: 10,
        weight_decay: 0.0001
      },
      advanced_options: {
        ensemble_methods: frontendConfig.advancedOptions.ensembleMethods,
        bayesian_uncertainty: frontendConfig.advancedOptions.bayesianUncertainty,
        adversarial_training: false,
        data_augmentation: true,
        transfer_learning: false,
        multi_task_learning: false,
        automated_feature_selection: false,
        hyperparameter_optimization: false
      },
      dataset: frontendConfig.dataset,
      cross_validation_folds: 5,
      test_split_ratio: 0.15
    }
  }

  const startTraining = async () => {
    if (!isAuthenticated) return
    
    try {
      setTrainingStatus(prev => ({
        ...prev,
        isRunning: true,
        status: 'preparing',
        currentEpoch: 0,
        totalEpochs: trainingConfig.hyperparameters.epochs,
        progress: 0,
        logs: ['Connecting to training API...', 'Validating configuration...', 'Initializing training pipeline...']
      }))

      // Convert config and start training
      const backendConfig = convertToBackendConfig(trainingConfig)
      const response = await trainingService.startTraining(backendConfig)
      
      const jobId = response.job_id
      setCurrentJobId(jobId)
      
      setTrainingStatus(prev => ({
        ...prev,
        logs: [...prev.logs, `Training job created: ${jobId}`, 'Starting model training...']
      }))

      // Start polling for updates
      const cleanup = trainingService.pollTrainingStatus(
        jobId,
        (status: TrainingStatusResponse) => {
          setTrainingStatus(prev => ({
            ...prev,
            status: status.status as any,
            progress: status.progress,
            currentEpoch: status.current_epoch,
            totalEpochs: status.total_epochs,
            estimatedTimeRemaining: status.estimated_time_remaining || 0,
            logs: status.logs,
            metrics: status.latest_metrics ? [...prev.metrics, {
              epoch: status.latest_metrics.epoch,
              trainLoss: status.latest_metrics.train_loss,
              valLoss: status.latest_metrics.val_loss,
              accuracy: status.latest_metrics.accuracy,
              prAuc: status.latest_metrics.pr_auc,
              leadTimeMae: status.latest_metrics.lead_time_mae,
              confidenceCalibration: status.latest_metrics.confidence_calibration
            }] : prev.metrics
          }))
        },
        (finalStatus: TrainingStatusResponse) => {
          setTrainingStatus(prev => ({
            ...prev,
            isRunning: false,
            status: finalStatus.status as any,
            progress: finalStatus.progress,
            logs: finalStatus.logs
          }))
          setPollingCleanup(null)
        },
        (error: any) => {
          setTrainingStatus(prev => ({
            ...prev,
            isRunning: false,
            status: 'failed',
            error: error.message || 'Training failed',
            logs: [...prev.logs, `Error: ${error.message || 'Unknown error'}`]
          }))
          setPollingCleanup(null)
        }
      )
      
      setPollingCleanup(() => cleanup)

    } catch (error: any) {
      setTrainingStatus(prev => ({
        ...prev,
        isRunning: false,
        status: 'failed',
        error: error.message || 'Failed to start training',
        logs: [...prev.logs, `Error: ${error.message || 'Failed to start training'}`]
      }))
    }
  }

  const cancelTraining = async () => {
    if (currentJobId && pollingCleanup) {
      try {
        await trainingService.cancelTraining(currentJobId)
        pollingCleanup()
        setPollingCleanup(null)
        setCurrentJobId(null)
        
        setTrainingStatus(prev => ({
          ...prev,
          isRunning: false,
          status: 'cancelled',
          logs: [...prev.logs, 'Training cancelled by user.']
        }))
      } catch (error: any) {
        console.error('Failed to cancel training:', error)
        setTrainingStatus(prev => ({
          ...prev,
          logs: [...prev.logs, `Warning: ${error.message || 'Failed to cancel training'}`]
        }))
      }
    }
  }

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (pollingCleanup) {
        pollingCleanup()
      }
      if (sessionTimeout) {
        clearTimeout(sessionTimeout)
      }
    }
  }, [pollingCleanup, sessionTimeout])

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center p-4">
        {/* Small Password Popup Modal */}
        <div className="bg-white border border-gray-300 rounded-xl shadow-lg p-6 w-full max-w-sm">
          <div className="text-center mb-4">
            <div className="mx-auto w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mb-3">
              <span className="text-xl">🔒</span>
            </div>
            <h2 className="text-lg font-semibold text-gray-900 mb-1">Access Required</h2>
            <p className="text-sm text-gray-600">Enter password to access training</p>
          </div>
          
          <form onSubmit={handlePasswordSubmit} className="space-y-4">
            <div>
              <input
                type="password"
                value={trainingPassword}
                onChange={(e) => setTrainingPassword(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900 text-sm"
                placeholder="Enter password"
                required
              />
              {passwordError && (
                <p className="mt-1 text-red-600 text-xs">{passwordError}</p>
              )}
            </div>
            
            <button
              type="submit"
              className="w-full bg-blue-600 text-white py-2 rounded-lg text-sm font-medium hover:bg-blue-700 transition-colors"
            >
              Access Training
            </button>
          </form>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-white">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-4 py-3">
        <div className="max-w-6xl mx-auto flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center">
              <span className="text-lg">🤖</span>
            </div>
            <div>
              <h1 className="text-lg font-semibold text-gray-900">AI Model Training</h1>
              <p className="text-xs text-gray-600">Professional training interface</p>
            </div>
          </div>
          <button
            onClick={handleLogout}
            className="bg-red-50 border border-red-200 text-red-700 px-3 py-1 rounded-md text-xs hover:bg-red-100 transition-colors"
          >
            Logout
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-6xl mx-auto p-4 space-y-4">
        
        {/* Data Import Section */}
        <div className="bg-white border border-gray-200 rounded-lg p-4">
          <h2 className="text-sm font-semibold text-gray-900 mb-3 flex items-center">
            📂 Data Import
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {/* CSV Import */}
            <div className="border border-gray-200 rounded-lg p-3">
              <h3 className="text-sm font-medium text-gray-900 mb-2">CSV Data</h3>
              <input
                type="file"
                accept=".csv"
                onChange={(e) => handleFileImport(e, 'csv')}
                className="block w-full text-xs text-gray-500
                  file:mr-3 file:py-1 file:px-3
                  file:rounded-md file:border-0
                  file:text-xs file:font-medium
                  file:bg-blue-50 file:text-blue-700
                  hover:file:bg-blue-100"
              />
              <p className="text-xs text-gray-500 mt-1">Upload CSV training data</p>
            </div>
            
            {/* JSON Import */}
            <div className="border border-gray-200 rounded-lg p-3">
              <h3 className="text-sm font-medium text-gray-900 mb-2">JSON Data</h3>
              <input
                type="file"
                accept=".json"
                onChange={(e) => handleFileImport(e, 'json')}
                className="block w-full text-xs text-gray-500
                  file:mr-3 file:py-1 file:px-3
                  file:rounded-md file:border-0
                  file:text-xs file:font-medium
                  file:bg-green-50 file:text-green-700
                  hover:file:bg-green-100"
              />
              <p className="text-xs text-gray-500 mt-1">Upload JSON training data</p>
            </div>
          </div>

          {/* Import Status */}
          {importStatus && (
            <div className={`mt-3 p-2 rounded-md text-xs ${
              importStatus.includes('Error') || importStatus.includes('❌') ? 'bg-red-50 text-red-700' : 'bg-green-50 text-green-700'
            }`}>
              {importStatus}
            </div>
          )}
        </div>

        {/* Model Architecture */}
        <div className="bg-white border border-gray-200 rounded-lg p-4">
          <h2 className="text-sm font-semibold text-gray-900 mb-3 flex items-center">
            🏗️ Model Architecture
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            {/* Temporal Model */}
            <div className="border border-gray-200 rounded-lg p-3">
              <h3 className="text-sm font-medium text-gray-900 mb-2">Temporal Model</h3>
              <select
                value={trainingConfig.temporalModel.type}
                onChange={(e) => setTrainingConfig(prev => ({
                  ...prev,
                  temporalModel: { ...prev.temporalModel, type: e.target.value as any }
                }))}
                className="w-full px-2 py-1 text-xs border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500 text-gray-900"
              >
                <option value="LSTM">LSTM</option>
                <option value="GRU">GRU</option>
                <option value="Temporal_Transformer">Transformer</option>
              </select>
            </div>

            {/* Spatial Model */}
            <div className="border border-gray-200 rounded-lg p-3">
              <h3 className="text-sm font-medium text-gray-900 mb-2">Spatial Model</h3>
              <select
                value={trainingConfig.spatialModel.type}
                onChange={(e) => setTrainingConfig(prev => ({
                  ...prev,
                  spatialModel: { ...prev.spatialModel, type: e.target.value as any }
                }))}
                className="w-full px-2 py-1 text-xs border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500 text-gray-900"
              >
                <option value="CNN">CNN</option>
                <option value="PointNet">PointNet</option>
                <option value="PointNet_Plus">PointNet++</option>
              </select>
            </div>

            {/* Fusion Model */}
            <div className="border border-gray-200 rounded-lg p-3">
              <h3 className="text-sm font-medium text-gray-900 mb-2">Fusion Model</h3>
              <select
                value={trainingConfig.fusionModel.type}
                onChange={(e) => setTrainingConfig(prev => ({
                  ...prev,
                  fusionModel: { ...prev.fusionModel, type: e.target.value as any }
                }))}
                className="w-full px-2 py-1 text-xs border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500 text-gray-900"
              >
                <option value="MLP">MLP</option>
                <option value="Fusion_Network">Advanced Fusion</option>
              </select>
            </div>
          </div>
        </div>

        {/* Training Controls */}
        <div className="bg-white border border-gray-200 rounded-lg p-4">
          <h2 className="text-sm font-semibold text-gray-900 mb-3 flex items-center">
            ⚡ Training Controls
          </h2>
          
          <div className="flex items-center space-x-3">
            {!trainingStatus.isRunning ? (
              <button
                onClick={startTraining}
                className="bg-green-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-green-700 transition-colors"
              >
                🚀 Start Training
              </button>
            ) : (
              <button
                onClick={cancelTraining}
                className="bg-red-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-red-700 transition-colors"
              >
                ⏹️ Cancel Training
              </button>
            )}
            
            <div className="text-gray-900">
              <span className="text-xs text-gray-600">Status: </span>
              <span className="text-sm font-medium capitalize">{trainingStatus.status}</span>
            </div>
          </div>
        </div>

        {/* Training Progress */}
        <div className="bg-white border border-gray-200 rounded-lg p-4">
          <h2 className="text-sm font-semibold text-gray-900 mb-3 flex items-center">
            📊 Training Progress
          </h2>
          
          <div className="space-y-3">
            <div>
              <div className="flex justify-between text-xs text-gray-600 mb-1">
                <span>Progress</span>
                <span>{trainingStatus.progress.toFixed(1)}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${trainingStatus.progress}%` }}
                ></div>
              </div>
            </div>
            
            <div className="text-gray-900 text-xs">
              <p>Epoch: {trainingStatus.currentEpoch} / {trainingStatus.totalEpochs}</p>
              {trainingStatus.estimatedTimeRemaining > 0 && (
                <p>Time remaining: ~{Math.ceil(trainingStatus.estimatedTimeRemaining / 60)} minutes</p>
              )}
            </div>
          </div>
        </div>

        {/* Training Logs */}
        <div className="bg-white border border-gray-200 rounded-lg p-4">
          <h2 className="text-sm font-semibold text-gray-900 mb-3 flex items-center">
            📝 Training Logs
          </h2>
          
          <div className="bg-gray-50 border border-gray-200 rounded-md p-3 h-48 overflow-y-auto">
            {trainingStatus.logs.length > 0 ? (
              trainingStatus.logs.map((log, index) => (
                <div key={index} className="text-gray-700 text-xs font-mono mb-1">
                  {log}
                </div>
              ))
            ) : (
              <div className="text-gray-500 text-xs">No training logs yet...</div>
            )}
          </div>
        </div>

      </div>
    </div>
  )
}

export default ModelTrainingPage