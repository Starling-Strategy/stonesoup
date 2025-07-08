# STONESOUP Database Migration Instructions

## Overview
This document provides comprehensive instructions for setting up and managing the STONESOUP database migrations using Alembic.

## Database Schema
The STONESOUP database consists of three main tables with proper multi-tenancy support:

1. **Cauldrons** - Organizations/workspaces (parent table)
2. **Members** - User profiles with semantic search capabilities 
3. **Stories** - Member contributions and achievements
4. **Story_Members** - Many-to-many relationship between stories and members

## Key Features

### Multi-Tenancy
- All tables include `cauldron_id` with NOT NULL constraints
- Proper foreign key relationships ensure data integrity
- Composite unique constraints prevent data leakage between cauldrons

### Semantic Search with pgvector
- **pgvector extension** is automatically installed
- **HNSW indexes** for efficient vector similarity search
- 1536-dimensional embeddings (compatible with OpenAI text-embedding-ada-002)

### HNSW Index Configuration
```sql
-- Member profile embeddings
CREATE INDEX ix_members_profile_embedding_hnsw 
ON members USING hnsw (profile_embedding vector_cosine_ops) 
WITH (m = 16, ef_construction = 64);

-- Story content embeddings  
CREATE INDEX ix_stories_embedding_hnsw 
ON stories USING hnsw (embedding vector_cosine_ops) 
WITH (m = 16, ef_construction = 64);
```

**HNSW Parameters Explained:**
- `m = 16`: Number of connections in the graph (higher = more accurate, more memory)
- `ef_construction = 64`: Search depth during index construction (higher = more accurate, slower builds)
- `vector_cosine_ops`: Use cosine similarity for distance calculations

## Migration Files

### Created Files
1. `/alembic/versions/001_initial_migration.py` - Complete initial schema
2. `/app/models/member.py` - Updated Member model with proper relationships
3. `/app/models/story.py` - Updated Story model with cauldron_id field
4. `/app/models/cauldron.py` - Updated Cauldron model with proper relationships
5. `/alembic/env.py` - Updated Alembic configuration

## Running Migrations

### Prerequisites
1. Ensure PostgreSQL is running with pgvector extension available
2. Update your `.env` file with a valid DATABASE_URL
3. Activate your virtual environment

### Migration Commands

```bash
# Activate virtual environment
source .venv/bin/activate

# Check current migration status
alembic current

# Show migration history
alembic history --verbose

# Apply migrations (run this to create all tables)
alembic upgrade head

# Check if migrations were applied successfully
alembic current
```

### Rollback Commands (Use with caution)

```bash
# Rollback to previous migration
alembic downgrade -1

# Rollback to specific revision
alembic downgrade <revision_id>

# Rollback all migrations (WARNING: This will drop all tables)
alembic downgrade base
```

## Database URL Configuration

Update your `.env` file with a valid PostgreSQL connection string:

```env
# Local development
DATABASE_URL=postgresql://username:password@localhost:5432/stonesoup

# Railway/Production
DATABASE_URL=postgresql://username:password@host:port/database?sslmode=require
```

## Verification Steps

After running migrations, verify your database:

```sql
-- Check tables exist
\dt

-- Check pgvector extension
SELECT * FROM pg_extension WHERE extname = 'vector';

-- Check HNSW indexes
SELECT indexname, indexdef 
FROM pg_indexes 
WHERE indexname LIKE '%hnsw%';

-- Verify table structures
\d cauldrons
\d members  
\d stories
\d story_members
```

## Troubleshooting

### Common Issues

1. **pgvector extension not found**
   ```bash
   # Install pgvector extension
   sudo apt-get install postgresql-15-pgvector
   # Or follow PGVECTOR_SETUP.md
   ```

2. **Invalid DATABASE_URL**
   - Ensure the URL format is correct
   - Check that the database exists and is accessible
   - Verify credentials are correct

3. **Migration fails with relationship errors**
   - Check that all model imports are correct in `alembic/env.py`
   - Ensure foreign key relationships are properly defined

### Development vs Production

**Development:**
- Use local PostgreSQL with pgvector
- Run migrations manually for testing
- Use `alembic downgrade` for quick schema changes

**Production:**
- Always backup database before migrations
- Test migrations on staging environment first
- Use `alembic upgrade head` in deployment scripts

## Best Practices

1. **Always backup before migrations** in production
2. **Test migrations** on a copy of production data
3. **Review migration files** before applying
4. **Use transactions** for complex migrations
5. **Monitor performance** after adding indexes

## Schema Highlights

### Cauldrons Table
- Multi-tenant organizations
- Configurable AI settings
- Subscription management
- Custom branding options

### Members Table
- Full user profiles
- Semantic search via embeddings
- Skills and expertise tracking
- Social media integration

### Stories Table
- Member contributions
- AI-generated content support
- Comprehensive metadata
- Review workflow support

### Story_Members Table
- Many-to-many relationships
- Role-based associations
- Multi-tenant constraints

## Support

For questions or issues:
1. Check the troubleshooting section above
2. Review the migration file comments
3. Consult the model documentation in each file
4. Check Alembic logs for detailed error messages