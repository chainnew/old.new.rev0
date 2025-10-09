# 🧪 Testing Chat-Integrated Swarm Creation

## ✅ **System Ready!**

Your AI chat agent on localhost:3000 is now **fully integrated** with Grok-4-Fast-Reasoning swarm creation. The agent will:

1. **Detect project scopes** in conversation
2. **Auto-create AI swarms** with 12 modular tasks
3. **Show planner links** with visual 🚀 buttons
4. **Break down scopes** using 6 must-haves approach

---

## 🚀 **Quick Start (3 Terminals)**

### Terminal 1: MCP Server
```bash
cd backend
source venv/bin/activate
python3 mcp_servers.py
```

### Terminal 2: Swarm API
```bash
cd backend
source venv/bin/activate
python3 main.py
```

### Terminal 3: Frontend
```bash
npm run dev
# Open http://localhost:3000
```

---

## 🧪 **Test Scenarios**

### Test 1: E-Commerce Project (Complex)

**Chat with AI**:
```
You: Build an e-commerce store with Stripe payments
```

**Expected AI Response**:
```
🎯 PROJECT SCOPE DETECTED! Let me create an AI swarm for this...

✅ AI SWARM CREATED!

Project: abc12345...
Status: Scope populated! Swarm started for ECommerceStripeStore

🔗 View Progress: [Open Planner 🚀] ← Clickable violet button

📋 What's Happening:
- 🔬 Research Agent: Analyzing requirements & competitors
- 🎨 Design Agent: Creating architecture & wireframes  
- 💻 Implementation Agent: Planning resources & timeline

Total Tasks: 3 main phases × 4 subtasks = 12 execution units

The swarm is breaking down your project using Grok-4-Fast-Reasoning. 
Click the link above to watch real-time progress!
```

**Actions**:
- ✅ Click the **🚀 Open Planner** button
- ✅ View 12 structured tasks in Global Planner
- ✅ See expandable subtasks with MCP tool badges
- ✅ Status updates: pending → in-progress → completed

---

### Test 2: Task Tracker (Moderate)

**Chat with AI**:
```
You: Create a task tracking dashboard like Trello with Next.js
```

**Expected**:
- AI detects "build/create + task tracker"
- Creates swarm named "TrackFlow"
- Shows planner link
- 12 tasks generated specific to Trello-like features

---

### Test 3: Vague Input → Clarification

**Chat with AI**:
```
You: hey, can you help me build something?
```

**Expected AI Response**:
```
🤔 Need More Details

To create an AI swarm, I need to clarify:
1. What's the main goal/idea for your project?
2. What type of application? (web app, mobile, API, dashboard, etc.)
3. Any specific features or requirements?

Once you provide this info, I'll create the AI swarm!
```

**Follow-up**:
```
You: I want to build a blog with markdown support
```

**Expected**:
- AI now has enough info
- Creates swarm
- Shows planner link

---

### Test 4: Regular Chat (No Swarm)

**Chat with AI**:
```
You: What's the best way to center a div in CSS?
```

**Expected**:
- AI responds normally with CSS help
- **No swarm created** (not a project scope)
- Regular chat mode

---

### Test 5: Multiple Projects in One Session

**Chat Flow**:
```
You: Build an e-commerce store
AI: ✅ Swarm created! [Link to Planner A]

You: Also make a blog with comments
AI: ✅ Swarm created! [Link to Planner B]

You: Show me both planners
AI: Here are your active swarms:
     - Planner A: ECommerceStripeStore
     - Planner B: BlogWithComments
```

**Actions**:
- ✅ Click violet Zap button (bottom-left) → See both swarms
- ✅ Each has 12 tasks
- ✅ Running simultaneously

---

## 🎯 **What AI Detects as "Project Scope"**

**Keywords that trigger swarm creation**:
- build, create, make, develop, design, implement
- e-commerce, store, tracker, dashboard, app, platform, system
- site, website, blog, CMS, API, backend, frontend, full-stack
- MVP, prototype, SaaS

**Examples that trigger**:
- ✅ "Build an e-commerce store"
- ✅ "Create a task tracker"
- ✅ "Make a SaaS dashboard"
- ✅ "I want to develop a chat app"
- ✅ "Design a blog platform"

**Examples that DON'T trigger**:
- ❌ "How do I use React hooks?"
- ❌ "Explain closures in JavaScript"
- ❌ "Debug this TypeScript error"
- ❌ "What's the best database?"

---

## 🔍 **Verification Steps**

### 1. Check Backend Logs

**Terminal 2** (main.py) should show:
```
📨 Received: 'Build an e-commerce store with Stripe' from user default
✅ Scope fleshed: ECommerceStripeStore
   Goal: Build scalable online store for browsing products...
   Features: 5 items
   Timeline: 1-2h MVP
🚀 Swarm abc12345-... started for 'ECommerceStripeStore'
✅ Agent agent-123 (research): 4 subtasks generated
✅ Agent agent-456 (design): 4 subtasks generated
✅ Agent agent-789 (implementation): 4 subtasks generated
```

