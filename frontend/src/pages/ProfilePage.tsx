import React, { useState, useRef, useEffect } from 'react'
import { useAuth } from '../contexts/AuthContext'
import trainingService, { TrainingConfig as BackendTrainingConfig, TrainingStatusResponse } from '../services/training'

interface UserProfile {
  id: string
  full_name: string
  username: string
  email: string
  role: string
  phone?: string
  department?: string
  location?: string
  bio?: string
  avatar?: string
  status: 'active' | 'away' | 'busy' | 'offline'
  joined_date: Date
  last_login: Date
}

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
    unit: 'hours' | 'days'
  }
  predictionHorizon: {
    shortTerm: number // hours
    longTerm: number // hours
  }
  hyperparameters: {
    learningRate: number
    batchSize: number
    epochs: number
    dropoutRate: number
    sequenceLength: number // for temporal models
    hiddenDimensions: number
    attentionHeads: number // for transformer
  }
  dataset: 'historical' | 'synthetic' | 'augmented' | 'combined'
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

function ProfilePage() {
  const { state } = useAuth()
  const [isEditing, setIsEditing] = useState(false)
  const [activeTab, setActiveTab] = useState('overview')
  const fileInputRef = useRef<HTMLInputElement>(null)
  
  // Model Training Modal States
  const [showTrainingModal, setShowTrainingModal] = useState(false)
  const [trainingPassword, setTrainingPassword] = useState('')
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [passwordError, setPasswordError] = useState('')
  const [sessionTimeout, setSessionTimeout] = useState<number | null>(null)
  
  // Training Configuration States
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
      bayesianUncertainty: false,
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
      groundwaterLevel: false
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
  
  // Track current training job
  const [currentJobId, setCurrentJobId] = useState<string | null>(null)
  const [pollingCleanup, setPollingCleanup] = useState<(() => void) | null>(null)
  
  // Mock user profile data
  const [userProfile, setUserProfile] = useState<UserProfile>({
    id: state.user?.id || '1',
    full_name: state.user?.full_name || 'Dr. Sarah Chen',
    username: state.user?.username || 'sarah.chen',
    email: state.user?.email || 'sarah.chen@rockfall.com',
    role: state.user?.role || 'admin',
    phone: '+1 (555) 123-4567',
    department: 'Geological Engineering',
    location: 'Vancouver, BC, Canada',
    bio: 'Senior Geological Engineer with 15+ years of experience in rockfall prediction and mining safety systems. Specialized in AI-driven risk assessment and predictive modeling.',
    avatar: undefined,
    status: 'active',
    joined_date: new Date('2020-03-15'),
    last_login: new Date()
  })

  const [editForm, setEditForm] = useState({
    full_name: userProfile.full_name,
    phone: userProfile.phone || '',
    department: userProfile.department || '',
    location: userProfile.location || '',
    bio: userProfile.bio || '',
    status: userProfile.status
  })

  const getRoleDisplayName = (role: string) => {
    const roleMap: { [key: string]: string } = {
      'admin': 'System Administrator',
      'geologist': 'Geologist',
      'engineer': 'Engineer',
      'operator': 'Site Operator',
      'viewer': 'Viewer'
    }
    return roleMap[role] || role
  }

  const getStatusColor = (status: string) => {
    const statusColors: { [key: string]: string } = {
      'active': 'bg-green-500',
      'away': 'bg-yellow-500',
      'busy': 'bg-red-500',
      'offline': 'bg-gray-500'
    }
    return statusColors[status] || 'bg-gray-500'
  }

  const handleSaveProfile = () => {
    setUserProfile(prev => ({
      ...prev,
      full_name: editForm.full_name,
      phone: editForm.phone,
      department: editForm.department,
      location: editForm.location,
      bio: editForm.bio,
      status: editForm.status
    }))
    setIsEditing(false)
  }

  const handleAvatarClick = () => {
    fileInputRef.current?.click()
  }

  const handleAvatarChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      const reader = new FileReader()
      reader.onload = (e) => {
        setUserProfile(prev => ({
          ...prev,
          avatar: e.target?.result as string
        }))
      }
      reader.readAsDataURL(file)
    }
  }

  // Training Modal Functions
  const handleTrainingAccess = () => {
    const correctPassword = "admintime"
    if (trainingPassword === correctPassword) {
      setIsAuthenticated(true)
      setPasswordError('')
      setTrainingPassword('')
      
      // Set session timeout for 30 minutes
      if (sessionTimeout) clearTimeout(sessionTimeout)
      const timeout = setTimeout(() => {
        setIsAuthenticated(false)
        setShowTrainingModal(false)
      }, 30 * 60 * 1000) // 30 minutes
      setSessionTimeout(timeout)
    } else {
      setPasswordError('Incorrect password. Access denied.')
      setTrainingPassword('')
    }
  }

  const closeTrainingModal = () => {
    setShowTrainingModal(false)
    setIsAuthenticated(false)
    setTrainingPassword('')
    setPasswordError('')
    if (sessionTimeout) clearTimeout(sessionTimeout)
    setSessionTimeout(null)
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
        type: frontendConfig.spatialModel.type === 'PointNet_Plus' ? 'PointNet' : frontendConfig.spatialModel.type,
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
        hyperparameter_optimization: frontendConfig.advancedOptions.gradientBoosting
      },
      dataset: frontendConfig.dataset,
      cross_validation_folds: 5,
      test_split_ratio: 0.15
    }
  }

  const startTraining = async () => {
    if (!isAuthenticated) return
    
    try {
      // Clean up any existing polling
      if (pollingCleanup) {
        pollingCleanup()
        setPollingCleanup(null)
      }
      
      setTrainingStatus(prev => ({
        ...prev,
        isRunning: true,
        status: 'preparing',
        currentEpoch: 0,
        totalEpochs: trainingConfig.hyperparameters.epochs,
        progress: 0,
        logs: ['Submitting training job to backend...']
      }))

      // Convert config and start training
      const backendConfig = convertToBackendConfig(trainingConfig)
      const response = await trainingService.startTraining(backendConfig)
      
      setCurrentJobId(response.job_id)
      
      setTrainingStatus(prev => ({
        ...prev,
        logs: [...prev.logs, `Training job created: ${response.job_id}`, response.message]
      }))

      // Start polling for status updates
      const cleanup = trainingService.pollTrainingStatus(
        response.job_id,
        (status: TrainingStatusResponse) => {
          // Update training status from backend
          setTrainingStatus(prev => ({
            ...prev,
            currentEpoch: status.current_epoch,
            totalEpochs: status.total_epochs,
            progress: status.progress,
            status: status.status as any,
            estimatedTimeRemaining: status.estimated_time_remaining || 0,
            logs: status.logs,
            metrics: status.latest_metrics ? [
              ...prev.metrics.slice(0, -1), // Remove last metric if exists
              {
                epoch: status.latest_metrics.epoch,
                trainLoss: status.latest_metrics.train_loss,
                valLoss: status.latest_metrics.val_loss,
                accuracy: status.latest_metrics.accuracy,
                prAuc: status.latest_metrics.pr_auc,
                leadTimeMae: status.latest_metrics.lead_time_mae,
                confidenceCalibration: status.latest_metrics.confidence_calibration
              }
            ] : prev.metrics
          }))
        },
        (finalStatus: TrainingStatusResponse) => {
          // Training completed
          setTrainingStatus(prev => ({
            ...prev,
            isRunning: false,
            status: finalStatus.status as any,
            progress: 100,
            logs: finalStatus.logs
          }))
          setCurrentJobId(null)
          setPollingCleanup(null)
        },
        (error: any) => {
          // Training failed
          console.error('Training polling error:', error)
          setTrainingStatus(prev => ({
            ...prev,
            isRunning: false,
            status: 'failed',
            error: error.response?.data?.detail || 'Failed to communicate with training service',
            logs: [...prev.logs, `Error: ${error.response?.data?.detail || error.message}`]
          }))
          setCurrentJobId(null)
          setPollingCleanup(null)
        }
      )
      
      setPollingCleanup(() => cleanup)
      
    } catch (error: any) {
      console.error('Failed to start training:', error)
      setTrainingStatus(prev => ({
        ...prev,
        isRunning: false,
        status: 'failed',
        error: error.response?.data?.detail || 'Failed to start training',
        logs: [...prev.logs, `Error: ${error.response?.data?.detail || error.message}`]
      }))
    }
  }

  const cancelTraining = async () => {
    if (!currentJobId) return
    
    try {
      await trainingService.cancelTraining(currentJobId)
      
      // Clean up polling
      if (pollingCleanup) {
        pollingCleanup()
        setPollingCleanup(null)
      }
      
      setTrainingStatus(prev => ({
        ...prev,
        isRunning: false,
        status: 'cancelled',
        logs: [...prev.logs, 'Training cancelled by user.']
      }))
      
      setCurrentJobId(null)
    } catch (error: any) {
      console.error('Failed to cancel training:', error)
      setTrainingStatus(prev => ({
        ...prev,
        logs: [...prev.logs, `Failed to cancel training: ${error.response?.data?.detail || error.message}`]
      }))
    }
  }

  // Cleanup on component unmount
  useEffect(() => {
    return () => {
      if (pollingCleanup) {
        pollingCleanup()
      }
    }
  }, [pollingCleanup])

  // Cleanup session timeout on unmount
  useEffect(() => {
    return () => {
      if (sessionTimeout) clearTimeout(sessionTimeout)
    }
  }, [sessionTimeout])

  return (
    <div className="min-h-screen bg-white relative">
      <div className="absolute inset-0 bg-gradient-to-br from-blue-50/20 via-purple-50/10 to-cyan-50/20"></div>
      <div className="relative z-10">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          {/* Profile Header */}
          <div className="mb-6">
            <div className="backdrop-blur-lg bg-white/40 border border-white/50 rounded-3xl shadow-xl overflow-hidden mb-6">
              <div className="bg-gradient-to-r from-blue-600 via-purple-600 to-cyan-600 px-6 py-12 relative overflow-hidden">
                <div className="absolute inset-0 bg-gradient-to-r from-blue-600/90 via-purple-600/90 to-cyan-600/90"></div>
                <div className="relative z-10 flex items-center space-x-8">
                  {/* Avatar */}
                  <div className="relative group">
                    <div 
                      className="w-32 h-32 rounded-full bg-white/20 backdrop-blur-sm border-4 border-white/30 flex items-center justify-center cursor-pointer group-hover:scale-105 transition-all duration-300 overflow-hidden"
                      onClick={handleAvatarClick}
                    >
                      {userProfile.avatar ? (
                        <img 
                          src={userProfile.avatar} 
                          alt="Profile Avatar" 
                          className="w-full h-full object-cover"
                        />
                      ) : (
                        <span className="text-5xl text-white/80">👤</span>
                      )}
                    </div>
                    <div className="absolute inset-0 rounded-full bg-black/20 opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex items-center justify-center">
                      <span className="text-white text-sm font-medium">Change Photo</span>
                    </div>
                    <input
                      ref={fileInputRef}
                      type="file"
                      accept="image/*"
                      onChange={handleAvatarChange}
                      className="hidden"
                    />
                  </div>

                  {/* User Info */}
                  <div className="flex-1">
                    <div className="flex items-center space-x-4 mb-4">
                      <h1 className="text-4xl font-bold text-white">{userProfile.full_name}</h1>
                      <div className={`w-4 h-4 rounded-full ${getStatusColor(userProfile.status)} border-2 border-white`}></div>
                    </div>
                    <div className="space-y-2">
                      <p className="text-white/90 text-lg">@{userProfile.username}</p>
                      <p className="text-white/80">{userProfile.email}</p>
                      <div className="flex items-center space-x-4 text-white/70">
                        <span>{getRoleDisplayName(userProfile.role)}</span>
                        <span>•</span>
                        <span>{userProfile.department}</span>
                        <span>•</span>
                        <span>{userProfile.location}</span>
                      </div>
                    </div>
                    <div className="mt-6 flex space-x-4">
                      <button
                        onClick={() => setIsEditing(!isEditing)}
                        className="bg-white/20 backdrop-blur-sm text-white px-6 py-2 rounded-2xl border border-white/30 hover:bg-white/30 transition-all duration-300 font-medium"
                      >
                        {isEditing ? 'Cancel Edit' : 'Edit Profile'}
                      </button>
                      <button className="bg-white/20 backdrop-blur-sm text-white px-6 py-2 rounded-2xl border border-white/30 hover:bg-white/30 transition-all duration-300 font-medium">
                        Download Report
                      </button>
                    </div>
                  </div>
                </div>
              </div>

              {/* Navigation Tabs */}
              <div className="px-6 py-4 bg-white/20 backdrop-blur-sm border-t border-white/20">
                <nav className="flex space-x-4">
                  {[
                    { id: 'overview', label: 'Overview', icon: '👤' },
                    { id: 'activity', label: 'Activity', icon: '📊' },
                    { id: 'settings', label: 'Settings', icon: '⚙️' },
                    { id: 'training', label: 'Model Training', icon: '🤖' }
                  ].map((tab) => (
                    <button
                      key={tab.id}
                      onClick={() => setActiveTab(tab.id)}
                      className={`group flex items-center space-x-3 px-4 py-2 rounded-2xl font-semibold transition-all duration-300 hover:scale-105 ${
                        activeTab === tab.id
                          ? 'bg-white/30 text-white shadow-lg border border-white/30'
                          : 'text-white/70 hover:text-white hover:bg-white/20 border border-white/10'
                      }`}
                    >
                      <span className="group-hover:scale-110 transition-transform duration-300">{tab.icon}</span>
                      <span>{tab.label}</span>
                    </button>
                  ))}
                </nav>
              </div>
            </div>
          </div>

          {/* Tab Content */}
          {activeTab === 'overview' && (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Profile Information */}
              <div className="lg:col-span-2 space-y-6">
                <div className="backdrop-blur-lg bg-white/40 border border-white/50 rounded-3xl shadow-xl p-5">
                  <div className="flex items-center mb-4">
                    <div className="p-3 bg-gradient-to-r from-blue-500 to-purple-500 rounded-2xl mr-4">
                      <span className="text-2xl">👤</span>
                    </div>
                    <div>
                      <h2 className="text-xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                        Profile Information
                      </h2>
                      <p className="text-gray-600">Manage your personal details</p>
                    </div>
                  </div>
                  
                  {isEditing ? (
                    <div className="space-y-6">
                      <div>
                        <label className="block text-sm font-semibold text-gray-700 mb-3 uppercase tracking-wider">Full Name</label>
                        <input
                          type="text"
                          value={editForm.full_name}
                          onChange={(e) => setEditForm(prev => ({ ...prev, full_name: e.target.value }))}
                          className="w-full px-4 py-3 backdrop-blur-sm bg-white/50 border border-white/30 rounded-2xl focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-transparent transition-all duration-300 text-gray-800"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-semibold text-gray-700 mb-3 uppercase tracking-wider">Phone</label>
                        <input
                          type="tel"
                          value={editForm.phone}
                          onChange={(e) => setEditForm(prev => ({ ...prev, phone: e.target.value }))}
                          className="w-full px-4 py-3 backdrop-blur-sm bg-white/50 border border-white/30 rounded-2xl focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-transparent transition-all duration-300 text-gray-800"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-semibold text-gray-700 mb-3 uppercase tracking-wider">Department</label>
                        <input
                          type="text"
                          value={editForm.department}
                          onChange={(e) => setEditForm(prev => ({ ...prev, department: e.target.value }))}
                          className="w-full px-4 py-3 backdrop-blur-sm bg-white/50 border border-white/30 rounded-2xl focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-transparent transition-all duration-300 text-gray-800"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-semibold text-gray-700 mb-3 uppercase tracking-wider">Location</label>
                        <input
                          type="text"
                          value={editForm.location}
                          onChange={(e) => setEditForm(prev => ({ ...prev, location: e.target.value }))}
                          className="w-full px-4 py-3 backdrop-blur-sm bg-white/50 border border-white/30 rounded-2xl focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-transparent transition-all duration-300 text-gray-800"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">Bio</label>
                        <textarea
                          value={editForm.bio}
                          onChange={(e) => setEditForm(prev => ({ ...prev, bio: e.target.value }))}
                          rows={4}
                          className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">Status</label>
                        <select
                          value={editForm.status}
                          onChange={(e) => setEditForm(prev => ({ ...prev, status: e.target.value as any }))}
                          className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        >
                          <option value="active">Active</option>
                          <option value="away">Away</option>
                          <option value="busy">Busy</option>
                          <option value="offline">Offline</option>
                        </select>
                      </div>
                      <div className="flex space-x-3 pt-4">
                        <button
                          onClick={handleSaveProfile}
                          className="bg-blue-600 text-white px-6 py-2 rounded-xl hover:bg-blue-700 transition-colors font-medium"
                        >
                          Save Changes
                        </button>
                        <button
                          onClick={() => setIsEditing(false)}
                          className="bg-gray-100 text-gray-700 px-6 py-2 rounded-xl hover:bg-gray-200 transition-colors font-medium"
                        >
                          Cancel
                        </button>
                      </div>
                    </div>
                  ) : (
                    <div className="space-y-4">
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                          <label className="block text-sm font-medium text-gray-500">Full Name</label>
                          <p className="text-gray-900 font-medium">{userProfile.full_name}</p>
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-gray-500">Username</label>
                          <p className="text-gray-900 font-medium">@{userProfile.username}</p>
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-gray-500">Email</label>
                          <p className="text-gray-900 font-medium">{userProfile.email}</p>
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-gray-500">Phone</label>
                          <p className="text-gray-900 font-medium">{userProfile.phone || 'Not provided'}</p>
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-gray-500">Department</label>
                          <p className="text-gray-900 font-medium">{userProfile.department || 'Not specified'}</p>
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-gray-500">Location</label>
                          <p className="text-gray-900 font-medium">{userProfile.location || 'Not specified'}</p>
                        </div>
                      </div>
                      {userProfile.bio && (
                        <div className="pt-4 border-t border-gray-100">
                          <label className="block text-sm font-medium text-gray-500 mb-2">Bio</label>
                          <p className="text-gray-700 leading-relaxed">{userProfile.bio}</p>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              </div>

              {/* Sidebar */}
              <div className="space-y-4">
                {/* Quick Stats */}
                <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-4">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Stats</h3>
                  <div className="space-y-3">
                    <div className="flex justify-between">
                      <span className="text-gray-600">Reports Generated</span>
                      <span className="font-semibold text-gray-900">47</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Sites Monitored</span>
                      <span className="font-semibold text-gray-900">12</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Predictions Made</span>
                      <span className="font-semibold text-gray-900">234</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Last Login</span>
                      <span className="font-semibold text-gray-900">Today</span>
                    </div>
                  </div>
                </div>

                {/* Role & Permissions */}
                <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-4">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Role & Permissions</h3>
                  <div className="space-y-3">
                    <div className="flex items-center space-x-3">
                      <div className="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center">
                        🛡️
                      </div>
                      <div>
                        <p className="font-medium text-gray-900">{getRoleDisplayName(userProfile.role)}</p>
                        <p className="text-sm text-gray-600">Full system access</p>
                      </div>
                    </div>
                    <div className="text-sm text-gray-600 space-y-1 pl-11">
                      <p>✅ View all sites and reports</p>
                      <p>✅ Manage users and permissions</p>
                      <p>✅ Configure system settings</p>
                      <p>✅ Generate and export reports</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'activity' && (
            <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-4">
              <h2 className="text-lg font-semibold text-gray-900 mb-3">Recent Activity</h2>
              <div className="space-y-4">
                {[
                  { action: 'Generated weekly risk assessment report', time: '2 hours ago', icon: '📊' },
                  { action: 'Updated sensor configuration for Site Alpha-7', time: '5 hours ago', icon: '🔧' },
                  { action: 'Reviewed high-risk alert for geological instability', time: '1 day ago', icon: '🚨' },
                  { action: 'Completed ML model calibration', time: '2 days ago', icon: '🤖' }
                ].map((activity, index) => (
                  <div key={index} className="flex items-center space-x-4 p-3 rounded-xl hover:bg-gray-50">
                    <div className="text-2xl">{activity.icon}</div>
                    <div className="flex-1">
                      <p className="text-gray-900">{activity.action}</p>
                      <p className="text-sm text-gray-500">{activity.time}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {activeTab === 'training' && (
            <div className="backdrop-blur-lg bg-white/40 border border-white/50 rounded-3xl shadow-xl p-8">
              <div className="text-center">
                <div className="mx-auto w-20 h-20 bg-gradient-to-r from-purple-500 to-blue-500 rounded-full flex items-center justify-center mb-6">
                  <span className="text-3xl">🤖</span>
                </div>
                <h2 className="text-2xl font-bold bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent mb-4">
                  AI Model Training Center
                </h2>
                <p className="text-gray-600 mb-8 max-w-2xl mx-auto">
                  Access advanced machine learning model training capabilities. This secure area allows you to configure, train, and deploy custom AI models for enhanced rockfall prediction accuracy.
                </p>
                <button
                  onClick={() => setShowTrainingModal(true)}
                  className="bg-gradient-to-r from-purple-600 to-blue-600 text-white px-8 py-4 rounded-2xl font-semibold hover:shadow-lg transform hover:scale-105 transition-all duration-300"
                >
                  🔐 Access Model Training
                </button>
              </div>
            </div>
          )}

          {activeTab === 'settings' && (
            <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-4">
              <h2 className="text-lg font-semibold text-gray-900 mb-3">Account Settings</h2>
              <div className="space-y-6">
                <div className="flex items-center justify-between py-4 border-b border-gray-100">
                  <div>
                    <h3 className="font-medium text-gray-900">Email Notifications</h3>
                    <p className="text-sm text-gray-600">Receive alerts and updates via email</p>
                  </div>
                  <button className="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm">
                    Configure
                  </button>
                </div>
                <div className="flex items-center justify-between py-4 border-b border-gray-100">
                  <div>
                    <h3 className="font-medium text-gray-900">Two-Factor Authentication</h3>
                    <p className="text-sm text-gray-600">Add an extra layer of security</p>
                  </div>
                  <button className="bg-green-600 text-white px-4 py-2 rounded-lg text-sm">
                    Enable
                  </button>
                </div>
                <div className="flex items-center justify-between py-4">
                  <div>
                    <h3 className="font-medium text-gray-900">Change Password</h3>
                    <p className="text-sm text-gray-600">Update your account password</p>
                  </div>
                  <button className="bg-gray-600 text-white px-4 py-2 rounded-lg text-sm">
                    Update
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Secure Model Training Modal */}
      {showTrainingModal && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-3xl shadow-2xl max-w-6xl w-full max-h-[90vh] overflow-y-auto">
            {!isAuthenticated ? (
              // Password Authentication Screen
              <div className="p-8 text-center">
                <div className="mx-auto w-20 h-20 bg-gradient-to-r from-red-500 to-orange-500 rounded-full flex items-center justify-center mb-6">
                  <span className="text-3xl">🔒</span>
                </div>
                <h2 className="text-3xl font-bold text-gray-900 mb-4">Secure Access Required</h2>
                <p className="text-gray-600 mb-8 max-w-lg mx-auto">
                  This area contains sensitive AI model training capabilities. Please enter the administrator password to continue.
                </p>
                
                <div className="max-w-md mx-auto">
                  <input
                    type="password"
                    value={trainingPassword}
                    onChange={(e) => setTrainingPassword(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && handleTrainingAccess()}
                    placeholder="Enter administrator password"
                    className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent mb-4 text-center text-lg"
                  />
                  
                  {passwordError && (
                    <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-xl mb-4">
                      <span className="flex items-center">
                        <span className="mr-2">⚠️</span>
                        {passwordError}
                      </span>
                    </div>
                  )}
                  
                  <div className="flex space-x-4">
                    <button
                      onClick={handleTrainingAccess}
                      className="flex-1 bg-blue-600 text-white px-6 py-3 rounded-xl font-semibold hover:bg-blue-700 transition-colors"
                    >
                      🔓 Authenticate
                    </button>
                    <button
                      onClick={closeTrainingModal}
                      className="flex-1 bg-gray-200 text-gray-700 px-6 py-3 rounded-xl font-semibold hover:bg-gray-300 transition-colors"
                    >
                      Cancel
                    </button>
                  </div>
                </div>
              </div>
            ) : (
              // Model Training Interface
              <div className="p-8">
                <div className="flex items-center justify-between mb-8">
                  <div>
                    <h2 className="text-3xl font-bold bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent">
                      🤖 AI-Based Rockfall Prediction Training Center
                    </h2>
                    <p className="text-gray-600 mt-2 max-w-3xl">
                      Advanced multi-modal machine learning pipeline for high-accuracy rockfall prediction. 
                      Combines temporal analysis (LSTM/GRU/Transformer), spatial processing (CNN/PointNet), 
                      and fusion networks to predict risk probability and lead times with 24-48 hour horizons.
                    </p>
                    <div className="mt-3 flex flex-wrap gap-2">
                      <span className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-xs font-medium">
                        ⏰ Temporal Models: Time-series sensor data
                      </span>
                      <span className="px-3 py-1 bg-green-100 text-green-700 rounded-full text-xs font-medium">
                        🗺️ Spatial Models: Drone imagery & LiDAR
                      </span>
                      <span className="px-3 py-1 bg-purple-100 text-purple-700 rounded-full text-xs font-medium">
                        🔗 Fusion Models: Multi-modal integration
                      </span>
                    </div>
                  </div>
                  <button
                    onClick={closeTrainingModal}
                    className="bg-red-100 text-red-600 p-3 rounded-xl hover:bg-red-200 transition-colors"
                  >
                    ✕ Close
                  </button>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                  {/* Training Configuration Panel */}
                  <div className="space-y-6">
                    <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-2xl p-6">
                      <h3 className="text-xl font-bold text-gray-900 mb-4 flex items-center">
                        <span className="mr-3">⚙️</span>
                        Training Configuration
                      </h3>

                      {/* Multi-Modal Architecture Selection */}
                      <div className="mb-6">
                        <label className="block text-sm font-semibold text-gray-700 mb-4">AI Model Architecture</label>
                        
                        {/* Temporal Models */}
                        <div className="bg-blue-50 rounded-xl p-4 mb-4">
                          <div className="flex items-center justify-between mb-3">
                            <h4 className="font-semibold text-blue-800 flex items-center">
                              <span className="mr-2">⏰</span>
                              Temporal Model (Time-Series)
                            </h4>
                            <input
                              type="checkbox"
                              checked={trainingConfig.temporalModel.enabled}
                              onChange={(e) => setTrainingConfig(prev => ({
                                ...prev,
                                temporalModel: { ...prev.temporalModel, enabled: e.target.checked }
                              }))}
                              className="w-5 h-5 text-blue-600 rounded"
                            />
                          </div>
                          <select
                            value={trainingConfig.temporalModel.type}
                            onChange={(e) => setTrainingConfig(prev => ({
                              ...prev,
                              temporalModel: { ...prev.temporalModel, type: e.target.value as any }
                            }))}
                            disabled={!trainingConfig.temporalModel.enabled}
                            className="w-full px-3 py-2 border border-blue-200 rounded-lg focus:ring-2 focus:ring-blue-500 text-sm disabled:bg-gray-100"
                          >
                            <option value="LSTM">LSTM - Long Short-Term Memory</option>
                            <option value="GRU">GRU - Gated Recurrent Unit</option>
                            <option value="Temporal_Transformer">Temporal Transformer</option>
                          </select>
                          <p className="text-xs text-blue-600 mt-1">
                            Handles displacement, velocity, pore pressure trends over time
                          </p>
                        </div>

                        {/* Spatial Models */}
                        <div className="bg-green-50 rounded-xl p-4 mb-4">
                          <div className="flex items-center justify-between mb-3">
                            <h4 className="font-semibold text-green-800 flex items-center">
                              <span className="mr-2">🗺️</span>
                              Spatial Model (Image/3D Data)
                            </h4>
                            <input
                              type="checkbox"
                              checked={trainingConfig.spatialModel.enabled}
                              onChange={(e) => setTrainingConfig(prev => ({
                                ...prev,
                                spatialModel: { ...prev.spatialModel, enabled: e.target.checked }
                              }))}
                              className="w-5 h-5 text-green-600 rounded"
                            />
                          </div>
                          <select
                            value={trainingConfig.spatialModel.type}
                            onChange={(e) => setTrainingConfig(prev => ({
                              ...prev,
                              spatialModel: { ...prev.spatialModel, type: e.target.value as any }
                            }))}
                            disabled={!trainingConfig.spatialModel.enabled}
                            className="w-full px-3 py-2 border border-green-200 rounded-lg focus:ring-2 focus:ring-green-500 text-sm disabled:bg-gray-100"
                          >
                            <option value="CNN">CNN - Convolutional Neural Network</option>
                            <option value="PointNet">PointNet - Point Cloud Processing</option>
                            <option value="PointNet_Plus">PointNet++ - Advanced Point Cloud</option>
                          </select>
                          <p className="text-xs text-green-600 mt-1">
                            Processes drone imagery, crack detection, LiDAR point clouds
                          </p>
                        </div>

                        {/* Fusion Models */}
                        <div className="bg-purple-50 rounded-xl p-4 mb-4">
                          <div className="flex items-center justify-between mb-3">
                            <h4 className="font-semibold text-purple-800 flex items-center">
                              <span className="mr-2">🔗</span>
                              Fusion Model (Multi-Modal)
                            </h4>
                            <input
                              type="checkbox"
                              checked={trainingConfig.fusionModel.enabled}
                              onChange={(e) => setTrainingConfig(prev => ({
                                ...prev,
                                fusionModel: { ...prev.fusionModel, enabled: e.target.checked }
                              }))}
                              className="w-5 h-5 text-purple-600 rounded"
                            />
                          </div>
                          <select
                            value={trainingConfig.fusionModel.type}
                            onChange={(e) => setTrainingConfig(prev => ({
                              ...prev,
                              fusionModel: { ...prev.fusionModel, type: e.target.value as any }
                            }))}
                            disabled={!trainingConfig.fusionModel.enabled}
                            className="w-full px-3 py-2 border border-purple-200 rounded-lg focus:ring-2 focus:ring-purple-500 text-sm disabled:bg-gray-100"
                          >
                            <option value="MLP">MLP - Multi-Layer Perceptron</option>
                            <option value="Fusion_Network">Advanced Fusion Network</option>
                          </select>
                          <p className="text-xs text-purple-600 mt-1">
                            Combines temporal + spatial features for final risk prediction
                          </p>
                        </div>

                        {/* Advanced Options */}
                        <div className="bg-orange-50 rounded-xl p-4">
                          <h4 className="font-semibold text-orange-800 mb-3 flex items-center">
                            <span className="mr-2">🚀</span>
                            Advanced Options
                          </h4>
                          <div className="space-y-2">
                            <label className="flex items-center space-x-3">
                              <input
                                type="checkbox"
                                checked={trainingConfig.advancedOptions.ensembleMethods}
                                onChange={(e) => setTrainingConfig(prev => ({
                                  ...prev,
                                  advancedOptions: { ...prev.advancedOptions, ensembleMethods: e.target.checked }
                                }))}
                                className="w-4 h-4 text-orange-600 rounded"
                              />
                              <span className="text-sm text-orange-700">Ensemble Methods</span>
                            </label>
                            <label className="flex items-center space-x-3">
                              <input
                                type="checkbox"
                                checked={trainingConfig.advancedOptions.bayesianUncertainty}
                                onChange={(e) => setTrainingConfig(prev => ({
                                  ...prev,
                                  advancedOptions: { ...prev.advancedOptions, bayesianUncertainty: e.target.checked }
                                }))}
                                className="w-4 h-4 text-orange-600 rounded"
                              />
                              <span className="text-sm text-orange-700">Bayesian Uncertainty Estimation</span>
                            </label>
                            <label className="flex items-center space-x-3">
                              <input
                                type="checkbox"
                                checked={trainingConfig.advancedOptions.gradientBoosting}
                                onChange={(e) => setTrainingConfig(prev => ({
                                  ...prev,
                                  advancedOptions: { ...prev.advancedOptions, gradientBoosting: e.target.checked }
                                }))}
                                className="w-4 h-4 text-orange-600 rounded"
                              />
                              <span className="text-sm text-orange-700">Gradient Boosting Baseline</span>
                            </label>
                          </div>
                        </div>
                      </div>

                      {/* Output Types */}
                      <div className="mb-6">
                        <label className="block text-sm font-semibold text-gray-700 mb-3">Model Outputs</label>
                        <div className="space-y-2">
                          {Object.entries(trainingConfig.outputTypes).map(([key, value]) => (
                            <label key={key} className="flex items-center space-x-3">
                              <input
                                type="checkbox"
                                checked={value}
                                onChange={(e) => setTrainingConfig(prev => ({
                                  ...prev,
                                  outputTypes: { ...prev.outputTypes, [key]: e.target.checked }
                                }))}
                                className="w-5 h-5 text-blue-600 rounded focus:ring-blue-500"
                              />
                              <span className="text-gray-700 capitalize">
                                {key.replace(/([A-Z])/g, ' $1').replace(/^./, str => str.toUpperCase())}
                              </span>
                            </label>
                          ))}
                        </div>
                      </div>

                      {/* Prediction Horizon */}
                      <div className="mb-6">
                        <label className="block text-sm font-semibold text-gray-700 mb-3">Prediction Horizons</label>
                        <div className="grid grid-cols-2 gap-4">
                          <div>
                            <label className="block text-xs text-gray-600 mb-1">Short-term (hours)</label>
                            <input
                              type="number"
                              value={trainingConfig.predictionHorizon.shortTerm}
                              onChange={(e) => setTrainingConfig(prev => ({
                                ...prev,
                                predictionHorizon: { ...prev.predictionHorizon, shortTerm: parseInt(e.target.value) }
                              }))}
                              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 text-sm"
                              min="1"
                              max="72"
                            />
                          </div>
                          <div>
                            <label className="block text-xs text-gray-600 mb-1">Long-term (hours)</label>
                            <input
                              type="number"
                              value={trainingConfig.predictionHorizon.longTerm}
                              onChange={(e) => setTrainingConfig(prev => ({
                                ...prev,
                                predictionHorizon: { ...prev.predictionHorizon, longTerm: parseInt(e.target.value) }
                              }))}
                              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 text-sm"
                              min="24"
                              max="168"
                            />
                          </div>
                        </div>
                        <p className="text-xs text-gray-500 mt-1">
                          Configure prediction time horizons for risk assessment
                        </p>
                      </div>

                      {/* Feature Selection */}
                      <div className="mb-6">
                        <label className="block text-sm font-semibold text-gray-700 mb-4">Feature Selection</label>
                        
                        {/* Temporal Features */}
                        <div className="mb-4">
                          <h4 className="text-sm font-medium text-blue-700 mb-2 flex items-center">
                            <span className="mr-2">⏰</span>
                            Temporal Features (Time-Series Data)
                          </h4>
                          <div className="grid grid-cols-2 gap-2 pl-4">
                            {Object.entries(trainingConfig.temporalFeatures).map(([key, value]) => (
                              <label key={key} className="flex items-center space-x-2">
                                <input
                                  type="checkbox"
                                  checked={value}
                                  onChange={(e) => setTrainingConfig(prev => ({
                                    ...prev,
                                    temporalFeatures: { ...prev.temporalFeatures, [key]: e.target.checked }
                                  }))}
                                  className="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
                                />
                                <span className="text-sm text-gray-700 capitalize">
                                  {key.replace(/([A-Z])/g, ' $1').replace(/^./, str => str.toUpperCase())}
                                </span>
                              </label>
                            ))}
                          </div>
                        </div>

                        {/* Spatial Features */}
                        <div>
                          <h4 className="text-sm font-medium text-green-700 mb-2 flex items-center">
                            <span className="mr-2">🗺️</span>
                            Spatial Features (Image/3D Data)
                          </h4>
                          <div className="grid grid-cols-2 gap-2 pl-4">
                            {Object.entries(trainingConfig.spatialFeatures).map(([key, value]) => (
                              <label key={key} className="flex items-center space-x-2">
                                <input
                                  type="checkbox"
                                  checked={value}
                                  onChange={(e) => setTrainingConfig(prev => ({
                                    ...prev,
                                    spatialFeatures: { ...prev.spatialFeatures, [key]: e.target.checked }
                                  }))}
                                  className="w-4 h-4 text-green-600 rounded focus:ring-green-500"
                                />
                                <span className="text-sm text-gray-700 capitalize">
                                  {key.replace(/([A-Z])/g, ' $1').replace(/^./, str => str.toUpperCase())}
                                </span>
                              </label>
                            ))}
                          </div>
                        </div>
                      </div>

                      {/* Training Window */}
                      <div className="mb-6">
                        <label className="block text-sm font-semibold text-gray-700 mb-3">Training Window</label>
                        <div className="flex space-x-2">
                          <input
                            type="number"
                            value={trainingConfig.trainingWindow.value}
                            onChange={(e) => setTrainingConfig(prev => ({
                              ...prev,
                              trainingWindow: { ...prev.trainingWindow, value: parseInt(e.target.value) }
                            }))}
                            className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                            min="1"
                          />
                          <select
                            value={trainingConfig.trainingWindow.unit}
                            onChange={(e) => setTrainingConfig(prev => ({
                              ...prev,
                              trainingWindow: { ...prev.trainingWindow, unit: e.target.value as any }
                            }))}
                            className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                          >
                            <option value="hours">Hours</option>
                            <option value="days">Days</option>
                          </select>
                        </div>
                      </div>

                      {/* Hyperparameters */}
                      <div className="mb-6">
                        <label className="block text-sm font-semibold text-gray-700 mb-3">Hyperparameters</label>
                        <div className="grid grid-cols-2 gap-4">
                          <div>
                            <label className="block text-xs text-gray-600 mb-1">Learning Rate</label>
                            <input
                              type="number"
                              step="0.0001"
                              value={trainingConfig.hyperparameters.learningRate}
                              onChange={(e) => setTrainingConfig(prev => ({
                                ...prev,
                                hyperparameters: { ...prev.hyperparameters, learningRate: parseFloat(e.target.value) }
                              }))}
                              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 text-sm"
                            />
                          </div>
                          <div>
                            <label className="block text-xs text-gray-600 mb-1">Batch Size</label>
                            <input
                              type="number"
                              value={trainingConfig.hyperparameters.batchSize}
                              onChange={(e) => setTrainingConfig(prev => ({
                                ...prev,
                                hyperparameters: { ...prev.hyperparameters, batchSize: parseInt(e.target.value) }
                              }))}
                              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 text-sm"
                            />
                          </div>
                          <div>
                            <label className="block text-xs text-gray-600 mb-1">Epochs</label>
                            <input
                              type="number"
                              value={trainingConfig.hyperparameters.epochs}
                              onChange={(e) => setTrainingConfig(prev => ({
                                ...prev,
                                hyperparameters: { ...prev.hyperparameters, epochs: parseInt(e.target.value) }
                              }))}
                              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 text-sm"
                            />
                          </div>
                          <div>
                            <label className="block text-xs text-gray-600 mb-1">Dropout Rate</label>
                            <input
                              type="number"
                              step="0.1"
                              min="0"
                              max="1"
                              value={trainingConfig.hyperparameters.dropoutRate}
                              onChange={(e) => setTrainingConfig(prev => ({
                                ...prev,
                                hyperparameters: { ...prev.hyperparameters, dropoutRate: parseFloat(e.target.value) }
                              }))}
                              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 text-sm"
                            />
                          </div>
                          <div>
                            <label className="block text-xs text-gray-600 mb-1">Sequence Length</label>
                            <input
                              type="number"
                              value={trainingConfig.hyperparameters.sequenceLength}
                              onChange={(e) => setTrainingConfig(prev => ({
                                ...prev,
                                hyperparameters: { ...prev.hyperparameters, sequenceLength: parseInt(e.target.value) }
                              }))}
                              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 text-sm"
                            />
                          </div>
                          <div>
                            <label className="block text-xs text-gray-600 mb-1">Hidden Dimensions</label>
                            <input
                              type="number"
                              value={trainingConfig.hyperparameters.hiddenDimensions}
                              onChange={(e) => setTrainingConfig(prev => ({
                                ...prev,
                                hyperparameters: { ...prev.hyperparameters, hiddenDimensions: parseInt(e.target.value) }
                              }))}
                              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 text-sm"
                            />
                          </div>
                          <div>
                            <label className="block text-xs text-gray-600 mb-1">Attention Heads</label>
                            <input
                              type="number"
                              value={trainingConfig.hyperparameters.attentionHeads}
                              onChange={(e) => setTrainingConfig(prev => ({
                                ...prev,
                                hyperparameters: { ...prev.hyperparameters, attentionHeads: parseInt(e.target.value) }
                              }))}
                              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 text-sm"
                              disabled={trainingConfig.temporalModel.type !== 'Temporal_Transformer'}
                            />
                          </div>
                        </div>
                        <p className="text-xs text-gray-500 mt-2">
                          Sequence length applies to temporal models. Attention heads only for Transformer models.
                        </p>
                      </div>

                      {/* Dataset Selection */}
                      <div className="mb-6">
                        <label className="block text-sm font-semibold text-gray-700 mb-3">Training Dataset</label>
                        <select
                          value={trainingConfig.dataset}
                          onChange={(e) => setTrainingConfig(prev => ({ ...prev, dataset: e.target.value as any }))}
                          className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        >
                          <option value="historical">Historical Data Only</option>
                          <option value="synthetic">Synthetic Data Only</option>
                          <option value="augmented">Augmented Historical Data</option>
                          <option value="combined">Combined (Historical + Synthetic + Augmented)</option>
                        </select>
                        <p className="text-xs text-gray-500 mt-2">
                          Combined dataset provides best performance for multi-modal training
                        </p>
                      </div>

                      {/* Start Training Button */}
                      <div className="flex space-x-4">
                        {trainingStatus.isRunning ? (
                          <button
                            onClick={cancelTraining}
                            className="flex-1 bg-red-600 text-white px-6 py-3 rounded-xl font-semibold hover:bg-red-700 transition-colors"
                          >
                            🛑 Cancel Training
                          </button>
                        ) : (
                          <button
                            onClick={startTraining}
                            className="flex-1 bg-green-600 text-white px-6 py-3 rounded-xl font-semibold hover:bg-green-700 transition-colors"
                          >
                            🚀 Start Training
                          </button>
                        )}
                      </div>
                    </div>
                  </div>

                  {/* Training Monitoring Panel */}
                  <div className="space-y-6">
                    <div className="bg-gradient-to-r from-green-50 to-blue-50 rounded-2xl p-6">
                      {/* Training Monitor */}
                      <h3 className="text-xl font-bold text-gray-900 mb-4 flex items-center">
                        <span className="mr-3">📈</span>
                        Multi-Modal Training Monitor
                      </h3>

                      {/* Active Models Display */}
                      <div className="mb-4">
                        <h4 className="text-sm font-semibold text-gray-700 mb-2">Active Model Pipeline</h4>
                        <div className="flex flex-wrap gap-2">
                          {trainingConfig.temporalModel.enabled && (
                            <span className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-xs font-medium">
                              {trainingConfig.temporalModel.type}
                            </span>
                          )}
                          {trainingConfig.spatialModel.enabled && (
                            <span className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-xs font-medium">
                              {trainingConfig.spatialModel.type}
                            </span>
                          )}
                          {trainingConfig.fusionModel.enabled && (
                            <span className="px-3 py-1 bg-purple-100 text-purple-800 rounded-full text-xs font-medium">
                              {trainingConfig.fusionModel.type}
                            </span>
                          )}
                          {trainingConfig.advancedOptions.ensembleMethods && (
                            <span className="px-3 py-1 bg-orange-100 text-orange-800 rounded-full text-xs font-medium">
                              Ensemble
                            </span>
                          )}
                          {trainingConfig.advancedOptions.bayesianUncertainty && (
                            <span className="px-3 py-1 bg-red-100 text-red-800 rounded-full text-xs font-medium">
                              Bayesian
                            </span>
                          )}
                        </div>
                      </div>

                      {/* Status */}
                      <div className="mb-6">
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-sm font-semibold text-gray-700">Status</span>
                          <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                            trainingStatus.status === 'training' ? 'bg-blue-100 text-blue-800' :
                            trainingStatus.status === 'completed' ? 'bg-green-100 text-green-800' :
                            trainingStatus.status === 'failed' ? 'bg-red-100 text-red-800' :
                            trainingStatus.status === 'cancelled' ? 'bg-gray-100 text-gray-800' :
                            'bg-gray-100 text-gray-600'
                          }`}>
                            {trainingStatus.status.toUpperCase()}
                          </span>
                        </div>
                        
                        {trainingStatus.isRunning && (
                          <div className="w-full bg-gray-200 rounded-full h-2 mb-2">
                            <div 
                              className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                              style={{ width: `${trainingStatus.progress}%` }}
                            ></div>
                          </div>
                        )}
                        
                        {trainingStatus.isRunning && (
                          <div className="text-sm text-gray-600">
                            Epoch {trainingStatus.currentEpoch} / {trainingStatus.totalEpochs} 
                            {trainingStatus.estimatedTimeRemaining > 0 && (
                              <span className="ml-2">
                                • ETA: {Math.ceil(trainingStatus.estimatedTimeRemaining / 60)}m
                              </span>
                            )}
                          </div>
                        )}
                      </div>

                      {/* Real-time Metrics */}
                      {trainingStatus.metrics.length > 0 && (
                        <div className="mb-6">
                          <h4 className="text-lg font-semibold text-gray-800 mb-3">Latest Training Metrics</h4>
                          <div className="grid grid-cols-2 gap-3">
                            {(() => {
                              const latest = trainingStatus.metrics[trainingStatus.metrics.length - 1]
                              return (
                                <>
                                  <div className="bg-white rounded-lg p-3 border border-blue-200">
                                    <div className="text-xs text-blue-600 font-medium">Temporal Loss</div>
                                    <div className="text-lg font-bold text-blue-700">{latest.trainLoss.toFixed(4)}</div>
                                  </div>
                                  <div className="bg-white rounded-lg p-3 border border-green-200">
                                    <div className="text-xs text-green-600 font-medium">Spatial Loss</div>
                                    <div className="text-lg font-bold text-green-700">{latest.valLoss.toFixed(4)}</div>
                                  </div>
                                  <div className="bg-white rounded-lg p-3 border border-purple-200">
                                    <div className="text-xs text-purple-600 font-medium">Fusion Accuracy</div>
                                    <div className="text-lg font-bold text-purple-700">{(latest.accuracy * 100).toFixed(1)}%</div>
                                  </div>
                                  <div className="bg-white rounded-lg p-3 border border-orange-200">
                                    <div className="text-xs text-orange-600 font-medium">Risk PR-AUC</div>
                                    <div className="text-lg font-bold text-orange-700">{latest.prAuc.toFixed(3)}</div>
                                  </div>
                                  <div className="bg-white rounded-lg p-3 border border-red-200">
                                    <div className="text-xs text-red-600 font-medium">Lead Time MAE</div>
                                    <div className="text-lg font-bold text-red-700">{latest.leadTimeMae.toFixed(2)}h</div>
                                  </div>
                                  <div className="bg-white rounded-lg p-3 border border-cyan-200">
                                    <div className="text-xs text-cyan-600 font-medium">Confidence Cal.</div>
                                    <div className="text-lg font-bold text-cyan-700">{latest.confidenceCalibration.toFixed(3)}</div>
                                  </div>
                                </>
                              )
                            })()}
                          </div>
                          <div className="mt-3 text-xs text-gray-500">
                            Real-time metrics from temporal, spatial, and fusion model components
                          </div>
                        </div>
                      )}

                      {/* Training Logs */}
                      <div>
                        <h4 className="text-lg font-semibold text-gray-800 mb-3">Training Logs</h4>
                        <div className="bg-gray-900 rounded-lg p-4 h-48 overflow-y-auto">
                          <div className="font-mono text-sm space-y-1">
                            {trainingStatus.logs.length === 0 ? (
                              <div className="text-gray-500">Waiting for training to start...</div>
                            ) : (
                              trainingStatus.logs.map((log, index) => (
                                <div key={index} className="text-green-400">
                                  <span className="text-gray-500">[{new Date().toLocaleTimeString()}]</span> {log}
                                </div>
                              ))
                            )}
                          </div>
                        </div>
                      </div>

                      {/* Post-Training Summary */}
                      {trainingStatus.status === 'completed' && (
                        <div className="mt-6 p-4 bg-green-50 border border-green-200 rounded-lg">
                          <h4 className="text-lg font-semibold text-green-800 mb-2">Multi-Modal Training Completed! 🎉</h4>
                          <p className="text-green-700 mb-4">
                            Successfully trained {[
                              trainingConfig.temporalModel.enabled && trainingConfig.temporalModel.type,
                              trainingConfig.spatialModel.enabled && trainingConfig.spatialModel.type,
                              trainingConfig.fusionModel.enabled && trainingConfig.fusionModel.type
                            ].filter(Boolean).join(' + ')} pipeline for high-accuracy rockfall prediction.
                          </p>
                          <div className="grid grid-cols-2 gap-4 mb-4">
                            <div className="bg-white rounded p-3 border border-green-200">
                              <div className="text-sm text-green-600">Prediction Horizons</div>
                              <div className="font-semibold">{trainingConfig.predictionHorizon.shortTerm}h / {trainingConfig.predictionHorizon.longTerm}h</div>
                            </div>
                            <div className="bg-white rounded p-3 border border-green-200">
                              <div className="text-sm text-green-600">Feature Count</div>
                              <div className="font-semibold">
                                {Object.values(trainingConfig.temporalFeatures).filter(Boolean).length + 
                                 Object.values(trainingConfig.spatialFeatures).filter(Boolean).length} features
                              </div>
                            </div>
                          </div>
                          <div className="flex space-x-3">
                            <button className="bg-green-600 text-white px-4 py-2 rounded-lg text-sm font-semibold hover:bg-green-700 transition-colors">
                              📊 View Performance Report
                            </button>
                            <button className="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-semibold hover:bg-blue-700 transition-colors">
                              🚀 Deploy to Production
                            </button>
                            <button className="bg-purple-600 text-white px-4 py-2 rounded-lg text-sm font-semibold hover:bg-purple-700 transition-colors">
                              🧪 Run Validation Tests
                            </button>
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

export default ProfilePage