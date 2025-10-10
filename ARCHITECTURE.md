# 🏗️ HECTIC SWARM - Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│                         USER (Browser)                              │
│                                                                     │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             │ HTTP
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    Next.js Frontend (Port 3000)                     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────┐               │
│  │  AI Chat    │  │ Code Window  │  │ AI Planner  │               │
│  │  Interface  │  │ & Editor     │  │ Dashboard   │               │
│  └─────────────┘  └──────────────┘  └─────────────┘               │
│                                                                     │
│  ┌───────────────────────────────────────────────────────────┐     │
│  │  React Components                                         │     │
│  │  • AnimatedAIChat                                         │     │
│  │  • CodeWindow                                             │     │
│  │  • CodeActionPanel                                        │     │
│  │  • AgentPlan                                              │     │
│  └───────────────────────────────────────────────────────────┘     │
│                                                                     │
└─────────────────┬───────────────────────────────────────────────────┘
                  │
                  │ REST API
                  │
        ┌─────────┴──────────┐
        │                    │
        ▼                    ▼
┌─────────────────┐  ┌─────────────────────────────────────────────┐
│  API Routes     │  │    API Server (Port 8000)                   │
│  (Next.js)      │  │    FastAPI Backend                          │
│                 │  ├─────────────────────────────────────────────┤
│  /api/chat      │  │                                             │
│  /api/swarm     │  │  ┌──────────────────────────────────────┐  │
│  /api/create    │  │  │   Orchestrator Agent                 │  │
│  /api/planner   │  │  │   (Grok 4 Fast Reasoning)            │  │
│                 │  │  └──────────────────────────────────────┘  │
└─────────────────┘  │                                             │
                     │  ┌──────────────────────────────────────┐  │
                     │  │   3 Specialized Agents:              │  │
                     │  │                                      │  │
                     │  │   1. Frontend Architect              │  │
                     │  │      → Design & UI Implementation    │  │
                     │  │                                      │  │
                     │  │   2. Backend Integrator              │  │
                     │  │      → API & DB Integration          │  │
                     │  │                                      │  │
                     │  │   3. Deployment Guardian             │  │
                     │  │      → Testing & CI/CD               │  │
                     │  └──────────────────────────────────────┘  │
                     │                                             │
                     │  ┌──────────────────────────────────────┐  │
                     │  │   Swarm Coordinator                  │  │
                     │  │   • Task Distribution                │  │
                     │  │   • Agent Management                 │  │
                     │  │   • Parallel Execution               │  │
                     │  └──────────────────────────────────────┘  │
                     │                                             │
                     └─────────┬───────────────────────────────────┘
                               │
                               │ Internal API
                               ▼
                     ┌─────────────────────────────────────────────┐
                     │    MCP Server (Port 8001)                   │
                     │    Multi-Agent Control Platform             │
                     ├─────────────────────────────────────────────┤
                     │                                             │
                     │  ┌──────────────────────────────────────┐  │
                     │  │   Agent Tools (MCP)                  │  │
                     │  │                                      │  │
                     │  │   🌐 Browser Tool                    │  │
                     │  │      → Web search & research         │  │
                     │  │      → Market comps                  │  │
                     │  │                                      │  │
                     │  │   💻 Code-Gen Tool                   │  │
                     │  │      → AI code generation            │  │
                     │  │      → Grok 4 Fast powered           │  │
                     │  │                                      │  │
                     │  │   🗄️ DB-Sync Tool                    │  │
                     │  │      → Database operations           │  │
                     │  │      → State management              │  │
                     │  │                                      │  │
                     │  │   💬 Communication Tool              │  │
                     │  │      → Agent messaging               │  │
                     │  │      → Event coordination            │  │
                     │  └──────────────────────────────────────┘  │
                     │                                             │
                     │  ┌──────────────────────────────────────┐  │
                     │  │   Hive-Mind Database (SQLite)        │  │
                     │  │   • Shared agent state               │  │
                     │  │   • Task tracking                    │  │
                     │  └──────────────────────────────────────┘  │
                     │                                             │
                     └─────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                       External Services                             │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────────┐  ┌──────────────┐  ┌─────────────────────┐   │
│  │  OpenRouter     │  │  PostgreSQL  │  │  DuckDuckGo Search  │   │
│  │  (Grok 4 Fast)  │  │  Database    │  │  API                │   │
│  └─────────────────┘  └──────────────┘  └─────────────────────┘   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

## Data Flow

### 1. User Sends Message

```
User → Frontend (3000) → /api/chat → Grok 4 Fast → Response
                              │
                              └─> Code Extraction → CodeWindow
```

### 2. Swarm Creation (Complex Task)

```
User → Frontend → /orchestrator/process → Orchestrator Agent
                                              │
                                              ├─> Parse Scope
                                              ├─> Generate Tasks
                                              └─> Create Swarm in DB
                                                      │
                                                      └─> Return Swarm ID
                                                              │
                                                              └─> Frontend redirects to /planner/[id]
```

### 3. Task Execution

```
Planner → API Server → Orchestrator
              │
              ├─> Assign to Agent 1 (Frontend)
              ├─> Assign to Agent 2 (Backend)  } Parallel
              └─> Assign to Agent 3 (Deploy)   } Execution
                  │
                  └─> Each agent calls MCP tools:
                          │
                          ├─> Browser (research)
                          ├─> Code-Gen (create code)
                          ├─> DB-Sync (update state)
                          └─> Communication (coordinate)
```

### 4. Code Generation Flow

```
Agent → MCP Code-Gen Tool → Grok 4 Fast → Generated Code
                                              │
                                              ├─> Save to disk
                                              └─> Send to CodeWindow
                                                      │
                                                      └─> Display in UI
```

