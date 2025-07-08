#!/usr/bin/env python3
"""
STONESOUP Database Migration Runner

This script helps run database migrations for the STONESOUP application.
It handles virtual environment activation and provides helpful feedback.

Usage:
    python run_migrations.py [command]

Commands:
    setup    - Initial database setup with pgvector extension
    migrate  - Run all pending migrations
    status   - Check current migration status
    history  - Show migration history
    rollback - Rollback the last migration (use with caution)
"""

import os
import sys
import subprocess
from pathlib import Path

def run_command(cmd, description=""):
    """Run a shell command and return the result."""
    print(f"\n🔄 {description}")
    print(f"Running: {cmd}")
    
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        if e.stderr:
            print(f"stderr: {e.stderr}")
        return False

def check_prerequisites():
    """Check if prerequisites are met."""
    print("🔍 Checking prerequisites...")
    
    # Check if .env file exists
    if not Path('.env').exists():
        print("❌ .env file not found. Please create it with your database configuration.")
        return False
    
    # Check if virtual environment exists
    if not Path('.venv').exists():
        print("❌ Virtual environment not found. Please run: python -m venv .venv")
        return False
    
    print("✅ Prerequisites check passed")
    return True

def setup_database():
    """Set up the database with pgvector extension."""
    print("\n🏗️ Setting up database with pgvector extension...")
    
    # Activate virtual environment and install pgvector
    activate_cmd = "source .venv/bin/activate"
    
    commands = [
        f"{activate_cmd} && pip install pgvector",
        f"{activate_cmd} && python -c \"from sqlalchemy import create_engine, text; from app.core.config import settings; engine = create_engine(str(settings.DATABASE_URL).replace('postgresql+asyncpg://', 'postgresql://')); conn = engine.connect(); conn.execute(text('CREATE EXTENSION IF NOT EXISTS vector')); conn.close(); print('✅ pgvector extension installed')\"",
    ]
    
    for cmd in commands:
        if not run_command(cmd):
            return False
    
    print("✅ Database setup completed")
    return True

def run_migrations():
    """Run database migrations."""
    print("\n🚀 Running database migrations...")
    
    activate_cmd = "source .venv/bin/activate"
    
    commands = [
        f"{activate_cmd} && alembic upgrade head",
        f"{activate_cmd} && alembic current",
    ]
    
    for cmd in commands:
        if not run_command(cmd):
            return False
    
    print("✅ Migrations completed successfully")
    return True

def check_status():
    """Check migration status."""
    print("\n📊 Checking migration status...")
    
    activate_cmd = "source .venv/bin/activate"
    run_command(f"{activate_cmd} && alembic current", "Current migration")
    run_command(f"{activate_cmd} && alembic history --verbose", "Migration history")

def rollback_migration():
    """Rollback the last migration."""
    print("\n⚠️  WARNING: This will rollback the last migration!")
    response = input("Are you sure you want to continue? (yes/no): ")
    
    if response.lower() != 'yes':
        print("❌ Rollback cancelled")
        return
    
    activate_cmd = "source .venv/bin/activate"
    if run_command(f"{activate_cmd} && alembic downgrade -1", "Rolling back migration"):
        print("✅ Rollback completed")
    else:
        print("❌ Rollback failed")

def main():
    """Main function to handle command line arguments."""
    if not check_prerequisites():
        sys.exit(1)
    
    command = sys.argv[1] if len(sys.argv) > 1 else 'help'
    
    if command == 'setup':
        if not setup_database():
            sys.exit(1)
    elif command == 'migrate':
        if not run_migrations():
            sys.exit(1)
    elif command == 'status':
        check_status()
    elif command == 'history':
        activate_cmd = "source .venv/bin/activate"
        run_command(f"{activate_cmd} && alembic history --verbose", "Migration history")
    elif command == 'rollback':
        rollback_migration()
    else:
        print(__doc__)
        sys.exit(1)

if __name__ == "__main__":
    main()