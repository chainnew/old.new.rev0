# 🚀 HECTIC SWARM - AI-Powered Development Platform

> **Multi-Agent AI System with Grok 4 Fast** | Full-Stack Code Generation | Intelligent Task Planning

[![Next.js](https://img.shields.io/badge/Next.js-15-black)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Python-green)](https://fastapi.tiangolo.com/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5-blue)](https://www.typescriptlang.org/)
[![Grok](https://img.shields.io/badge/AI-Grok%204%20Fast-purple)](https://x.ai/)

---

## ⚡ Quick Start

```bash
# 1. Start all services (ports 3000, 8000, 8001)
./start.sh

# 2. Open http://localhost:3000

# 3. Try it out:
#    Simple: "Create a React button component"
#    Complex: "Build a todo app with auth and database"

# 4. Stop services
./stop.sh
```

---

## 🤖 What is HECTIC SWARM?

An **AI-powered development platform** that uses specialized agents to generate full-stack applications.

### Key Features

- **🎯 Dual-Mode AI** - Simple code generation or complex project orchestration
- **📋 AI Planner** - Breaks projects into 12 manageable tasks (3 areas × 4 subtasks)
- **👥 3 Specialized Agents** - Frontend Architect, Backend Integrator, Deployment Guardian
- **💻 Real-Time Code Window** - See generated code instantly
- **🔄 2M Token Context** - Remembers entire conversation
- **🚀 Production-Ready** - From idea to deployable code

---

## 🏗️ Architecture

```
USER → grok-orc (Master Orchestrator)
              ├─→ MODE 1: Simple Code → Direct Output → Code Window
              └─→ MODE 2: Complex Project → AI Planner → 3 Agents → Code Window
```

### Services

| Port | Service | Description |
|------|---------|-------------|
| **3000** | Next.js Frontend | UI, Chat, Code Window, AI Planner |
| **8000** | API Server | Orchestrator + 3 Specialized Agents |
| **8001** | MCP Server | Agent Tools (browser, code-gen, db-sync) |

### Technology Stack

**Frontend**: Next.js 15 + TypeScript + Tailwind CSS + Framer Motion
**Backend**: FastAPI + Grok 4 Fast + PostgreSQL + SQLite
**AI**: xAI Grok 4 Fast (via OpenRouter)
**Deployment**: Vercel (frontend) + Railway (backend)

---

## 🎯 How It Works

### Mode 1: Simple Code Generation

For single files, components, or questions.

**Example**:
```
User: "Create a React button component in src/components/Button.tsx"
→ grok-orc generates code with filename
→ Code appears in Code Window instantly
→ File saved to disk automatically
```

**Filename Formats** (AI must use one of these):

````markdown
// Format 1: Inline comment
```tsx // src/components/Button.tsx
export function Button() { return <button>Click</button>; }
```

// Format 2: Heading
Create `src/utils/helpers.ts`:
```typescript
export function formatDate(date: Date) { return date.toISOString(); }
```

// Format 3: File comment
```python
# File: backend/api/routes.py
def get_users(): pass
```
````

### Mode 2: Swarm Creation (Complex Projects)

For full apps with multiple features.

**Triggers**: Words like "build", "create app", "full-stack", or mentions of database/auth/deployment

**Example**:
```
User: "Build a blog platform with auth, posts, comments, and PostgreSQL"
→ grok-orc detects complexity
→ Creates swarm with 3 agents
→ AI Planner shows 12 tasks
→ All code generated and shown in Code Window
→ User can view progress at /planner/[swarmId]
```

**The 12-Task Breakdown**:

**Frontend & UI** (4 tasks)
1. Component architecture
2. UI components (Shadcn)
3. State management
4. Responsive design

**Middleware & Integration** (4 tasks)
5. API routes
6. Authentication
7. Form validation
8. Error handling

**Backend & Hosting** (4 tasks)
9. Database schema (Prisma)
10. API endpoints
11. Testing setup
12. Deployment config

### The 3 Specialized Agents

- **🎨 Frontend Architect** - UI/UX, React components, responsive layouts
- **⚙️ Backend Integrator** - APIs, databases, authentication, validation
- **🚀 Deployment Guardian** - Testing, CI/CD, monitoring, deployments

---

## 💻 Installation

### Prerequisites

- Node.js 18+ ([Download](https://nodejs.org/))
- Python 3.8+ ([Download](https://python.org/))
- PostgreSQL (optional but recommended)

### Setup

1. **Clone & Navigate**
```bash
git clone <your-repo>
cd my-app
```

2. **Environment Variables**

Create `.env.local`:
```bash
# OpenRouter API Keys (get from https://openrouter.ai/)
OPENROUTER_API_KEY1=sk-or-v1-xxxxxxxxxxxxx
OPENROUTER_API_KEY2=sk-or-v1-xxxxxxxxxxxxx
OPENROUTER_API_KEY3=sk-or-v1-xxxxxxxxxxxxx
OPENROUTER_API_KEY4=sk-or-v1-xxxxxxxxxxxxx  # Main orchestrator key

# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/hectic_swarm

# MCP Server
MCP_API_KEY=your-secret-key

# URLs
NEXT_PUBLIC_SITE_URL=http://localhost:3000
NEXT_PUBLIC_ORCHESTRATOR_URL=http://localhost:8000
```

3. **Launch**
```bash
chmod +x start.sh stop.sh
./start.sh
```

The start script automatically:
- Creates Python virtual environment
- Installs all dependencies (Python + Node)
- Initializes databases
- Starts all 3 services
- Performs health checks

---

## 🎨 Usage Examples

### Example 1: Single Component

```
Create a Card component with title and description props in TypeScript
```

**Result**: `src/components/Card.tsx` appears in Code Window

### Example 2: Full Application

```
Build a task management app with:
- User authentication (NextAuth)
- Create/edit/delete tasks
- PostgreSQL database with Prisma
- Responsive Tailwind UI
- Task categories and priorities
```

**Result**:
- Swarm created with 12 tasks
- Multiple files generated (components, APIs, schema)
- View progress: `/planner/[swarmId]`
- All code in Code Window

### Example 3: Code Question

```
How do I implement debouncing in React with TypeScript?
```

**Result**: Explanation with code examples

---

## 🐛 Troubleshooting

### Code Not Appearing?

1. Open browser console (F12)
2. Look for logs:
   ```
   🔍 Code blocks extracted: X
   📤 Sending files to CodeWindow: X
   ```
3. If missing:
   - Check Code Window is open (<Code2> button)
   - Verify AI included filename
   - Ensure code has language tags (```tsx)

### Swarm Not Created?

1. Check response includes `SWARM_CREATE_REQUEST`
2. Verify backend running: `curl http://localhost:8000`
3. Check logs: `tail -f logs/api-server.log`
4. Use trigger words: "build", "create app", "full-stack"

### Port in Use?

```bash
./stop.sh
./start.sh
```

Or manually:
```bash
lsof -ti:3000 | xargs kill -9
lsof -ti:8000 | xargs kill -9
lsof -ti:8001 | xargs kill -9
```

### Dependencies Broken?

```bash
# Python
cd backend && source venv/bin/activate
pip install -r requirements.txt

# Node.js
rm -rf node_modules package-lock.json
npm install
```

---

## 📚 API Documentation

### Service URLs

- **Frontend**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs (Swagger)
- **MCP Tools**: http://localhost:8001/docs
- **Planner**: http://localhost:3000/planner/[swarmId]

### Main Endpoints

**Frontend API Routes** (Port 3000)
- `POST /api/chat` - Send message to AI
- `GET /api/conversations/[id]` - Get history
- `POST /api/create-files` - Create files from code

**API Server** (Port 8000)
- `POST /orchestrator/process` - Create swarm
- `GET /swarms` - List all swarms
- `GET /api/planner/{swarmId}` - Get tasks
- `GET /swarm/health` - Health check

**MCP Server** (Port 8001)
- `POST /tool/call` - Execute tool
  - `browser` - Web search
  - `code-gen` - AI code generation
  - `db-sync` - Database operations
  - `communication` - Agent messaging

---

## 🎓 Advanced Features

### MCP Tool System

Agents use powerful tools:

- **Browser Tool**: DuckDuckGo search, web research, competitor analysis
- **Code-Gen Tool**: AI-powered generation with Grok 4 Fast
- **DB-Sync Tool**: Database operations, state management
- **Communication Tool**: Agent messaging, event coordination

### Hive-Mind Database

SQLite shared state for agent coordination:
- Location: `backend/swarms/active_swarm.db`
- Tables: `swarms`, `agents`, `tasks`
- Purpose: Cross-agent coordination

### 2M Token Context

grok-orc remembers:
- Last 100 messages
- Stored in PostgreSQL
- Natural follow-up questions
- Builds on previous code

---

## 📊 Monitoring

### View Logs

```bash
tail -f logs/nextjs.log       # Frontend
tail -f logs/api-server.log   # API
tail -f logs/mcp-server.log   # MCP
```

### Health Checks

```bash
curl http://localhost:3000    # Frontend
curl http://localhost:8000    # API
curl http://localhost:8001    # MCP
curl http://localhost:8000/swarm/health  # Swarm status
```

### Process IDs

PIDs stored in: `logs/*.pid`

---

## 🚀 Production Deployment

### Recommended

- **Frontend**: Vercel
- **Backend**: Railway or Fly.io
- **Database**: Railway PostgreSQL
- **Monitoring**: Sentry + Datadog

### Environment

Set production variables:
- `OPENROUTER_API_KEY1-4`: Production keys
- `DATABASE_URL`: Production database
- `NEXT_PUBLIC_SITE_URL`: Your domain
- `NEXT_PUBLIC_ORCHESTRATOR_URL`: API domain

---

## 📞 Support & Contributing

- **Issues**: [GitHub Issues](your-repo-url/issues)
- **Contributions**: Fork → Branch → PR
- **Documentation**: This README + inline comments

---

## 🎯 Quick Reference Card

```bash
# Essential Commands
./start.sh                    # Start all services
./stop.sh                     # Stop all services
tail -f logs/*.log            # View logs

# URLs
http://localhost:3000         # Frontend
http://localhost:8000/docs    # API docs
http://localhost:8001/docs    # MCP tools

# Sample Prompts
"Create a loading spinner"    # Simple (Mode 1)
"Build a blog platform"       # Complex (Mode 2)
"How do I use React hooks?"   # Question
```

---

**Built with ❤️ using AI** | **Powered by Grok 4 Fast** | **2025**
