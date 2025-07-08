-- Initialize PostgreSQL database for STONESOUP
-- This script runs automatically when the Docker container starts

-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Enable UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create enum types
CREATE TYPE story_status AS ENUM ('draft', 'published', 'archived');
CREATE TYPE confidence_level AS ENUM ('low', 'medium', 'high', 'verified');

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Grant permissions to the application user
GRANT ALL PRIVILEGES ON DATABASE stonesoup TO stonesoup;
GRANT ALL ON SCHEMA public TO stonesoup;

-- Create indexes for better performance
-- Note: Actual table creation will be handled by Alembic migrations

-- Example of creating an HNSW index for vector similarity search (after tables are created):
-- CREATE INDEX idx_members_embedding_hnsw ON members USING hnsw (embedding vector_cosine_ops);
-- CREATE INDEX idx_stories_embedding_hnsw ON stories USING hnsw (embedding vector_cosine_ops);

-- Row Level Security policies will be added by migrations

-- Performance settings for pgvector
ALTER SYSTEM SET max_parallel_workers_per_gather = 4;
ALTER SYSTEM SET max_parallel_workers = 8;
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET work_mem = '16MB';

-- Settings for vector operations
ALTER SYSTEM SET ivfflat.probes = 10;

-- Apply settings
SELECT pg_reload_conf();

-- Create a function to search similar vectors with tenant isolation
CREATE OR REPLACE FUNCTION search_similar_vectors(
    table_name text,
    cauldron_id_param text,
    query_embedding vector,
    limit_param integer DEFAULT 10
)
RETURNS TABLE(
    id uuid,
    similarity float
) AS $$
BEGIN
    RETURN QUERY EXECUTE format('
        SELECT id, 1 - (embedding <=> %L) as similarity
        FROM %I
        WHERE cauldron_id = %L
        ORDER BY embedding <=> %L
        LIMIT %s
    ', query_embedding, table_name, cauldron_id_param, query_embedding, limit_param);
END;
$$ LANGUAGE plpgsql STABLE;

-- Create audit log table
CREATE TABLE IF NOT EXISTS audit_logs (
    id uuid DEFAULT uuid_generate_v4() PRIMARY KEY,
    cauldron_id VARCHAR(255) NOT NULL,
    user_id VARCHAR(255),
    action VARCHAR(100) NOT NULL,
    table_name VARCHAR(100),
    record_id uuid,
    old_values jsonb,
    new_values jsonb,
    ip_address inet,
    user_agent text,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_audit_logs_cauldron_id ON audit_logs(cauldron_id);
CREATE INDEX idx_audit_logs_created_at ON audit_logs(created_at);

-- Notify that database is ready
DO $$
BEGIN
    RAISE NOTICE 'STONESOUP database initialization complete!';
    RAISE NOTICE 'pgvector extension enabled';
    RAISE NOTICE 'Ready for Alembic migrations';
END $$;