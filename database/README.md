# MongoDB Database Setup for Rockfall Prediction System

## Collections Overview

This document outlines the MongoDB collections used in the Rockfall Prediction & Alert System.

### Collection List

1. **users** - User authentication and roles
2. **dem_collection** - Digital Elevation Model data
3. **drone_images** - Drone imagery metadata
4. **sensor_timeseries** - Time-series sensor data
5. **environmental_data** - Weather and environmental readings
6. **predictions** - AI model predictions and risk assessments
7. **alerts** - System alerts and notifications
8. **sites** - Mining site information
9. **models** - ML model metadata and versions

### Indexing Strategy

- **Geospatial Indexes**: 2dsphere on location fields
- **Time-series Indexes**: Compound indexes on timestamp + site_id
- **Search Indexes**: Text indexes on search fields
- **Performance Indexes**: Site-based partitioning indexes

### Backup Strategy

- Daily automated backups
- Point-in-time recovery enabled
- Cross-region replication for disaster recovery

### Security

- Role-based access control (RBAC)
- Field-level encryption for sensitive data
- Connection encryption (TLS)
- IP whitelisting

## Setup Instructions

1. Run `init_database.py` to create collections and indexes
2. Run `seed_demo_data.py` to populate with sample data
3. Configure connection string in environment variables
4. Enable monitoring and alerting