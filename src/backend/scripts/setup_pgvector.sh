#!/bin/bash

# STONESOUP PostgreSQL + pgvector Setup Script
# ============================================
# This script sets up PostgreSQL with the pgvector extension for vector similarity search
# pgvector allows storing and querying high-dimensional vectors, essential for AI/ML applications

# Color codes for output formatting
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Function to detect the operating system
detect_os() {
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "macos"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if [ -f /etc/debian_version ]; then
            echo "debian"
        elif [ -f /etc/redhat-release ]; then
            echo "redhat"
        else
            echo "linux"
        fi
    else
        echo "unknown"
    fi
}

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Main setup function
main() {
    print_info "Starting PostgreSQL + pgvector setup for STONESOUP..."
    
    OS=$(detect_os)
    print_info "Detected OS: $OS"
    
    # Step 1: Install PostgreSQL if not already installed
    print_info "Checking PostgreSQL installation..."
    
    if ! command_exists psql; then
        print_warning "PostgreSQL not found. Installing..."
        
        case $OS in
            "macos")
                # macOS installation using Homebrew
                if ! command_exists brew; then
                    print_error "Homebrew not found. Please install Homebrew first:"
                    print_error "Visit: https://brew.sh"
                    exit 1
                fi
                
                print_info "Installing PostgreSQL via Homebrew..."
                brew install postgresql@15
                
                # Start PostgreSQL service
                print_info "Starting PostgreSQL service..."
                brew services start postgresql@15
                
                # Add PostgreSQL to PATH
                echo 'export PATH="/opt/homebrew/opt/postgresql@15/bin:$PATH"' >> ~/.zshrc
                source ~/.zshrc
                ;;
                
            "debian")
                # Debian/Ubuntu installation
                print_info "Installing PostgreSQL on Debian/Ubuntu..."
                sudo apt-get update
                sudo apt-get install -y postgresql postgresql-contrib
                
                # Start PostgreSQL service
                sudo systemctl start postgresql
                sudo systemctl enable postgresql
                ;;
                
            "redhat")
                # RedHat/CentOS/Fedora installation
                print_info "Installing PostgreSQL on RedHat-based system..."
                sudo yum install -y postgresql-server postgresql-contrib
                sudo postgresql-setup initdb
                sudo systemctl start postgresql
                sudo systemctl enable postgresql
                ;;
                
            *)
                print_error "Unsupported OS. Please install PostgreSQL manually."
                exit 1
                ;;
        esac
    else
        print_success "PostgreSQL is already installed"
    fi
    
    # Step 2: Install pgvector extension
    print_info "Installing pgvector extension..."
    
    case $OS in
        "macos")
            # Check if pgvector is already installed via Homebrew
            if brew list pgvector &>/dev/null; then
                print_success "pgvector is already installed via Homebrew"
            else
                print_info "Installing pgvector via Homebrew..."
                brew install pgvector
            fi
            ;;
            
        "debian")
            # Install build dependencies for pgvector
            print_info "Installing build dependencies..."
            sudo apt-get install -y build-essential postgresql-server-dev-all git
            
            # Clone and build pgvector from source
            print_info "Building pgvector from source..."
            cd /tmp
            git clone --branch v0.5.1 https://github.com/pgvector/pgvector.git
            cd pgvector
            make
            sudo make install
            ;;
            
        "redhat")
            # Install build dependencies
            print_info "Installing build dependencies..."
            sudo yum install -y gcc make postgresql-devel git
            
            # Clone and build pgvector
            print_info "Building pgvector from source..."
            cd /tmp
            git clone --branch v0.5.1 https://github.com/pgvector/pgvector.git
            cd pgvector
            make
            sudo make install
            ;;
            
        *)
            print_error "Unsupported OS for pgvector installation"
            exit 1
            ;;
    esac
    
    # Step 3: Create STONESOUP database and user
    print_info "Setting up STONESOUP database..."
    
    # Create database user
    # Note: We're using peer authentication for the postgres user
    # This means we connect as the OS user 'postgres' to the PostgreSQL user 'postgres'
    
    if [[ "$OS" == "macos" ]]; then
        # On macOS, use the current user
        DB_USER=$(whoami)
    else
        # On Linux, use sudo to run as postgres user
        DB_USER="postgres"
    fi
    
    # Create the setup SQL script
    cat > /tmp/stonesoup_setup.sql << 'EOF'
-- Create STONESOUP user if it doesn't exist
-- Using CREATE USER ... IF NOT EXISTS is PostgreSQL 9.5+
DO
$$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_user WHERE usename = 'stonesoup_user') THEN
        CREATE USER stonesoup_user WITH PASSWORD 'stonesoup_secure_password';
    END IF;
END
$$;

-- Create STONESOUP database if it doesn't exist
-- We check pg_database to avoid errors if database already exists
SELECT 'CREATE DATABASE stonesoup_db OWNER stonesoup_user'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'stonesoup_db')\gexec

