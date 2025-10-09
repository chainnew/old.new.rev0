# 🔥 HECTIC SWARM - Python Backend

**Semi-Swarm Multi-Agent System for ETERNA Hypervisor Porting (ARM64 → x86_64)**

Powered by **Grok-4-Fast** via OpenRouter with advanced RAG, swarm coordination, and cargo integration.

## 🎯 Features

- ✅ **Semi-Swarm Architecture** - Agents with handshakes, message queues, health monitoring
- ✅ **3 Specialized Agents** - Primary (coordinator), CodeAgent, EternaPortAgent  
- ✅ **RAG with pgvector** - Semantic search over code artifacts & architecture docs
- ✅ **Cargo Integration** - Auto-validate generated Rust code with `cargo check`
- ✅ **QEMU Support** - Build and test hypervisor in QEMU
- ✅ **Pytest Test Suite** - Comprehensive unit and integration tests
- ✅ **Linting & Formatting** - Black, Ruff, MyPy pre-configured
- ✅ **Database Optimized** - HNSW indexes for fast vector search

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  Next.js Frontend (TypeScript)                              │
│  /app/api/swarm/python/route.ts                             │
└──────────────┬──────────────────────────────────────────────┘
               │ HTTP/REST
               ▼
┌─────────────────────────────────────────────────────────────┐
│  FastAPI Backend (Python 3.13) - localhost:8000             │
│  ├── main.py (FastAPI app + swarm orchestration)            │
│  ├── hypervisor_port_orchestrator.py (cargo + QEMU)         │
│  ├── agents/                                                 │
│  │   ├── primary_agent.py (task decomposer)                 │
│  │   ├── code_agent.py (general code migration)             │
│  │   ├── eterna_port_agent.py (ARM64→x86 specialist)        │
│  │   └── swarm_coordinator.py (message passing, health)     │
│  └── utils/                                                  │
│      ├── openrouter_client.py (3 API keys, load balancing)  │
│      └── rag_engine.py (embeddings, vector search)          │
└──────────────┬──────────────────────────────────────────────┘
               │
               ├─────────► OpenRouter.ai (Grok-4-Fast)
               ├─────────► PostgreSQL + pgvector (RAG)
               └─────────► Cargo/Rustc (validation)
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd backend
make install  # Or: pip install -r requirements.txt
```

For development (includes linters, pre-commit):
```bash
make install-dev
```

### 2. Configure Environment

Create `.env` file in `backend/`:

```bash
# OpenRouter API Keys (at least one required, 3 for load balancing)
OPENROUTER_API_KEY1=sk-or-v1-...
OPENROUTER_API_KEY2=sk-or-v1-...
OPENROUTER_API_KEY3=sk-or-v1-...

# OpenAI (for embeddings only - optional)
OPENAI_API_KEY=sk-...

# PostgreSQL with pgvector
DATABASE_URL=postgresql://user:pass@localhost:5432/hectic_swarm

# Optional: Override defaults
PYTHON_BACKEND_URL=http://localhost:8000
NEXT_PUBLIC_APP_URL=http://localhost:3000
```

### 3. Setup Database (Optional but Recommended)

```bash
# Create database
createdb hectic_swarm

# Run schema + migrations
make db-migrate

# Or manually:
psql $DATABASE_URL -f ../database/schema.sql
psql $DATABASE_URL -f ../database/migrations/001_optimize_indexes.sql
```

### 4. Start Backend

**Production mode:**
```bash
make run  # Or: python main.py
```

**Development mode (auto-reload):**
```bash
make dev  # Or: uvicorn main:app --reload
```

You should see:
```
╔═══════════════════════════════════╗
║   🚀 HECTIC SWARM STARTING 🚀     ║
╚═══════════════════════════════════╝

✅ Environment configured
✅ Agents loaded: ['code', 'port', 'eterna_port']
✅ Agent 'primary' registered
✅ Agent 'code' registered
✅ Agent 'eterna_port' registered

