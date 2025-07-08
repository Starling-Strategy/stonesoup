#!/usr/bin/env python3
"""
STONESOUP Seed Environment Setup Script

This script helps set up the environment for running the seed data generation,
including checking dependencies, database setup, and environment configuration.

Usage:
    python setup_seed_environment.py [--check-only] [--install-deps]
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path


def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ is required")
        return False
    print(f"✅ Python {sys.version.split()[0]} is compatible")
    return True


def check_postgresql():
    """Check if PostgreSQL is available."""
    try:
        result = subprocess.run(["psql", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ PostgreSQL found: {result.stdout.strip()}")
            return True
        else:
            print("❌ PostgreSQL not found in PATH")
            return False
    except FileNotFoundError:
        print("❌ PostgreSQL not installed or not in PATH")
        return False


def check_database_connection():
    """Check database connection."""
    try:
        # Try to import and test the database connection
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from app.core.config import settings
        import asyncio
        from app.db.session import get_db_context
        
        async def test_connection():
            try:
                async with get_db_context() as db:
                    result = await db.execute("SELECT 1")
                    return True
            except Exception as e:
                print(f"❌ Database connection failed: {e}")
                return False
        
        if asyncio.run(test_connection()):
            print("✅ Database connection successful")
            return True
        else:
            return False
            
    except Exception as e:
        print(f"❌ Cannot test database connection: {e}")
        return False


def check_pgvector_extension():
    """Check if pgvector extension is available."""
    try:
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        import asyncio
        from app.db.session import get_db_context
        
        async def test_pgvector():
            try:
                async with get_db_context() as db:
                    result = await db.execute("SELECT 1 FROM pg_extension WHERE extname = 'vector'")
                    if result.fetchone():
                        return True
                    else:
                        # Try to create the extension
                        await db.execute("CREATE EXTENSION IF NOT EXISTS vector")
                        result = await db.execute("SELECT 1 FROM pg_extension WHERE extname = 'vector'")
                        return bool(result.fetchone())
            except Exception as e:
                print(f"❌ pgvector extension check failed: {e}")
                return False
        
        if asyncio.run(test_pgvector()):
            print("✅ pgvector extension available")
            return True
        else:
            print("❌ pgvector extension not available")
            return False
            
    except Exception as e:
        print(f"❌ Cannot check pgvector extension: {e}")
        return False


def check_environment_variables():
    """Check required environment variables."""
    required_vars = {
        "OPENROUTER_API_KEY": "Required for embedding generation"
    }
    
    optional_vars = {
        "DATABASE_URL": "Uses config default if not set"
    }
    
    all_good = True
    
    print("\n📋 Environment Variables:")
    for var, description in required_vars.items():
        if os.getenv(var):
            print(f"   ✅ {var}: Set")
        else:
            print(f"   ❌ {var}: Not set ({description})")
            all_good = False
    
    for var, description in optional_vars.items():
        if os.getenv(var):
            print(f"   ✅ {var}: Set")
        else:
            print(f"   ⚠️  {var}: Not set ({description})")
    
    return all_good


def check_python_dependencies():
    """Check if required Python packages are installed."""
    required_packages = [
        "fastapi",
        "sqlalchemy",
        "asyncpg",
        "pgvector",
        "httpx",
        "numpy",
        "pydantic",
        "pydantic-settings"
    ]
    
    missing_packages = []
    
    print("\n📦 Python Dependencies:")
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print(f"   ✅ {package}")
        except ImportError:
            print(f"   ❌ {package}")
            missing_packages.append(package)
    
    return missing_packages


def install_dependencies():
    """Install missing Python dependencies."""
    print("\n🔧 Installing dependencies...")
    
    # Check if requirements.txt exists
    requirements_file = Path("requirements.txt")
    if requirements_file.exists():
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
            print("✅ Dependencies installed from requirements.txt")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install dependencies: {e}")
            return False
    else:
        print("❌ requirements.txt not found")
        return False


def create_env_template():
    """Create a .env template file."""
    env_template = """# STONESOUP Environment Configuration

