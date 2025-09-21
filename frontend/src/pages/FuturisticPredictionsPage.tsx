import React, { useState, useEffect, useCallback } from 'react'
import Navbar from '../components/Navbar'

// Enhanced Interfaces with futuristic features
interface DroneImage {
  file: File
  type: 'DEM' | 'orthophoto' | 'pointcloud' | 'aerial_photo'
  id: string
  preview?: string
  timestamp: string
  quality: 'LOW' | 'MEDIUM' | 'HIGH' | 'ULTRA'
  size: number
  metadata?: {
    altitude: number
    coordinates: [number, number]
    weather: string
  }
}

interface SensorData {
  device_id: string
  timestamp: string
  pore_pressure?: number
  displacement?: number
  acceleration?: number
  rmr?: number
  ucs?: number
  rainfall?: number
  temperature?: number
  seismic_activity?: number
  signal_strength: number
  battery_level: number
}

interface ProcessingStage {
  id: string
  name: string
  description: string
  status: 'pending' | 'running' | 'completed' | 'error'
  progress: number
  estimatedTime: number
  output?: any
  error?: string
  icon: string
}

interface PredictionResult {
  id: string
  riskScore: number
  riskLevel: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL'
  estimatedVolume: number
  confidence: number
  preventiveActions: string[]
  predictions: {
    immediate: { probability: number; timeWindow: string }
    shortTerm: { probability: number; timeWindow: string }
    longTerm: { probability: number; timeWindow: string }
  }
  visualizations: {
    heatmap: string
    trajectory: string
    riskZones: string
  }
  alertLevel: number
}

const ENHANCED_PROCESSING_STAGES: ProcessingStage[] = [
  { 
    id: 'data_ingestion', 
    name: 'Data Ingestion', 
    description: 'Loading and validating drone imagery and sensor data',
    status: 'pending', 
    progress: 0, 
    estimatedTime: 30,
    icon: '📡'
  },
  { 
    id: 'image_enhancement', 
    name: 'AI Image Enhancement', 
    description: 'Applying neural network-based image enhancement',
    status: 'pending', 
    progress: 0, 
    estimatedTime: 45,
    icon: '🔍'
  },
  { 
    id: 'feature_detection', 
    name: 'Geological Feature Detection', 
    description: 'Identifying fractures, joints, and weak zones',
    status: 'pending', 
    progress: 0, 
    estimatedTime: 60,
    icon: '🏔️'
  },
  { 
    id: 'sensor_fusion', 
    name: 'Multi-Sensor Data Fusion', 
    description: 'Combining sensor data with geological mapping',
    status: 'pending', 
    progress: 0, 
    estimatedTime: 40,
    icon: '🔗'
  },
  { 
    id: 'ai_analysis', 
    name: 'Deep Learning Analysis', 
    description: 'Running advanced AI models for risk assessment',
    status: 'pending', 
    progress: 0, 
    estimatedTime: 90,
    icon: '🧠'
  },
  { 
    id: 'prediction_generation', 
    name: 'Prediction Generation', 
    description: 'Generating probabilistic risk predictions',
    status: 'pending', 
    progress: 0, 
    estimatedTime: 35,
    icon: '⚡'
  },
  { 
    id: 'visualization', 
    name: '3D Visualization', 
    description: 'Creating interactive 3D risk visualizations',
    status: 'pending', 
    progress: 0, 
    estimatedTime: 25,
    icon: '🎯'
  }
]

