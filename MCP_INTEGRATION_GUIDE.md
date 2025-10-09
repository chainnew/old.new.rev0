# 🔧 MCP Integration Guide

Complete guide for integrating **MCP (Multi-Agent Control Platform)** servers with your Orchestrator → Swarm → Planner pipeline.

## 🎯 Overview

MCP servers provide grounded tool APIs for your AI swarm agents:
- **Browser Tool**: Web research, competitor analysis
- **Code-Gen Tool**: Generate Next.js/React code with Grok-4-Fast
- **DB-Sync Tool**: Update hive-mind database and session state
- **Communication Tool**: Agent-user interactions

## 🏗️ Architecture

```
Frontend (agent-plan.tsx)
    ↓ [Tool badge click]
Swarm API (port 8000)
    ↓ [Proxy /api/mcp/tools/*]
MCP Server (port 8001)
    ↓ [Execute tool]
    ↓ [Update Hive-Mind DB]
Agent sees results → Updates planner UI
```

## ⚙️ Setup

### 1. Environment Variables

Add to `.env`:

```env
# MCP Server Configuration
MCP_URL=http://localhost:8001
MCP_API_KEY=mcp-secret-key

# OpenRouter for Code Generation (required)
OPENROUTER_API_KEY=your_key_here
OPENROUTER_MODEL=x-ai/grok-4-fast
```

### 2. Start MCP Server

```bash
cd backend

# Terminal 1: Start MCP server
python mcp_servers.py
# Output: 🔧 Starting MCP Servers on port 8001...
```

### 3. Start Swarm API (with MCP proxy)

```bash
# Terminal 2: Start main API
python swarm_api.py
# Output: 🔧 MCP Proxy: /api/mcp/tools/*
```

### 4. Run Tests

```bash
# Terminal 3: Test integration
python test_mcp_integration.py
```

## 🔧 Available Tools

### 1. Browser Tool

**Purpose**: Web research, competitor analysis, market data

**Example Call**:
```python
from orchestrator_agent import OrchestratorAgent

orchestrator = OrchestratorAgent()

result = orchestrator.call_mcp_tool(
    tool_name="browser",
    args={
        "query": "task tracking SaaS like Trello",
        "num_results": 5
    },
    swarm_id="abc-123",
    agent_id="agent-research-xyz"
)

print(result['output'])
# {
#   "query": "task tracking SaaS like Trello",
#   "results": [
#     {"text": "Trello: Kanban boards...", "url": "https://..."},
#     ...
#   ],
#   "count": 5
# }
```

**API Endpoint**:
```bash
curl -X POST http://localhost:8001/tools/browser \
  -H "Authorization: Bearer mcp-secret-key" \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "browser",
    "args": {"query": "Trello alternatives", "num_results": 3},
    "swarm_id": "test",
    "agent_id": "research"
  }'
```

**Frontend Usage**:
```typescript
const result = await fetch('/api/mcp/tools/browser', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    tool_name: 'browser',
    args: { query: 'task tracker comps', num_results: 5 },
    swarm_id: swarmId,
    agent_id: agentId
  })
});
```

### 2. Code-Gen Tool

**Purpose**: Generate production-ready code with Grok-4-Fast

**Example Call**:
```python
result = orchestrator.call_mcp_tool(
    tool_name="code-gen",
    args={
        "framework": "Next.js",
        "component": "task card",
        "scope_data": {
            "features": ["drag-drop", "priority", "due dates"],
            "styling": "Tailwind + Shadcn"
        }
    },
    swarm_id="abc-123",
    agent_id="agent-implementation-xyz"
)

print(result['output']['code'])
# Generated TypeScript/React code...
```

**What it generates**:
- TypeScript components
- Tailwind CSS styling
- Shadcn/UI integration
- Error handling
- Responsive design
- Accessibility features

### 3. DB-Sync Tool

**Purpose**: Update hive-mind database, track progress

**Operations**:

**Update Task**:
```python
result = orchestrator.call_mcp_tool(
    tool_name="db-sync",
    args={
        "operation": "update_task",
        "data": {
            "task_id": "task-123",
            "status": "completed",
            "output": {"research_findings": [...]}
        }
    },
    swarm_id="abc-123",
    agent_id="agent-research"
)
```