🌐 Server starting on http://localhost:8000
📚 API docs: http://localhost:8000/docs
```

### 5. Test It

**Health check:**
```bash
curl http://localhost:8000/
curl http://localhost:8000/swarm/health  # Detailed agent health
```

**Port a hypervisor component:**
```bash
make orchestrate TASK="Port VMCS to x86"
# Or directly:
python hypervisor_port_orchestrator.py "Port full VCPU management" --build
```

**Run tests:**
```bash
make test        # Full test suite with coverage
make test-fast   # Quick tests without coverage
make lint        # Linters (ruff + mypy)
make format      # Auto-format with black
```

**Run CI checks:**
```bash
make ci  # Format check + lint + test
```

## 📡 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Health check with system status |
| `/swarm/health` | GET | Swarm coordinator stats & agent health |
| `/swarm/orchestrate` | POST | Main orchestration endpoint |
| `/agent/{type}/execute` | POST | Execute single agent (testing) |
| `/eterna/port` | POST | Port single ETERNA file |
| `/eterna/port/bulk` | POST | Port multiple files |
| `/docs` | GET | Interactive API documentation |

### Example: Port Hypervisor Component

**Request:**
```bash
curl -X POST http://localhost:8000/swarm/orchestrate \
  -H "Content-Type: application/json" \
  -d '{
    "userMessage": "Port ETERNA VMCS to x86 with full validation",
    "conversationId": "test-123"
  }'
```

**Response:**
```json
{
  "response": "✅ Successfully ported VMCS implementation...",
  "tasks": [
    {
      "task_id": "test-123-task-0",
      "status": "completed",
      "file_path": "x86_port/src/cpu/vmcs.rs",
      "output": {
        "code": "pub struct Vmcs { ... }",
        "analysis": "Mapped ARM64 EL2 to x86 VMX root mode...",
        "summary": "Generated x86 VMCS with inline assembly"
      }
    }
  ],
  "swarm_stats": {
    "completion_time_ms": 4523,
    "total_tasks": 3,
    "failures": 0
  }
}
```

## 🤖 Available Agents

| Agent | Type | Model | Capabilities |
|-------|------|-------|--------------|
| **PrimaryAgent** | Coordinator | Grok-4-Fast | Task decomposition, result integration |
| **CodeAgent** | Specialist | Grok-4-Fast | General code migration with RAG |
| **EternaPortAgent** | Specialist | Grok-4-Fast | ARM64→x86 hypervisor porting, Rust expert |

### Agent Communication

Agents communicate via `SwarmCoordinator`:
- **Message queues** - Async task passing between agents
- **Handshakes** - Agents announce capabilities on startup
- **Health monitoring** - Heartbeats and status tracking
- **Task routing** - Intelligent agent selection based on task type

```python
# Example: Agent handshake
await coordinator.handshake('eterna_port', {
    'specialization': 'hypervisor',
    'languages': ['rust', 'x86_asm'],
    'model': 'grok-4-fast'
})
```

## Model

Using: **Grok 4 Fast** (`x-ai/grok-4-fast`)

Why Grok 4 Fast?
- ⚡ Fast inference (lower latency)
- 💰 Cost-effective
- 🎯 Great for code generation
- 🔄 Load-balanced across 3 API keys

All agents use this model by default.

## Database Schema

Uses your existing PostgreSQL schema:
- `agent_memory` - RAG context
- `code_artifacts` - Generated diffs
- `agent_tasks` - Task tracking

Code Agent automatically:
1. Queries `agent_memory` for context (RAG)
2. Stores results in `code_artifacts`

## Development

### Add New Agent

1. Create `backend/agents/your_agent.py`:
```python
class YourAgent:
    async def execute(self, task: Dict) -> Dict:
        # Your logic here
        return {"task_id": task['id'], "status": "completed", "output": {...}}
```

2. Register in `main.py`:
```python
from agents.your_agent import YourAgent

AGENTS = {
    'code': code_agent,
    'your_agent': YourAgent(),  # Add here
}
```

3. Update Primary Agent to route to it:
```python
# In primary_agent.py system prompt
Available specialist agents:
- YOUR_AGENT: Does cool stuff
```

### Run Tests

```bash
# TODO: Add pytest tests
pytest backend/tests/
```

## Troubleshooting

**"Module not found" errors:**
```bash
pip install -r requirements.txt
```

**Database connection fails:**
- Check `DATABASE_URL` in `.env`
- Ensure PostgreSQL is running
- Test: `psql $DATABASE_URL`

**OpenRouter errors:**
- Verify API keys in `.env`
- Check OpenRouter dashboard for usage limits
- Try different model if rate-limited

**"Python backend not reachable":**
- Ensure `python main.py` is running on port 8000
- Check firewall/network settings
- Test: `curl http://localhost:8000/`

## Next Steps

- [ ] Add Debug Agent (hypervisor error analysis)
- [ ] Add Research Agent (arch documentation lookup)
- [ ] Implement streaming responses (SSE)
- [ ] Add Celery for background tasks
- [ ] Deploy to Railway/Fly.io
- [ ] Add auth middleware
- [ ] Implement agent memory persistence
- [ ] Add WebSocket for real-time updates

## Resources

- [OpenRouter Docs](https://openrouter.ai/docs)
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [Grok API Docs](https://docs.x.ai/)
