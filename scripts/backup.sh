#!/bin/bash
# Backup database
docker compose exec -T db pg_dump -U addressbook_prod addressbook_prod > backups/db_$(date +%Y%m%d).sql

# Backup media files
tar -czvf backups/media_$(date +%Y%m%d).tar.gz media/

# Rotate backups (keep 7 days)
find backups/ -type f -mtime +7 -delete