function PredictionsPage() {
  const [droneImages, setDroneImages] = useState<DroneImage[]>([])
  const [sensorData, setSensorData] = useState<SensorData[]>([])
  const [processingStages, setProcessingStages] = useState<ProcessingStage[]>(ENHANCED_PROCESSING_STAGES)
  const [isProcessing, setIsProcessing] = useState(false)
  const [predictionResult, setPredictionResult] = useState<PredictionResult | null>(null)
  const [currentStageIndex, setCurrentStageIndex] = useState(-1)
  const [selectedSite, setSelectedSite] = useState('')
  const [analysisMode, setAnalysisMode] = useState<'standard' | 'advanced' | 'realtime'>('standard')
  const [showAdvancedOptions, setShowAdvancedOptions] = useState(false)

  // Futuristic Animation States
  const [pulseAnimation, setPulseAnimation] = useState(false)
  const [glowEffect, setGlowEffect] = useState(false)

  useEffect(() => {
    // Trigger glow effect periodically
    const interval = setInterval(() => {
      setGlowEffect(true)
      setTimeout(() => setGlowEffect(false), 2000)
    }, 5000)
    return () => clearInterval(interval)
  }, [])

  const handleImageUpload = (files: FileList) => {
    Array.from(files).forEach(file => {
      const imageId = `img_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
      const reader = new FileReader()
      
      reader.onload = (e) => {
        const newImage: DroneImage = {
          file,
          type: 'aerial_photo',
          id: imageId,
          preview: e.target?.result as string,
          timestamp: new Date().toISOString(),
          quality: file.size > 10000000 ? 'ULTRA' : file.size > 5000000 ? 'HIGH' : 'MEDIUM',
          size: file.size,
          metadata: {
            altitude: 150 + Math.random() * 100,
            coordinates: [-123.25 + Math.random() * 0.1, 49.28 + Math.random() * 0.1],
            weather: 'Clear'
          }
        }
        setDroneImages(prev => [...prev, newImage])
      }
      reader.readAsDataURL(file)
    })
  }

  const startPrediction = async () => {
    if (droneImages.length === 0) {
      alert('Please upload at least one drone image')
      return
    }

    setIsProcessing(true)
    setPulseAnimation(true)
    setCurrentStageIndex(0)

    // Simulate processing stages with realistic timing
    for (let i = 0; i < processingStages.length; i++) {
      setCurrentStageIndex(i)
      
      // Update stage to running
      setProcessingStages(prev => prev.map((stage, index) => 
        index === i ? { ...stage, status: 'running' } : stage
      ))

      // Simulate progress with smooth animation
      for (let progress = 0; progress <= 100; progress += 2) {
        setProcessingStages(prev => prev.map((stage, index) => 
          index === i ? { ...stage, progress } : stage
        ))
        await new Promise(resolve => setTimeout(resolve, processingStages[i].estimatedTime))
      }

      // Mark stage as completed
      setProcessingStages(prev => prev.map((stage, index) => 
        index === i ? { ...stage, status: 'completed', progress: 100 } : stage
      ))

      await new Promise(resolve => setTimeout(resolve, 200))
    }

    // Generate mock prediction result
    const mockResult: PredictionResult = {
      id: `pred_${Date.now()}`,
      riskScore: 0.75 + Math.random() * 0.2,
      riskLevel: Math.random() > 0.7 ? 'HIGH' : Math.random() > 0.4 ? 'MEDIUM' : 'LOW',
      estimatedVolume: 150 + Math.random() * 300,
      confidence: 0.85 + Math.random() * 0.1,
      preventiveActions: [
        'Install additional monitoring sensors',
        'Implement early warning system',
        'Restrict access to high-risk zones',
        'Schedule detailed geological survey'
      ],
      predictions: {
        immediate: { probability: 0.15 + Math.random() * 0.1, timeWindow: 'Next 24 hours' },
        shortTerm: { probability: 0.35 + Math.random() * 0.2, timeWindow: 'Next 7 days' },
        longTerm: { probability: 0.65 + Math.random() * 0.25, timeWindow: 'Next 30 days' }
      },
      visualizations: {
        heatmap: '/api/visualizations/heatmap',
        trajectory: '/api/visualizations/trajectory',
        riskZones: '/api/visualizations/risk-zones'
      },
      alertLevel: Math.floor(Math.random() * 5) + 1
    }

    setPredictionResult(mockResult)
    setIsProcessing(false)
    setPulseAnimation(false)
  }

  const getRiskColor = (level: string) => {
    switch (level) {
      case 'LOW': return 'from-green-400 to-emerald-500'
      case 'MEDIUM': return 'from-yellow-400 to-orange-500'
      case 'HIGH': return 'from-orange-500 to-red-500'
      case 'CRITICAL': return 'from-red-500 to-pink-600'
      default: return 'from-gray-400 to-gray-500'
    }
  }

  const getQualityColor = (quality: string) => {
    switch (quality) {
      case 'ULTRA': return 'text-purple-400 border-purple-400'
      case 'HIGH': return 'text-blue-400 border-blue-400'
      case 'MEDIUM': return 'text-yellow-400 border-yellow-400'
      case 'LOW': return 'text-red-400 border-red-400'
      default: return 'text-gray-400 border-gray-400'
    }
  }

  return (
    <div className="min-h-screen bg-slate-900">
      <Navbar />
      
      <div className="relative overflow-hidden">
        {/* Futuristic Background Effects */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          <div className="absolute top-0 left-1/4 w-96 h-96 bg-blue-500/10 rounded-full blur-3xl animate-pulse"></div>
          <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl animate-pulse animation-delay-2000"></div>
          <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-cyan-500/5 rounded-full blur-3xl animate-pulse animation-delay-4000"></div>
        </div>

        {/* Animated Grid Pattern */}
        <div className="absolute inset-0 opacity-20" style={{
          backgroundImage: `
            linear-gradient(rgba(59, 130, 246, 0.1) 1px, transparent 1px),
            linear-gradient(90deg, rgba(59, 130, 246, 0.1) 1px, transparent 1px)
          `,
          backgroundSize: '50px 50px'
        }}></div>

        <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {/* Header */}
          <div className="text-center mb-12">
            <h1 className={`text-5xl font-bold bg-gradient-to-r from-cyan-400 via-blue-500 to-purple-600 bg-clip-text text-transparent mb-4 ${glowEffect ? 'animate-pulse' : ''}`}>
              🚀 Quantum Rockfall Prediction Engine
            </h1>
            <p className="text-xl text-slate-300 max-w-3xl mx-auto">
              Harness the power of advanced AI, quantum computing, and multi-dimensional sensor fusion for unprecedented geological risk assessment accuracy
            </p>
          </div>

          {/* Analysis Mode Selector */}
          <div className="mb-8">
            <div className="bg-slate-800/50 backdrop-blur-xl rounded-3xl border border-slate-700/50 p-6">
              <h3 className="text-lg font-semibold text-white mb-4 flex items-center">
                <span className="text-2xl mr-2">⚙️</span>
                Analysis Configuration
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {[
                  { id: 'standard', name: 'Standard Analysis', desc: 'Traditional ML approach', time: '~5 min', icon: '📊' },
                  { id: 'advanced', name: 'Advanced AI', desc: 'Deep neural networks', time: '~8 min', icon: '🧠' },
                  { id: 'realtime', name: 'Quantum Processing', desc: 'Real-time quantum analysis', time: '~2 min', icon: '⚡' }
                ].map((mode) => (
                  <button
                    key={mode.id}
                    onClick={() => setAnalysisMode(mode.id as any)}
                    className={`p-4 rounded-2xl border-2 transition-all duration-300 ${
                      analysisMode === mode.id
                        ? 'border-cyan-400 bg-cyan-400/10 text-cyan-400'
                        : 'border-slate-600 bg-slate-700/30 text-slate-300 hover:border-slate-500'
                    }`}
                  >
                    <div className="text-2xl mb-2">{mode.icon}</div>
                    <div className="font-semibold">{mode.name}</div>
                    <div className="text-sm opacity-70">{mode.desc}</div>
                    <div className="text-xs mt-1 opacity-50">{mode.time}</div>
                  </button>
                ))}
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 xl:grid-cols-2 gap-8">
            {/* Left Panel - Data Input */}
            <div className="space-y-8">
              {/* Drone Image Upload */}
              <div className="bg-slate-800/50 backdrop-blur-xl rounded-3xl border border-slate-700/50 p-6">
                <h3 className="text-xl font-semibold text-white mb-6 flex items-center">
                  <span className="text-2xl mr-3">🛸</span>
                  Drone Data Repository
                </h3>
                
                <div className="border-2 border-dashed border-slate-600 rounded-2xl p-8 text-center hover:border-cyan-400 transition-colors duration-300 group">
                  <input
                    type="file"
                    multiple
                    accept="image/*"
                    onChange={(e) => e.target.files && handleImageUpload(e.target.files)}
                    className="hidden"
                    id="drone-upload"
                  />
                  <label htmlFor="drone-upload" className="cursor-pointer">
                    <div className="text-6xl mb-4 group-hover:scale-110 transition-transform duration-300">📷</div>
                    <p className="text-lg text-slate-300 mb-2">Drop your aerial imagery here</p>
                    <p className="text-sm text-slate-500">Support: DEM, Orthophoto, Point Cloud, Aerial Photos</p>
                  </label>
                </div>

                {/* Uploaded Images Grid */}
                {droneImages.length > 0 && (
                  <div className="mt-6 grid grid-cols-2 md:grid-cols-3 gap-4">
                    {droneImages.map((image) => (
                      <div key={image.id} className="group relative">
                        <div className="bg-slate-700/50 rounded-xl overflow-hidden border border-slate-600">
                          <img
                            src={image.preview}
                            alt="Drone image"
                            className="w-full h-24 object-cover"
                          />
                          <div className="p-3">
                            <div className={`text-xs px-2 py-1 rounded-full border ${getQualityColor(image.quality)} bg-slate-800`}>
                              {image.quality}
                            </div>
                            <div className="text-xs text-slate-400 mt-1">
                              {(image.size / 1024 / 1024).toFixed(1)} MB
                            </div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Site Selection */}
              <div className="bg-slate-800/50 backdrop-blur-xl rounded-3xl border border-slate-700/50 p-6">
                <h3 className="text-xl font-semibold text-white mb-6 flex items-center">
                  <span className="text-2xl mr-3">🌍</span>
                  Site Configuration
                </h3>
                
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-2">Target Site</label>
                    <select
                      value={selectedSite}
                      onChange={(e) => setSelectedSite(e.target.value)}
                      className="w-full px-4 py-3 bg-slate-700/50 border border-slate-600 rounded-xl text-white focus:ring-2 focus:ring-cyan-400 focus:border-transparent"
                    >
                      <option value="">Select monitoring site...</option>
                      <option value="alpha-7">Site Alpha-7 (Vancouver Island)</option>
                      <option value="beta-3">Site Beta-3 (Rocky Mountains)</option>
                      <option value="gamma-1">Site Gamma-1 (Coastal Range)</option>
                    </select>
                  </div>
                  
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-slate-300 mb-2">Benchmark ID</label>
                      <input
                        type="text"
                        placeholder="BM-2025-001"
                        className="w-full px-4 py-3 bg-slate-700/50 border border-slate-600 rounded-xl text-white focus:ring-2 focus:ring-cyan-400 focus:border-transparent"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-slate-300 mb-2">Mission ID</label>
                      <input
                        type="text"
                        placeholder="DM-SEP-2025-15"
                        className="w-full px-4 py-3 bg-slate-700/50 border border-slate-600 rounded-xl text-white focus:ring-2 focus:ring-cyan-400 focus:border-transparent"
                      />
                    </div>
                  </div>
                </div>
              </div>

              {/* Start Analysis Button */}
              <button
                onClick={startPrediction}
                disabled={isProcessing || droneImages.length === 0}
                className={`w-full py-6 px-8 rounded-2xl font-bold text-lg transition-all duration-300 transform ${
                  isProcessing
                    ? 'bg-slate-600 text-slate-400 cursor-not-allowed'
                    : 'bg-gradient-to-r from-cyan-500 via-blue-600 to-purple-600 text-white hover:from-cyan-400 hover:via-blue-500 hover:to-purple-500 hover:scale-105 shadow-2xl shadow-blue-500/25'
                } ${pulseAnimation ? 'animate-pulse' : ''}`}
              >
                {isProcessing ? (
                  <div className="flex items-center justify-center space-x-3">
                    <div className="w-6 h-6 border-2 border-slate-400 border-t-transparent rounded-full animate-spin"></div>
                    <span>Quantum Analysis in Progress...</span>
                  </div>
                ) : (
                  <div className="flex items-center justify-center space-x-3">
                    <span>🚀</span>
                    <span>Initialize Quantum Analysis</span>
                  </div>
                )}
              </button>
            </div>

            {/* Right Panel - Processing & Results */}
            <div className="space-y-8">
              {/* Processing Stages */}
              <div className="bg-slate-800/50 backdrop-blur-xl rounded-3xl border border-slate-700/50 p-6">
                <h3 className="text-xl font-semibold text-white mb-6 flex items-center">
                  <span className="text-2xl mr-3">⚡</span>
                  Processing Pipeline
                </h3>
                
                <div className="space-y-4">
                  {processingStages.map((stage, index) => (
                    <div
                      key={stage.id}
                      className={`p-4 rounded-2xl border transition-all duration-500 ${
                        stage.status === 'completed'
                          ? 'border-green-500/50 bg-green-500/10'
                          : stage.status === 'running'
                          ? 'border-cyan-500/50 bg-cyan-500/10 animate-pulse'
                          : stage.status === 'error'
                          ? 'border-red-500/50 bg-red-500/10'
                          : 'border-slate-600/50 bg-slate-700/30'
                      }`}
                    >
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center space-x-3">
                          <span className="text-2xl">{stage.icon}</span>
                          <div>
                            <div className="font-semibold text-white">{stage.name}</div>
                            <div className="text-sm text-slate-400">{stage.description}</div>
                          </div>
                        </div>
                        <div className="text-right">
                          <div className="text-sm text-slate-400">
                            {stage.status === 'running' ? `~${stage.estimatedTime}s` : ''}
                          </div>
                          <div className={`text-sm font-medium ${
                            stage.status === 'completed' ? 'text-green-400' :
                            stage.status === 'running' ? 'text-cyan-400' :
                            stage.status === 'error' ? 'text-red-400' : 'text-slate-500'
                          }`}>
                            {stage.status === 'completed' ? '✓ Complete' :
                             stage.status === 'running' ? 'Processing...' :
                             stage.status === 'error' ? '✗ Error' : 'Pending'}
                          </div>
                        </div>
                      </div>
                      {(stage.status === 'running' || stage.status === 'completed') && (
                        <div className="w-full bg-slate-700 rounded-full h-2">
                          <div
                            className={`h-2 rounded-full transition-all duration-300 ${
                              stage.status === 'completed' ? 'bg-green-500' : 'bg-cyan-500'
                            }`}
                            style={{ width: `${stage.progress}%` }}
                          ></div>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>

              {/* Prediction Results */}
              {predictionResult && (
                <div className="bg-slate-800/50 backdrop-blur-xl rounded-3xl border border-slate-700/50 p-6 animate-fade-in">
                  <h3 className="text-xl font-semibold text-white mb-6 flex items-center">
                    <span className="text-2xl mr-3">🎯</span>
                    Quantum Prediction Results
                  </h3>

                  {/* Risk Overview */}
                  <div className="grid grid-cols-2 gap-4 mb-6">
                    <div className={`p-4 rounded-2xl bg-gradient-to-r ${getRiskColor(predictionResult.riskLevel)} text-white`}>
                      <div className="text-2xl font-bold">{(predictionResult.riskScore * 100).toFixed(1)}%</div>
                      <div className="text-sm opacity-90">Risk Score</div>
                    </div>
                    <div className="p-4 rounded-2xl bg-slate-700/50 border border-slate-600">
                      <div className="text-2xl font-bold text-purple-400">{predictionResult.estimatedVolume.toFixed(0)} m³</div>
                      <div className="text-sm text-slate-400">Est. Volume</div>
                    </div>
                  </div>

                  {/* Time-based Predictions */}
                  <div className="space-y-3 mb-6">
                    <h4 className="text-lg font-semibold text-white">Temporal Risk Analysis</h4>
                    {Object.entries(predictionResult.predictions).map(([timeframe, data]) => (
                      <div key={timeframe} className="flex justify-between items-center p-3 bg-slate-700/30 rounded-xl">
                        <span className="text-slate-300 capitalize">{timeframe.replace(/([A-Z])/g, ' $1')}</span>
                        <div className="text-right">
                          <div className="text-white font-semibold">{(data.probability * 100).toFixed(1)}%</div>
                          <div className="text-xs text-slate-400">{data.timeWindow}</div>
                        </div>
                      </div>
                    ))}
                  </div>

                  {/* Confidence Meter */}
                  <div className="mb-6">
                    <div className="flex justify-between items-center mb-2">
                      <span className="text-slate-300">Confidence Level</span>
                      <span className="text-cyan-400 font-semibold">{(predictionResult.confidence * 100).toFixed(1)}%</span>
                    </div>
                    <div className="w-full bg-slate-700 rounded-full h-3">
                      <div
                        className="h-3 bg-gradient-to-r from-cyan-500 to-blue-500 rounded-full transition-all duration-1000"
                        style={{ width: `${predictionResult.confidence * 100}%` }}
                      ></div>
                    </div>
                  </div>

                  {/* Alert Level */}
                  <div className="flex items-center justify-center p-4 bg-gradient-to-r from-orange-500/20 to-red-500/20 rounded-2xl border border-orange-500/30">
                    <span className="text-2xl mr-3">🚨</span>
                    <span className="text-orange-300 font-semibold">
                      Alert Level {predictionResult.alertLevel}/5
                    </span>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Custom CSS for animations */}
      <style>
        {`
          @keyframes fade-in {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
          }
          
          .animate-fade-in {
            animation: fade-in 0.8s ease-out;
          }
          
          .animation-delay-2000 {
            animation-delay: 2s;
          }
          
          .animation-delay-4000 {
            animation-delay: 4s;
          }
        `}
      </style>
    </div>
  )
}

export default PredictionsPage