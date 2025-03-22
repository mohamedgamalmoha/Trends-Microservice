#!/bin/bash

# Wait for database using pg_isready
echo "Waiting for database..."
until pg_isready -h users-db-serv -p 5432 -U users_db_user; do
  echo "Database is unavailable - sleeping"
  sleep 1
done
echo "Database is ready!"

# Run migrations
echo "Running migrations..."
alembic -c alembic.ini upgrade head

# Start the app
echo "Starting the app..."
uvicorn main:app --host 0.0.0.0 --port 80 --reload --http httptools --loop uvloop
