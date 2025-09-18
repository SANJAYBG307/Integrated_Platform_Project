#!/bin/bash

# AI Productivity Platform Database Backup Script
# This script creates a backup of the MySQL database

set -e

# Configuration
DB_NAME="Integrated_Platform"
DB_USER="Saas_User"
DB_PASSWORD="Saas@123"
DB_HOST="localhost"
DB_PORT="3306"

# Backup directory
BACKUP_DIR="../backups"
mkdir -p "$BACKUP_DIR"

# Generate timestamp
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="$BACKUP_DIR/ai_platform_backup_$TIMESTAMP.sql"

echo "Starting database backup..."

# Create backup
mysqldump \
    --host="$DB_HOST" \
    --port="$DB_PORT" \
    --user="$DB_USER" \
    --password="$DB_PASSWORD" \
    --single-transaction \
    --routines \
    --triggers \
    --events \
    --add-drop-database \
    --databases "$DB_NAME" > "$BACKUP_FILE"

# Compress backup
gzip "$BACKUP_FILE"
BACKUP_FILE="$BACKUP_FILE.gz"

echo "Database backup completed: $BACKUP_FILE"

# Get file size
BACKUP_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
echo "Backup size: $BACKUP_SIZE"

# Clean up old backups (keep last 7 days)
find "$BACKUP_DIR" -name "ai_platform_backup_*.sql.gz" -mtime +7 -delete

echo "Backup process finished successfully!"