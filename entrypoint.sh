#!/bin/sh
set -e

# PostgreSQL connection parameters
DB_HOST="db"
DB_PORT="5432"
DB_USER="${POSTGRES_USER}"
DB_NAME="${POSTGRES_DB}"
MAX_ATTEMPTS=30
ATTEMPT=0
SLEEP_INTERVAL=5  # Reduced to 5 seconds for faster startup

# Wait for PostgreSQL to be available with better error handling
echo "Waiting for PostgreSQL to become available..."
echo "Testing connection to:"
echo "Host: $DB_HOST, Port: $DB_PORT"
echo "User: $DB_USER, Database: $DB_NAME"

until PGPASSWORD="${POSTGRES_PASSWORD}" psql \
      -h "$DB_HOST" \
      -p "$DB_PORT" \
      -U "$DB_USER" \
      -d "$DB_NAME" \
      -c '\q' >/dev/null 2>&1 || [ $ATTEMPT -eq $MAX_ATTEMPTS ]; do
  ATTEMPT=$((ATTEMPT+1))
  >&2 echo "PostgreSQL is unavailable (attempt ${ATTEMPT}/${MAX_ATTEMPTS}) - sleeping ${SLEEP_INTERVAL}s"
  sleep $SLEEP_INTERVAL
done

# Verify connection success
if [ $ATTEMPT -eq $MAX_ATTEMPTS ]; then
  >&2 echo "ERROR: Failed to connect to PostgreSQL after ${MAX_ATTEMPTS} attempts"
  >&2 echo "Last connection attempt output:"
  PGPASSWORD="${POSTGRES_PASSWORD}" psql \
    -h "$DB_HOST" \
    -p "$DB_PORT" \
    -U "$DB_USER" \
    -d "$DB_NAME" \
    -c '\q' || true
  exit 1
fi

echo "PostgreSQL connection successful - proceeding with startup"

# Database migrations
echo "Applying database migrations..."
if ! python manage.py migrate --noinput; then
  >&2 echo "ERROR: Database migrations failed"
  exit 1
fi

# Static files collection
echo "Collecting static files..."
if ! python manage.py collectstatic --noinput; then
  >&2 echo "ERROR: Static files collection failed"
  exit 1
fi

exec "$@"