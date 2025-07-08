"""
Railway API client for STONESOUP.

This module provides integration with Railway's GraphQL API to:
- Retrieve database connection strings
- Monitor service status
- Get environment variables
- Manage deployments programmatically
"""
import os
from typing import Dict, Any, Optional, List
import httpx
from pydantic import BaseModel, Field
import sentry_sdk
from tenacity import retry, stop_after_attempt, wait_exponential


class RailwayService(BaseModel):
    """Railway service information."""
    id: str
    name: str
    type: str  # postgresql, redis, etc.
    status: str
    connection_string: Optional[str] = None
    environment_variables: Dict[str, str] = Field(default_factory=dict)


class RailwayProject(BaseModel):
    """Railway project information."""
    id: str
    name: str
    services: List[RailwayService] = Field(default_factory=list)
    environment: str = "production"


class RailwayClient:
    """
    Client for interacting with Railway's GraphQL API.
    
    This client provides access to:
    - PostgreSQL connection strings
    - Redis connection strings
    - Environment variables
    - Service monitoring
    """
    
    GRAPHQL_URL = "https://backboard.railway.app/graphql/v2"
    
    def __init__(self, token: Optional[str] = None, project_id: Optional[str] = None):
        """
        Initialize Railway client.
        
        Args:
            token: Railway API token (defaults to RAILWAY_TOKEN env var)
            project_id: Railway project ID (defaults to RAILWAY_PROJECT_ID env var)
        """
        self.token = token or os.environ.get("RAILWAY_TOKEN", "")
        self.project_id = project_id or os.environ.get("RAILWAY_PROJECT_ID", "")
        
        if not self.token:
            raise ValueError("RAILWAY_TOKEN environment variable not set")
            
        if not self.project_id:
            raise ValueError("RAILWAY_PROJECT_ID environment variable not set")
            
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        reraise=True
    )
    async def _execute_query(self, query: str, variables: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute a GraphQL query against Railway API."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.GRAPHQL_URL,
                    headers=self.headers,
                    json={
                        "query": query,
                        "variables": variables or {}
                    },
                    timeout=30.0
                )
                response.raise_for_status()
                
            data = response.json()
            
            if "errors" in data:
                raise Exception(f"GraphQL errors: {data['errors']}")
                
            return data.get("data", {})
            
        except Exception as e:
            sentry_sdk.capture_exception(e)
            raise Exception(f"Railway API request failed: {str(e)}") from e
    
    async def get_project_info(self) -> RailwayProject:
        """Get project information including all services."""
        query = """
        query GetProject($projectId: String!) {
            project(id: $projectId) {
                id
                name
                environments {
                    edges {
                        node {
                            id
                            name
                            deployments {
                                edges {
                                    node {
                                        id
                                        status
                                        service {
                                            id
                                            name
                                        }
                                    }
                                }
                            }
                            serviceInstances {
                                edges {
                                    node {
                                        id
                                        serviceName
                                        serviceId
                                    }
                                }
                            }
                        }
                    }
                }
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
        """
        
        data = await self._execute_query(query, {"projectId": self.project_id})
        project_data = data.get("project", {})
        
        return RailwayProject(
            id=project_data.get("id", ""),
            name=project_data.get("name", ""),
            services=[],  # Will populate with specific service queries
            environment="production"
        )
    
    async def get_database_url(self, service_name: str = "postgres") -> str:
        """
        Get PostgreSQL database URL from Railway.
        
        Args:
            service_name: Name of the database service (default: "postgres")
            
        Returns:
            PostgreSQL connection string with pgvector support
        """
        # Query for environment variables of the specific service
        query = """
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
        """
        
        data = await self._execute_query(
            query, 
            {
                "projectId": self.project_id,
                "environmentName": "production"
            }
        )
        
        # Extract PostgreSQL connection info
        project = data.get("project", {})
        for env_edge in project.get("environments", {}).get("edges", []):
            env = env_edge.get("node", {})
            if env.get("name") == "production":
                for service_edge in env.get("serviceInstances", {}).get("edges", []):
                    service = service_edge.get("node", {})
                    if service_name.lower() in service.get("serviceName", "").lower():
                        variables = service.get("variables", {})
                        
                        # Railway provides these standard variables for Postgres
                        if "DATABASE_URL" in variables:
                            return variables["DATABASE_URL"]
                        
                        # Construct from individual variables if needed
                        if all(k in variables for k in ["PGUSER", "PGPASSWORD", "PGHOST", "PGPORT", "PGDATABASE"]):
                            user = variables["PGUSER"]
                            password = variables["PGPASSWORD"]
                            host = variables["PGHOST"]
                            port = variables["PGPORT"]
                            database = variables["PGDATABASE"]
                            return f"postgresql://{user}:{password}@{host}:{port}/{database}?sslmode=require"
        
        # Fallback: try plugin variables (Railway's database plugins)
        plugin_query = """
        query GetPluginVariables($projectId: String!) {
            project(id: $projectId) {
                plugins {
                    edges {
                        node {
                            id
                            name
                            variables
                        }
                    }
                }
            }
        }
        """
        
        plugin_data = await self._execute_query(plugin_query, {"projectId": self.project_id})
        project_plugins = plugin_data.get("project", {})
        
        for plugin_edge in project_plugins.get("plugins", {}).get("edges", []):
            plugin = plugin_edge.get("node", {})
            if "postgres" in plugin.get("name", "").lower():
                variables = plugin.get("variables", {})
                if "DATABASE_URL" in variables:
                    return variables["DATABASE_URL"]
        
        raise Exception(f"Could not find PostgreSQL service named '{service_name}' in Railway project")
    
    async def get_redis_url(self, service_name: str = "redis") -> str:
        """
        Get Redis URL from Railway.
        
        Args:
            service_name: Name of the Redis service (default: "redis")
            
        Returns:
            Redis connection string
        """
        # Similar query for Redis service
        query = """
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
        """
        
        data = await self._execute_query(
            query,
            {
                "projectId": self.project_id,
                "environmentName": "production"
            }
        )
        
        # Extract Redis connection info
        project = data.get("project", {})
        for env_edge in project.get("environments", {}).get("edges", []):
            env = env_edge.get("node", {})
            if env.get("name") == "production":
                for service_edge in env.get("serviceInstances", {}).get("edges", []):
                    service = service_edge.get("node", {})
                    if service_name.lower() in service.get("serviceName", "").lower():
                        variables = service.get("variables", {})
                        
                        # Railway provides REDIS_URL for Redis services
                        if "REDIS_URL" in variables:
                            return variables["REDIS_URL"]
                        
                        # Construct from individual variables if needed
                        if all(k in variables for k in ["REDISHOST", "REDISPORT", "REDISPASSWORD"]):
                            host = variables["REDISHOST"]
                            port = variables["REDISPORT"]
                            password = variables["REDISPASSWORD"]
                            return f"redis://default:{password}@{host}:{port}"
        
        # Try plugin approach for Redis
        plugin_query = """
        query GetPluginVariables($projectId: String!) {
            project(id: $projectId) {
                plugins {
                    edges {
                        node {
                            id
                            name
                            variables
                        }
                    }
                }
            }
        }
        """
        
        plugin_data = await self._execute_query(plugin_query, {"projectId": self.project_id})
        project_plugins = plugin_data.get("project", {})
        
        for plugin_edge in project_plugins.get("plugins", {}).get("edges", []):
            plugin = plugin_edge.get("node", {})
            if "redis" in plugin.get("name", "").lower():
                variables = plugin.get("variables", {})
                if "REDIS_URL" in variables:
                    return variables["REDIS_URL"]
        
        raise Exception(f"Could not find Redis service named '{service_name}' in Railway project")
    
    async def get_all_services(self) -> Dict[str, str]:
        """
        Get all service connection strings from Railway.
        
        Returns:
            Dictionary mapping service type to connection string
        """
        connections = {}
        
        try:
            # Get PostgreSQL
            connections["postgresql"] = await self.get_database_url()
        except Exception as e:
            print(f"Could not retrieve PostgreSQL URL: {e}")
            
        try:
            # Get Redis
            connections["redis"] = await self.get_redis_url()
        except Exception as e:
            print(f"Could not retrieve Redis URL: {e}")
            
        return connections
    
    async def verify_services(self) -> Dict[str, bool]:
        """
        Verify that services are running and accessible.
        
        Returns:
            Dictionary mapping service name to health status
        """
        query = """
        query GetServiceStatus($projectId: String!) {
            project(id: $projectId) {
                deployments {
                    edges {
                        node {
                            id
                            status
                            service {
                                name
                            }
                        }
                    }
                }
            }
        }
        """
        
        data = await self._execute_query(query, {"projectId": self.project_id})
        
        service_status = {}
        project = data.get("project", {})
        
        for deployment_edge in project.get("deployments", {}).get("edges", []):
            deployment = deployment_edge.get("node", {})
            service_name = deployment.get("service", {}).get("name", "unknown")
            status = deployment.get("status", "unknown")
            
            # Consider service healthy if deployment is successful
            service_status[service_name] = status in ["SUCCESS", "ACTIVE"]
        
        return service_status


# Global client instance
railway_client = None


def get_railway_client() -> RailwayClient:
    """Get or create Railway client instance."""
    global railway_client
    if railway_client is None:
        railway_client = RailwayClient()
    return railway_client


# Convenience functions
async def get_database_url() -> str:
    """Quick helper to get PostgreSQL URL."""
    client = get_railway_client()
    return await client.get_database_url()


async def get_redis_url() -> str:
    """Quick helper to get Redis URL."""
    client = get_railway_client()
    return await client.get_redis_url()


async def get_all_connection_strings() -> Dict[str, str]:
    """Get all service connection strings."""
    client = get_railway_client()
    return await client.get_all_services()