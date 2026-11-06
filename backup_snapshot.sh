#!/usr/bin/env bash
set -euo pipefail

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_DIR="/opt/leadpulse360/backups"
ARCHIVE_NAME="leadpulse_backup_${TIMESTAMP}.tar.gz"

# 1. Archive SQLite and audit files from the local SSD volume
tar -czf "${BACKUP_DIR}/${ARCHIVE_NAME}" -C /opt/leadpulse360 data

# 2. Sync to off-site cloud storage if rclone 'gdrive' remote is configured
if command -v rclone &> /dev/null && rclone listremotes | grep -q "^gdrive:"; then
    rclone copy "${BACKUP_DIR}/${ARCHIVE_NAME}" gdrive:LeadPulse360_Backups/
fi

# 3. Retain only the last 7 local snapshots on the VPS SSD
find "${BACKUP_DIR}" -name "leadpulse_backup_*.tar.gz" -type f -mtime +7 -delete