**Get Progress**:
```python
result = orchestrator.call_mcp_tool(
    tool_name="db-sync",
    args={
        "operation": "get_progress",
        "data": {}
    },
    swarm_id="abc-123",
    agent_id="orchestrator"
)
# Output: "Progress: 5/10 tasks (50.0%)"
```

### 4. Communication Tool

**Purpose**: Agent-user messaging, notifications

**Example**:
```python
result = orchestrator.call_mcp_tool(
    tool_name="communication",
    args={
        "message": "Research phase complete. Found 5 competitors.",
        "recipient": "user",
        "action": "notify"
    },
    swarm_id="abc-123",
    agent_id="agent-research"
)
```

**Actions**: `notify`, `clarify`, `update`, `error`

## 🔄 Integration Patterns

### Pattern 1: Research Agent with Browser Tool

```python
# In orchestrator_agent.py
def run_research_agent(self, swarm_id: str, scope: Dict[str, Any]):
    """Research agent uses browser tool for competitor analysis."""
    
    # Get research agent
    agents = self.db.get_swarm_status(swarm_id)['agents']
    research_agent = next(a for a in agents if a['role'] == 'research')
    
    # Call browser tool
    comps = scope.get('comps', ['Trello', 'Asana'])
    for comp in comps:
        result = self.call_mcp_tool(
            tool_name="browser",
            args={"query": f"{comp} features pricing", "num_results": 3},
            swarm_id=swarm_id,
            agent_id=research_agent['id']
        )
        
        if result['success']:
            # Update agent state with findings
            findings = result['output']['results']
            self.db.update_agent_state(
                research_agent['id'],
                {'research_data': findings}
            )
```

### Pattern 2: Implementation Agent with Code-Gen

```python
def run_implementation_agent(self, swarm_id: str, scope: Dict[str, Any]):
    """Implementation agent generates code."""
    
    agents = self.db.get_swarm_status(swarm_id)['agents']
    impl_agent = next(a for a in agents if a['role'] == 'implementation')
    
    # Generate components
    for feature in scope.get('features', []):
        result = self.call_mcp_tool(
            tool_name="code-gen",
            args={
                "framework": scope['tech_stack']['frontend'],
                "component": feature,
                "scope_data": scope
            },
            swarm_id=swarm_id,
            agent_id=impl_agent['id']
        )
        
        if result['success']:
            # Save generated code
            code = result['output']['code']
            # Write to file or return to user
```

### Pattern 3: Agent with Tool Chaining

```python
def execute_with_tool_chain(self, swarm_id: str):
    """Chain multiple tools for complex task."""
    
    # 1. Research competitors
    browser_result = self.call_mcp_tool(
        tool_name="browser",
        args={"query": "task tracker features"},
        swarm_id=swarm_id,
        agent_id="research"
    )
    
    # 2. Generate code based on research
    if browser_result['success']:
        findings = browser_result['output']['results']
        
        code_result = self.call_mcp_tool(
            tool_name="code-gen",
            args={
                "framework": "Next.js",
                "component": "task board",
                "scope_data": {"inspiration": findings}
            },
            swarm_id=swarm_id,
            agent_id="implementation"
        )
        
        # 3. Update progress
        self.call_mcp_tool(
            tool_name="db-sync",
            args={
                "operation": "update_task",
                "data": {"status": "completed", "output": code_result['output']}
            },
            swarm_id=swarm_id,
            agent_id="implementation"
        )
```

## 🎨 Frontend Integration

### Update agent-plan.tsx with Tool Calls

```tsx
// In agent-plan.tsx
const handleToolCall = async (
  toolName: string,
  args: any,
  swarmId: string,
  agentId: string
) => {
  try {
    const response = await fetch(`/api/mcp/tools/${toolName}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        tool_name: toolName,
        args,
        swarm_id: swarmId,
        agent_id: agentId
      })
    });
    
    const result = await response.json();
    
    if (result.success) {
      // Show success notification
      toast.success(`${toolName} executed successfully`);
      
      // Refresh planner data
      fetchPlannerData(swarmId);
    } else {
      toast.error(result.error || 'Tool execution failed');
    }
  } catch (error) {
    console.error('Tool call failed:', error);
  }
};

