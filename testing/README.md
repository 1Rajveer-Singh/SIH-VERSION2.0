# Testing Demo Dataset

This directory contains comprehensive demo data for testing the Rockfall Prediction System.

## Generated Data

The demo dataset includes:

- **3 Mining Sites**: Rocky Mountain Quarry, Alpine Granite Mine, Cascade Copper Mine
- **61 Monitoring Devices**: Various sensor types (vibration, temperature, humidity, strain, tilt, weather)
- **83,456 Sensor Readings**: 30 days of realistic sensor data with patterns and anomalies
- **50 Predictions**: AI predictions with varying risk levels and confidence scores
- **42 Alerts**: System alerts including high-risk predictions and device issues

## Data Files

- `sites.json` - Mining site definitions with zones and emergency contacts
- `devices.json` - Monitoring device configurations and specifications
- `sensor_readings.json` - Historical sensor data with realistic patterns
- `predictions.json` - Rockfall risk predictions with detailed analysis
- `alerts.json` - System alerts and notifications
- `dataset_summary.json` - Summary statistics of the generated data

## Usage

### 1. Generate Demo Data

```bash
cd testing/demo-data
python generate_demo_dataset.py
```

### 2. Import to Database

Make sure MongoDB is running and the backend is configured, then:

```bash
cd testing/demo-data
python import_demo_data.py
```

This will prompt you to clear existing data and then import all demo data into MongoDB.

### 3. Test Website Functionality

After importing the data:

1. Start the backend and frontend servers
2. Login with demo credentials:
   - **Admin**: admin@rockfall.com / secret123
   - **Operator**: operator@rockfall.com / secret123
3. Navigate through all pages to test functionality:
   - Dashboard - View overview and metrics
   - Predictions - Browse prediction history
   - Reports - Generate and export reports
   - Sites - Manage mining sites
   - Devices - Monitor device status
   - Settings - Configure user and system settings
   - Help - Access help documentation
   - Services - Check system status

## Data Characteristics

### Realistic Patterns

- **Sensor Data**: Includes daily cycles, seasonal variations, noise, and occasional anomalies
- **Risk Predictions**: Distribution across low/medium/high risk levels with confidence scores
- **Device Status**: Mix of active, maintenance, and offline devices
- **Alert Patterns**: Realistic alert frequencies and severities

### Time Spans

- **Sensor Readings**: Last 30 days with 15-60 minute intervals
- **Predictions**: Random distribution over the past month
- **Alerts**: Recent alerts with various acknowledgment states

## Testing Scenarios

The demo data supports testing:

1. **Real-time monitoring** - Recent sensor data and device status
2. **Historical analysis** - 30 days of trend data
3. **Risk assessment** - Various prediction scenarios
4. **Alert management** - Active and resolved alerts
5. **Report generation** - Multiple data points for comprehensive reports
6. **Multi-site operations** - 3 different mining sites with unique characteristics

## Data Refresh

To refresh the demo data:

1. Run `generate_demo_dataset.py` to create new data
2. Run `import_demo_data.py` and choose to clear existing data
3. Restart the application to see the new data

## Notes

- All timestamps are generated relative to the current date
- Device locations and sensor readings include realistic variations
- The data is designed to demonstrate all system features
- Risk levels and alerts are distributed to show various scenarios