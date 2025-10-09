"""
Authentication Middleware for FastAPI
Validates API keys and enforces endpoint permissions
"""
from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, List, Callable
import os
from dotenv import load_dotenv
from functools import wraps

load_dotenv()
load_dotenv(dotenv_path="backend/.env.keys")  # Load API keys

# Security scheme
security = HTTPBearer()

class APIKeyAuth:
    """API Key authentication and authorization."""

    # Load all keys from environment
    KEYS = {
        # Swarm Control
        "swarm_create": os.getenv("SWARM_CREATE_KEY"),
        "swarm_control": os.getenv("SWARM_CONTROL_KEY"),
        "swarm_monitor": os.getenv("SWARM_MONITOR_KEY"),

        # Agent Management
        "agent_control": os.getenv("AGENT_CONTROL_KEY"),
        "agent_monitor": os.getenv("AGENT_MONITOR_KEY"),
        "agent_logs": os.getenv("AGENT_LOGS_KEY"),

        # MCP Tools
        "mcp_browser": os.getenv("MCP_BROWSER_KEY"),
        "mcp_codegen": os.getenv("MCP_CODEGEN_KEY"),
        "mcp_dbsync": os.getenv("MCP_DBSYNC_KEY"),
        "mcp_comm": os.getenv("MCP_COMM_KEY"),
        "mcp_ui": os.getenv("MCP_UI_KEY"),

        # Workspace
        "workspace_write": os.getenv("WORKSPACE_WRITE_KEY"),
        "workspace_read": os.getenv("WORKSPACE_READ_KEY"),

        # UI Components
        "ui_search": os.getenv("UI_SEARCH_KEY"),
        "ui_catalog": os.getenv("UI_CATALOG_KEY"),

        # Admin
        "admin_master": os.getenv("ADMIN_MASTER_KEY"),
        "admin_readonly": os.getenv("ADMIN_READONLY_KEY"),

        # Master
        "api_master": os.getenv("API_MASTER_KEY"),
    }

    # Endpoint to required keys mapping
    ENDPOINT_PERMISSIONS = {
        # Swarm endpoints
        "/swarms": ["swarm_create", "admin_master", "api_master"],
        "/swarms/{swarm_id}": ["swarm_monitor", "swarm_control", "admin_master", "api_master"],
        "/swarms/{swarm_id}/status": ["swarm_control", "admin_master", "api_master"],
        "/swarms/{swarm_id}/agents": ["swarm_monitor", "agent_monitor", "admin_master", "api_master"],

        # Agent endpoints
        "/agents/{agent_id}": ["agent_monitor", "agent_control", "admin_master", "api_master"],
        "/agents/{agent_id}/tasks": ["agent_monitor", "admin_master", "api_master"],
        "/agents/{agent_id}/state": ["agent_control", "admin_master", "api_master"],

        # Task endpoints
        "/tasks/{task_id}": ["agent_control", "admin_master", "api_master"],

        # MCP tool endpoints
        "/tools/browser": ["mcp_browser", "admin_master", "api_master"],
        "/tools/code-gen": ["mcp_codegen", "admin_master", "api_master"],
        "/tools/db-sync": ["mcp_dbsync", "admin_master", "api_master"],
        "/tools/communication": ["mcp_comm", "admin_master", "api_master"],
        "/tools/ui-component": ["mcp_ui", "ui_search", "admin_master", "api_master"],

        # Workspace endpoints
        "/workspace/create": ["workspace_write", "admin_master", "api_master"],
        "/workspace/write": ["workspace_write", "admin_master", "api_master"],
        "/workspace/read": ["workspace_read", "workspace_write", "admin_master", "api_master"],

        # UI endpoints
        "/ui/search": ["ui_search", "mcp_ui", "admin_master", "api_master"],
        "/ui/categories": ["ui_catalog", "ui_search", "admin_master", "api_master"],
    }

    @classmethod
    def validate_key(cls, api_key: str, endpoint_path: str) -> bool:
        """
        Validate API key for a specific endpoint.

        Args:
            api_key: The API key from Authorization header
            endpoint_path: The endpoint being accessed

        Returns:
            True if valid, raises HTTPException otherwise
        """
        if not api_key:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="No API key provided",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Find matching endpoint pattern
        allowed_keys = cls._get_allowed_keys(endpoint_path)

        if not allowed_keys:
            # No specific permissions required (public endpoint)
            return True

        # Check if provided key matches any allowed key
        for key_name in allowed_keys:
            expected_key = cls.KEYS.get(key_name)
            if expected_key and api_key == expected_key:
                return True

        # Invalid key
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Invalid API key or insufficient permissions for {endpoint_path}",
            headers={"WWW-Authenticate": "Bearer"},
        )

    @classmethod
    def _get_allowed_keys(cls, endpoint_path: str) -> List[str]:
        """Get list of allowed keys for an endpoint path."""
        # Direct match
        if endpoint_path in cls.ENDPOINT_PERMISSIONS:
            return cls.ENDPOINT_PERMISSIONS[endpoint_path]

        # Pattern matching for dynamic routes
        for pattern, keys in cls.ENDPOINT_PERMISSIONS.items():
            if cls._match_pattern(pattern, endpoint_path):
                return keys

        return []

    @staticmethod
    def _match_pattern(pattern: str, path: str) -> bool:
        """Match URL pattern with dynamic segments."""
        pattern_parts = pattern.split("/")
        path_parts = path.split("/")

        if len(pattern_parts) != len(path_parts):
            return False

        for pattern_part, path_part in zip(pattern_parts, path_parts):
            if pattern_part.startswith("{") and pattern_part.endswith("}"):
                # Dynamic segment, always matches
                continue
            if pattern_part != path_part:
                return False

        return True


