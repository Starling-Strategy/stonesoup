# Environment Variables Setup Guide

This guide helps you obtain all necessary API keys and credentials for STONESOUP.

## 🔑 Required Services & Keys

### 1. PostgreSQL Database (Railway)
1. Sign up at [Railway](https://railway.app)
2. Create a new project
3. Add PostgreSQL service
4. Get the `DATABASE_URL` from the service settings
5. Enable pgvector extension in PostgreSQL

### 2. Redis (Railway)
1. In the same Railway project
2. Add Redis service
3. Get the `REDIS_URL` from the service settings

### 3. Clerk Authentication
1. Sign up at [Clerk](https://clerk.com)
2. Create a new application
3. From the dashboard, get:
   - `CLERK_SECRET_KEY` (Backend API Keys)
   - `CLERK_PUBLISHABLE_KEY` (Frontend API Keys)
   - Set up JWT verification key if using JWT templates

### 4. Google Gemini API
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Copy as `GEMINI_API_KEY`
4. Default models:
   - Text: `gemini-1.5-pro`
   - Embeddings: `text-embedding-004`

### 5. LangChain/LangGraph
1. Sign up at [LangSmith](https://smith.langchain.com)
2. Create a new project called "stonesoup"
3. Get your API key from settings
4. Copy as `LANGCHAIN_API_KEY`

### 6. Sentry Error Monitoring
1. Sign up at [Sentry](https://sentry.io)
2. Create a new project (one for backend, one for frontend)
3. Get the DSN from project settings
4. Copy as `SENTRY_DSN` and `NEXT_PUBLIC_SENTRY_DSN`

### 7. Railway Deployment Token
1. In Railway dashboard, go to Account Settings
2. Create a new token
3. Copy as `RAILWAY_TOKEN`
4. Get project ID from project settings

### 8. Vercel (Frontend)
1. Sign up at [Vercel](https://vercel.com)
2. Install Vercel CLI: `npm i -g vercel`
3. Run `vercel login`
4. Get token from account settings
5. Create project and get project/org IDs

## 🚀 Quick Setup Steps

1. **Copy the environment file:**
   ```bash
   cp .env.example .env
   ```

2. **Fill in required values** in order:
   - Database URLs (Railway)
   - Clerk keys
   - Gemini API key
   - LangChain key
   - Sentry DSNs

3. **Generate secure keys:**
   ```bash
   # Generate JWT_SECRET_KEY
   openssl rand -hex 32
   ```

4. **Verify setup:**
   ```bash
   # Check if all required vars are set
   source .env
   echo "Database: ${DATABASE_URL:0:20}..."
   echo "Clerk: ${CLERK_SECRET_KEY:0:20}..."
   echo "Gemini: ${GEMINI_API_KEY:0:20}..."
   ```

## 🎛️ Configuration Notes

### Development vs Production
- Use `development` for local work
- Change to `production` for deployment
- Adjust sample rates for Sentry in production

### Feature Flags
Control features via environment:
- `ENABLE_AI_PIPELINE`: Turn on/off AI processing
- `ENABLE_HUMAN_REVIEW`: Require human approval
- `ENABLE_AUTO_TAGGING`: Automatic tag generation

### Performance Tuning
- `RATE_LIMIT_*`: Adjust based on usage
- `MAX_TOKENS_*`: Control AI costs
- `SIMILARITY_THRESHOLD`: Tune search relevance

### Multi-tenancy
- `DEFAULT_CAULDRON_ID`: First tenant identifier
- Set up Clerk organizations for each cauldron

## 🔒 Security Reminders

1. **Never commit .env to git**
2. **Use different keys for dev/staging/prod**
3. **Rotate keys regularly**
4. **Use Railway/Vercel secrets for production**

## 📋 Verification Checklist

- [ ] PostgreSQL connection works
- [ ] Redis connection works
- [ ] Clerk authentication works
- [ ] Gemini API calls succeed
- [ ] Sentry receives test events
- [ ] LangChain tracing active

Run the verification script:
```bash
python scripts/verify_env.py
```