#!/usr/bin/env python3
"""
STONESOUP Backend Startup Script

This script demonstrates the complete startup sequence:
1. Railway auto-configuration
2. Database connection verification
3. OpenRouter AI client testing
4. Sentry error tracking setup
"""
import asyncio
import os
import sys
from pathlib import Path

# Add the app directory to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from app.core.auto_config import ensure_railway_config
from app.ai import openrouter_client
from app.db.session import get_db, init_db
from app.core.config import settings
import sentry_sdk


async def main():
    """Main startup sequence."""
    print("""
    ╔══════════════════════════════════════════╗
    ║         STONESOUP Backend Startup        ║
    ╚══════════════════════════════════════════╝
    """)
    
    # Step 1: Railway Auto-Configuration
    print("\n1️⃣  Configuring from Railway...")
    try:
        connections = await ensure_railway_config()
        if connections:
            print("   ✅ Railway configuration successful")
        else:
            print("   ⚠️  Using manual configuration")
    except Exception as e:
        print(f"   ❌ Railway configuration failed: {e}")
    
    # Step 2: Verify Database Connection
    print("\n2️⃣  Testing database connection...")
    try:
        # This will use the auto-configured DATABASE_URL
        await init_db()
        print("   ✅ Database connected successfully")
        print(f"   📊 Using: {os.environ.get('DATABASE_URL', 'Not configured')[:50]}...")
    except Exception as e:
        print(f"   ❌ Database connection failed: {e}")
    
    # Step 3: Test OpenRouter AI
    print("\n3️⃣  Testing OpenRouter AI integration...")
    try:
        if os.environ.get("OPENROUTER_API_KEY"):
            # Quick test
            response = await openrouter_client.generate_text(
                "Say 'STONESOUP is ready!' in exactly 3 words."
            )
            print(f"   ✅ AI Response: {response.text}")
            print(f"   💰 Cost: ${response.cost:.4f}")
        else:
            print("   ⚠️  OPENROUTER_API_KEY not set - AI features disabled")
    except Exception as e:
        print(f"   ❌ OpenRouter test failed: {e}")
    
    # Step 4: Verify Sentry
    print("\n4️⃣  Checking Sentry error tracking...")
    if settings.SENTRY_DSN:
        print("   ✅ Sentry configured")
        print(f"   🔍 Environment: {settings.SENTRY_ENVIRONMENT}")
    else:
        print("   ⚠️  Sentry not configured - error tracking disabled")
    
    # Step 5: Check Clerk Auth
    print("\n5️⃣  Checking Clerk authentication...")
    if settings.CLERK_SECRET_KEY:
        print("   ✅ Clerk configured")
    else:
        print("   ❌ Clerk not configured - authentication will fail")
    
    # Summary
    print("\n" + "="*50)
    print("📊 Configuration Summary:")
    print(f"   Environment: {settings.ENVIRONMENT}")
    print(f"   Database: {'✅' if os.environ.get('DATABASE_URL') else '❌'}")
    print(f"   Redis: {'✅' if os.environ.get('REDIS_URL') else '❌'}")
    print(f"   AI (OpenRouter): {'✅' if os.environ.get('OPENROUTER_API_KEY') else '❌'}")
    print(f"   Auth (Clerk): {'✅' if settings.CLERK_SECRET_KEY else '❌'}")
    print(f"   Monitoring (Sentry): {'✅' if settings.SENTRY_DSN else '❌'}")
    
    print("\n✅ Startup checks complete!")
    print("\nTo start the API server, run:")
    print("  uvicorn app.main:app --reload")


if __name__ == "__main__":
    asyncio.run(main())