import React, { createContext, useContext, useState, useCallback, ReactNode } from 'react'

/**
 * Data Flow Context for managing data transfer between pages
 * Device Page → Dashboard → Predictions Page
 */

export interface DeviceImportData {
  csvFiles: FileData[]
  jsonFiles: FileData[]
  imageFiles?: FileData[]
  timestamp: Date
  source: 'device-upload' | 'api-import' | 'manual-entry'
  totalRecords: number
  deviceIds: string[]
  dataTypes: string[]
  qualityMetrics?: {
    completeness: number
    accuracy: number
    consistency: number
    timeliness: number
  }
}

export interface FileData {
  id: string
  name: string
  size: number
  type: string
  content?: any
  preview?: string
  lastModified: Date
}

export interface ProcessedData {
  cleanedData: any[]
  combinedData: any[]
  features: string[]
  timeRange: {
    start: Date
    end: Date
  }
  sampleCount: number
  processingMetadata: {
    cleaningSteps: string[]
    combinationMethod: string
    qualityScore: number
  }
}

export interface PredictionResults {
  id: string
  riskScore: number
  riskLevel: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL'
  estimatedVolume: number
  confidence: number
  timestamp: string
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
  siteId?: string
  siteName?: string
}

export interface DataFlowState {
  // Import stage
  importedData: DeviceImportData | null
  hasImportedData: boolean
  
  // Processing stage
  isProcessing: boolean
  processedData: ProcessedData | null
  
  // Pipeline stage
  pipelineActive: boolean
  pipelineResults: any | null
  
  // Prediction results
  predictionResults: PredictionResults | null
  
  // Flow control
  currentStep: 'import' | 'processing' | 'prediction' | 'dashboard' | 'completed'
  dataPassedToPredictions: boolean
}

interface DataFlowContextType {
  state: DataFlowState
  
  // Actions
  setImportedData: (data: DeviceImportData) => void
  clearImportedData: () => void
  setProcessedData: (data: ProcessedData) => void
  setPipelineResults: (results: any) => void
  setPredictionResults: (results: PredictionResults) => void
  setCurrentStep: (step: DataFlowState['currentStep']) => void
  markDataPassedToPredictions: () => void
  
  // Utilities
  getDataForPredictions: () => { imported: DeviceImportData | null; processed: ProcessedData | null }
  hasDataReadyForPredictions: () => boolean
  resetDataFlow: () => void
}

const initialState: DataFlowState = {
  importedData: null,
  hasImportedData: false,
  isProcessing: false,
  processedData: null,
  pipelineActive: false,
  pipelineResults: null,
  predictionResults: null,
  currentStep: 'import',
  dataPassedToPredictions: false
}

const DataFlowContext = createContext<DataFlowContextType | undefined>(undefined)

export const DataFlowProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [state, setState] = useState<DataFlowState>(initialState)

  const setImportedData = useCallback((data: DeviceImportData) => {
    setState(prev => ({
      ...prev,
      importedData: data,
      hasImportedData: true,
      currentStep: 'processing'
    }))
    
    // Store in localStorage for cross-page access
    localStorage.setItem('deviceImportedData', JSON.stringify({
      ...data,
      timestamp: data.timestamp.toISOString()
    }))
  }, [])

  const clearImportedData = useCallback(() => {
    setState(prev => ({
      ...prev,
      importedData: null,
      hasImportedData: false
    }))
    localStorage.removeItem('deviceImportedData')
  }, [])

  const setProcessedData = useCallback((data: ProcessedData) => {
    setState(prev => ({
      ...prev,
      processedData: data,
      isProcessing: false,
      currentStep: 'prediction'
    }))
  }, [])

  const setPipelineResults = useCallback((results: any) => {
    setState(prev => ({
      ...prev,
      pipelineResults: results,
      pipelineActive: false,
      currentStep: 'dashboard'
    }))
  }, [])

  const setPredictionResults = useCallback((results: PredictionResults) => {
    setState(prev => ({
      ...prev,
      predictionResults: results,
      currentStep: 'completed'
    }))
    // Also save to localStorage for persistence
    localStorage.setItem('predictionResults', JSON.stringify(results))
  }, [])

  const setCurrentStep = useCallback((step: DataFlowState['currentStep']) => {
    setState(prev => ({ ...prev, currentStep: step }))
  }, [])

  const markDataPassedToPredictions = useCallback(() => {
    setState(prev => ({
      ...prev,
      dataPassedToPredictions: true,
      currentStep: 'prediction'
    }))
  }, [])

  const getDataForPredictions = useCallback(() => {
    return {
      imported: state.importedData,
      processed: state.processedData
    }
  }, [state.importedData, state.processedData])

  const hasDataReadyForPredictions = useCallback(() => {
    return state.hasImportedData && state.importedData !== null
  }, [state.hasImportedData, state.importedData])

  const resetDataFlow = useCallback(() => {
    setState(initialState)
    localStorage.removeItem('deviceImportedData')
    localStorage.removeItem('processedData')
    localStorage.removeItem('pipelineResults')
  }, [])

  const contextValue: DataFlowContextType = {
    state,
    setImportedData,
    clearImportedData,
    setProcessedData,
    setPipelineResults,
    setPredictionResults,
    setCurrentStep,
    markDataPassedToPredictions,
    getDataForPredictions,
    hasDataReadyForPredictions,
    resetDataFlow
  }

  return (
    <DataFlowContext.Provider value={contextValue}>
      {children}
    </DataFlowContext.Provider>
  )
}

export const useDataFlow = (): DataFlowContextType => {
  const context = useContext(DataFlowContext)
  if (!context) {
    throw new Error('useDataFlow must be used within a DataFlowProvider')
  }
  return context
}

// Utility function to create mock imported data
export const createMockImportedData = (recordCount: number = 10000): DeviceImportData => {
  return {
    csvFiles: [
      {
        id: 'csv1',
        name: 'sensor_data.csv',
        size: recordCount * 50, // roughly 50 bytes per record
        type: 'text/csv',
        lastModified: new Date(),
        preview: 'timestamp,device_id,pore_pressure,displacement,temperature...'
      },
      {
        id: 'csv2',
        name: 'weather_data.csv',
        size: recordCount * 30,
        type: 'text/csv',
        lastModified: new Date(),
        preview: 'timestamp,temperature,humidity,rainfall,wind_speed...'
      }
    ],
    jsonFiles: [
      {
        id: 'json1',
        name: 'device_config.json',
        size: 2048,
        type: 'application/json',
        lastModified: new Date(),
        content: { devices: ['SEIS_001', 'PORE_001', 'TEMP_001'] }
      }
    ],
    timestamp: new Date(),
    source: 'device-upload',
    totalRecords: recordCount,
    deviceIds: ['SEIS_001', 'PORE_001', 'TEMP_001', 'RAIN_001'],
    dataTypes: ['pore_pressure', 'displacement', 'temperature', 'rainfall', 'acceleration'],
    qualityMetrics: {
      completeness: 0.95 + Math.random() * 0.04,
      accuracy: 0.92 + Math.random() * 0.06,
      consistency: 0.89 + Math.random() * 0.08,
      timeliness: 0.97 + Math.random() * 0.02
    }
  }
}

export default DataFlowContext