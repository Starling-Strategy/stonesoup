#!/usr/bin/env python3
"""
Test script to verify Railway configuration works correctly.

This script:
1. Tests the Railway API client
2. Retrieves database connection strings
3. Verifies services are running
4. Tests the auto-configuration
"""
import asyncio
import os
import sys
from pathlib import Path

# Add the app directory to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from app.core.railway_client import get_railway_client
from app.core.auto_config import ensure_railway_config


async def test_railway_client():
    """Test Railway API client functionality."""
    print("=== Testing Railway API Client ===\n")
    
    try:
        client = get_railway_client()
        print(f"✓ Railway client initialized")
        print(f"  Project ID: {client.project_id}")
        print(f"  Token: {client.token[:10]}...")
        
        # Test getting project info
        print("\n📋 Getting project information...")
        try:
            project = await client.get_project_info()
            print(f"✓ Project: {project.name} ({project.id})")
        except Exception as e:
            print(f"✗ Failed to get project info: {e}")
        
        # Test getting PostgreSQL URL
        print("\n🐘 Getting PostgreSQL connection...")
        try:
            db_url = await client.get_database_url()
            # Mask password for security
            masked_url = db_url.split('@')[0].rsplit(':', 1)[0] + ':****@' + db_url.split('@')[1] if '@' in db_url else db_url
            print(f"✓ PostgreSQL URL: {masked_url}")
        except Exception as e:
            print(f"✗ Failed to get PostgreSQL URL: {e}")
        
        # Test getting Redis URL
        print("\n🔴 Getting Redis connection...")
        try:
            redis_url = await client.get_redis_url()
            # Mask password for security
            masked_url = redis_url.split('@')[0].rsplit(':', 1)[0] + ':****@' + redis_url.split('@')[1] if '@' in redis_url else redis_url
            print(f"✓ Redis URL: {masked_url}")
        except Exception as e:
            print(f"✗ Failed to get Redis URL: {e}")
        
        # Test getting all services
        print("\n🔍 Getting all service connections...")
        try:
            connections = await client.get_all_services()
            for service, url in connections.items():
                if url:
                    masked_url = url.split('@')[0].rsplit(':', 1)[0] + ':****@' + url.split('@')[1] if '@' in url else url
                    print(f"✓ {service}: {masked_url}")
                else:
                    print(f"✗ {service}: Not found")
        except Exception as e:
            print(f"✗ Failed to get services: {e}")
        
        # Test service health
        print("\n💓 Checking service health...")
        try:
            health = await client.verify_services()
            for service, is_healthy in health.items():
                status = "✓ Healthy" if is_healthy else "✗ Not healthy"
                print(f"  {service}: {status}")
        except Exception as e:
            print(f"✗ Failed to check health: {e}")
            
    except Exception as e:
        print(f"✗ Railway client test failed: {e}")
        import traceback
        traceback.print_exc()


async def test_auto_config():
    """Test automatic configuration."""
    print("\n\n=== Testing Auto Configuration ===\n")
    
    # Clear existing env vars to test auto-config
    original_db = os.environ.get("DATABASE_URL")
    original_redis = os.environ.get("REDIS_URL")
    
    if original_db:
        del os.environ["DATABASE_URL"]
    if original_redis:
        del os.environ["REDIS_URL"]
    
    try:
        # Test auto configuration
        print("🔧 Running auto-configuration...")
        connections = await ensure_railway_config()
        
        if connections:
            print(f"✓ Auto-configuration successful")
            print(f"  Services configured: {list(connections.keys())}")
            
            # Check if environment variables were set
            if os.environ.get("DATABASE_URL"):
                print("✓ DATABASE_URL was set automatically")
            else:
                print("✗ DATABASE_URL was not set")
                
            if os.environ.get("REDIS_URL"):
                print("✓ REDIS_URL was set automatically")
            else:
                print("✗ REDIS_URL was not set")
        else:
            print("✗ Auto-configuration failed (no connections returned)")
            
    except Exception as e:
        print(f"✗ Auto-configuration test failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Restore original env vars
        if original_db:
            os.environ["DATABASE_URL"] = original_db
        if original_redis:
            os.environ["REDIS_URL"] = original_redis


async def main():
    """Run all tests."""
    print("🚀 STONESOUP Railway Configuration Test\n")
    
    # Check for Railway token
    if not os.environ.get("RAILWAY_TOKEN"):
        print("⚠️  RAILWAY_TOKEN not set in environment")
        print("   Please set RAILWAY_TOKEN to test Railway integration")
        return
    
    if not os.environ.get("RAILWAY_PROJECT_ID"):
        print("⚠️  RAILWAY_PROJECT_ID not set in environment")
        print("   Please set RAILWAY_PROJECT_ID to test Railway integration")
        return
    
    # Run tests
    await test_railway_client()
    await test_auto_config()
    
    print("\n✅ All tests completed!")


if __name__ == "__main__":
    asyncio.run(main())