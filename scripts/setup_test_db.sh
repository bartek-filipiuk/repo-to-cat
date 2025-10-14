#!/bin/bash
# Setup test database for running tests
#
# This script creates a separate test database to ensure tests never
# touch production data. Run this once before running tests.

set -e

echo "Setting up test database..."

# Database configuration
DB_USER="repo_user"
DB_PASSWORD="repo_password"
DB_HOST="localhost"
DB_PORT="5434"
TEST_DB="repo_to_cat_test"

# Check if PostgreSQL is running
if ! docker compose ps postgres | grep -q "running"; then
    echo "Starting PostgreSQL container..."
    docker compose up -d postgres
    sleep 3
fi

# Drop test database if it exists (clean slate)
echo "Dropping existing test database (if exists)..."
PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d postgres \
    -c "DROP DATABASE IF EXISTS $TEST_DB;" 2>/dev/null || true

# Create test database
echo "Creating test database: $TEST_DB"
PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d postgres \
    -c "CREATE DATABASE $TEST_DB;"

# Run migrations on test database
echo "Running Alembic migrations on test database..."
export DATABASE_URL="postgresql://$DB_USER:$DB_PASSWORD@$DB_HOST:$DB_PORT/$TEST_DB"
alembic upgrade head

echo ""
echo "✅ Test database setup complete!"
echo ""
echo "Test database: $TEST_DB"
echo "Connection: postgresql://$DB_USER:$DB_PASSWORD@$DB_HOST:$DB_PORT/$TEST_DB"
echo ""
echo "You can now run tests with: pytest"
