#!/bin/bash

# STONESOUP Database Setup Script
# This script sets up PostgreSQL with pgvector extension for the STONESOUP project
# It creates the database, installs pgvector, and prepares the environment for vector similarity search

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
DB_NAME="stonesoup"
DB_USER="stonesoup_user"
DB_PASSWORD="stonesoup_pass"
DB_HOST="localhost"
DB_PORT="5432"

echo -e "${GREEN}=== STONESOUP Database Setup ===${NC}"
echo "This script will set up PostgreSQL with pgvector for STONESOUP"
echo ""

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check if PostgreSQL is installed
if ! command_exists psql; then
    echo -e "${RED}Error: PostgreSQL is not installed${NC}"
    echo "Please install PostgreSQL first:"
    echo "  macOS: brew install postgresql"
    echo "  Ubuntu: sudo apt-get install postgresql postgresql-contrib"
    exit 1
fi

# Check if PostgreSQL is running
if ! pg_isready -q; then
    echo -e "${YELLOW}PostgreSQL is not running. Attempting to start...${NC}"
    if [[ "$OSTYPE" == "darwin"* ]]; then
        brew services start postgresql
    else
        sudo systemctl start postgresql
    fi
    sleep 2
fi

echo -e "${GREEN}Step 1: Creating database and user${NC}"

# Create user and database
# Note: In production, use stronger passwords and proper security measures
psql -U postgres <<EOF
-- Drop existing connections to the database if it exists
SELECT pg_terminate_backend(pg_stat_activity.pid)
FROM pg_stat_activity
WHERE pg_stat_activity.datname = '${DB_NAME}'
  AND pid <> pg_backend_pid();

-- Create user if not exists
DO \$\$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_user WHERE usename = '${DB_USER}') THEN
        CREATE USER ${DB_USER} WITH PASSWORD '${DB_PASSWORD}';
    END IF;
END
\$\$;

-- Drop and recreate database
DROP DATABASE IF EXISTS ${DB_NAME};
CREATE DATABASE ${DB_NAME} OWNER ${DB_USER};

-- Grant all privileges
GRANT ALL PRIVILEGES ON DATABASE ${DB_NAME} TO ${DB_USER};
EOF

if [ $? -ne 0 ]; then
    echo -e "${RED}Error: Failed to create database${NC}"
    exit 1
fi

echo -e "${GREEN}Step 2: Installing pgvector extension${NC}"

# Install pgvector
# For macOS with Homebrew
if [[ "$OSTYPE" == "darwin"* ]]; then
    if ! brew list pgvector >/dev/null 2>&1; then
        echo "Installing pgvector via Homebrew..."
        brew install pgvector
    fi
fi

# Connect to the new database and create pgvector extension
psql -U postgres -d ${DB_NAME} <<EOF
-- Create pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Verify installation
SELECT extname, extversion FROM pg_extension WHERE extname = 'vector';

-- Create a test table to verify vector operations work
CREATE TABLE IF NOT EXISTS vector_test (
    id SERIAL PRIMARY KEY,
    embedding vector(3)
);

-- Insert test data
INSERT INTO vector_test (embedding) VALUES 
    ('[1,2,3]'::vector),
    ('[4,5,6]'::vector);

-- Test similarity search
SELECT id, embedding, embedding <-> '[1,2,3]'::vector as distance
FROM vector_test
ORDER BY embedding <-> '[1,2,3]'::vector
LIMIT 5;

-- Clean up test table
DROP TABLE vector_test;
EOF

if [ $? -ne 0 ]; then
    echo -e "${RED}Error: Failed to install pgvector extension${NC}"
    echo "You may need to install pgvector manually:"
    echo "  macOS: brew install pgvector"
    echo "  Ubuntu: sudo apt install postgresql-14-pgvector"
    exit 1
fi

echo -e "${GREEN}Step 3: Creating .env file for database connection${NC}"

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    cat > .env <<EOF
# STONESOUP Database Configuration
DATABASE_URL=postgresql://${DB_USER}:${DB_PASSWORD}@${DB_HOST}:${DB_PORT}/${DB_NAME}
DB_NAME=${DB_NAME}
DB_USER=${DB_USER}
DB_PASSWORD=${DB_PASSWORD}
DB_HOST=${DB_HOST}
DB_PORT=${DB_PORT}

# Vector dimension for embeddings (adjust based on your model)
EMBEDDING_DIMENSION=1536
EOF
    echo -e "${GREEN}Created .env file with database configuration${NC}"
else
    echo -e "${YELLOW}.env file already exists, skipping creation${NC}"
fi

echo ""
echo -e "${GREEN}=== Setup Complete! ===${NC}"
echo ""
echo "Database Details:"
echo "  Name: ${DB_NAME}"
echo "  User: ${DB_USER}"
echo "  Host: ${DB_HOST}:${DB_PORT}"
echo "  Connection: postgresql://${DB_USER}:${DB_PASSWORD}@${DB_HOST}:${DB_PORT}/${DB_NAME}"
echo ""
echo "pgvector extension has been installed and verified."
echo ""
echo "Next steps:"
echo "1. Run the verification script: python verify_pgvector.py"
echo "2. Run database migrations to create tables"
echo "3. Start developing with vector similarity search!"