// MongoDB initialization script for Rockfall Prediction System
// This script creates collections and indexes for optimal performance

db = db.getSiblingDB('rockfall_prediction');

// Create collections with validation schemas

// Users collection
db.createCollection("users", {
   validator: {
      $jsonSchema: {
         bsonType: "object",
         required: ["email", "username", "password_hash", "role", "created_at"],
         properties: {
            email: {
               bsonType: "string",
               pattern: "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$"
            },
            username: {
               bsonType: "string",
               minLength: 3,
               maxLength: 50
            },
            full_name: {
               bsonType: "string",
               maxLength: 100
            },
            password_hash: {
               bsonType: "string"
            },
            role: {
               enum: ["admin", "operator", "viewer"]
            },
            is_active: {
               bsonType: "bool"
            },
            profile_picture: {
               bsonType: "string"
            },
            last_login: {
               bsonType: "date"
            },
            created_at: {
               bsonType: "date"
            },
            updated_at: {
               bsonType: "date"
            }
         }
      }
   }
});

// Mining sites collection
db.createCollection("mining_sites", {
   validator: {
      $jsonSchema: {
         bsonType: "object",
         required: ["name", "location", "status", "created_at"],
         properties: {
            name: {
               bsonType: "string",
               minLength: 1,
               maxLength: 100
            },
            description: {
               bsonType: "string"
            },
            location: {
               bsonType: "object",
               required: ["latitude", "longitude"],
               properties: {
                  latitude: {
                     bsonType: "double",
                     minimum: -90,
                     maximum: 90
                  },
                  longitude: {
                     bsonType: "double", 
                     minimum: -180,
                     maximum: 180
                  },
                  elevation: {
                     bsonType: "double"
                  },
                  address: {
                     bsonType: "string"
                  }
               }
            },
            zones: {
               bsonType: "array",
               items: {
                  bsonType: "object",
                  properties: {
                     zone_id: { bsonType: "string" },
                     name: { bsonType: "string" },
                     risk_level: { enum: ["low", "medium", "high", "critical"] }
                  }
               }
            },
            status: {
               enum: ["active", "inactive", "maintenance"]
            },
            emergency_contacts: {
               bsonType: "array",
               items: {
                  bsonType: "object",
                  properties: {
                     name: { bsonType: "string" },
                     role: { bsonType: "string" },
                     phone: { bsonType: "string" },
                     email: { bsonType: "string" }
                  }
               }
            }
         }
      }
   }
});

// Devices/Sensors collection
db.createCollection("devices", {
   validator: {
      $jsonSchema: {
         bsonType: "object",
         required: ["device_id", "name", "type", "site_id", "status", "created_at"],
         properties: {
            device_id: {
               bsonType: "string",
               minLength: 1
            },
            name: {
               bsonType: "string",
               minLength: 1,
               maxLength: 100
            },
            type: {
               enum: ["accelerometer", "inclinometer", "seismometer", "weather_station", "gps", "temperature", "humidity", "pressure"]
            },
            site_id: {
               bsonType: "objectId"
            },
            zone_id: {
               bsonType: "string"
            },
            location: {
               bsonType: "object",
               properties: {
                  latitude: { bsonType: "double" },
                  longitude: { bsonType: "double" },
                  elevation: { bsonType: "double" }
               }
            },
            status: {
               enum: ["online", "offline", "maintenance", "error"]
            },
            configuration: {
               bsonType: "object",
               properties: {
                  sampling_rate: { bsonType: "int" },
                  thresholds: { bsonType: "object" },
                  calibration_date: { bsonType: "date" }
               }
            },
            last_reading: {
               bsonType: "date"
            },
            last_maintenance: {
               bsonType: "date"
            }
         }
      }
   }
});

// Sensor readings collection
db.createCollection("sensor_readings", {
   validator: {
      $jsonSchema: {
         bsonType: "object",
         required: ["device_id", "timestamp", "readings"],
         properties: {
            device_id: {
               bsonType: "objectId"
            },
            timestamp: {
               bsonType: "date"
            },
            readings: {
               bsonType: "object"
            },
            quality_score: {
               bsonType: "double",
               minimum: 0,
               maximum: 1
            }
         }
      }
   }
});

