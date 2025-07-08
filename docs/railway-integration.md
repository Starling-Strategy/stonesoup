# Railway Integration Guide

STONESOUP uses Railway for hosting backend services and databases. This guide explains how the automatic configuration works.

## Overview

The Railway integration provides:
- Automatic PostgreSQL connection configuration
- Automatic Redis connection configuration
- Service health monitoring
- Zero-configuration deployment

## How It Works

### 1. Automatic Configuration

When the backend starts, it automatically:
1. Connects to Railway API using `RAILWAY_TOKEN`
2. Retrieves PostgreSQL and Redis connection strings
3. Sets environment variables if not already configured
4. Verifies services are healthy

### 2. Environment Variables

Required Railway variables:
```bash
RAILWAY_TOKEN=your-railway-api-token
RAILWAY_PROJECT_ID=your-project-id
RAILWAY_ENVIRONMENT=production  # optional, defaults to production
```

### 3. Manual Override

You can still manually set database URLs:
```bash
DATABASE_URL=postgresql://user:pass@host:port/db
REDIS_URL=redis://user:pass@host:port
```

If these are set, Railway auto-config won't override them.

## Testing the Integration

Run the test script:
```bash
cd src/backend
python test_railway_config.py
```

Expected output:
```
🚀 STONESOUP Railway Configuration Test

=== Testing Railway API Client ===

✓ Railway client initialized
  Project ID: 3728a107-4a99-49ab-9f04-a8d63f24c86e
  Token: 77fd8100-2...

📋 Getting project information...
✓ Project: stonesoup (3728a107-4a99-49ab-9f04-a8d63f24c86e)

🐘 Getting PostgreSQL connection...
✓ PostgreSQL URL: postgresql://postgres:****@viaduct.proxy.rlwy.net:5432/railway

🔴 Getting Redis connection...
✓ Redis URL: redis://default:****@viaduct.proxy.rlwy.net:6379

💓 Checking service health...
  postgres: ✓ Healthy
  redis: ✓ Healthy
```

## Deployment

### 1. Create Railway Services

In your Railway project, create:
1. PostgreSQL service with pgvector extension
2. Redis service
3. Backend service (FastAPI)

### 2. Set Environment Variables

In Railway dashboard:
1. Go to your backend service
2. Add these variables:
   - `RAILWAY_TOKEN` (your API token)
   - `RAILWAY_PROJECT_ID` (from project settings)
   - `SENTRY_DSN` (your Sentry DSN)
   - `CLERK_SECRET_KEY` (from Clerk dashboard)
   - `OPENROUTER_API_KEY` (from OpenRouter)

### 3. Deploy

Railway will automatically:
1. Build the Docker image
2. Run database migrations
3. Start the FastAPI server
4. Configure database connections

## GraphQL API Reference

The Railway client uses these GraphQL queries:

### Get Project Info
```graphql
query GetProject($projectId: String!) {
  project(id: $projectId) {
    id
    name
    services {
      edges {
        node {
          id
          name
        }
      }
    }
  }
}
```

### Get Service Variables
```graphql
query GetServiceVariables($projectId: String!, $environmentName: String!) {
  project(id: $projectId) {
    environments {
      edges {
        node {
          name
          serviceInstances {
            edges {
              node {
                serviceName
                variables
              }
            }
          }
        }
      }
    }
  }
}
```

## Troubleshooting

### Connection Fails

1. Check Railway token is valid:
   ```bash
   curl -H "Authorization: Bearer $RAILWAY_TOKEN" \
        https://backboard.railway.app/graphql/v2
   ```

2. Verify project ID matches your Railway project

3. Ensure services are deployed and running in Railway

### Services Not Found

1. Service names must contain "postgres" or "redis"
2. Services must be in the "production" environment
3. Check Railway dashboard for actual service names

### Manual Configuration

If auto-config fails, set these manually:
```bash
# Get from Railway dashboard
export DATABASE_URL="postgresql://..."
export REDIS_URL="redis://..."
```

## Security Notes

1. Railway tokens are sensitive - never commit them
2. Connection strings contain passwords - use environment variables
3. The test script masks passwords in output
4. Use Railway's built-in SSL for database connections