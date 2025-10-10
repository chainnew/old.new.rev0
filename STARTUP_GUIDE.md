# 🚀 HECTIC SWARM - Startup Guide

Complete guide to launching all services for the HECTIC SWARM multi-agent AI system.

## 📋 Architecture Overview

The HECTIC SWARM system consists of three main services:

```
┌──────────────────────────────────────────────────────────────┐
│                     HECTIC SWARM STACK                       │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  Port 3000  │  Next.js Frontend                              │
│             │  • AI Chat Interface                           │
│             │  • Code Window                                 │
│             │  • AI Planner                                  │
│             │  • Admin Panel                                 │
│                                                              │
│  ──────────────────────────────────────────────────────────  │
│                                                              │
│  Port 8000  │  FastAPI API Server (Orchestrator)             │
│             │  • Swarm Coordination                          │
│             │  • Agent Management                            │
│             │  • Task Distribution                           │
│             │  • 3 Specialized Agents:                       │
│             │    - Frontend Architect                        │
│             │    - Backend Integrator                        │
│             │    - Deployment Guardian                       │
│                                                              │
│  ──────────────────────────────────────────────────────────  │
│                                                              │
│  Port 8001  │  MCP Server (Multi-Agent Control Platform)     │
│             │  • Agent Tool APIs                             │
│             │  • Browser Tool (web research)                 │
│             │  • Code-Gen Tool (AI code generation)          │
│             │  • DB-Sync Tool (database operations)          │
│             │  • Communication Tool (agent messaging)        │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

## 🎯 Quick Start

### Option 1: One-Command Launch (Recommended)

```bash
./start.sh
```

This single command will:
1. ✅ Validate environment (Node.js, Python, API keys)
2. ✅ Set up Python virtual environment
3. ✅ Install all dependencies (Python + Node.js)
4. ✅ Initialize databases (PostgreSQL + SQLite)
5. ✅ Start all 3 services in the correct order
6. ✅ Perform health checks

### Option 2: Manual Launch

If you need more control:

```bash
# Terminal 1: Start MCP Server
cd backend
source venv/bin/activate
python3 mcp_servers.py

# Terminal 2: Start API Server
cd backend
source venv/bin/activate
python3 main.py

# Terminal 3: Start Next.js App
npm run dev
```

## 🛑 Stopping Services

### Quick Stop

```bash
./stop.sh
```

### Manual Stop

```bash
# Find and kill processes
lsof -ti:3000 | xargs kill
lsof -ti:8000 | xargs kill
lsof -ti:8001 | xargs kill
```

## 🔧 Prerequisites

### Required Software

- **Node.js** 18+ (for Next.js frontend)
- **npm** 9+ (Node package manager)
- **Python** 3.8+ (for backend services)
- **pip** (Python package manager)

Check your versions:

```bash
node --version    # Should be v18.0.0 or higher
npm --version     # Should be 9.0.0 or higher
python3 --version # Should be 3.8.0 or higher
```

### Environment Variables

Create a `.env.local` file in the project root with the following:

```bash
# OpenRouter API Keys (for Grok 4 Fast model)
OPENROUTER_API_KEY1=sk-or-v1-xxxxxxxxxxxxx
OPENROUTER_API_KEY2=sk-or-v1-xxxxxxxxxxxxx
OPENROUTER_API_KEY3=sk-or-v1-xxxxxxxxxxxxx
OPENROUTER_API_KEY4=sk-or-v1-xxxxxxxxxxxxx  # For orchestrator

# Database (PostgreSQL)
DATABASE_URL=postgresql://user:password@localhost:5432/hectic_swarm

# MCP Server Authentication
MCP_API_KEY=your-secure-mcp-secret-key

# Next.js
NEXT_PUBLIC_SITE_URL=http://localhost:3000
NEXT_PUBLIC_ORCHESTRATOR_URL=http://localhost:8000
```

### Optional: Use backend/.env

Alternatively, you can create `backend/.env` with the same variables.

## 📊 Service Details

### 1. Next.js Frontend (Port 3000)

**What it does:**
- Main user interface for interacting with AI agents
- Real-time code generation and preview
- AI planner for task breakdown
- Admin panel for monitoring

**Tech Stack:**
- Next.js 15 (App Router)
- TypeScript
- Tailwind CSS
- Framer Motion (animations)
- React Syntax Highlighter

**Endpoints:**
- http://localhost:3000 - Main app
- http://localhost:3000/planner/[swarmId] - Task planner

### 2. API Server (Port 8000)

**What it does:**
- Orchestrates AI agent swarms
- Manages task distribution and coordination
- Handles 3 specialized agents with different roles

**Tech Stack:**
- FastAPI (Python)
- SQLite (for swarm state)
- PostgreSQL (for conversations)
- Grok 4 Fast (via OpenRouter)

**Endpoints:**
- http://localhost:8000 - Health check
- http://localhost:8000/docs - API documentation (Swagger)
- http://localhost:8000/swarm/orchestrate - Main orchestration
- http://localhost:8000/orchestrator/process - Swarm creation
- http://localhost:8000/swarms - List all swarms
- http://localhost:8000/api/planner/[swarmId] - Get tasks

**Agents:**
1. **Frontend Architect** - UI/UX design and implementation
2. **Backend Integrator** - API and database integration
3. **Deployment Guardian** - Testing, deployment, CI/CD

### 3. MCP Server (Port 8001)

**What it does:**
- Provides tool APIs for AI agents
- Handles web research, code generation, database sync
- Enables agent-to-agent communication

**Tech Stack:**
- FastAPI (Python)
- OpenAI SDK (for Grok)
- SQLite (for hive-mind database)

**Endpoints:**
- http://localhost:8001 - Health check
- http://localhost:8001/docs - API documentation
- POST /tool/call - Execute any tool

**Available Tools:**
- `browser` - Web search and research (DuckDuckGo)
- `code-gen` - AI-powered code generation
- `db-sync` - Database operations and sync
- `communication` - Agent messaging and coordination

## 🔍 Monitoring & Logs

### Real-Time Logs

All services write to `logs/` directory:

```bash
tail -f logs/nextjs.log      # Frontend logs
tail -f logs/api-server.log  # API server logs
tail -f logs/mcp-server.log  # MCP server logs
```

### Process IDs

Process IDs are saved in:
- `logs/nextjs.pid`
- `logs/api-server.pid`
- `logs/mcp-server.pid`

### Health Checks

Check if services are running:

```bash
# Frontend
curl http://localhost:3000

