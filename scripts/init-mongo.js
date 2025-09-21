// MongoDB Initialization Script

// Create application database user
db.createUser({
  user: 'app_user',
  pwd: 'app_password',
  roles: [
    {
      role: 'readWrite',
      db: 'rockfall_prediction'
    }
  ]
});

// Create collections with indexes
db.createCollection('sites');
db.createCollection('sensors');
db.createCollection('sensor_readings');
db.createCollection('predictions');
db.createCollection('alerts');
db.createCollection('users');
db.createCollection('dem_files');
db.createCollection('drone_imagery');
db.createCollection('environmental_data');
db.createCollection('historical_events');

// Create indexes for better performance
db.sensor_readings.createIndex({ "sensor_id": 1, "timestamp": -1 });
db.sensor_readings.createIndex({ "site_id": 1, "timestamp": -1 });
db.predictions.createIndex({ "site_id": 1, "timestamp": -1 });
db.predictions.createIndex({ "risk_level": 1, "timestamp": -1 });
db.alerts.createIndex({ "site_id": 1, "created_at": -1 });
db.alerts.createIndex({ "status": 1, "severity": 1 });
db.drone_imagery.createIndex({ "site_id": 1, "flight_date": -1 });
db.historical_events.createIndex({ "site_id": 1, "date": -1 });
db.historical_events.createIndex({ "event_type": 1, "severity": 1 });
db.environmental_data.createIndex({ "date": -1 });

print('Database initialized with collections and indexes');