export interface DeviceFieldDefinition {
  name: string
  unit: string
  type: 'number' | 'string' | 'boolean' | 'timestamp'
  description: string
  required: boolean
}

export interface DeviceConfiguration {
  samplingRate?: number
  threshold?: number
  calibrationDate?: string
  alertEnabled?: boolean
  dataRetentionDays?: number
  [key: string]: any
}

export interface DeviceData {
  timestamp: string
  values: Record<string, any>
  quality: 'good' | 'warning' | 'poor'
  anomaly?: boolean
}

export interface BaseDevice {
  id: string
  name: string
  type: DeviceType
  description: string
  category: string
  fields: DeviceFieldDefinition[]
  status: 'online' | 'offline' | 'maintenance' | 'error'
  enabled: boolean
  location?: {
    latitude: number
    longitude: number
    elevation?: number
  }
  configuration: DeviceConfiguration
  lastReading?: string
  csvImportEnabled: boolean
  apiEndpoint?: string
  notes: string
  createdAt: string
  updatedAt: string
}

export type DeviceType = 
  | 'gb-insar'
  | 'lidar'
  | 'borehole-inclinometer'
  | 'piezometer'
  | 'weather-station'
  | 'geophone'
  | 'drone-imagery'

// Specific device type definitions
export interface GBInSARDevice extends BaseDevice {
  type: 'gb-insar'
  fields: [
    { name: 'displacement', unit: 'mm', type: 'number', description: 'Slope displacement measurement', required: true },
    { name: 'velocity', unit: 'mm/day', type: 'number', description: 'Displacement velocity', required: true },
    { name: 'acceleration', unit: 'mm/day²', type: 'number', description: 'Displacement acceleration', required: true },
    { name: 'areaId', unit: '', type: 'string', description: 'Monitoring area identifier', required: true },
    { name: 'timestamp', unit: '', type: 'timestamp', description: 'Measurement timestamp', required: true }
  ]
}

export interface LiDARDevice extends BaseDevice {
  type: 'lidar'
  fields: [
    { name: 'coordinates', unit: 'X,Y,Z', type: 'string', description: 'Point cloud coordinates', required: true },
    { name: 'demElevation', unit: 'm', type: 'number', description: 'Digital Elevation Model height', required: true },
    { name: 'volumeChange', unit: 'm³', type: 'number', description: 'Surface volume change', required: true },
    { name: 'timestamp', unit: '', type: 'timestamp', description: 'Scan timestamp', required: true },
    { name: 'areaId', unit: '', type: 'string', description: 'Scan area identifier', required: true }
  ]
}

export interface BoreholeInclinometerDevice extends BaseDevice {
  type: 'borehole-inclinometer'
  fields: [
    { name: 'displacementAtDepth', unit: 'mm', type: 'number', description: 'Subsurface displacement measurement', required: true },
    { name: 'strain', unit: 'µm/m', type: 'number', description: 'Material strain measurement', required: true },
    { name: 'depth', unit: 'm', type: 'number', description: 'Measurement depth', required: true },
    { name: 'timestamp', unit: '', type: 'timestamp', description: 'Measurement timestamp', required: true },
    { name: 'boreholeId', unit: '', type: 'string', description: 'Borehole identifier', required: true }
  ]
}

export interface PiezometerDevice extends BaseDevice {
  type: 'piezometer'
  fields: [
    { name: 'porePressure', unit: 'kPa', type: 'number', description: 'Pore water pressure', required: true },
    { name: 'waterLevel', unit: 'm', type: 'number', description: 'Water level measurement', required: true },
    { name: 'temperature', unit: '°C', type: 'number', description: 'Water temperature', required: true },
    { name: 'timestamp', unit: '', type: 'timestamp', description: 'Measurement timestamp', required: true },
    { name: 'locationId', unit: '', type: 'string', description: 'Installation location ID', required: true }
  ]
}

export interface WeatherStationDevice extends BaseDevice {
  type: 'weather-station'
  fields: [
    { name: 'rainfall', unit: 'mm', type: 'number', description: 'Rainfall measurement', required: true },
    { name: 'temperature', unit: '°C', type: 'number', description: 'Air temperature', required: true },
    { name: 'humidity', unit: '%', type: 'number', description: 'Relative humidity', required: true },
    { name: 'windSpeed', unit: 'm/s', type: 'number', description: 'Wind speed', required: true },
    { name: 'timestamp', unit: '', type: 'timestamp', description: 'Measurement timestamp', required: true },
    { name: 'stationId', unit: '', type: 'string', description: 'Weather station ID', required: true }
  ]
}

export interface GeophoneDevice extends BaseDevice {
  type: 'geophone'
  fields: [
    { name: 'vibrationAmplitude', unit: 'mm/s', type: 'number', description: 'Peak vibration amplitude', required: true },
    { name: 'frequency', unit: 'Hz', type: 'number', description: 'Dominant frequency', required: true },
    { name: 'cumulativeEnergy', unit: 'J', type: 'number', description: 'Cumulative energy measurement', required: true },
    { name: 'timestamp', unit: '', type: 'timestamp', description: 'Detection timestamp', required: true },
    { name: 'locationId', unit: '', type: 'string', description: 'Sensor location ID', required: true }
  ]
}

export interface DroneImageryDevice extends BaseDevice {
  type: 'drone-imagery'
  fields: [
    { name: 'imageVideo', unit: '', type: 'string', description: 'Image/Video file path', required: true },
    { name: 'gpsCoordinates', unit: 'lat,lon', type: 'string', description: 'GPS coordinates', required: true },
    { name: 'timestamp', unit: '', type: 'timestamp', description: 'Capture timestamp', required: true },
    { name: 'areaId', unit: '', type: 'string', description: 'Survey area ID', required: true }
  ]
}

export type Device = 
  | GBInSARDevice 
  | LiDARDevice 
  | BoreholeInclinometerDevice 
  | PiezometerDevice 
  | WeatherStationDevice 
  | GeophoneDevice 
  | DroneImageryDevice

export const deviceTypeConfigs: Record<DeviceType, {
  icon: string
  color: string
  category: string
  description: string
}> = {
  'gb-insar': {
    icon: '📡',
    color: 'blue',
    category: 'Ground Radar',
    description: 'Wide-area slope displacement monitoring'
  },
  'lidar': {
    icon: '🔍',
    color: 'green',
    category: 'Terrestrial/Drone',
    description: 'Surface geometry & volumetric changes'
  },
  'borehole-inclinometer': {
    icon: '🕳️',
    color: 'purple',
    category: 'Subsurface',
    description: 'Subsurface slope deformation monitoring'
  },
  'piezometer': {
    icon: '💧',
    color: 'cyan',
    category: 'Vibrating-wire',
    description: 'Pore water pressure monitoring'
  },
  'weather-station': {
    icon: '🌤️',
    color: 'yellow',
    category: 'AWS/Rain Gauge',
    description: 'Environmental trigger monitoring'
  },
  'geophone': {
    icon: '📊',
    color: 'red',
    category: 'Microseismic',
    description: 'Vibration & blasting activity detection'
  },
  'drone-imagery': {
    icon: '🚁',
    color: 'indigo',
    category: 'High-Resolution',
    description: 'Crack mapping & surface change analysis'
  }
}