## Technology Stack

### Frontend (Port 3000)
- **Framework**: Next.js 15 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Animations**: Framer Motion
- **State**: React Hooks + Context API
- **Code Display**: React Syntax Highlighter
- **Markdown**: React Markdown

### Backend - API Server (Port 8000)
- **Framework**: FastAPI (Python)
- **Language**: Python 3.8+
- **AI Model**: Grok 4 Fast (via OpenRouter)
- **Database**:
  - PostgreSQL (conversations, persistence)
  - SQLite (swarm state, hive-mind)
- **Async**: asyncio for parallel agent execution

### Backend - MCP Server (Port 8001)
- **Framework**: FastAPI (Python)
- **Language**: Python 3.8+
- **Database**: SQLite (hive-mind shared state)
- **Tools**:
  - Requests (HTTP calls)
  - OpenAI SDK (code generation)
  - DuckDuckGo API (web search)

## Database Schema

### PostgreSQL (Conversations)

```sql
-- Conversations table
CREATE TABLE conversations (
  id TEXT PRIMARY KEY,
  title TEXT,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Messages table
CREATE TABLE messages (
  id SERIAL PRIMARY KEY,
  conversation_id TEXT REFERENCES conversations(id),
  role TEXT, -- 'user' or 'assistant'
  content TEXT,
  created_at TIMESTAMP DEFAULT NOW(),
  prompt_tokens INTEGER,
  completion_tokens INTEGER,
  model TEXT
);
```

### SQLite (Swarm State)

```sql
-- Swarms table
CREATE TABLE swarms (
  id TEXT PRIMARY KEY,
  name TEXT,
  status TEXT, -- 'active', 'completed', 'failed'
  num_agents INTEGER,
  created_at TIMESTAMP,
  metadata JSON
);

-- Agents table
CREATE TABLE agents (
  id TEXT PRIMARY KEY,
  swarm_id TEXT REFERENCES swarms(id),
  name TEXT,
  role TEXT, -- 'frontend_architect', 'backend_integrator', 'deployment_guardian'
  state JSON, -- Current task, subtasks, progress
  created_at TIMESTAMP
);

-- Tasks table
CREATE TABLE tasks (
  id TEXT PRIMARY KEY,
  swarm_id TEXT REFERENCES swarms(id),
  agent_id TEXT REFERENCES agents(id),
  description TEXT,
  status TEXT, -- 'pending', 'in_progress', 'completed', 'failed'
  output JSON,
  created_at TIMESTAMP
);
```

## API Endpoints

### Next.js API Routes (Port 3000)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/chat` | Send message to AI |
| GET | `/api/conversations/[id]` | Get conversation history |
| POST | `/api/create-files` | Create files from code |

### API Server (Port 8000)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check + system status |
| POST | `/swarm/orchestrate` | Orchestrate multi-agent task |
| POST | `/agent/{type}/execute` | Execute single agent |
| GET | `/swarm/health` | Swarm coordinator health |
| POST | `/orchestrator/process` | Create swarm from user message |
| GET | `/swarms` | List all swarms |
| GET | `/api/planner/{swarmId}` | Get planner tasks |
| POST | `/api/planner/{swarmId}/clear` | Clear subtasks |

### MCP Server (Port 8001)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/tool/call` | Execute any tool |
| POST | `/tools/{tool_name}` | Execute specific tool |

**Available Tools:**
- `browser` - Web search and research
- `code-gen` - AI code generation
- `db-sync` - Database sync
- `communication` - Agent messaging

## Security

### Authentication Flow

```
Frontend → API Server: JWT/Session (NextAuth)
API Server → MCP Server: Bearer Token (MCP_API_KEY)
API Server → OpenRouter: API Key (OPENROUTER_API_KEY)
```

### Environment Variables

- Frontend has access to: `NEXT_PUBLIC_*` variables only
- Backend has access to: All variables
- MCP Server validates: `MCP_API_KEY` for all requests

## Scalability

### Current Architecture
- Single server per service
- SQLite for swarm state (file-based)
- PostgreSQL for conversations (hosted)

### Scale-Up Path
1. **Horizontal Scaling**: Run multiple API server instances behind load balancer
2. **Database Migration**: Move from SQLite to PostgreSQL for swarm state
3. **Queue System**: Add Redis/BullMQ for task queuing
4. **Caching**: Add Redis for response caching
5. **CDN**: Add Cloudflare for static assets

## Monitoring

### Logs
- `logs/nextjs.log` - Frontend logs
- `logs/api-server.log` - API server logs
- `logs/mcp-server.log` - MCP server logs

### Metrics to Track
- Response time per agent
- Task completion rate
- API call costs (OpenRouter)
- Database query performance
- Error rates per service

### Health Checks
- Frontend: `GET http://localhost:3000`
- API Server: `GET http://localhost:8000`
- MCP Server: `GET http://localhost:8001`
- Swarm Health: `GET http://localhost:8000/swarm/health`

## Development Workflow

```
Developer
    │
    ├─> Edit code
    │   ├─> Frontend: Hot reload (Turbopack)
    │   └─> Backend: Auto reload (uvicorn --reload)
    │
    ├─> Test locally
    │   ├─> pytest (backend)
    │   └─> npm test (frontend)
    │
    ├─> Commit changes
    │   └─> Pre-commit hooks (black, mypy, eslint)
    │
    └─> Deploy
        ├─> Frontend → Vercel
        ├─> Backend → Railway/Fly.io
        └─> Database → Railway PostgreSQL
```

---

**For detailed startup instructions, see [STARTUP_GUIDE.md](./STARTUP_GUIDE.md)**