// Render tool badges with click handlers
{subtask.tools?.map((tool) => (
  <motion.button
    key={tool}
    onClick={() => handleToolCall(
      tool,
      { query: subtask.description }, // Parse args from subtask
      swarmId,
      agentId
    )}
    className="bg-violet-500/20 text-violet-300 px-2 py-1 rounded text-xs"
    whileHover={{ scale: 1.05 }}
  >
    🔧 {tool}
  </motion.button>
))}
```

## 📊 Monitoring & Observability

### View Tool Call Logs

```python
# Query sessions table for tool calls
db.cursor.execute("""
    SELECT data FROM sessions 
    WHERE swarm_id = ? 
    ORDER BY timestamp DESC
""", (swarm_id,))

for row in db.cursor.fetchall():
    session_data = json.loads(row[0])
    if 'tool_call' in session_data:
        print(f"Tool: {session_data['tool_call']['tool_name']}")
        print(f"Result: {session_data.get('result', 'N/A')}")
```

### Track Tool Performance

```python
# Add timing to mcp_servers.py
import time

@app.post("/tools/browser")
async def call_browser(call: ToolCall):
    start_time = time.time()
    
    # ... execute tool
    
    elapsed = time.time() - start_time
    
    # Log performance
    print(f"⏱️ Browser tool: {elapsed:.2f}s")
    
    return ToolResponse(...)
```

## 🚀 Production Deployment

### Deploy MCP Server

```bash
# Option 1: Same server as Swarm API
# Run both on same host, different ports

# Option 2: Separate microservice
# Deploy to Railway/Render/Fly.io
# Update MCP_URL in .env
```

### Security Best Practices

```python
# 1. Rotate API keys regularly
MCP_API_KEY = os.getenv('MCP_API_KEY')  # From secrets manager

# 2. Rate limiting (add to mcp_servers.py)
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/tools/browser")
@limiter.limit("10/minute")
async def call_browser(...):
    ...

# 3. Input validation
from pydantic import validator

class ToolCall(BaseModel):
    @validator('args')
    def validate_args(cls, v):
        # Sanitize inputs
        if 'query' in v:
            v['query'] = v['query'][:200]  # Limit length
        return v
```

### Scaling

```python
# Use Redis for caching tool results
import redis

cache = redis.Redis(host='localhost', port=6379)

def browser_tool_cached(query: str):
    cache_key = f"browser:{query}"
    cached = cache.get(cache_key)
    
    if cached:
        return json.loads(cached)
    
    result = browser_tool(query)
    cache.setex(cache_key, 3600, json.dumps(result))  # 1 hour TTL
    
    return result
```

## 🧪 Testing

### Unit Tests for Tools

```python
# test_mcp_tools.py
import pytest
from mcp_servers import browser_tool, code_gen_tool

def test_browser_tool():
    result = browser_tool("test query", num_results=3)
    assert 'results' in result
    assert isinstance(result['results'], list)

def test_code_gen_tool():
    result = code_gen_tool(
        framework="Next.js",
        component="button",
        scope_data={"styling": "Tailwind"}
    )
    assert len(result) > 0
    assert "export" in result or "function" in result
```

### Integration Tests

```bash
# Run full integration test
python test_mcp_integration.py

# Expected output:
# ✅ PASS MCP Server Health
# ✅ PASS Tool Schemas
# ✅ PASS Browser Tool
# ✅ PASS Code Gen Tool
# ✅ PASS Db Sync Tool
# ✅ PASS Full Pipeline
```

## 📚 Troubleshooting

### MCP Server Not Starting

```bash
# Check port availability
lsof -ti:8001

# Kill existing process if needed
kill -9 $(lsof -ti:8001)

# Start with debug logging
python mcp_servers.py --reload
```

### Tool Calls Timing Out

```python
# Increase timeout in orchestrator_agent.py
response = requests.post(
    f"{self.mcp_url}/tools/{tool_name}",
    timeout=60  # Increase from 30s
)
```

### API Key Errors

```bash
# Verify .env has correct key
grep MCP_API_KEY .env

# Test with curl
curl -H "Authorization: Bearer mcp-secret-key" \
  http://localhost:8001/tools/schemas
```

## ✅ Success Checklist

- [ ] MCP server running on port 8001
- [ ] Swarm API running on port 8000 with MCP proxy
- [ ] All integration tests pass
- [ ] OpenRouter API key configured (for code-gen)
- [ ] Frontend can call tools via /api/mcp/tools/*
- [ ] Agent planner shows tool badges
- [ ] Tool results update in DB
- [ ] Ready for production! 🚀

---

**Your swarm agents now have grounded tools!** Research real competitors, generate real code, sync real state. No hallucinations—pure execution. 🔧✨
