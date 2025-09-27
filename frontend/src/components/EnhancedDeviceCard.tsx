import React, { useState, useRef } from 'react'
import { Device, deviceTypeConfigs } from '../types/devices'
import { useDataFlow } from '../contexts/DataFlowContext'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
} from 'chart.js'
import { Line } from 'react-chartjs-2'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
)

interface EnhancedDeviceCardProps {
  device: Device
  onShowDetails: (device: Device) => void
  onDeleteDevice: (deviceId: string) => void
  onUpdateDevice: (device: Device) => void
}

interface ChartData {
  labels: string[]
  datasets: Array<{
    label: string
    data: number[]
    borderColor: string
    backgroundColor: string
    tension?: number
  }>
}

export const EnhancedDeviceCard: React.FC<EnhancedDeviceCardProps> = ({
  device,
  onShowDetails,
  onDeleteDevice,
  onUpdateDevice
}) => {
  const [showConfig, setShowConfig] = useState(false)
  const [showChart, setShowChart] = useState(false)
  const [apiTesting, setApiTesting] = useState(false)
  const [csvImporting, setCsvImporting] = useState(false)
  const [chartData, setChartData] = useState<ChartData | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const { setImportedData } = useDataFlow()

  const config = deviceTypeConfigs[device.type as keyof typeof deviceTypeConfigs] || {
    icon: '📱',
    color: 'gray',
    category: 'Unknown',
    description: 'Unknown device type'
  }
  
  // Get file format info based on device type
  const getFileFormatInfo = () => {
    switch (device.type) {
      case 'lidar':
        return {
          accept: '.las,.laz',
          buttonText: 'Import LAS',
          description: 'LiDAR point cloud data'
        }
      case 'drone-imagery':
        return {
          accept: '.png,.jpg,.jpeg',
          buttonText: 'Import Images',
          description: 'Drone imagery files'
        }
      default:
        return {
          accept: '.csv',
          buttonText: 'Import CSV',
          description: 'CSV data files'
        }
    }
  }
  
  const fileFormatInfo = getFileFormatInfo()
  
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'online':
      case 'active': 
        return 'text-emerald-600 bg-emerald-100 border-emerald-200'
      case 'offline':
      case 'inactive': 
        return 'text-red-600 bg-red-100 border-red-200'
      case 'maintenance': 
        return 'text-yellow-600 bg-yellow-100 border-yellow-200'
      case 'error': 
        return 'text-orange-600 bg-orange-100 border-orange-200'
      default: 
        return 'text-gray-600 bg-gray-100 border-gray-200'
    }
  }



  const handleApiTest = async () => {
    setApiTesting(true)
    try {
      // Simulate API test
      await new Promise(resolve => setTimeout(resolve, 2000))
      alert(`API Test for ${device.name}: Connection successful!`)
    } catch (error) {
      alert(`API Test for ${device.name}: Connection failed!`)
    } finally {
      setApiTesting(false)
    }
  }

  const handleFileImport = () => {
    fileInputRef.current?.click()
  }

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files
    if (files && files.length > 0) {
      setCsvImporting(true)
      
      const processFiles = async () => {
        try {
          let processedData: any[] = []
          let fileArray: any[] = []
          
          for (let i = 0; i < files.length; i++) {
            const file = files[i]
            const fileExt = file.name.split('.').pop()?.toLowerCase()
            
            if (device.type === 'lidar' && (fileExt === 'las' || fileExt === 'laz')) {
              // Handle LAS/LAZ files for LiDAR
              const mockLidarData = {
                timestamp: new Date().toISOString(),
                coordinates: `${Math.random() * 1000},${Math.random() * 1000},${Math.random() * 100}`,
                demElevation: Math.random() * 2000 + 1000,
                volumeChange: (Math.random() - 0.5) * 1000,
                areaId: `area_${Math.floor(Math.random() * 10) + 1}`,
                device_id: device.id
              }
              processedData.push(mockLidarData)
              fileArray.push({
                id: `las-${Date.now()}-${i}`,
                name: file.name,
                size: file.size,
                type: file.type,
                content: [mockLidarData],
                lastModified: new Date(file.lastModified)
              })
              
            } else if (device.type === 'drone-imagery' && ['png', 'jpg', 'jpeg'].includes(fileExt || '')) {
              // Handle image files for drone imagery
              const reader = new FileReader()
              await new Promise((resolve) => {
                reader.onload = (e) => {
                  const imageData = {
                    timestamp: new Date().toISOString(),
                    imageUrl: e.target?.result as string,
                    crackDetection: Math.random() > 0.7,
                    imageQuality: Math.random() * 0.3 + 0.7,
                    fileName: file.name,
                    device_id: device.id
                  }
                  processedData.push(imageData)
                  fileArray.push({
                    id: `img-${Date.now()}-${i}`,
                    name: file.name,
                    size: file.size,
                    type: file.type,
                    content: [imageData],
                    lastModified: new Date(file.lastModified)
                  })
                  resolve(null)
                }
                reader.readAsDataURL(file)
              })
              
            } else if (fileExt === 'csv') {
              // Handle CSV files
              const reader = new FileReader()
              await new Promise((resolve) => {
                reader.onload = (e) => {
                  const csvText = e.target?.result as string
                  const lines = csvText.split('\n')
                  const headers = lines[0].split(',')
                  const data = lines.slice(1).filter(line => line.trim()).map(line => {
                    const values = line.split(',')
                    const row: any = {}
                    headers.forEach((header, index) => {
                      row[header.trim()] = values[index]?.trim() || ''
                    })
                    return row
                  })
                  processedData = processedData.concat(data)
                  fileArray.push({
                    id: `csv-${Date.now()}-${i}`,
                    name: file.name,
                    size: file.size,
                    type: file.type,
                    content: data,
                    lastModified: new Date(file.lastModified)
                  })
                  resolve(null)
                }
                reader.readAsText(file)
              })
            }
          }

          // Create import data structure
          const importData = {
            csvFiles: device.type === 'drone-imagery' ? [] : fileArray,
            imageFiles: device.type === 'drone-imagery' ? fileArray : [],
            jsonFiles: [],
            timestamp: new Date(),
            source: 'device-upload' as const,
            totalRecords: processedData.length,
            deviceIds: [...new Set(processedData.map(row => row.device_id))],
            dataTypes: device.type === 'lidar' ? ['coordinates', 'demElevation', 'volumeChange'] : 
                      device.type === 'drone-imagery' ? ['imageUrl', 'crackDetection', 'imageQuality'] : 
                      Object.keys(processedData[0] || {}),
            qualityMetrics: {
              completeness: 95,
              accuracy: 98,
              consistency: 94,
              timeliness: 97
            }
          }

          // Transfer to DataFlow context for Predictions page
          setImportedData(importData)

          // Generate chart data for device card display
          if (processedData.length > 0) {
            const timestamps = processedData.map(row => new Date(row.timestamp).toLocaleTimeString())
            const values = processedData.map(row => {
              // Get relevant numeric value based on device type
              switch (device.type) {
                case 'gb-insar': return parseFloat(row.displacement) || 0
                case 'lidar': return parseFloat(row.volumeChange) || 0
                case 'drone-imagery': return parseFloat(row.imageQuality) || 0
                case 'borehole-inclinometer': return parseFloat(row.displacementAtDepth) || 0
                case 'piezometer': return parseFloat(row.porePressure) || 0
                case 'weather-station': return parseFloat(row.temperature) || 0
                case 'geophone': return parseFloat(row.vibrationAmplitude) || 0
                default: return Math.random() * 100
              }
            })

            const mockChartData: ChartData = {
              labels: timestamps.slice(-24), // Show last 24 readings
              datasets: [
                {
                  label: `${device.name} Readings`,
                  data: values.slice(-24),
                  borderColor: 'rgb(59, 130, 246)',
                  backgroundColor: 'rgba(59, 130, 246, 0.1)',
                  tension: 0.4
                }
              ]
            }
            
            setChartData(mockChartData)
          }
          
          setCsvImporting(false)
          
          // Success message based on device type
          const fileTypeText = device.type === 'lidar' ? 'LAS point cloud' : 
                              device.type === 'drone-imagery' ? 'image' : 'CSV'
          alert(`✅ ${fileTypeText} data imported successfully for ${device.name}!\n📊 ${processedData.length} records processed\n🔄 Data automatically transferred to Predictions page`)
          
        } catch (error) {
          setCsvImporting(false)
          alert(`❌ Error processing files: ${error}`)
        }
      }
      
      processFiles()
          
    }
  }

  const handleToggleEnabled = () => {
    const updatedDevice = { ...device, enabled: !device.enabled }
    onUpdateDevice(updatedDevice)
  }

  const handleToggleCsvEnabled = () => {
    const updatedDevice = { ...device, csvImportEnabled: !device.csvImportEnabled }
    onUpdateDevice(updatedDevice)
  }

  const handleShowChart = () => {
    if (!chartData) {
      // Generate mock chart data if none exists
      const mockChartData: ChartData = {
        labels: Array.from({ length: 24 }, (_, i) => `${23 - i}h ago`),
        datasets: [
          {
            label: 'Battery Level',
            data: Array.from({ length: 24 }, () => Math.random() * 30 + 70),
            borderColor: 'rgb(34, 197, 94)',
            backgroundColor: 'rgba(34, 197, 94, 0.1)',
            tension: 0.4
          },
          {
            label: 'Signal Strength',
            data: Array.from({ length: 24 }, () => Math.random() * 40 + 60),
            borderColor: 'rgb(59, 130, 246)',
            backgroundColor: 'rgba(59, 130, 246, 0.1)',
            tension: 0.4
          }
        ]
      }
      setChartData(mockChartData)
    }
    setShowChart(!showChart)
  }

  const handleDeleteDevice = () => {
    if (window.confirm(`Are you sure you want to delete ${device.name}?`)) {
      onDeleteDevice(device.id)
    }
  }

  const handleSaveConfig = (configData: any) => {
    const updatedDevice = { ...device, configuration: { ...device.configuration, ...configData } }
    onUpdateDevice(updatedDevice)
    setShowConfig(false)
    alert('Configuration saved successfully!')
  }

  return (
    <div className="bg-white rounded-2xl shadow-lg border border-gray-200 p-6 transition-all duration-300 hover:shadow-xl hover:border-blue-300">
      <input
        type="file"
        ref={fileInputRef}
        onChange={handleFileChange}
        accept={fileFormatInfo.accept}
        multiple={device.type === 'drone-imagery'}  
        className="hidden"
      />
      
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center space-x-3">
          <div className="p-2 bg-blue-100 rounded-lg">
            <span className="text-2xl">{config.icon}</span>
          </div>
          <div>
            <h3 className="font-semibold text-gray-900 text-lg">{device.name}</h3>
            <p className="text-sm text-gray-600">{device.category}</p>
          </div>
        </div>
        
        <span className={`px-3 py-1 rounded-full text-xs font-medium border ${getStatusColor(device.status)}`}>
          {device.status.charAt(0).toUpperCase() + device.status.slice(1)}
        </span>
      </div>



      {/* Action Buttons */}
      <div className="grid grid-cols-2 gap-2 mb-4">
        <button
          onClick={handleFileImport}
          disabled={csvImporting}
          className="flex items-center justify-center space-x-1 px-3 py-2 bg-green-100 text-green-700 rounded-lg hover:bg-green-200 transition-colors disabled:opacity-50"
        >
          {csvImporting ? (
            <div className="w-4 h-4 border-2 border-green-600 border-t-transparent rounded-full animate-spin"></div>
          ) : (
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M9 12l2 2 4-4" />
            </svg>
          )}
          <span className="text-xs">{fileFormatInfo.buttonText}</span>
        </button>

        <button
          onClick={handleApiTest}
          disabled={apiTesting}
          className="flex items-center justify-center space-x-1 px-3 py-2 bg-blue-100 text-blue-700 rounded-lg hover:bg-blue-200 transition-colors disabled:opacity-50"
        >
          {apiTesting ? (
            <div className="w-4 h-4 border-2 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
          ) : (
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
          )}
          <span className="text-xs">API Test</span>
        </button>

        <button
          onClick={() => setShowConfig(true)}
          className="flex items-center justify-center space-x-1 px-3 py-2 bg-purple-100 text-purple-700 rounded-lg hover:bg-purple-200 transition-colors"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
          </svg>
          <span className="text-xs">Config</span>
        </button>

        <button
          onClick={handleShowChart}
          className="flex items-center justify-center space-x-1 px-3 py-2 bg-indigo-100 text-indigo-700 rounded-lg hover:bg-indigo-200 transition-colors"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
          </svg>
          <span className="text-xs">Chart</span>
        </button>
      </div>

      {/* Toggle Switches */}
      <div className="flex items-center justify-between py-2 border-t border-gray-200">
        <div className="flex items-center space-x-2">
          <span className="text-xs text-gray-600">API:</span>
          <label className="relative inline-flex items-center cursor-pointer">
            <input
              type="checkbox"
              checked={device.enabled}
              onChange={handleToggleEnabled}
              className="sr-only peer"
            />
            <div className="w-9 h-5 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-blue-600"></div>
          </label>
        </div>

        <div className="flex items-center space-x-2">
          <span className="text-xs text-gray-600">{device.type === 'lidar' ? 'LAS:' : device.type === 'drone-imagery' ? 'Images:' : 'CSV:'}:</span>
          <label className="relative inline-flex items-center cursor-pointer">
            <input
              type="checkbox"
              checked={device.csvImportEnabled}
              onChange={handleToggleCsvEnabled}
              className="sr-only peer"
            />
            <div className="w-9 h-5 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-blue-600"></div>
          </label>
        </div>
      </div>

      {/* Bottom Actions */}
      <div className="flex items-center justify-between pt-4 border-t border-gray-200">
        <button
          onClick={() => onShowDetails(device)}
          className="text-blue-600 hover:text-blue-800 text-sm font-medium"
        >
          View Details
        </button>
        
        <button
          onClick={handleDeleteDevice}
          className="text-red-600 hover:text-red-800 text-sm font-medium"
        >
          Delete
        </button>
      </div>

      {/* Chart Modal */}
      {showChart && chartData && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" onClick={() => setShowChart(false)}>
          <div className="bg-white rounded-lg p-6 max-w-4xl w-full mx-4 max-h-[80vh] overflow-auto" onClick={(e) => e.stopPropagation()}>
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900">{device.name} - Data Visualization</h3>
              <button
                onClick={() => setShowChart(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            <div className="h-96">
              <Line
                data={chartData}
                options={{
                  responsive: true,
                  maintainAspectRatio: false,
                  plugins: {
                    legend: {
                      position: 'top' as const,
                    },
                    title: {
                      display: true,
                      text: `${device.name} - 24 Hour Data`,
                    },
                  },
                  scales: {
                    y: {
                      beginAtZero: true,
                    },
                  },
                }}
              />
            </div>
          </div>
        </div>
      )}

      {/* Configuration Modal */}
      {showConfig && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" onClick={() => setShowConfig(false)}>
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4" onClick={(e) => e.stopPropagation()}>
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900">Device Configuration</h3>
              <button
                onClick={() => setShowConfig(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            
            <form onSubmit={(e) => {
              e.preventDefault()
              const formData = new FormData(e.currentTarget)
              const configData = {
                apiUrl: formData.get('apiUrl'),
                authToken: formData.get('authToken'),
                samplingRate: Number(formData.get('samplingRate')),
                threshold: Number(formData.get('threshold')),
                alertEnabled: formData.get('alertEnabled') === 'on'
              }
              handleSaveConfig(configData)
            }}>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">API URL</label>
                  <input
                    type="url"
                    name="apiUrl"
                    defaultValue={device.configuration?.apiUrl || ''}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="https://api.device.com/endpoint"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Auth Token</label>
                  <input
                    type="text"
                    name="authToken"
                    defaultValue={device.configuration?.authToken || ''}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Bearer token or API key"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Sampling Rate (Hz)</label>
                  <input
                    type="number"
                    name="samplingRate"
                    defaultValue={device.configuration?.samplingRate || 100}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    min="1"
                    max="1000"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Alert Threshold</label>
                  <input
                    type="number"
                    name="threshold"
                    step="0.1"
                    defaultValue={device.configuration?.threshold || 0.8}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    min="0"
                    max="1"
                  />
                </div>
                
                <div className="flex items-center">
                  <input
                    type="checkbox"
                    name="alertEnabled"
                    defaultChecked={device.configuration?.alertEnabled || false}
                    className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                  />
                  <label className="ml-2 block text-sm text-gray-900">
                    Enable Alerts
                  </label>
                </div>
              </div>
              
              <div className="flex justify-end space-x-3 mt-6">
                <button
                  type="button"
                  onClick={() => setShowConfig(false)}
                  className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-md"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-md"
                >
                  Save Config
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}