# Real-World Rockfall Prediction System - Predictions Page

## 🎯 Overview

The Predictions Page is a comprehensive, real-world deployable interface for AI-powered rockfall prediction analysis. It integrates drone imagery, real-time sensor data, and advanced ML models to provide present-time and short-term future rockfall predictions for mining sites.

## ✨ Key Features

### 📥 Data Input Panel
- **Drone Image Upload**: Support for up to 10 drone images per prediction task
- **Image Types**: DEM, Orthophoto, Point Cloud, Aerial Photo
- **Automatic Sensor Data Fetching**: Real-time data from Device Manager
- **Metadata Input**: Site ID, Bench ID, Timestamp, Drone Mission ID
- **Input Validation**: File type, resolution, timestamp, and sensor value validation

### ⚙️ Step-by-Step Processing Pipeline

The system processes data through 7 distinct stages, showing temporary outputs at each step:

1. **Image Preprocessing**
   - Normalize images, remove noise, correct lighting/shadows
   - Output: Cleaned thumbnails and preprocessing report

2. **DEM & 3D Model Generation** 
   - Generate Digital Elevation Model from drone images
   - Create slope, elevation, and bench geometry maps
   - Output: DEM heatmaps and 3D model preview

3. **Structural Feature Extraction**
   - Detect cracks and fissures using computer vision
   - Calculate slope angles, bench height & width, surface roughness
   - Output: Annotated images showing cracks, slope maps, roughness visualization

4. **Sensor Data Validation & Preprocessing**
   - Fetch data from Device Manager (real-time and historical)
   - Clean missing/outlier values
   - Output: Table preview of sensor readings

5. **Data Fusion**
   - Combine drone-derived features, current sensor readings, and historical rockfall data
   - Align by timestamp and location
   - Output: Preview of fused dataset (sample rows)

6. **AI/ML Prediction**
   - Present-time prediction: Risk probability for current moment
   - Short-term future prediction: Probability of rockfall in the next few hours
   - Output: Stepwise progress showing intermediate AI model results, feature importance, and confidence scores

7. **Final Prediction Result**
   - Risk score (probability), risk level (Low/Medium/High)
   - Estimated rockfall volume and predicted landing zone
   - Suggested preventive actions

### 📊 Results Dashboard

- **Risk Gauge**: Color-coded risk level display with probability percentage
- **Present vs Future Predictions**: Side-by-side comparison of current and short-term risk
- **Key Metrics**: Estimated volume, landing zone area, confidence scores
- **Feature Importance**: Visual display of factors contributing to prediction
- **Preventive Actions**: Contextual recommendations based on risk level
- **Reset Functionality**: Clear temporary outputs after completion

## 🔧 Technical Implementation

### Frontend (React + TypeScript + Tailwind CSS)
- **Component Architecture**: Modular design with DataInputPanel, ProcessingPipeline, and ResultsDashboard
- **State Management**: Comprehensive state management for images, sensor data, processing stages, and results
- **Real-time Updates**: Progress polling and stage status updates
- **Responsive Design**: Mobile-friendly interface with grid layouts

### Backend (FastAPI + Python)
- **API Endpoints**: 
  - `/api/predictions/enhanced/comprehensive-analysis` - Start analysis
  - `/api/predictions/enhanced/analysis-progress/{id}` - Get progress
- **File Upload**: Multi-file drone image upload with metadata
- **Background Processing**: Asynchronous processing pipeline
- **Progress Tracking**: Real-time stage-by-stage progress updates

### Database Integration (MongoDB)
- **Prediction Storage**: Final predictions with metadata
- **Temporary Output Management**: Optional storage and cleanup
- **Audit Trail**: Complete data lineage for retraining and compliance

## 🚀 Usage Workflow

1. **Select Site**: Choose mining site from dropdown
2. **Upload Images**: Add up to 10 drone images with type classification
3. **Configure Metadata**: Set bench ID, drone mission ID
4. **Auto-fetch Sensors**: System automatically retrieves sensor data for selected site
5. **Start Prediction**: Initiate comprehensive analysis
6. **Monitor Progress**: Watch real-time processing through 7 stages
7. **Review Results**: Analyze risk scores, feature importance, and recommendations
8. **Reset/Repeat**: Clear outputs and start new analysis

## 📋 Sensor Data Integration

The system automatically fetches data from the following sensor types:
- **Geotechnical**: Pore pressure, displacement, acceleration, RMR, UCS
- **Environmental**: Rainfall, temperature, seismic activity
- **Derived**: Slope angles, surface roughness, crack detection

## 🎯 AI/ML Pipeline

### Present-Time Prediction
- **CNN/ResNet**: Computer vision analysis of drone imagery
- **XGBoost/LightGBM**: Tabular sensor data analysis
- **Fusion Models**: Combined predictions with confidence scoring

### Short-Term Future Prediction
- **Temporal Models**: LSTM/GRU for time-series forecasting
- **Prophet**: Seasonal trend analysis
- **Time Window**: Configurable prediction horizon (default: 6 hours)

## 🔒 Production Considerations

- **Real-world Deployable**: Robust error handling and validation
- **Mining Operations Ready**: Designed for 24/7 industrial use
- **Data Integrity**: Complete audit trail in MongoDB
- **Scalable Architecture**: Supports multiple concurrent analyses
- **Security**: JWT-based authentication and authorization

## 🚦 Error Handling

- **Input Validation**: File type, size, and format checking
- **Network Resilience**: Automatic retry for failed requests
- **Processing Errors**: Graceful error display with recovery options
- **Timeout Management**: Configurable analysis timeouts

## 📈 Performance Features

- **Progress Visualization**: Real-time stage-by-stage updates
- **Temporary Output Display**: Immediate feedback during processing
- **Result Caching**: Optional result storage for quick access
- **Background Processing**: Non-blocking analysis execution

## 🔧 Configuration

### Environment Variables
- `MONGODB_URI`: Database connection string
- `ML_MODEL_PATH`: Path to trained ML models
- `MAX_UPLOAD_SIZE`: Maximum file upload size
- `ANALYSIS_TIMEOUT`: Maximum analysis duration

### API Configuration
- **Max Images**: 10 per analysis
- **Supported Formats**: JPG, PNG, TIFF
- **Max File Size**: 50MB per image
- **Progress Polling**: 1-second intervals

## 🎉 Success Metrics

The Predictions Page successfully delivers:
- ✅ **Real-time Processing**: Live updates through all 7 stages
- ✅ **Dual Predictions**: Present-time and short-term future forecasting
- ✅ **Visual Outputs**: Temporary outputs at each processing stage
- ✅ **Comprehensive Results**: Risk scores, feature importance, recommendations
- ✅ **Production Ready**: Robust error handling and data integrity
- ✅ **User-Friendly**: Intuitive interface with clear progress indication

This implementation provides a complete, production-ready rockfall prediction system that integrates seamlessly with existing mining operations and delivers actionable insights for safety and operational decisions.