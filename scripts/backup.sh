#!/bin/bash
# MongoDB Backup Script

set -e

# Configuration
BACKUP_DIR="/backup"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="rockfall_backup_${DATE}"
MONGO_HOST="mongodb"
MONGO_PORT="27017"

# Create backup directory
mkdir -p "$BACKUP_DIR"

echo "Starting MongoDB backup at $(date)"

# Perform backup
mongodump \
  --host ${MONGO_HOST}:${MONGO_PORT} \
  --username ${MONGO_ROOT_USERNAME} \
  --password ${MONGO_ROOT_PASSWORD} \
  --authenticationDatabase admin \
  --db ${MONGO_DATABASE} \
  --out ${BACKUP_DIR}/${BACKUP_NAME}

# Compress backup
cd ${BACKUP_DIR}
tar -czf ${BACKUP_NAME}.tar.gz ${BACKUP_NAME}
rm -rf ${BACKUP_NAME}

echo "Backup completed: ${BACKUP_NAME}.tar.gz"

# Cleanup old backups (keep last 30 days)
find ${BACKUP_DIR} -name "rockfall_backup_*.tar.gz" -mtime +30 -delete

echo "Backup cleanup completed"

# Optional: Upload to cloud storage
# aws s3 cp ${BACKUP_DIR}/${BACKUP_NAME}.tar.gz s3://your-bucket/backups/
# gsutil cp ${BACKUP_DIR}/${BACKUP_NAME}.tar.gz gs://your-bucket/backups/

echo "Backup process finished at $(date)"