-- Grant all privileges on the database to the user
GRANT ALL PRIVILEGES ON DATABASE stonesoup_db TO stonesoup_user;
EOF
    
    # Execute the setup script
    if [[ "$OS" == "macos" ]]; then
        psql -U "$DB_USER" -f /tmp/stonesoup_setup.sql
    else
        sudo -u postgres psql -f /tmp/stonesoup_setup.sql
    fi
    
    # Step 4: Enable pgvector extension in the database
    print_info "Enabling pgvector extension in stonesoup_db..."
    
    cat > /tmp/enable_pgvector.sql << 'EOF'
-- Connect to stonesoup_db and enable pgvector
\c stonesoup_db

-- Create extension if it doesn't exist
-- pgvector provides vector data type and similarity search functions
CREATE EXTENSION IF NOT EXISTS vector;

-- Verify the extension is installed
SELECT extname, extversion FROM pg_extension WHERE extname = 'vector';
EOF
    
    if [[ "$OS" == "macos" ]]; then
        psql -U "$DB_USER" -f /tmp/enable_pgvector.sql
    else
        sudo -u postgres psql -f /tmp/enable_pgvector.sql
    fi
    
    # Step 5: Create example vector table
    print_info "Creating example vector table..."
    
    cat > /tmp/create_vector_table.sql << 'EOF'
-- Example table demonstrating pgvector usage
-- This table could store embeddings from various AI models

CREATE TABLE IF NOT EXISTS embeddings (
    id SERIAL PRIMARY KEY,
    
    -- Text content that was embedded
    content TEXT NOT NULL,
    
    -- Vector column storing embeddings
    -- 1536 dimensions is common for OpenAI embeddings
    -- You can adjust this based on your model
    embedding vector(1536),
    
    -- Metadata about the embedding
    model_name VARCHAR(255) DEFAULT 'text-embedding-ada-002',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Additional metadata as JSONB for flexibility
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Create indexes for efficient similarity search
-- HNSW (Hierarchical Navigable Small World) index for fast approximate nearest neighbor search
-- This is the recommended index type for most use cases
CREATE INDEX IF NOT EXISTS embeddings_embedding_hnsw_idx 
ON embeddings 
USING hnsw (embedding vector_cosine_ops);

-- Alternative index types (commented out, choose based on your needs):
-- IVFFlat index (requires less memory but slightly slower)
-- CREATE INDEX embeddings_embedding_ivfflat_idx ON embeddings USING ivfflat (embedding vector_l2_ops) WITH (lists = 100);

-- B-tree index on created_at for time-based queries
CREATE INDEX IF NOT EXISTS embeddings_created_at_idx ON embeddings(created_at);

-- GIN index on metadata for JSONB queries
CREATE INDEX IF NOT EXISTS embeddings_metadata_gin_idx ON embeddings USING GIN(metadata);

-- Grant permissions to stonesoup_user
GRANT ALL PRIVILEGES ON TABLE embeddings TO stonesoup_user;
GRANT USAGE, SELECT ON SEQUENCE embeddings_id_seq TO stonesoup_user;
EOF
    
    # Execute as stonesoup_user to ensure proper ownership
    PGPASSWORD='stonesoup_secure_password' psql -h localhost -U stonesoup_user -d stonesoup_db -f /tmp/create_vector_table.sql
    
    # Step 6: Create a test configuration file
    print_info "Creating database configuration file..."
    
    cat > database_config.env << 'EOF'
# STONESOUP PostgreSQL Configuration
# ==================================
# Source this file to set environment variables for database connection

# Database connection parameters
export PGHOST="localhost"
export PGPORT="5432"
export PGDATABASE="stonesoup_db"
export PGUSER="stonesoup_user"
export PGPASSWORD="stonesoup_secure_password"

# Connection string for various programming languages
export DATABASE_URL="postgresql://stonesoup_user:stonesoup_secure_password@localhost:5432/stonesoup_db"

# pgvector-specific settings
export VECTOR_DIMENSIONS="1536"  # Default for OpenAI embeddings
export HNSW_EF_CONSTRUCTION="200"  # Higher = better quality, slower build
export HNSW_M="16"  # Number of connections per layer

echo "Database configuration loaded!"
echo "Connection string: $DATABASE_URL"
EOF
    
    # Cleanup temporary files
    rm -f /tmp/stonesoup_setup.sql /tmp/enable_pgvector.sql /tmp/create_vector_table.sql
    
    print_success "PostgreSQL + pgvector setup completed successfully!"
    print_info "Database: stonesoup_db"
    print_info "User: stonesoup_user"
    print_info "Password: stonesoup_secure_password (CHANGE IN PRODUCTION!)"
    print_info ""
    print_info "Next steps:"
    print_info "1. Source the configuration: source database_config.env"
    print_info "2. Run the verification script: ./scripts/verify_pgvector.sh"
    print_info "3. Run the test script: python scripts/test_pgvector.py"
}

# Run the main function
main