### 2. Check Database

```bash
cd backend
sqlite3 swarms/active_swarm.db

# List swarms
SELECT id, name, status FROM swarms ORDER BY created_at DESC LIMIT 3;

# Check agents
SELECT id, role, state FROM agents WHERE swarm_id = '<your-swarm-id>';

# Verify tasks
SELECT COUNT(*) FROM tasks WHERE swarm_id = '<your-swarm-id>';
# Should return 3 (one per agent, each with subtasks in JSON)
```

### 3. Test Planner UI

1. Open chat link: http://localhost:3000
2. Submit: "Build an e-commerce store"
3. Wait ~5-10s for swarm creation
4. Click **🚀 Open Planner** button
5. Verify planner page shows:
   - Header with swarm name
   - 3 main tasks (Research, Design, Implementation)
   - Each with 4 expandable subtasks
   - Tool badges (browser, code-gen, prisma-gen, etc.)
   - Status indicators (pending/in-progress/completed)

---

## 🐛 **Troubleshooting**

### "AI doesn't detect project scope"

**Check**:
- Use explicit keywords: "Build X", "Create Y"
- Be specific: "e-commerce store" not just "store"

**Fix**: Try these exact phrases:
```
Build an e-commerce store with Stripe
Create a task tracker like Trello
Make a blog with markdown support
```

### "Swarm created but link doesn't work"

**Check**:
- Backend running on :8000? `curl http://localhost:8000/swarms`
- Frontend on :3000? Open in browser
- Database exists? `ls backend/swarms/active_swarm.db`

**Fix**:
```bash
# Restart backend
cd backend
python3 main.py
```

### "Planner shows 'No tasks'"

**Check**:
```bash
cd backend
python3 test_grok_reasoning.py "Build a blog"
# Should show 12 tasks generated
```

**Fix**: Grok API might be rate-limited. Wait 30s and retry.

### "Chat response is slow"

**Expected**: 5-12s for swarm creation (Grok reasoning + DB inserts)

**If >30s**:
- Check OpenRouter API status
- Verify API key in `.env`
- Check terminal logs for errors

---

## 📊 **Performance Expectations**

| Action | Time | Details |
|--------|------|---------|
| **Project detection** | <1s | AI scans for keywords |
| **Scope breakdown** | 2-5s | Grok extracts 6 must-haves |
| **Task generation** | 3-6s | 3 agents × Grok calls |
| **Total swarm creation** | 5-12s | End-to-end |
| **Planner render** | <100ms | React + Framer Motion |
| **Regular chat** | 1-3s | Non-project queries |

---

## 🎓 **Advanced Testing**

### Test Backend Directly (Python)

```bash
cd backend
python3 test_grok_reasoning.py
# Runs 4 test cases automatically
```

### Test Single Scope

```bash
python3 test_grok_reasoning.py "Build a real-time chat app with WebSockets"
```

### Test API Directly (cURL)

```bash
# Create swarm via API
curl -X POST http://localhost:8000/orchestrator/process \
  -H "Content-Type: application/json" \
  -d '{"message": "Build a blog with markdown", "user_id": "test"}'

# Get planner data
curl http://localhost:8000/api/planner/<swarm-id-from-above>
```

### Test Chat API

```bash
curl -X POST http://localhost:3000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Build an e-commerce store with Stripe",
    "conversationId": "test-123"
  }'
```

**Expected response** includes:
```json
{
  "response": "🎯 PROJECT SCOPE DETECTED!...\n✅ AI SWARM CREATED!...",
  "model": "x-ai/grok-code-fast-1",
  "conversationId": "test-123"
}
```

---

## 🎯 **Success Criteria**

✅ **Chat Integration**:
- AI detects "build/create" keywords
- Auto-submits to orchestrator backend
- Shows swarm link in chat

✅ **Swarm Creation**:
- 5-12s total time
- 3 agents created
- 12 subtasks generated (4 per agent)
- Database populated

✅ **Planner UI**:
- Clickable 🚀 button in chat
- Links to `/planner/<swarm_id>`
- Shows hierarchical tasks
- Expandable subtasks with tools

✅ **Dual Mode**:
- Project scopes → Swarms
- Regular questions → Normal chat

---

## 🚀 **You're Ready!**

**Start Testing**:
1. Run 3 terminals (MCP, API, Frontend)
2. Open http://localhost:3000
3. Chat: "Build an e-commerce store with Stripe"
4. Click the 🚀 button
5. Watch your swarm work!

**Have fun creating AI swarms!** 🎉

---

**Last Updated**: 2025-10-09  
**Version**: 1.0 (Chat Integration Complete)  
**Status**: ✅ Production Ready - Rock & Roll! 🎸
