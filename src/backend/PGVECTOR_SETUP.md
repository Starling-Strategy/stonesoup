# PostgreSQL with pgvector Setup for STONESOUP

This document explains how to set up PostgreSQL with pgvector extension for the STONESOUP project, including the corrected database schema with HNSW indexes.

## Overview

STONESOUP uses PostgreSQL with the pgvector extension to enable semantic search capabilities through vector embeddings. The setup includes:

1. **Database Creation**: PostgreSQL database with pgvector extension
2. **Schema Updates**: Corrected models with cauldron_id in all tables
3. **HNSW Indexes**: High-performance vector similarity search indexes
4. **Verification**: Comprehensive testing of pgvector functionality

## Files Created

### 1. `setup_db.sh` - Database Setup Script
- **Purpose**: Automated setup of PostgreSQL with pgvector
- **Features**:
  - Checks for PostgreSQL installation
  - Creates database and user
  - Installs pgvector extension
  - Generates `.env` file with connection details
  - Includes educational comments explaining each step

### 2. `verify_pgvector.py` - Verification Script
- **Purpose**: Comprehensive testing of pgvector functionality
- **Tests**:
  - Extension installation verification
  - Basic vector operations (distance calculations)
  - HNSW index creation and performance
  - STONESOUP schema validation with cauldron_id

### 3. Updated Database Models
- **Files Modified**:
  - `app/models/story.py` - HNSW index for embeddings
  - `app/models/member.py` - HNSW index for profile embeddings
- **Key Changes**:
  - Replaced IVFFlat indexes with HNSW
  - Added educational comments about HNSW benefits
  - Configured optimal HNSW parameters (m=16, ef_construction=64)

## Quick Start

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run Database Setup**:
   ```bash
   ./setup_db.sh
   ```

3. **Verify Installation**:
   ```bash
   python verify_pgvector.py
   ```

## Database Schema Overview

### Multi-Tenancy with cauldron_id
All tables include `cauldron_id` for proper data isolation:
- **cauldrons**: Organizations/workspaces
- **members**: Users within cauldrons
- **stories**: Content with embeddings for semantic search

### Vector Embeddings
- **stories.embedding**: 1536-dimensional vectors for story content
- **members.profile_embedding**: 1536-dimensional vectors for member profiles
- **Both use HNSW indexes** for optimal similarity search performance

### HNSW Index Configuration
```sql
-- Example HNSW index configuration
CREATE INDEX ix_stories_embedding_hnsw 
ON stories USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);
```

**Parameters Explained**:
- `m = 16`: Number of bi-directional links per node (trade-off between recall and index size)
- `ef_construction = 64`: Size of dynamic candidate list during construction
- `vector_cosine_ops`: Use cosine distance for similarity

## Environment Variables

The setup script creates a `.env` file with:
```env
DATABASE_URL=postgresql://stonesoup_user:stonesoup_pass@localhost:5432/stonesoup
DB_NAME=stonesoup
DB_USER=stonesoup_user
DB_PASSWORD=stonesoup_pass
DB_HOST=localhost
DB_PORT=5432
EMBEDDING_DIMENSION=1536
```

## Vector Search Examples

### Semantic Story Search
```python
# Find similar stories using cosine similarity
query = "machine learning project"
results = await conn.fetch("""
    SELECT title, content, embedding <-> $1::vector as distance
    FROM stories
    WHERE cauldron_id = $2
    ORDER BY embedding <-> $1::vector
    LIMIT 10
""", query_embedding, cauldron_id)
```

### Member Profile Search
```python
# Find members with similar profiles
results = await conn.fetch("""
    SELECT name, bio, profile_embedding <-> $1::vector as distance
    FROM members
    WHERE cauldron_id = $2 AND is_active = true
    ORDER BY profile_embedding <-> $1::vector
    LIMIT 10
""", profile_embedding, cauldron_id)
```

## Performance Considerations

### HNSW vs IVFFlat
- **HNSW**: Better for high-dimensional vectors (1536 dims), faster queries
- **IVFFlat**: Better for lower-dimensional vectors, requires training

### Index Parameters
- **m**: Higher values = better recall, larger index size
- **ef_construction**: Higher values = better index quality, slower construction
- **ef_search**: Query-time parameter for recall vs speed trade-off

## Troubleshooting

### Common Issues
1. **pgvector not installed**: Install via `brew install pgvector` (macOS) or package manager
2. **Permission denied**: Ensure PostgreSQL user has proper permissions
3. **Connection refused**: Check if PostgreSQL is running

### Verification Failures
- Run `python verify_pgvector.py` to identify specific issues
- Check PostgreSQL logs for detailed error messages
- Ensure all dependencies are installed: `pip install asyncpg numpy python-dotenv`

## Next Steps

1. **Run Migrations**: Use Alembic to create the database schema
2. **Generate Embeddings**: Create embeddings for existing content
3. **Implement Search**: Add semantic search endpoints to the API
4. **Monitor Performance**: Track query performance and adjust HNSW parameters

## Additional Resources

- [pgvector Documentation](https://github.com/pgvector/pgvector)
- [HNSW Algorithm](https://arxiv.org/abs/1603.09320)
- [PostgreSQL Vector Operations](https://github.com/pgvector/pgvector#vector-operations)