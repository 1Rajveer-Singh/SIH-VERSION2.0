import React, { useState, useEffect, useCallback, useRef } from 'react'
import Navbar from '../components/Navbar'
import { Line, Bar, Doughnut, Scatter } from 'react-chartjs-2'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js'

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler
)

// Report Data Interfaces
interface ReportFilter {
  predictionId?: string
  siteId?: string
  startDate?: string
  endDate?: string
  droneMissionId?: string
}

interface DroneAnalysisData {
  images: {
    id: string
    filename: string
    type: string
    annotations: string[]
    processed: boolean
  }[]
  demData: {
    elevationRange: { min: number; max: number }
    slopeDistribution: number[]
    roughnessMap: string
    benchGeometry: {
      height: number
      width: number
      angle: number
    }
  }
  crackAnalysis: {
    totalCracks: number
    crackDensity: number
    severityDistribution: Record<string, number>
    annotatedImages: string[]
  }
}

interface SensorReportData {
  summary: {
    deviceCount: number
    readingsCount: number
    timeRange: { start: string; end: string }
    dataQuality: string
  }
  readings: {
    deviceId: string
    timestamp: string
    porePressure?: number
    displacement?: number
    acceleration?: number
    rmr?: number
    ucs?: number
    rainfall?: number
    temperature?: number
    seismicActivity?: number
  }[]
  trends: {
    porePressure: { timestamps: string[]; values: number[] }
    temperature: { timestamps: string[]; values: number[] }
    seismicActivity: { timestamps: string[]; values: number[] }
    displacement: { timestamps: string[]; values: number[] }
  }
}

interface StepwiseAnalysisData {
  stages: {
    id: string
    name: string
    status: string
    progress: number
    output: any
    processingTime: number
  }[]
  intermediateResults: {
    visionModelConfidence: number
    sensorModelConfidence: number
    fusionConfidence: number
    featureImportance: Record<string, number>
  }
  riskEvolution: {
    stage: string
    riskScore: number
    confidence: number
  }[]
}

interface FinalPredictionData {
  id: string
  timestamp: string
  riskScore: number
  riskLevel: string
  confidence: number
  estimatedVolume: number
  landingZone: {
    coordinates: number[][]
    area: number
  }
  presentTime: {
    probability: number
    timestamp: string
  }
  shortTermFuture: {
    probability: number
    timeWindow: number
    predictedTime: string
  }
  featureImportance: Record<string, number>
  preventiveActions: string[]
}

interface ReportData {
  metadata: {
    reportId: string
    siteId: string
    siteName: string
    benchId: string
    droneMissionId: string
    timestamp: string
    analysisId: string
  }
  droneAnalysis: DroneAnalysisData
  sensorData: SensorReportData
  stepwiseAnalysis: StepwiseAnalysisData
  finalPrediction: FinalPredictionData
  summary: {
    keyFindings: string[]
    recommendations: string[]
    overallAssessment: string
  }
}

