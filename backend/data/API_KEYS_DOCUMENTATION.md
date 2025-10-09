# 🔐 API Key Documentation

**Generated:** 2025-10-10T04:59:55.162203

## Security Guidelines

1. **Never commit keys to git** - Add `.env.keys` to `.gitignore`
2. **Rotate keys regularly** - Every 90 days minimum
3. **Use least privilege** - Each endpoint has specific key requirements
4. **Monitor usage** - Log all API key usage for security audits

## Key Categories

### Swarm Control Keys

**Description:** Control swarm lifecycle and operations

**Keys:**
- `SWARM_CREATE_KEY`: `sk_3ab389a1788964f3b...`
- `SWARM_CONTROL_KEY`: `sk_5e80545f250eddf44...`
- `SWARM_MONITOR_KEY`: `sk_4122e3a43297d25b1...`

**Allowed Endpoints:**
- `/api/swarm/create`
- `/api/swarm/start`
- `/api/swarm/stop`

### Agent Management Keys

**Description:** Manage AI agents and view their status

**Keys:**
- `AGENT_CONTROL_KEY`: `sk_d8bd5e0334d1d58ba...`
- `AGENT_MONITOR_KEY`: `sk_f75b3deb19e580408...`
- `AGENT_LOGS_KEY`: `sk_ae9d5868beb4e1875...`

**Allowed Endpoints:**
- `/api/agents/list`
- `/api/agents/status`
- `/api/agents/logs`

### MCP Tool Keys

**Description:** Access MCP tool endpoints for agent operations

**Keys:**
- `MCP_BROWSER_KEY`: `mcp_d0126f7226ffd4a4...`
- `MCP_CODEGEN_KEY`: `mcp_7c96ba4b4bb9b0f2...`
- `MCP_DBSYNC_KEY`: `mcp_ecca53c228d5564c...`
- `MCP_COMM_KEY`: `mcp_a85390e3c5dea3d1...`
- `MCP_UI_KEY`: `mcp_ca5a5907489470f8...`

**Allowed Endpoints:**
- `/tools/*`

### Workspace Keys

**Description:** Read/write access to project workspaces

**Keys:**
- `WORKSPACE_WRITE_KEY`: `sk_14a2166d197e5f1a8...`
- `WORKSPACE_READ_KEY`: `sk_429c1f45ae9c4047e...`

**Allowed Endpoints:**
- `/api/workspace/*`

### UI Component Keys

**Description:** Search and access UI component database

**Keys:**
- `UI_SEARCH_KEY`: `sk_606339560e06bb118...`
- `UI_CATALOG_KEY`: `sk_eeb7e7fff850d16a9...`

**Allowed Endpoints:**
- `/api/ui/*`
- `/tools/ui-component`

### Admin Keys

**Description:** Administrative access (master key = full access)

**Keys:**
- `ADMIN_MASTER_KEY`: `admin_e14aebb377980f...`
- `ADMIN_READONLY_KEY`: `admin_a80723b8a03b84...`

**Allowed Endpoints:**
- `/api/admin/*`
- `ALL`

### Master Key

**Description:** **HIGHEST SECURITY** - Full system access

**Keys:**
- `API_MASTER_KEY`: `master_1b9a9bc7ad265...`

**Allowed Endpoints:**
- `ALL`

## Usage Examples

```bash
# Create a swarm
curl -X POST http://localhost:8000/api/swarm/create \
  -H "Authorization: Bearer $SWARM_CREATE_KEY" \
  -d '{"scope": "Build a dashboard"}'

# Search UI components
curl -X POST http://localhost:8001/tools/ui-component \
  -H "Authorization: Bearer $MCP_UI_KEY" \
  -d '{"query": "button"}'
```