// Predictions collection
db.createCollection("predictions", {
   validator: {
      $jsonSchema: {
         bsonType: "object",
         required: ["site_id", "timestamp", "risk_level", "probability", "model_version"],
         properties: {
            site_id: {
               bsonType: "objectId"
            },
            zone_id: {
               bsonType: "string"
            },
            timestamp: {
               bsonType: "date"
            },
            risk_level: {
               enum: ["low", "medium", "high", "critical"]
            },
            probability: {
               bsonType: "double",
               minimum: 0,
               maximum: 1
            },
            confidence: {
               bsonType: "double",
               minimum: 0,
               maximum: 1
            },
            model_version: {
               bsonType: "string"
            },
            contributing_factors: {
               bsonType: "array",
               items: {
                  bsonType: "object",
                  properties: {
                     factor: { bsonType: "string" },
                     weight: { bsonType: "double" }
                  }
               }
            },
            recommendations: {
               bsonType: "array",
               items: { bsonType: "string" }
            }
         }
      }
   }
});

// Alerts collection
db.createCollection("alerts", {
   validator: {
      $jsonSchema: {
         bsonType: "object",
         required: ["type", "severity", "message", "timestamp", "status"],
         properties: {
            type: {
               enum: ["prediction", "device", "system", "maintenance"]
            },
            severity: {
               enum: ["info", "warning", "error", "critical"]
            },
            message: {
               bsonType: "string",
               minLength: 1
            },
            site_id: {
               bsonType: "objectId"
            },
            device_id: {
               bsonType: "objectId"
            },
            prediction_id: {
               bsonType: "objectId"
            },
            timestamp: {
               bsonType: "date"
            },
            acknowledged_by: {
               bsonType: "objectId"
            },
            acknowledged_at: {
               bsonType: "date"
            },
            status: {
               enum: ["active", "acknowledged", "resolved"]
            }
         }
      }
   }
});

// System settings collection
db.createCollection("system_settings", {
   validator: {
      $jsonSchema: {
         bsonType: "object",
         required: ["key", "value", "updated_at"],
         properties: {
            key: {
               bsonType: "string",
               minLength: 1
            },
            value: {},
            description: {
               bsonType: "string"
            },
            updated_by: {
               bsonType: "objectId"
            },
            updated_at: {
               bsonType: "date"
            }
         }
      }
   }
});

// System logs collection
db.createCollection("system_logs", {
   validator: {
      $jsonSchema: {
         bsonType: "object",
         required: ["level", "message", "timestamp"],
         properties: {
            level: {
               enum: ["debug", "info", "warning", "error", "critical"]
            },
            message: {
               bsonType: "string"
            },
            source: {
               bsonType: "string"
            },
            user_id: {
               bsonType: "objectId"
            },
            details: {
               bsonType: "object"
            },
            timestamp: {
               bsonType: "date"
            }
         }
      }
   }
});

// Create indexes for optimal query performance

// Users indexes
db.users.createIndex({ "email": 1 }, { unique: true });
db.users.createIndex({ "username": 1 }, { unique: true });
db.users.createIndex({ "role": 1 });

// Mining sites indexes
db.mining_sites.createIndex({ "name": 1 });
db.mining_sites.createIndex({ "status": 1 });
db.mining_sites.createIndex({ "location.latitude": 1, "location.longitude": 1 });

// Devices indexes
db.devices.createIndex({ "device_id": 1 }, { unique: true });
db.devices.createIndex({ "site_id": 1 });
db.devices.createIndex({ "type": 1 });
db.devices.createIndex({ "status": 1 });
db.devices.createIndex({ "last_reading": 1 });

// Sensor readings indexes
db.sensor_readings.createIndex({ "device_id": 1, "timestamp": -1 });
db.sensor_readings.createIndex({ "timestamp": -1 });

// Predictions indexes
db.predictions.createIndex({ "site_id": 1, "timestamp": -1 });
db.predictions.createIndex({ "risk_level": 1 });
db.predictions.createIndex({ "timestamp": -1 });

// Alerts indexes
db.alerts.createIndex({ "timestamp": -1 });
db.alerts.createIndex({ "status": 1 });
db.alerts.createIndex({ "severity": 1 });
db.alerts.createIndex({ "site_id": 1 });

// System settings indexes
db.system_settings.createIndex({ "key": 1 }, { unique: true });

// System logs indexes
db.system_logs.createIndex({ "timestamp": -1 });
db.system_logs.createIndex({ "level": 1 });
db.system_logs.createIndex({ "source": 1 });

print("✅ Database initialization completed successfully!");
print("📊 Collections created with validation schemas");
print("🔍 Performance indexes created");
print("🚀 Ready for Rockfall Prediction System!");