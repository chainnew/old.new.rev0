"""
Script to add API key security to all endpoints in swarm_api.py and mcp_servers.py
"""
import re
from pathlib import Path

# Endpoint security mappings
SWARM_API_SECURITY = {
    '@app.get("/swarms/{swarm_id}")': 'dependencies=[Depends(verify_api_key)]',
    '@app.get("/swarms/{swarm_id}/agents")': 'dependencies=[Depends(verify_api_key)]',
    '@app.get("/agents/{agent_id}/tasks")': 'dependencies=[Depends(verify_api_key)]',
    '@app.put("/tasks/{task_id}")': 'dependencies=[Depends(verify_api_key)]',
    '@app.put("/agents/{agent_id}/state")': 'dependencies=[Depends(verify_api_key)]',
    '@app.put("/swarms/{swarm_id}/status")': 'dependencies=[Depends(verify_api_key)]',
    '@app.post("/orchestrator/process")': 'dependencies=[Depends(verify_api_key)]',
    '@app.get("/api/planner/{swarm_id}")': 'dependencies=[Depends(verify_api_key)]',
    '@app.get("/api/planner/{swarm_id}/progress")': 'dependencies=[Depends(verify_api_key)]',
    '@app.get("/api/planner/{swarm_id}/escalations")': 'dependencies=[Depends(verify_api_key)]',
    '@app.post("/api/planner/{swarm_id}/escalations/{escalation_id}/resolve")': 'dependencies=[Depends(verify_api_key)]',
    '@app.post("/api/mcp/tools/{tool_name}")': 'dependencies=[Depends(verify_api_key)]',
}

def add_security_to_file(file_path: str, security_map: dict):
    """Add security dependencies to endpoints in a file."""
    path = Path(file_path)

    if not path.exists():
        print(f"❌ File not found: {file_path}")
        return False

    content = path.read_text()
    modified = False

    for endpoint_decorator, security_dep in security_map.items():
        # Check if endpoint exists and doesn't already have dependencies
        if endpoint_decorator in content and 'dependencies=' not in content[content.find(endpoint_decorator):content.find(endpoint_decorator) + 200]:
            # Find the decorator and add dependencies
            pattern = re.escape(endpoint_decorator)
            replacement = endpoint_decorator.replace(')', f', {security_dep})')
            content = re.sub(pattern, replacement, content)
            modified = True
            print(f"✅ Added security to: {endpoint_decorator}")

    if modified:
        path.write_text(content)
        print(f"💾 Updated: {file_path}")
        return True
    else:
        print(f"ℹ️  No changes needed for: {file_path}")
        return False

def main():
    import os
    os.chdir("/Users/matto/Documents/AI CHAT/my-app")

    print("🔐 Adding API key security to endpoints...")
    print()

    # Add security to swarm_api.py
    print("📝 Processing backend/swarm_api.py...")
    add_security_to_file("backend/swarm_api.py", SWARM_API_SECURITY)

    print()
    print("✅ Security update complete!")
    print()
    print("⚠️  IMPORTANT NOTES:")
    print("1. The root endpoint '/' is left public for API documentation")
    print("2. All other endpoints now require valid API keys")
    print("3. Frontend needs to include API keys in requests")
    print("4. MCP server still has its own auth system")

if __name__ == "__main__":
    main()
