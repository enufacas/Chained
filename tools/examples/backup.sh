#!/bin/bash
#
# Simple backup script
# Creates a backup of specified directory
#

# Configuration
source_directory="/home/user/documents"
backup_directory="/home/user/backups"
timestamp=$(date +"%Y%m%d_%H%M%S")
backup_name="backup_${timestamp}.tar.gz"

# Create backup directory if it doesn't exist
if [ ! -d "${backup_directory}" ]; then
    mkdir -p "${backup_directory}"
    echo "Created backup directory: ${backup_directory}"
fi

# Check if source directory exists
if [ ! -d "${source_directory}" ]; then
    echo "Error: Source directory does not exist: ${source_directory}"
    exit 1
fi

# Create the backup
echo "Creating backup..."
tar -czf "${backup_directory}/${backup_name}" "${source_directory}"

# Check if backup was successful
if [ $? -eq 0 ]; then
    echo "Backup created successfully: ${backup_directory}/${backup_name}"
    
    # Display backup size
    backup_size=$(du -h "${backup_directory}/${backup_name}" | cut -f1)
    echo "Backup size: ${backup_size}"
else
    echo "Error: Backup failed"
    exit 1
fi

# Clean up old backups (keep only last 5)
echo "Cleaning up old backups..."
cd "${backup_directory}"
ls -t backup_*.tar.gz | tail -n +6 | xargs -r rm
echo "Cleanup complete"