function ReportPage() {
  // State management
  const [reportData, setReportData] = useState<ReportData | null>(null)
  const [filters, setFilters] = useState<ReportFilter>({})
  const [isLoading, setIsLoading] = useState(false)
  const [availablePredictions, setAvailablePredictions] = useState<any[]>([])
  const [sites, setSites] = useState<any[]>([])
  const [isExporting, setIsExporting] = useState(false)
  const reportRef = useRef<HTMLDivElement>(null)

  // Load available data on component mount
  useEffect(() => {
    fetchAvailablePredictions()
    fetchSites()
  }, [])

  const fetchAvailablePredictions = async () => {
    try {
      const response = await fetch('/api/predictions', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      })
      if (response.ok) {
        const data = await response.json()
        setAvailablePredictions(data)
      }
    } catch (error) {
      console.error('Error fetching predictions:', error)
    }
  }

  const fetchSites = async () => {
    try {
      const response = await fetch('/api/sites', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      })
      if (response.ok) {
        const data = await response.json()
        setSites(data)
      }
    } catch (error) {
      console.error('Error fetching sites:', error)
    }
  }

  const fetchReportData = async () => {
    if (!filters.predictionId) {
      alert('Please select a prediction to generate report')
      return
    }

    setIsLoading(true)
    try {
      const response = await fetch(`/api/predictions/enhanced/report/${filters.predictionId}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      })
      if (response.ok) {
        const data = await response.json()
        setReportData(data)
      } else {
        alert('Failed to fetch report data')
      }
    } catch (error) {
      console.error('Error fetching report data:', error)
      alert('Error loading report data')
    } finally {
      setIsLoading(false)
    }
  }

  const exportReport = async (format: 'pdf' | 'csv' | 'excel' | 'json') => {
    if (!reportData) {
      alert('No report data available for export')
      return
    }

    setIsExporting(true)
    try {
      let blob: Blob
      let filename: string

      switch (format) {
        case 'pdf':
          blob = await exportToPDF()
          filename = `rockfall_report_${reportData.metadata.reportId}.pdf`
          break
        case 'csv':
          blob = await exportToCSV()
          filename = `rockfall_report_${reportData.metadata.reportId}.csv`
          break
        case 'excel':
          blob = await exportToExcel()
          filename = `rockfall_report_${reportData.metadata.reportId}.xlsx`
          break
        case 'json':
          blob = exportToJSON()
          filename = `rockfall_report_${reportData.metadata.reportId}.json`
          break
        default:
          throw new Error('Unsupported export format')
      }

      // Download file
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = filename
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)

    } catch (error) {
      console.error(`Error exporting to ${format}:`, error)
      alert(`Failed to export to ${format.toUpperCase()}`)
    } finally {
      setIsExporting(false)
    }
  }

  const exportToPDF = async (): Promise<Blob> => {
    // Import libraries dynamically
    const jsPDF = (await import('jspdf')).default
    const html2canvas = (await import('html2canvas')).default

    if (!reportRef.current) throw new Error('Report content not found')

    // Create PDF
    const pdf = new jsPDF('p', 'mm', 'a4')
    
    // Add title page
    pdf.setFontSize(20)
    pdf.text('Rockfall Prediction Report', 20, 30)
    pdf.setFontSize(12)
    pdf.text(`Site: ${reportData!.metadata.siteName}`, 20, 50)
    pdf.text(`Report ID: ${reportData!.metadata.reportId}`, 20, 60)
    pdf.text(`Generated: ${new Date().toLocaleString()}`, 20, 70)

    // Capture charts and content
    const canvas = await html2canvas(reportRef.current, {
      scale: 2,
      useCORS: true,
      allowTaint: true
    })

    const imgData = canvas.toDataURL('image/png')
    const imgProps = pdf.getImageProperties(imgData)
    const pdfWidth = pdf.internal.pageSize.getWidth()
    const pdfHeight = (imgProps.height * pdfWidth) / imgProps.width

    let heightLeft = pdfHeight
    let position = 90

    // Add image to PDF with page breaks
    pdf.addImage(imgData, 'PNG', 10, position, pdfWidth - 20, pdfHeight)
    heightLeft -= pdf.internal.pageSize.getHeight() - position

    while (heightLeft >= 0) {
      position = heightLeft - pdfHeight + 10
      pdf.addPage()
      pdf.addImage(imgData, 'PNG', 10, position, pdfWidth - 20, pdfHeight)
      heightLeft -= pdf.internal.pageSize.getHeight()
    }

    return new Blob([pdf.output('blob')], { type: 'application/pdf' })
  }

  const exportToCSV = async (): Promise<Blob> => {
    if (!reportData) throw new Error('No report data')

    let csvContent = 'Rockfall Prediction Report - Raw Data\n\n'

    // Metadata
    csvContent += 'METADATA\n'
    csvContent += `Report ID,${reportData.metadata.reportId}\n`
    csvContent += `Site,${reportData.metadata.siteName}\n`
    csvContent += `Bench ID,${reportData.metadata.benchId}\n`
    csvContent += `Timestamp,${reportData.metadata.timestamp}\n\n`

    // Drone Analysis
    csvContent += 'DRONE IMAGES\n'
    csvContent += 'Filename,Type,Processed,Annotations\n'
    reportData.droneAnalysis.images.forEach(img => {
      csvContent += `${img.filename},${img.type},${img.processed},${img.annotations.join(';')}\n`
    })

    csvContent += '\nDEM DATA\n'
    csvContent += `Min Elevation,${reportData.droneAnalysis.demData.elevationRange.min}\n`
    csvContent += `Max Elevation,${reportData.droneAnalysis.demData.elevationRange.max}\n`
    csvContent += `Bench Height,${reportData.droneAnalysis.demData.benchGeometry.height}\n`
    csvContent += `Bench Width,${reportData.droneAnalysis.demData.benchGeometry.width}\n`
    csvContent += `Slope Angle,${reportData.droneAnalysis.demData.benchGeometry.angle}\n\n`

    // Sensor Data
    csvContent += 'SENSOR READINGS\n'
    csvContent += 'Device ID,Timestamp,Pore Pressure,Displacement,Acceleration,Temperature,Seismic Activity\n'
    reportData.sensorData.readings.forEach(reading => {
      csvContent += `${reading.deviceId},${reading.timestamp},${reading.porePressure || ''},${reading.displacement || ''},${reading.acceleration || ''},${reading.temperature || ''},${reading.seismicActivity || ''}\n`
    })

    // Final Prediction
    csvContent += '\nFINAL PREDICTION\n'
    csvContent += `Risk Score,${reportData.finalPrediction.riskScore}\n`
    csvContent += `Risk Level,${reportData.finalPrediction.riskLevel}\n`
    csvContent += `Confidence,${reportData.finalPrediction.confidence}\n`
    csvContent += `Estimated Volume,${reportData.finalPrediction.estimatedVolume}\n`
    csvContent += `Landing Zone Area,${reportData.finalPrediction.landingZone.area}\n`

    // Feature Importance
    csvContent += '\nFEATURE IMPORTANCE\n'
    csvContent += 'Feature,Importance\n'
    Object.entries(reportData.finalPrediction.featureImportance).forEach(([feature, importance]) => {
      csvContent += `${feature},${importance}\n`
    })

    return new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
  }

  const exportToExcel = async (): Promise<Blob> => {
    const XLSX = await import('xlsx')
    
    if (!reportData) throw new Error('No report data')

    const workbook = XLSX.utils.book_new()

    // Metadata Sheet
    const metadataWS = XLSX.utils.json_to_sheet([reportData.metadata])
    XLSX.utils.book_append_sheet(workbook, metadataWS, 'Metadata')

    // Drone Images Sheet
    const droneWS = XLSX.utils.json_to_sheet(reportData.droneAnalysis.images)
    XLSX.utils.book_append_sheet(workbook, droneWS, 'Drone Images')

    // DEM Data Sheet
    const demData = [
      { Parameter: 'Min Elevation', Value: reportData.droneAnalysis.demData.elevationRange.min },
      { Parameter: 'Max Elevation', Value: reportData.droneAnalysis.demData.elevationRange.max },
      { Parameter: 'Bench Height', Value: reportData.droneAnalysis.demData.benchGeometry.height },
      { Parameter: 'Bench Width', Value: reportData.droneAnalysis.demData.benchGeometry.width },
      { Parameter: 'Slope Angle', Value: reportData.droneAnalysis.demData.benchGeometry.angle }
    ]
    const demWS = XLSX.utils.json_to_sheet(demData)
    XLSX.utils.book_append_sheet(workbook, demWS, 'DEM Data')

    // Sensor Readings Sheet
    const sensorWS = XLSX.utils.json_to_sheet(reportData.sensorData.readings)
    XLSX.utils.book_append_sheet(workbook, sensorWS, 'Sensor Readings')

    // Stepwise Analysis Sheet
    const stepsWS = XLSX.utils.json_to_sheet(reportData.stepwiseAnalysis.stages)
    XLSX.utils.book_append_sheet(workbook, stepsWS, 'Processing Stages')

    // Feature Importance Sheet
    const featureData = Object.entries(reportData.finalPrediction.featureImportance).map(([feature, importance]) => ({
      Feature: feature,
      Importance: importance
    }))
    const featureWS = XLSX.utils.json_to_sheet(featureData)
    XLSX.utils.book_append_sheet(workbook, featureWS, 'Feature Importance')

    // Final Prediction Sheet
    const predictionData = [{
      'Risk Score': reportData.finalPrediction.riskScore,
      'Risk Level': reportData.finalPrediction.riskLevel,
      'Confidence': reportData.finalPrediction.confidence,
      'Estimated Volume': reportData.finalPrediction.estimatedVolume,
      'Landing Zone Area': reportData.finalPrediction.landingZone.area,
      'Present Time Probability': reportData.finalPrediction.presentTime.probability,
      'Future Probability': reportData.finalPrediction.shortTermFuture.probability,
      'Time Window (hours)': reportData.finalPrediction.shortTermFuture.timeWindow
    }]
    const predictionWS = XLSX.utils.json_to_sheet(predictionData)
    XLSX.utils.book_append_sheet(workbook, predictionWS, 'Final Prediction')

    const excelBuffer = XLSX.write(workbook, { bookType: 'xlsx', type: 'array' })
    return new Blob([excelBuffer], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' })
  }

  const exportToJSON = (): Blob => {
    if (!reportData) throw new Error('No report data')
    
    const jsonData = JSON.stringify(reportData, null, 2)
    return new Blob([jsonData], { type: 'application/json' })
  }

  return (
    <div className="min-h-screen bg-white relative">
      <div className="absolute inset-0 bg-gradient-to-br from-blue-50/20 via-purple-50/10 to-cyan-50/20"></div>
      <div className="relative z-10">
        <Navbar />
        
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {/* Header Section */}
          <ReportHeader
            filters={filters}
            onFiltersChange={setFilters}
            onGenerateReport={fetchReportData}
            onExport={exportReport}
            availablePredictions={availablePredictions}
            sites={sites}
            isLoading={isLoading}
            isExporting={isExporting}
          />

          {/* Report Content */}
          {reportData && (
            <div ref={reportRef} className="mt-8 space-y-8">
            <DroneAnalysisSection data={reportData.droneAnalysis} metadata={reportData.metadata} />
            <SensorDataSection data={reportData.sensorData} />
            <StepwiseAnalysisSection data={reportData.stepwiseAnalysis} />
            <FinalPredictionSection data={reportData.finalPrediction} />
            <SummarySection data={reportData.summary} />
          </div>
        )}

        {/* Loading State */}
        {isLoading && (
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            <p className="mt-4 text-gray-600">Generating comprehensive report...</p>
          </div>
        )}

        {/* Empty State */}
        {!reportData && !isLoading && (
          <div className="text-center py-12">
            <div className="text-6xl mb-4">📋</div>
            <h3 className="text-lg font-medium text-gray-700 mb-2">No Report Generated</h3>
            <p className="text-gray-500">Select a prediction and click "Generate Report" to view comprehensive analysis</p>
          </div>
        )}
        </div>
      </div>
    </div>
  )
}

// Report Header Component
interface ReportHeaderProps {
  filters: ReportFilter
  onFiltersChange: (filters: ReportFilter) => void
  onGenerateReport: () => void
  onExport: (format: 'pdf' | 'csv' | 'excel' | 'json') => void
  availablePredictions: any[]
  sites: any[]
  isLoading: boolean
  isExporting: boolean
}

function ReportHeader({ 
  filters, 
  onFiltersChange, 
  onGenerateReport, 
  onExport, 
  availablePredictions, 
  sites,
  isLoading,
  isExporting 
}: ReportHeaderProps) {
  return (
    <div className="backdrop-blur-lg bg-white/40 border border-white/50 rounded-3xl shadow-xl p-6">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center">
          <div className="p-2 bg-gradient-to-r from-blue-500 to-purple-500 rounded-2xl mr-3">
            <span className="text-xl">📋</span>
          </div>
          <div>
            <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-600 via-purple-600 to-cyan-600 bg-clip-text text-transparent">
              Rockfall Prediction Report
            </h1>
            <p className="text-gray-600 mt-1 text-sm">Comprehensive analysis and risk assessment</p>
          </div>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => onExport('pdf')}
            disabled={!filters.predictionId || isExporting}
            className="group bg-gradient-to-r from-red-500 to-pink-500 hover:from-red-600 hover:to-pink-600 text-white px-4 py-2 rounded-2xl disabled:opacity-50 disabled:cursor-not-allowed text-sm flex items-center transition-all duration-300 hover:scale-105 shadow-lg"
          >
            <span className="group-hover:scale-110 transition-transform duration-300">📄 PDF</span>
          </button>
          <button
            onClick={() => onExport('csv')}
            disabled={!filters.predictionId || isExporting}
            className="group bg-gradient-to-r from-green-500 to-emerald-500 hover:from-green-600 hover:to-emerald-600 text-white px-4 py-2 rounded-2xl disabled:opacity-50 disabled:cursor-not-allowed text-sm flex items-center transition-all duration-300 hover:scale-105 shadow-lg"
          >
            <span className="group-hover:scale-110 transition-transform duration-300">📊 CSV</span>
          </button>
          <button
            onClick={() => onExport('excel')}
            disabled={!filters.predictionId || isExporting}
            className="group bg-gradient-to-r from-blue-500 to-cyan-500 hover:from-blue-600 hover:to-cyan-600 text-white px-4 py-2 rounded-2xl disabled:opacity-50 disabled:cursor-not-allowed text-sm flex items-center transition-all duration-300 hover:scale-105 shadow-lg"
          >
            <span className="group-hover:scale-110 transition-transform duration-300">📈 Excel</span>
          </button>
          <button
            onClick={() => onExport('json')}
            disabled={!filters.predictionId || isExporting}
            className="group bg-gradient-to-r from-purple-500 to-indigo-500 hover:from-purple-600 hover:to-indigo-600 text-white px-4 py-2 rounded-2xl disabled:opacity-50 disabled:cursor-not-allowed text-sm flex items-center transition-all duration-300 hover:scale-105 shadow-lg"
          >
            <span className="group-hover:scale-110 transition-transform duration-300">🔗 JSON</span>
          </button>
        </div>
      </div>

      {/* Filters */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <div>
          <label className="block text-sm font-semibold text-gray-700 mb-2 uppercase tracking-wider">Prediction Task</label>
          <select
            value={filters.predictionId || ''}
            onChange={(e) => onFiltersChange({ ...filters, predictionId: e.target.value })}
            className="w-full px-3 py-2 backdrop-blur-sm bg-white/50 border border-white/30 rounded-2xl focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-transparent transition-all duration-300 text-gray-800"
          >
            <option value="">Select Prediction</option>
            {availablePredictions.map(prediction => (
              <option key={prediction.id} value={prediction.id}>
                {prediction.site_name} - {new Date(prediction.timestamp).toLocaleDateString()}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-semibold text-gray-700 mb-3 uppercase tracking-wider">Site</label>
          <select
            value={filters.siteId || ''}
            onChange={(e) => onFiltersChange({ ...filters, siteId: e.target.value })}
            className="w-full px-4 py-3 backdrop-blur-sm bg-white/50 border border-white/30 rounded-2xl focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-transparent transition-all duration-300 text-gray-800"
          >
            <option value="">All Sites</option>
            {sites.map(site => (
              <option key={site.id} value={site.id}>{site.name}</option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-semibold text-gray-700 mb-3 uppercase tracking-wider">Start Date</label>
          <input
            type="date"
            value={filters.startDate || ''}
            onChange={(e) => onFiltersChange({ ...filters, startDate: e.target.value })}
            className="w-full px-4 py-3 backdrop-blur-sm bg-white/50 border border-white/30 rounded-2xl focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-transparent transition-all duration-300 text-gray-800"
          />
        </div>

        <div>
          <label className="block text-sm font-semibold text-gray-700 mb-3 uppercase tracking-wider">End Date</label>
          <input
            type="date"
            value={filters.endDate || ''}
            onChange={(e) => onFiltersChange({ ...filters, endDate: e.target.value })}
            className="w-full px-4 py-3 backdrop-blur-sm bg-white/50 border border-white/30 rounded-2xl focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-transparent transition-all duration-300 text-gray-800"
          />
        </div>
      </div>

      {/* Generate Report Button */}
      <button
        onClick={onGenerateReport}
        disabled={!filters.predictionId || isLoading}
        className="w-full group bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white py-4 px-8 rounded-2xl disabled:opacity-50 disabled:cursor-not-allowed font-semibold flex items-center justify-center transition-all duration-300 hover:scale-105 shadow-xl"
      >
        {isLoading ? (
          <>
            <div className="animate-spin rounded-full h-6 w-6 border-2 border-white border-t-transparent mr-3"></div>
            Generating Report...
          </>
        ) : (
          <span className="group-hover:scale-110 transition-transform duration-300">🔍 Generate Comprehensive Report</span>
        )}
      </button>
    </div>
  )
}

// Drone Analysis Section Component
interface DroneAnalysisSectionProps {
  data: DroneAnalysisData
  metadata: any
}

function DroneAnalysisSection({ data, metadata }: DroneAnalysisSectionProps) {
  // Chart data for slope distribution
  const slopeChartData = {
    labels: ['0-15°', '15-30°', '30-45°', '45-60°', '60-75°', '75-90°'],
    datasets: [{
      label: 'Slope Distribution (%)',
      data: data.demData.slopeDistribution,
      backgroundColor: 'rgba(59, 130, 246, 0.5)',
      borderColor: 'rgba(59, 130, 246, 1)',
      borderWidth: 2
    }]
  }

  // Chart data for crack severity
  const crackSeverityData = {
    labels: Object.keys(data.crackAnalysis.severityDistribution),
    datasets: [{
      data: Object.values(data.crackAnalysis.severityDistribution),
      backgroundColor: ['#10B981', '#F59E0B', '#EF4444', '#7C3AED'],
      borderWidth: 2
    }]
  }

  return (
    <div className="bg-white rounded-lg shadow-lg p-4">
      <h2 className="text-lg font-semibold text-gray-900 mb-4">📸 Drone Image Analysis</h2>
      
      {/* Uploaded Images */}
      <div className="mb-6">
        <h3 className="text-base font-medium text-gray-700 mb-3">Uploaded Images</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {data.images.map((image, index) => (
            <div key={image.id} className="border rounded-lg p-3">
              <div className="bg-gray-200 h-32 rounded mb-2 flex items-center justify-center">
                <span className="text-gray-500">📷 {image.filename}</span>
              </div>
              <div className="text-sm">
                <p><strong>Type:</strong> {image.type}</p>
                <p><strong>Processed:</strong> {image.processed ? '✅' : '❌'}</p>
                <p><strong>Annotations:</strong> {image.annotations.length}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* DEM Analysis */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        <div>
          <h3 className="text-base font-medium text-gray-700 mb-3">DEM & 3D Model Data</h3>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-sm text-gray-600">Elevation Range:</span>
              <span className="font-medium">{data.demData.elevationRange.min}m - {data.demData.elevationRange.max}m</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-gray-600">Bench Height:</span>
              <span className="font-medium">{data.demData.benchGeometry.height}m</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-gray-600">Bench Width:</span>
              <span className="font-medium">{data.demData.benchGeometry.width}m</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-gray-600">Average Slope:</span>
              <span className="font-medium">{data.demData.benchGeometry.angle}°</span>
            </div>
          </div>
        </div>

        <div>
          <h3 className="text-base font-medium text-gray-700 mb-3">Slope Distribution</h3>
          <div className="h-48">
            <Bar data={slopeChartData} options={{ responsive: true, maintainAspectRatio: false }} />
          </div>
        </div>
      </div>

      {/* Crack Analysis */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div>
          <h3 className="text-base font-medium text-gray-700 mb-3">Crack Detection Results</h3>
          <div className="space-y-2">
            <div className="flex justify-between">
              <span className="text-sm text-gray-600">Total Cracks Detected:</span>
              <span className="font-medium">{data.crackAnalysis.totalCracks}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-gray-600">Crack Density:</span>
              <span className="font-medium">{data.crackAnalysis.crackDensity} cracks/m²</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-gray-600">Annotated Images:</span>
              <span className="font-medium">{data.crackAnalysis.annotatedImages.length}</span>
            </div>
          </div>
        </div>

        <div>
          <h3 className="text-base font-medium text-gray-700 mb-3">Crack Severity Distribution</h3>
          <div className="h-48">
            <Doughnut 
              data={crackSeverityData} 
              options={{ 
                responsive: true, 
                maintainAspectRatio: false,
                plugins: {
                  legend: {
                    position: 'bottom'
                  }
                }
              }} 
            />
          </div>
        </div>
      </div>
    </div>
  )
}

// Sensor Data Section Component
interface SensorDataSectionProps {
  data: SensorReportData
}

function SensorDataSection({ data }: SensorDataSectionProps) {
  // Time series chart data
  const timeSeriesData = {
    labels: data.trends.porePressure.timestamps.map(ts => new Date(ts).toLocaleDateString()),
    datasets: [
      {
        label: 'Pore Pressure (kPa)',
        data: data.trends.porePressure.values,
        borderColor: 'rgba(59, 130, 246, 1)',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        fill: true,
        yAxisID: 'y'
      },
      {
        label: 'Temperature (°C)',
        data: data.trends.temperature.values,
        borderColor: 'rgba(239, 68, 68, 1)',
        backgroundColor: 'rgba(239, 68, 68, 0.1)',
        fill: true,
        yAxisID: 'y1'
      },
      {
        label: 'Seismic Activity',
        data: data.trends.seismicActivity.values,
        borderColor: 'rgba(16, 185, 129, 1)',
        backgroundColor: 'rgba(16, 185, 129, 0.1)',
        fill: true,
        yAxisID: 'y2'
      }
    ]
  }

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    scales: {
      y: {
        type: 'linear' as const,
        display: true,
        position: 'left' as const,
        title: {
          display: true,
          text: 'Pore Pressure (kPa)'
        }
      },
      y1: {
        type: 'linear' as const,
        display: true,
        position: 'right' as const,
        title: {
          display: true,
          text: 'Temperature (°C)'
        },
        grid: {
          drawOnChartArea: false,
        },
      },
      y2: {
        type: 'linear' as const,
        display: false
      }
    }
  }

  return (
    <div className="bg-white rounded-lg shadow-lg p-4">
      <h2 className="text-lg font-semibold text-gray-900 mb-4">📊 Sensor Data Analysis</h2>
      
      {/* Summary */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-3 mb-6">
        <div className="bg-blue-50 p-3 rounded-lg">
          <h3 className="font-medium text-blue-900 text-sm">Total Devices</h3>
          <p className="text-xl font-bold text-blue-700">{data.summary.deviceCount}</p>
        </div>
        <div className="bg-green-50 p-3 rounded-lg">
          <h3 className="font-medium text-green-900 text-sm">Total Readings</h3>
          <p className="text-xl font-bold text-green-700">{data.summary.readingsCount}</p>
        </div>
        <div className="bg-purple-50 p-3 rounded-lg">
          <h3 className="font-medium text-purple-900 text-sm">Data Quality</h3>
          <p className="text-xl font-bold text-purple-700">{data.summary.dataQuality}</p>
        </div>
        <div className="bg-orange-50 p-3 rounded-lg">
          <h3 className="font-medium text-orange-900 text-sm">Time Range</h3>
          <p className="text-xs font-medium text-orange-700">
            {new Date(data.summary.timeRange.start).toLocaleDateString()} - {new Date(data.summary.timeRange.end).toLocaleDateString()}
          </p>
        </div>
      </div>

      {/* Time Series Charts */}
      <div className="mb-8">
        <h3 className="text-lg font-medium text-gray-700 mb-4">Historical Trends</h3>
        <div className="h-80">
          <Line data={timeSeriesData} options={chartOptions} />
        </div>
      </div>

      {/* Recent Readings Table */}
      <div>
        <h3 className="text-lg font-medium text-gray-700 mb-4">Recent Sensor Readings</h3>
        <div className="overflow-x-auto">
          <table className="min-w-full bg-white border border-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Device ID</th>
                <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Timestamp</th>
                <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Pore Pressure</th>
                <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Displacement</th>
                <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Temperature</th>
                <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Seismic</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {data.readings.slice(0, 10).map((reading, index) => (
                <tr key={index}>
                  <td className="px-4 py-2 text-sm text-gray-900">{reading.deviceId.slice(-8)}</td>
                  <td className="px-4 py-2 text-sm text-gray-900">{new Date(reading.timestamp).toLocaleString()}</td>
                  <td className="px-4 py-2 text-sm text-gray-900">{reading.porePressure?.toFixed(1) || '-'}</td>
                  <td className="px-4 py-2 text-sm text-gray-900">{reading.displacement?.toFixed(2) || '-'}</td>
                  <td className="px-4 py-2 text-sm text-gray-900">{reading.temperature?.toFixed(1) || '-'}</td>
                  <td className="px-4 py-2 text-sm text-gray-900">{reading.seismicActivity?.toFixed(3) || '-'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}

// Stepwise Analysis Section Component
interface StepwiseAnalysisSectionProps {
  data: StepwiseAnalysisData
}

function StepwiseAnalysisSection({ data }: StepwiseAnalysisSectionProps) {
  // Risk evolution chart
  const riskEvolutionData = {
    labels: data.riskEvolution.map(item => item.stage),
    datasets: [
      {
        label: 'Risk Score',
        data: data.riskEvolution.map(item => item.riskScore * 100),
        borderColor: 'rgba(239, 68, 68, 1)',
        backgroundColor: 'rgba(239, 68, 68, 0.1)',
        fill: true
      },
      {
        label: 'Confidence',
        data: data.riskEvolution.map(item => item.confidence * 100),
        borderColor: 'rgba(59, 130, 246, 1)',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        fill: true
      }
    ]
  }

  // Feature importance chart
  const featureImportanceData = {
    labels: Object.keys(data.intermediateResults.featureImportance),
    datasets: [{
      label: 'Feature Importance',
      data: Object.values(data.intermediateResults.featureImportance),
      backgroundColor: 'rgba(16, 185, 129, 0.5)',
      borderColor: 'rgba(16, 185, 129, 1)',
      borderWidth: 2
    }]
  }

  return (
    <div className="bg-white rounded-lg shadow-lg p-4">
      <h2 className="text-lg font-semibold text-gray-900 mb-4">🤖 Stepwise AI/ML Analysis</h2>
      
      {/* Processing Stages Timeline */}
      <div className="mb-6">
        <h3 className="text-base font-medium text-gray-700 mb-3">Processing Stages</h3>
        <div className="space-y-4">
          {data.stages.map((stage, index) => (
            <div key={stage.id} className="flex items-center">
              <div className={`w-8 h-8 rounded-full flex items-center justify-center text-white text-sm ${
                stage.status === 'completed' ? 'bg-green-500' : 
                stage.status === 'error' ? 'bg-red-500' : 
                'bg-gray-400'
              }`}>
                {index + 1}
              </div>
              <div className="ml-4 flex-1">
                <div className="flex justify-between items-center">
                  <h4 className="font-medium text-gray-900">{stage.name}</h4>
                  <span className="text-sm text-gray-500">{stage.processingTime}ms</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2 mt-1">
                  <div 
                    className={`h-2 rounded-full ${
                      stage.status === 'completed' ? 'bg-green-500' : 
                      stage.status === 'error' ? 'bg-red-500' : 
                      'bg-blue-500'
                    }`}
                    style={{ width: `${stage.progress}%` }}
                  />
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Intermediate Results */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        <div>
          <h3 className="text-base font-medium text-gray-700 mb-3">Model Confidence Scores</h3>
          <div className="space-y-2">
            <div className="flex justify-between">
              <span className="text-sm text-gray-600">Vision Model (CNN):</span>
              <span className="font-medium">{(data.intermediateResults.visionModelConfidence * 100).toFixed(1)}%</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-gray-600">Sensor Model (XGBoost):</span>
              <span className="font-medium">{(data.intermediateResults.sensorModelConfidence * 100).toFixed(1)}%</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-gray-600">Fusion Model:</span>
              <span className="font-medium">{(data.intermediateResults.fusionConfidence * 100).toFixed(1)}%</span>
            </div>
          </div>
        </div>

        <div>
          <h3 className="text-lg font-medium text-gray-700 mb-4">Feature Importance</h3>
          <div className="h-64">
            <Bar 
              data={featureImportanceData} 
              options={{ 
                responsive: true, 
                maintainAspectRatio: false,
                indexAxis: 'y' as const
              }} 
            />
          </div>
        </div>
      </div>

      {/* Risk Evolution Chart */}
      <div>
        <h3 className="text-lg font-medium text-gray-700 mb-4">Risk Score Evolution Through Processing</h3>
        <div className="h-64">
          <Line 
            data={riskEvolutionData} 
            options={{ 
              responsive: true, 
              maintainAspectRatio: false,
              scales: {
                y: {
                  beginAtZero: true,
                  max: 100,
                  title: {
                    display: true,
                    text: 'Score (%)'
                  }
                }
              }
            }} 
          />
        </div>
      </div>
    </div>
  )
}

// Final Prediction Section Component
interface FinalPredictionSectionProps {
  data: FinalPredictionData
}

function FinalPredictionSection({ data }: FinalPredictionSectionProps) {
  const getRiskColor = (riskLevel: string) => {
    switch (riskLevel) {
      case 'LOW': return 'text-green-600 bg-green-100'
      case 'MEDIUM': return 'text-yellow-600 bg-yellow-100'
      case 'HIGH': return 'text-orange-600 bg-orange-100'
      case 'CRITICAL': return 'text-red-600 bg-red-100'
      default: return 'text-gray-600 bg-gray-100'
    }
  }

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <h2 className="text-xl font-semibold text-gray-900 mb-6">🎯 Final Prediction Results</h2>
      
      {/* Risk Assessment */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-8">
        <div className="text-center">
          <div className={`inline-flex items-center px-6 py-3 rounded-full text-lg font-bold ${getRiskColor(data.riskLevel)}`}>
            {data.riskLevel} RISK
          </div>
          <div className="mt-4 text-4xl font-bold text-gray-900">
            {(data.riskScore * 100).toFixed(1)}%
          </div>
          <div className="text-sm text-gray-500">Overall Risk Probability</div>
        </div>

        <div className="text-center">
          <div className="text-lg font-medium text-gray-700 mb-2">Estimated Volume</div>
          <div className="text-3xl font-bold text-blue-600">{data.estimatedVolume.toFixed(1)} m³</div>
          <div className="text-sm text-gray-500">Potential Rockfall Volume</div>
        </div>

        <div className="text-center">
          <div className="text-lg font-medium text-gray-700 mb-2">Confidence Score</div>
          <div className="text-3xl font-bold text-green-600">{(data.confidence * 100).toFixed(1)}%</div>
          <div className="text-sm text-gray-500">Model Confidence</div>
        </div>
      </div>

      {/* Present vs Future Predictions */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
        <div className="bg-blue-50 p-6 rounded-lg">
          <h3 className="font-medium text-blue-900 mb-4">Present Time Risk</h3>
          <div className="text-3xl font-bold text-blue-700 mb-2">
            {(data.presentTime.probability * 100).toFixed(1)}%
          </div>
          <div className="text-sm text-blue-600">
            Current moment assessment
          </div>
          <div className="text-xs text-blue-500 mt-2">
            {new Date(data.presentTime.timestamp).toLocaleString()}
          </div>
        </div>

        <div className="bg-purple-50 p-6 rounded-lg">
          <h3 className="font-medium text-purple-900 mb-4">Short-Term Future Risk</h3>
          <div className="text-3xl font-bold text-purple-700 mb-2">
            {(data.shortTermFuture.probability * 100).toFixed(1)}%
          </div>
          <div className="text-sm text-purple-600">
            Next {data.shortTermFuture.timeWindow} hours
          </div>
          <div className="text-xs text-purple-500 mt-2">
            Predicted peak: {new Date(data.shortTermFuture.predictedTime).toLocaleString()}
          </div>
        </div>
      </div>

      {/* Landing Zone Information */}
      <div className="mb-8">
        <h3 className="text-lg font-medium text-gray-700 mb-4">Predicted Landing Zone</h3>
        <div className="bg-gray-100 p-4 rounded-lg">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <span className="text-sm text-gray-600">Area:</span>
              <span className="ml-2 font-medium">{data.landingZone.area.toFixed(0)} m²</span>
            </div>
            <div>
              <span className="text-sm text-gray-600">Coordinates:</span>
              <span className="ml-2 font-medium">{data.landingZone.coordinates.length} points defined</span>
            </div>
          </div>
        </div>
      </div>

      {/* Preventive Actions */}
      <div>
        <h3 className="text-lg font-medium text-gray-700 mb-4">Recommended Preventive Actions</h3>
        <div className="space-y-2">
          {data.preventiveActions.map((action, index) => (
            <div key={index} className="flex items-start">
              <span className="text-blue-500 mr-2 mt-1">•</span>
              <span className="text-gray-700">{action}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

// Summary Section Component
interface SummarySectionProps {
  data: {
    keyFindings: string[]
    recommendations: string[]
    overallAssessment: string
  }
}

function SummarySection({ data }: SummarySectionProps) {
  return (
    <div className="backdrop-blur-lg bg-white/40 border border-white/50 rounded-3xl shadow-xl p-8">
      <div className="flex items-center mb-8">
        <div className="p-3 bg-gradient-to-r from-green-500 to-emerald-500 rounded-2xl mr-4">
          <span className="text-2xl">📋</span>
        </div>
        <div>
          <h2 className="text-2xl font-bold bg-gradient-to-r from-green-600 to-emerald-600 bg-clip-text text-transparent">
            Summary & Recommendations
          </h2>
          <p className="text-gray-600">Key insights and strategic guidance</p>
        </div>
      </div>
      
      {/* Overall Assessment */}
      <div className="mb-8">
        <h3 className="text-xl font-semibold text-gray-800 mb-4 flex items-center">
          <span className="mr-2">🎯</span>
          Overall Assessment
        </h3>
        <div className="backdrop-blur-sm bg-gradient-to-r from-blue-50/80 to-cyan-50/80 border border-blue-200/30 p-6 rounded-2xl">
          <p className="text-gray-800 leading-relaxed">{data.overallAssessment}</p>
        </div>
      </div>

      {/* Key Findings */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div>
          <h3 className="text-xl font-semibold text-gray-800 mb-6 flex items-center">
            <span className="mr-2">🔍</span>
            Key Findings
          </h3>
          <div className="space-y-4">
            {data.keyFindings.map((finding, index) => (
              <div key={index} className="backdrop-blur-sm bg-white/30 border border-white/30 rounded-2xl p-4 hover:bg-white/40 transition-all duration-300 hover:scale-[1.01] hover:shadow-lg">
                <div className="flex items-start">
                  <div className="p-2 bg-gradient-to-r from-green-400 to-emerald-400 rounded-xl mr-3 mt-0.5">
                    <span className="text-white text-sm">🔍</span>
                  </div>
                  <span className="text-gray-800 leading-relaxed flex-1">{finding}</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div>
          <h3 className="text-xl font-semibold text-gray-800 mb-6 flex items-center">
            <span className="mr-2">💡</span>
            Strategic Recommendations
          </h3>
          <div className="space-y-4">
            {data.recommendations.map((recommendation, index) => (
              <div key={index} className="backdrop-blur-sm bg-white/30 border border-white/30 rounded-2xl p-4 hover:bg-white/40 transition-all duration-300 hover:scale-[1.01] hover:shadow-lg">
                <div className="flex items-start">
                  <div className="p-2 bg-gradient-to-r from-blue-400 to-cyan-400 rounded-xl mr-3 mt-0.5">
                    <span className="text-white text-sm">💡</span>
                  </div>
                  <span className="text-gray-800 leading-relaxed flex-1">{recommendation}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}

export default ReportPage