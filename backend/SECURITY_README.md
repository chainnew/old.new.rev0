# 🔐 API Security Implementation

## Overview

All API endpoints are now secured with cryptographically strong API keys (18 unique keys across 7 categories).

---

## 🔑 Generated API Keys

**Location:** `backend/.env.keys`

**⚠️ CRITICAL:** This file contains secret keys. It has been added to `.gitignore` and must NEVER be committed to version control.

### Key Categories:

1. **Swarm Control** (3 keys)
   - `SWARM_CREATE_KEY` - Create new swarms
   - `SWARM_CONTROL_KEY` - Start/stop swarms
   - `SWARM_MONITOR_KEY` - View swarm status

2. **Agent Management** (3 keys)
   - `AGENT_CONTROL_KEY` - Control agent actions
   - `AGENT_MONITOR_KEY` - View agent status
   - `AGENT_LOGS_KEY` - Access agent logs

3. **MCP Tools** (5 keys)
   - `MCP_BROWSER_KEY` - Browser tool access
   - `MCP_CODEGEN_KEY` - Code generation
   - `MCP_DBSYNC_KEY` - Database sync
   - `MCP_COMM_KEY` - Communication tool
   - `MCP_UI_KEY` - UI component search

4. **Workspace** (2 keys)
   - `WORKSPACE_WRITE_KEY` - Write files to projects
   - `WORKSPACE_READ_KEY` - Read project files

5. **UI Components** (2 keys)
   - `UI_SEARCH_KEY` - Search UI catalog
   - `UI_CATALOG_KEY` - Access full catalog

6. **Admin** (2 keys)
   - `ADMIN_MASTER_KEY` - Full admin access
   - `ADMIN_READONLY_KEY` - Read-only admin

7. **Master** (1 key)
   - `API_MASTER_KEY` - **HIGHEST SECURITY** - Bypasses all restrictions

---

## 📋 Endpoint Security Matrix

| Endpoint | Required Keys | Purpose |
|----------|--------------|---------|
| `POST /swarms` | `SWARM_CREATE_KEY`, `ADMIN_MASTER_KEY`, `API_MASTER_KEY` | Create swarm |
| `GET /swarms/{id}` | `SWARM_MONITOR_KEY`, `SWARM_CONTROL_KEY`, `ADMIN_MASTER_KEY`, `API_MASTER_KEY` | Get swarm status |
| `PUT /tasks/{id}` | `AGENT_CONTROL_KEY`, `ADMIN_MASTER_KEY`, `API_MASTER_KEY` | Update task |
| `POST /orchestrator/process` | `SWARM_CREATE_KEY`, `ADMIN_MASTER_KEY`, `API_MASTER_KEY` | Process user input |
| `POST /tools/ui-component` | `MCP_UI_KEY`, `UI_SEARCH_KEY`, `ADMIN_MASTER_KEY`, `API_MASTER_KEY` | Search UI components |
| `POST /workspace/write` | `WORKSPACE_WRITE_KEY`, `ADMIN_MASTER_KEY`, `API_MASTER_KEY` | Write project files |

---

## 🔧 Implementation Details

### Authentication Middleware

**File:** `backend/security/auth_middleware.py`

- `APIKeyAuth` class - Validates keys and checks permissions
- `verify_api_key()` - FastAPI dependency for protected endpoints
- `require_api_key()` - Decorator for custom key requirements

### Secured APIs

1. **Swarm API** (`backend/swarm_api.py`)
   - All endpoints except `/` (docs) require authentication
   - Uses `dependencies=[Depends(verify_api_key)]`

2. **MCP Server** (`backend/mcp_servers.py`)
   - Tool endpoints require MCP keys
   - Admin endpoints require admin keys

---

## 🚀 Usage Examples

### cURL

```bash
# Create a swarm
curl -X POST http://localhost:8000/swarms \
  -H "Authorization: Bearer $SWARM_CREATE_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "project": "Dashboard",
    "goal": "Build analytics dashboard",
    "tech_stack": {"frontend": "Next.js", "backend": "FastAPI"},
    "features": ["charts", "auth"],
    "num_agents": 5
  }'

# Search UI components
curl -X POST http://localhost:8001/tools/ui-component \
  -H "Authorization: Bearer $MCP_UI_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "ui-component",
    "swarm_id": "test",
    "agent_id": "test",
    "args": {"query": "dashboard", "limit": 5}
  }'
```

### JavaScript/TypeScript

```typescript
//  app/lib/api-client.ts
const API_BASE = 'http://localhost:8000';
const SWARM_CREATE_KEY = process.env.NEXT_PUBLIC_SWARM_CREATE_KEY;

async function createSwarm(scope) {
  const response = await fetch(`${API_BASE}/swarms`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${SWARM_CREATE_KEY}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(scope)
  });

  if (!response.ok) {
    if (response.status === 401) {
      throw new Error('Unauthorized: Invalid API key');
    }
    if (response.status === 403) {
      throw new Error('Forbidden: Insufficient permissions');
    }
  }

  return await response.json();
}
```

