# ⚡ Quick Start Guide

## 🚀 Launch Everything

```bash
./start.sh
```

## 🛑 Stop Everything

```bash
./stop.sh
```

## 📍 Service URLs

| Service | URL | Description |
|---------|-----|-------------|
| **Frontend** | http://localhost:3000 | Main UI & Chat |
| **API Docs** | http://localhost:8000/docs | API Documentation |
| **MCP Tools** | http://localhost:8001/docs | Tool APIs |

## 🔑 Required Setup

Create `.env.local` in project root:

```bash
OPENROUTER_API_KEY1=sk-or-v1-xxxxx
OPENROUTER_API_KEY2=sk-or-v1-xxxxx
OPENROUTER_API_KEY3=sk-or-v1-xxxxx
OPENROUTER_API_KEY4=sk-or-v1-xxxxx
DATABASE_URL=postgresql://user:pass@localhost:5432/db
MCP_API_KEY=your-secret-key
NEXT_PUBLIC_ORCHESTRATOR_URL=http://localhost:8000
```

## 📊 What's Running

```
Port 8001: MCP Server (Agent Tools)
Port 8000: API Server (Orchestrator + 3 Agents)
Port 3000: Next.js App (UI)
```

## 🐛 Quick Fixes

**Port in use?**
```bash
./stop.sh
./start.sh
```

**Dependencies broken?**
```bash
# Python
cd backend && source venv/bin/activate
pip install -r requirements.txt

# Node
npm install
```

**Logs?**
```bash
tail -f logs/api-server.log
tail -f logs/mcp-server.log
tail -f logs/nextjs.log
```

## ✨ Try It Out

Open http://localhost:3000 and ask:

```
Create a React todo list component with TypeScript
```

or

```
Build a full-stack app with Next.js, PostgreSQL, and auth
```

---

📚 **Full Documentation:** See [STARTUP_GUIDE.md](./STARTUP_GUIDE.md)