# API Server
curl http://localhost:8000

# MCP Server
curl http://localhost:8001
```

## 🐛 Troubleshooting

### Port Already in Use

If you get "port already in use" errors:

```bash
# Kill processes on specific ports
lsof -ti:3000 | xargs kill -9
lsof -ti:8000 | xargs kill -9
lsof -ti:8001 | xargs kill -9

# Then restart
./start.sh
```

### Python Dependencies Issues

```bash
cd backend
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

### Node.js Dependencies Issues

```bash
rm -rf node_modules package-lock.json
npm install
```

### Database Connection Errors

**PostgreSQL:**
```bash
# Check if PostgreSQL is running
pg_isready

# Check connection string in .env.local
echo $DATABASE_URL
```

**SQLite:**
```bash
# Ensure swarms directory exists
mkdir -p backend/swarms

# Check database files
ls -lh backend/swarms/*.db
```

### API Key Issues

```bash
# Verify API keys are loaded
grep OPENROUTER .env.local

# Test API key (should return 200)
curl -H "Authorization: Bearer $OPENROUTER_API_KEY1" \
     https://openrouter.ai/api/v1/models
```

## 📚 Development Workflow

### 1. Start Services

```bash
./start.sh
```

### 2. Open UI

Navigate to http://localhost:3000 in your browser

### 3. Try Sample Prompts

**Simple Code Generation:**
```
Create a React button component
```

**Complex Project:**
```
Build a todo list app with:
- Next.js 14
- TypeScript
- Tailwind CSS
- Local storage persistence
```

**Swarm Creation:**
```
I want to build a full-stack e-commerce platform with:
- Product catalog
- Shopping cart
- Stripe payment integration
- Admin dashboard
```

### 4. Monitor Agent Activity

- Check API docs: http://localhost:8000/docs
- View swarms: http://localhost:8000/swarms
- Open planner: http://localhost:3000/planner/[swarmId]

### 5. Stop Services

```bash
./stop.sh
```

## 🎓 Advanced Usage

### Running Individual Services

**Only MCP Server:**
```bash
cd backend
source venv/bin/activate
python3 mcp_servers.py
```

**Only API Server:**
```bash
cd backend
source venv/bin/activate
python3 main.py
```

**Only Frontend:**
```bash
npm run dev
```

### Custom Port Configuration

Edit the Python files to change ports:

**backend/main.py** (line 403):
```python
uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
```

**backend/mcp_servers.py** (line 516):
```python
uvicorn.run(app, host="0.0.0.0", port=8001)
```

**Next.js** (package.json):
```json
"scripts": {
  "dev": "next dev --port 3000"
}
```

### Running Tests

**Python Tests:**
```bash
cd backend
source venv/bin/activate
pytest
```

**TypeScript Tests:**
```bash
npm test
```

## 📝 Configuration Files

| File | Purpose |
|------|---------|
| `.env.local` | Environment variables for Next.js |
| `backend/.env` | Environment variables for Python services |
| `package.json` | Node.js dependencies and scripts |
| `backend/requirements.txt` | Python dependencies |
| `prisma/schema.prisma` | Database schema |
| `backend/swarms/active_swarm.db` | SQLite swarm state |

## 🔐 Security Notes

1. **Never commit** `.env`, `.env.local`, or `backend/.env` files
2. **Rotate API keys** regularly
3. **Use strong** MCP_API_KEY values
4. **Keep dependencies** up to date:
   ```bash
   npm audit fix
   pip list --outdated
   ```

## 🆘 Getting Help

- **Logs**: Check `logs/` directory for error messages
- **API Docs**: http://localhost:8000/docs (when running)
- **GitHub Issues**: Report bugs and feature requests

## 🎉 Success Checklist

After running `./start.sh`, verify:

- [ ] No error messages in terminal
- [ ] All 3 services show as "ready" ✅
- [ ] http://localhost:3000 loads the UI
- [ ] http://localhost:8000/docs shows API documentation
- [ ] http://localhost:8001/docs shows MCP tool documentation
- [ ] AI chat responds to messages
- [ ] Code generation works and appears in Code Window
- [ ] Console shows no errors (F12 → Console tab)

---

**Happy Swarm Building! 🚀**
