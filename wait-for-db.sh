#!/bin/sh

echo "Waiting for PostgreSQL to be ready..."

# Wait until the db is accepting connections
until nc -z "$DB_HOST" "$DB_PORT"; do
  sleep 1
done

echo "Database is up — starting Flask..."
exec flask run --host=0.0.0.0 --port=5000