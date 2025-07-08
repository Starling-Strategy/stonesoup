"""
Automatic configuration using Railway API.

This module automatically retrieves database connection strings
from Railway when the application starts.
"""
import os
import asyncio
from typing import Dict, Any, Optional
import sentry_sdk

from app.core.railway_client import get_railway_client


class AutoConfig:
    """Automatically configure database connections from Railway."""
    
    _instance = None
    _configured = False
    _connection_strings: Dict[str, str] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    async def configure(self) -> Dict[str, str]:
        """
        Retrieve and configure all connection strings from Railway.
        
        Returns:
            Dictionary of connection strings
        """
        if self._configured:
            return self._connection_strings
            
        try:
            client = get_railway_client()
            
            # Get all connection strings
            connections = await client.get_all_services()
            
            # Update environment variables if not already set
            if connections.get("postgresql") and not os.environ.get("DATABASE_URL"):
                os.environ["DATABASE_URL"] = connections["postgresql"]
                print("✓ Configured PostgreSQL connection from Railway")
                
            if connections.get("redis") and not os.environ.get("REDIS_URL"):
                os.environ["REDIS_URL"] = connections["redis"]
                print("✓ Configured Redis connection from Railway")
                
            self._connection_strings = connections
            self._configured = True
            
            # Verify services are running
            service_status = await client.verify_services()
            for service, is_healthy in service_status.items():
                status = "✓" if is_healthy else "✗"
                print(f"{status} Service '{service}' is {'healthy' if is_healthy else 'not healthy'}")
                
            return connections
            
        except Exception as e:
            print(f"Warning: Could not auto-configure from Railway: {e}")
            sentry_sdk.capture_exception(e)
            
            # Return empty dict on failure
            return {}
    
    async def get_database_url(self) -> Optional[str]:
        """Get PostgreSQL URL, auto-configuring if needed."""
        if not self._configured:
            await self.configure()
        return self._connection_strings.get("postgresql")
    
    async def get_redis_url(self) -> Optional[str]:
        """Get Redis URL, auto-configuring if needed."""
        if not self._configured:
            await self.configure()
        return self._connection_strings.get("redis")
    
    def reset(self):
        """Reset configuration (useful for testing)."""
        self._configured = False
        self._connection_strings = {}


# Global instance
auto_config = AutoConfig()


async def ensure_railway_config():
    """
    Ensure Railway configuration is loaded.
    Call this at application startup.
    """
    config = auto_config
    connections = await config.configure()
    
    if not connections:
        print("⚠️  Railway auto-configuration failed. Using environment variables.")
    else:
        print(f"✓ Railway auto-configuration complete: {list(connections.keys())}")
    
    return connections


# Synchronous wrapper for use in non-async contexts
def configure_from_railway():
    """Synchronous wrapper to configure from Railway."""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    return loop.run_until_complete(ensure_railway_config())