### Python

```python
import requests
import os

# Load API key
SWARM_CREATE_KEY = os.getenv('SWARM_CREATE_KEY')

# Create swarm
response = requests.post(
    'http://localhost:8000/swarms',
    headers={'Authorization': f'Bearer {SWARM_CREATE_KEY}'},
    json={
        'project': 'Dashboard',
        'goal': 'Build analytics dashboard',
        'tech_stack': {'frontend': 'Next.js'},
        'features': ['charts'],
        'num_agents': 5
    }
)

if response.status_code == 200:
    swarm = response.json()
    print(f"Swarm created: {swarm['swarm_id']}")
else:
    print(f"Error: {response.status_code} - {response.text}")
```

---

## 🛡️ Security Best Practices

### Key Management

1. **Never commit keys to git**
   - `.env.keys` is in `.gitignore`
   - Use environment variables in production

2. **Rotate keys regularly**
   - Regenerate keys every 90 days
   - Run: `python3 backend/security/api_key_manager.py`

3. **Use least privilege**
   - Give each service only the keys it needs
   - Frontend gets read keys, backend gets write keys

4. **Monitor key usage**
   - Log all API requests with key hashes
   - Alert on unusual patterns

### Production Deployment

```bash
# Set environment variables (not .env files)
export SWARM_CREATE_KEY="sk_..."
export MCP_UI_KEY="mcp_..."
export API_MASTER_KEY="master_..."

# Or use secrets management
# - AWS Secrets Manager
# - HashiCorp Vault
# - Kubernetes Secrets
```

### Error Handling

```typescript
try {
  const result = await createSwarm(scope);
} catch (error) {
  if (error.message.includes('Unauthorized')) {
    // Redirect to login or show auth error
    console.error('Invalid API key');
  } else if (error.message.includes('Forbidden')) {
    // User doesn't have permission
    console.error('Insufficient permissions');
  }
}
```

---

## 📊 Key Permissions Matrix

| Key Type | Swarm Control | Agent Management | MCP Tools | Workspace | UI Search | Admin |
|----------|---------------|------------------|-----------|-----------|-----------|-------|
| `SWARM_CREATE_KEY` | ✅ Create | ❌ | ❌ | ❌ | ❌ | ❌ |
| `SWARM_CONTROL_KEY` | ✅ Start/Stop | ❌ | ❌ | ❌ | ❌ | ❌ |
| `AGENT_CONTROL_KEY` | ❌ | ✅ Control | ❌ | ❌ | ❌ | ❌ |
| `MCP_UI_KEY` | ❌ | ❌ | ✅ UI Tool | ❌ | ✅ Search | ❌ |
| `WORKSPACE_WRITE_KEY` | ❌ | ❌ | ❌ | ✅ Write | ❌ | ❌ |
| `ADMIN_MASTER_KEY` | ✅ All | ✅ All | ✅ All | ✅ All | ✅ All | ✅ All |
| `API_MASTER_KEY` | ✅ All | ✅ All | ✅ All | ✅ All | ✅ All | ✅ All |

---

## 🔄 Key Rotation

To rotate all API keys:

```bash
cd /Users/matto/Documents/AI\ CHAT/my-app
python3 backend/security/api_key_manager.py

# This will:
# 1. Generate 18 new cryptographically secure keys
# 2. Update backend/.env.keys
# 3. Create new documentation

# Then restart services:
./stop.sh
./start.sh
```

---

## 📁 Files

- **Key Storage:** `backend/.env.keys` (gitignored)
- **Key Manager:** `backend/security/api_key_manager.py`
- **Auth Middleware:** `backend/security/auth_middleware.py`
- **Documentation:** `backend/data/API_KEYS_DOCUMENTATION.md`
- **This File:** `backend/SECURITY_README.md`

---

## ⚠️ Troubleshooting

### 401 Unauthorized

```bash
# Check if Authorization header is present
curl -v http://localhost:8000/swarms -H "Authorization: Bearer $KEY"

# Verify key format (should start with sk_, mcp_, admin_, or master_)
echo $SWARM_CREATE_KEY
```

### 403 Forbidden

```bash
# Using wrong key for endpoint
# Example: Using SWARM_MONITOR_KEY for POST /swarms
# Solution: Use SWARM_CREATE_KEY instead
```

### Keys Not Loading

```bash
# Ensure .env.keys exists
ls -la backend/.env.keys

# Load keys in application
# Python: load_dotenv(dotenv_path="backend/.env.keys")
# Node: require('dotenv').config({ path: 'backend/.env.keys' })
```

---

**Generated:** 2025-10-10
**Security Level:** Production-Ready
**Encryption:** SHA-256 hashing, HMAC signing support