# Database Configuration
DATABASE_URL=postgresql://stonesoup:stonesoup_dev@localhost:5432/stonesoup

# OpenRouter API Configuration (Required for embeddings)
OPENROUTER_API_KEY=your_openrouter_api_key_here

# Clerk Authentication (Optional for seed data)
CLERK_SECRET_KEY=your_clerk_secret_key_here
CLERK_PUBLISHABLE_KEY=your_clerk_publishable_key_here

# Application Settings
ENVIRONMENT=development
SECRET_KEY=your_secret_key_here

# Redis (Optional)
REDIS_URL=redis://localhost:6379

# Sentry (Optional)
SENTRY_DSN=your_sentry_dsn_here
"""
    
    env_file = Path(".env.example")
    if not env_file.exists():
        with open(env_file, "w") as f:
            f.write(env_template)
        print(f"✅ Created {env_file} template")
        print("   Copy this to .env and update with your actual values")
    else:
        print(f"⚠️  {env_file} already exists")


def print_setup_instructions():
    """Print setup instructions."""
    print("\n" + "="*60)
    print("SETUP INSTRUCTIONS")
    print("="*60)
    
    print("\n1. 🐘 PostgreSQL Setup:")
    print("   - Install PostgreSQL 13+ with pgvector extension")
    print("   - Create database: createdb stonesoup")
    print("   - Install pgvector: psql -d stonesoup -c 'CREATE EXTENSION vector;'")
    
    print("\n2. 🔑 API Keys:")
    print("   - Get OpenRouter API key from: https://openrouter.ai/")
    print("   - Add to .env file: OPENROUTER_API_KEY=your_key_here")
    
    print("\n3. 🐍 Python Environment:")
    print("   - Install dependencies: pip install -r requirements.txt")
    print("   - Or use: python setup_seed_environment.py --install-deps")
    
    print("\n4. 🌱 Running Seed Script:")
    print("   - Full seed: python seed_database.py --clear-existing --verbose")
    print("   - Quick seed: python seed_database.py --skip-embeddings --verbose")
    
    print("\n5. ✅ Validation:")
    print("   - Validate data: python validate_seed_data.py")
    print("   - Check search: python validate_seed_data.py --save-report")


def main():
    """Main setup and check function."""
    parser = argparse.ArgumentParser(description="Setup STONESOUP seed environment")
    parser.add_argument("--check-only", action="store_true", help="Only check environment, don't install")
    parser.add_argument("--install-deps", action="store_true", help="Install missing dependencies")
    
    args = parser.parse_args()
    
    print("🌱 STONESOUP Seed Environment Setup")
    print("=" * 50)
    
    # Run checks
    print("\n🔍 Environment Checks:")
    
    checks_passed = 0
    total_checks = 5
    
    if check_python_version():
        checks_passed += 1
    
    if check_postgresql():
        checks_passed += 1
    
    if check_database_connection():
        checks_passed += 1
    
    if check_pgvector_extension():
        checks_passed += 1
    
    if check_environment_variables():
        checks_passed += 1
    
    # Check Python dependencies
    missing_deps = check_python_dependencies()
    if not missing_deps:
        print("   ✅ All Python dependencies installed")
    else:
        print(f"   ❌ Missing {len(missing_deps)} Python packages")
    
    # Install dependencies if requested
    if args.install_deps and missing_deps:
        if install_dependencies():
            missing_deps = check_python_dependencies()  # Re-check
    
    # Create env template
    create_env_template()
    
    # Summary
    print(f"\n📊 Setup Summary:")
    print(f"   Checks Passed: {checks_passed}/{total_checks}")
    print(f"   Missing Dependencies: {len(missing_deps)}")
    
    if checks_passed == total_checks and not missing_deps:
        print("   🎉 Environment is ready for seeding!")
        print("\n   Next steps:")
        print("   1. Set OPENROUTER_API_KEY in .env file")
        print("   2. Run: python seed_database.py --clear-existing --verbose")
        return True
    else:
        print("   ⚠️  Environment needs attention")
        if not args.check_only:
            print_setup_instructions()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)