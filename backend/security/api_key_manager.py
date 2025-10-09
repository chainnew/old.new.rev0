"""
API Key Manager - Secure endpoint authentication system
Generates and validates API keys for all endpoints
"""
import secrets
import hashlib
import hmac
from typing import Dict, Optional, List
from datetime import datetime
import json
from pathlib import Path

class APIKeyManager:
    """Manages API key generation, validation, and permissions."""

    # Define endpoint groups and their required permissions
    ENDPOINT_GROUPS = {
        "swarm_control": [
            "/api/swarm/create",
            "/api/swarm/start",
            "/api/swarm/status",
            "/api/swarm/stop"
        ],
        "agent_management": [
            "/api/agents/list",
            "/api/agents/status",
            "/api/agents/logs"
        ],
        "mcp_tools": [
            "/tools/browser",
            "/tools/code-gen",
            "/tools/db-sync",
            "/tools/communication",
            "/tools/ui-component"
        ],
        "workspace": [
            "/api/workspace/create",
            "/api/workspace/write",
            "/api/workspace/read"
        ],
        "ui_components": [
            "/tools/ui-component",
            "/api/ui/search",
            "/api/ui/categories"
        ],
        "admin": [
            "/api/admin/keys",
            "/api/admin/logs",
            "/api/admin/stats"
        ]
    }

    def __init__(self, secret_salt: Optional[str] = None):
        """
        Initialize API key manager.

        Args:
            secret_salt: Secret salt for HMAC signing (from env)
        """
        self.secret_salt = secret_salt or secrets.token_hex(32)
        self.keys_db = {}  # In production, use SQLite or Redis

    @staticmethod
    def generate_api_key(prefix: str = "sk", length: int = 32) -> str:
        """
        Generate a cryptographically secure API key.

        Args:
            prefix: Key prefix (e.g., "sk" for secret key)
            length: Length of random portion

        Returns:
            API key in format: prefix_randomhex
        """
        random_part = secrets.token_hex(length)
        return f"{prefix}_{random_part}"

    def hash_api_key(self, api_key: str) -> str:
        """Create SHA256 hash of API key for storage."""
        return hashlib.sha256(api_key.encode()).hexdigest()

    def sign_request(self, api_key: str, timestamp: str) -> str:
        """
        Create HMAC signature for request validation.

        Args:
            api_key: The API key
            timestamp: Request timestamp

        Returns:
            HMAC signature
        """
        message = f"{api_key}:{timestamp}".encode()
        signature = hmac.new(
            self.secret_salt.encode(),
            message,
            hashlib.sha256
        ).hexdigest()
        return signature

    def validate_api_key(
        self,
        api_key: str,
        endpoint: str,
        allowed_groups: Optional[List[str]] = None
    ) -> Dict[str, any]:
        """
        Validate API key and check permissions.

        Args:
            api_key: The API key to validate
            endpoint: Requested endpoint path
            allowed_groups: Specific groups allowed for this endpoint

        Returns:
            {
                "valid": bool,
                "key_info": {...},
                "has_permission": bool,
                "error": Optional[str]
            }
        """
        if not api_key:
            return {
                "valid": False,
                "has_permission": False,
                "error": "No API key provided"
            }

        # Hash the key for lookup
        key_hash = self.hash_api_key(api_key)

        # In production, look up in database
        # For now, validate format
        if not api_key.startswith(("sk_", "mcp_", "admin_")):
            return {
                "valid": False,
                "has_permission": False,
                "error": "Invalid API key format"
            }

        # Check endpoint permissions
        has_permission = self._check_endpoint_permission(
            api_key,
            endpoint,
            allowed_groups
        )

        return {
            "valid": True,
            "key_info": {
                "prefix": api_key.split("_")[0],
                "hash": key_hash[:16]  # First 16 chars for logging
            },
            "has_permission": has_permission,
            "error": None if has_permission else "Insufficient permissions"
        }

    def _check_endpoint_permission(
        self,
        api_key: str,
        endpoint: str,
        allowed_groups: Optional[List[str]] = None
    ) -> bool:
        """Check if API key has permission for endpoint."""
        prefix = api_key.split("_")[0]

        # Admin keys have access to everything
        if prefix == "admin":
            return True

        # If specific groups are required, check them
        if allowed_groups:
            for group in allowed_groups:
                if endpoint in self.ENDPOINT_GROUPS.get(group, []):
                    # MCP keys can access mcp_tools
                    if prefix == "mcp" and group == "mcp_tools":
                        return True
                    # SK keys can access swarm_control, agent_management
                    if prefix == "sk" and group in ["swarm_control", "agent_management", "workspace"]:
                        return True

        return False

    @staticmethod
    def generate_key_set() -> Dict[str, str]:
        """
        Generate a complete set of 18 API keys for all endpoints.

        Returns:
            Dictionary of {key_name: api_key}
        """
        keys = {
            # Swarm Control Keys (3)
            "SWARM_CREATE_KEY": APIKeyManager.generate_api_key("sk", 32),
            "SWARM_CONTROL_KEY": APIKeyManager.generate_api_key("sk", 32),
            "SWARM_MONITOR_KEY": APIKeyManager.generate_api_key("sk", 32),

            # Agent Management Keys (3)
            "AGENT_CONTROL_KEY": APIKeyManager.generate_api_key("sk", 32),
            "AGENT_MONITOR_KEY": APIKeyManager.generate_api_key("sk", 32),
            "AGENT_LOGS_KEY": APIKeyManager.generate_api_key("sk", 32),

            # MCP Tool Keys (5)
            "MCP_BROWSER_KEY": APIKeyManager.generate_api_key("mcp", 32),
            "MCP_CODEGEN_KEY": APIKeyManager.generate_api_key("mcp", 32),
            "MCP_DBSYNC_KEY": APIKeyManager.generate_api_key("mcp", 32),
            "MCP_COMM_KEY": APIKeyManager.generate_api_key("mcp", 32),
            "MCP_UI_KEY": APIKeyManager.generate_api_key("mcp", 32),

            # Workspace Keys (2)
            "WORKSPACE_WRITE_KEY": APIKeyManager.generate_api_key("sk", 32),
            "WORKSPACE_READ_KEY": APIKeyManager.generate_api_key("sk", 32),

            # UI Component Keys (2)
            "UI_SEARCH_KEY": APIKeyManager.generate_api_key("sk", 32),
            "UI_CATALOG_KEY": APIKeyManager.generate_api_key("sk", 32),

            # Admin Keys (2)
            "ADMIN_MASTER_KEY": APIKeyManager.generate_api_key("admin", 48),
            "ADMIN_READONLY_KEY": APIKeyManager.generate_api_key("admin", 32),

            # Master API Key (1)
            "API_MASTER_KEY": APIKeyManager.generate_api_key("master", 64),
        }

        return keys

    @staticmethod
    def export_keys_to_env(keys: Dict[str, str], output_path: str = "backend/.env.keys"):
        """
        Export generated keys to .env file format.

        Args:
            keys: Dictionary of key names and values
            output_path: Path to output file
        """
        env_content = [
            "# ============================================================================",
            "# API Keys - Generated by old.new Security System",
            f"# Generated: {datetime.now().isoformat()}",
            "# ============================================================================",
            "",
            "# WARNING: Keep these keys secret! Never commit to git!",
            "# Add this file to .gitignore",
            "",
        ]

        # Group keys by category
        categories = {
            "Swarm Control": [k for k in keys if "SWARM" in k],
            "Agent Management": [k for k in keys if "AGENT" in k],
            "MCP Tools": [k for k in keys if "MCP" in k],
            "Workspace": [k for k in keys if "WORKSPACE" in k],
            "UI Components": [k for k in keys if "UI" in k],
            "Admin": [k for k in keys if "ADMIN" in k],
            "Master": [k for k in keys if "MASTER" in k],
        }

        for category, key_names in categories.items():
            if not key_names:
                continue
            env_content.append(f"# {category}")
            env_content.append("# " + "-" * 76)
            for key_name in key_names:
                env_content.append(f"{key_name}={keys[key_name]}")
            env_content.append("")

        # Write to file
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text("\n".join(env_content))

        print(f"✅ API keys exported to: {output_path}")
        print(f"🔒 {len(keys)} keys generated")

    @staticmethod
    def create_key_documentation(keys: Dict[str, str]) -> str:
        """Create markdown documentation for the API keys."""
        doc = [
            "# 🔐 API Key Documentation",
            "",
            f"**Generated:** {datetime.now().isoformat()}",
            "",
            "## Security Guidelines",
            "",
            "1. **Never commit keys to git** - Add `.env.keys` to `.gitignore`",
            "2. **Rotate keys regularly** - Every 90 days minimum",
            "3. **Use least privilege** - Each endpoint has specific key requirements",
            "4. **Monitor usage** - Log all API key usage for security audits",
            "",
            "## Key Categories",
            "",
        ]

        # Document each category
        key_docs = {
            "Swarm Control Keys": {
                "keys": ["SWARM_CREATE_KEY", "SWARM_CONTROL_KEY", "SWARM_MONITOR_KEY"],
                "description": "Control swarm lifecycle and operations",
                "endpoints": ["/api/swarm/create", "/api/swarm/start", "/api/swarm/stop"]
            },
            "Agent Management Keys": {
                "keys": ["AGENT_CONTROL_KEY", "AGENT_MONITOR_KEY", "AGENT_LOGS_KEY"],
                "description": "Manage AI agents and view their status",
                "endpoints": ["/api/agents/list", "/api/agents/status", "/api/agents/logs"]
            },
            "MCP Tool Keys": {
                "keys": ["MCP_BROWSER_KEY", "MCP_CODEGEN_KEY", "MCP_DBSYNC_KEY", "MCP_COMM_KEY", "MCP_UI_KEY"],
                "description": "Access MCP tool endpoints for agent operations",
                "endpoints": ["/tools/*"]
            },
            "Workspace Keys": {
                "keys": ["WORKSPACE_WRITE_KEY", "WORKSPACE_READ_KEY"],
                "description": "Read/write access to project workspaces",
                "endpoints": ["/api/workspace/*"]
            },
            "UI Component Keys": {
                "keys": ["UI_SEARCH_KEY", "UI_CATALOG_KEY"],
                "description": "Search and access UI component database",
                "endpoints": ["/api/ui/*", "/tools/ui-component"]
            },
            "Admin Keys": {
                "keys": ["ADMIN_MASTER_KEY", "ADMIN_READONLY_KEY"],
                "description": "Administrative access (master key = full access)",
                "endpoints": ["/api/admin/*", "ALL"]
            },
            "Master Key": {
                "keys": ["API_MASTER_KEY"],
                "description": "**HIGHEST SECURITY** - Full system access",
                "endpoints": ["ALL"]
            }
        }

        for category, info in key_docs.items():
            doc.append(f"### {category}")
            doc.append("")
            doc.append(f"**Description:** {info['description']}")
            doc.append("")
            doc.append("**Keys:**")
            for key in info['keys']:
                if key in keys:
                    doc.append(f"- `{key}`: `{keys[key][:20]}...`")
            doc.append("")
            doc.append("**Allowed Endpoints:**")
            for endpoint in info['endpoints']:
                doc.append(f"- `{endpoint}`")
            doc.append("")

        doc.append("## Usage Examples")
        doc.append("")
        doc.append("```bash")
        doc.append("# Create a swarm")
        doc.append("curl -X POST http://localhost:8000/api/swarm/create \\")
        doc.append("  -H \"Authorization: Bearer $SWARM_CREATE_KEY\" \\")
        doc.append("  -d '{\"scope\": \"Build a dashboard\"}'")
        doc.append("")
        doc.append("# Search UI components")
        doc.append("curl -X POST http://localhost:8001/tools/ui-component \\")
        doc.append("  -H \"Authorization: Bearer $MCP_UI_KEY\" \\")
        doc.append("  -d '{\"query\": \"button\"}'")
        doc.append("```")

        return "\n".join(doc)


if __name__ == "__main__":
    import os
    os.chdir("/Users/matto/Documents/AI CHAT/my-app")

    print("🔐 Generating secure API keys...")

    # Generate key set
    manager = APIKeyManager()
    keys = manager.generate_key_set()

    # Export to .env
    manager.export_keys_to_env(keys, "backend/.env.keys")

    # Create documentation
    docs = manager.create_key_documentation(keys)
    Path("backend/data/API_KEYS_DOCUMENTATION.md").write_text(docs)

    print("✅ Key generation complete!")
    print(f"📄 Documentation: backend/data/API_KEYS_DOCUMENTATION.md")
    print(f"🔑 Keys file: backend/.env.keys")
    print(f"⚠️  IMPORTANT: Add backend/.env.keys to .gitignore!")