async def verify_api_key(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = None
) -> str:
    """
    Dependency function to verify API key for protected endpoints.

    Usage in FastAPI:
        @app.get("/protected", dependencies=[Depends(verify_api_key)])
        def protected_route():
            ...
    """
    # Extract API key from Authorization header
    auth_header = request.headers.get("Authorization")

    if not auth_header:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Extract Bearer token
    try:
        scheme, api_key = auth_header.split()
        if scheme.lower() != "bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication scheme. Use 'Bearer'",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Authorization header format",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Validate key for this endpoint
    endpoint_path = request.url.path
    APIKeyAuth.validate_key(api_key, endpoint_path)

    return api_key


def require_api_key(*allowed_key_names: str):
    """
    Decorator to require specific API keys for an endpoint.

    Args:
        *allowed_key_names: Names of keys that can access this endpoint

    Usage:
        @app.post("/swarms")
        @require_api_key("swarm_create", "admin_master")
        def create_swarm():
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            # Get API key from header
            auth_header = request.headers.get("Authorization")

            if not auth_header:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Missing Authorization header"
                )

            try:
                scheme, api_key = auth_header.split()
                if scheme.lower() != "bearer":
                    raise ValueError("Invalid scheme")
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid Authorization header"
                )

            # Check if key matches any allowed key
            valid = False
            for key_name in allowed_key_names:
                expected_key = APIKeyAuth.KEYS.get(key_name)
                if expected_key and api_key == expected_key:
                    valid = True
                    break

            if not valid:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Invalid API key or insufficient permissions"
                )

            # Call original function
            return await func(request, *args, **kwargs)

        return wrapper
    return decorator


# Convenience functions for common key checks
def require_swarm_key():
    """Require swarm control keys."""
    return require_api_key("swarm_create", "swarm_control", "admin_master", "api_master")

def require_agent_key():
    """Require agent management keys."""
    return require_api_key("agent_control", "agent_monitor", "admin_master", "api_master")

def require_mcp_key(tool_name: str):
    """Require MCP tool keys."""
    return require_api_key(f"mcp_{tool_name}", "admin_master", "api_master")

def require_admin_key():
    """Require admin keys."""
    return require_api_key("admin_master", "admin_readonly", "api_master")
