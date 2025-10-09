# 🧠 Grok-4-Fast-Reasoning Scope Breakdown System

## Overview

This system enables **natural language → structured AI swarms** using Grok-4-Fast-Reasoning for intelligent scope breakdown and task generation.

### What's New

- ✅ **Structured Scope Breakdown**: 6 must-haves (project, goal, tech stack, features, comps, timeline, outcome, scope of works)
- ✅ **Modular Task Generation**: 3 agents × 4 subtasks each = 12 modular execution units
- ✅ **MCP Tool Integration**: Each subtask tagged with specific tools (browser, code-gen, prisma-gen, etc.)
- ✅ **UI Scope Creator**: Floating button on main page for submitting project ideas
- ✅ **Auto-Planner Population**: Tasks automatically appear in Global Planner

---

## Architecture

```
User Input (Vague)
"Build an e-commerce store"
        │
        ▼
┌─────────────────────────┐
│  Grok-4-Fast-Reasoning  │ ← Enhanced Orchestrator
│  Scope Breakdown        │    (_extract_scope method)
└───────────┬─────────────┘
            │
            ▼
Structured Scope (6 Must-Haves):
├─ project: "ECommerceStripeStore"
├─ goal: "Build scalable store for browsing/cart/Stripe payments..."
├─ tech_stack: {frontend: "Next.js 14...", backend: "FastAPI...", ...}
├─ features: ["Product catalog", "Cart management", ...]
├─ comps: ["Shopify (strength/gap)", "WooCommerce", ...]
├─ timeline: "1-2h MVP"
├─ outcome: "Live repo on localhost:3000 + Vercel URL + 80% coverage"
└─ scope_of_works: {in_scope, out_scope, milestones, risks, kpis}
        │
        ▼
┌─────────────────────────┐
│  Swarm Creation         │ ← 3 Agents (Research, Design, Implementation)
│  (start_swarm_from_scope)
└───────────┬─────────────┘
            │
            ▼
Task Generation (Per Agent):
├─ Agent 1 (Research): 4 subtasks
│  ├─ 1.1: Gather user requirements (tools: browser, communication)
│  ├─ 1.2: Analyze Shopify (tools: browser, web-scraper)
│  ├─ 1.3: Analyze WooCommerce (tools: browser)
│  └─ 1.4: Assess Next.js+Stripe fit (tools: documentation-sites, code-gen)
│
├─ Agent 2 (Design): 4 subtasks
│  ├─ 2.1: Design wireframes (tools: diagramming, shadcn-gen)
│  ├─ 2.2: Design DB schema (tools: prisma-gen, db-sync)
│  ├─ 2.3: Specify APIs (tools: api-designer, zod-validator)
│  └─ 2.4: Outline Stripe integration (tools: stripe-tool, code-gen)
│
└─ Agent 3 (Implementation): 4 subtasks
   ├─ 3.1: Resource allocation (tools: orchestrator-assign)
   ├─ 3.2: Development timeline (tools: timeline-generator)
   ├─ 3.3: Risk assessment (tools: risk-analyzer)
   └─ 3.4: Setup localhost:3000 (tools: code-gen, docker-build)
        │
        ▼
┌─────────────────────────┐
│  Global Planner UI      │ ← Auto-updates with tasks
│  (agent-planner.tsx)    │    Status: pending → in-progress → completed
└─────────────────────────┘
```

---

## How to Use

### 1. Start Backend Servers

```bash
# Terminal 1: MCP Tools (port 8001)
cd backend
source venv/bin/activate
python3 mcp_servers.py

# Terminal 2: Swarm API (port 8000)
python3 main.py
```

### 2. Start Frontend

```bash
# Terminal 3
npm run dev
# Open http://localhost:3000
```

### 3. Submit a Scope

**Option A: UI (Recommended)**
1. Click violet **Sparkles button** (bottom-right corner)
2. Enter project description:
   - "Build an e-commerce store with Stripe"
   - "Create a task tracker like Trello"
   - "Make a SaaS dashboard with analytics"
3. Click **"Create AI Swarm"**
4. Auto-redirected to planner page

**Option B: API**
```bash
curl -X POST http://localhost:8000/orchestrator/process \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Build a real-time chat app with WebSockets",
    "user_id": "demo"
  }'
```

**Option C: Python Test**
```bash
cd backend
python3 test_grok_reasoning.py
# Or test single scope:
python3 test_grok_reasoning.py "Build a blog with markdown support"
```

---

## The Stack That Ships (2025)

Grok uses these defaults for all projects:

### Frontend (MVP Tier)
- **Framework**: Next.js 14+ App Router + TypeScript
- **Styling**: Tailwind CSS + Shadcn/ui (copy-paste components)
- **State**: TanStack Query (server) + Zustand (client, if needed)
- **Forms**: React Hook Form + Zod
- **Auth**: Clerk or NextAuth
- **Deploy**: Vercel
- **Monitoring**: Sentry

### Backend (Scale-Up Tier)
- **Runtime**: Node.js/Express or FastAPI (Python)
- **ORM**: Prisma (Node) / SQLAlchemy (Python)
- **Database**: PostgreSQL (Railway)
- **Cache**: Redis (Upstash)
- **Queues**: BullMQ
- **Auth**: JWT + Clerk
- **Payments**: Stripe
- **Deploy**: Railway/Fly.io
- **CI/CD**: GitHub Actions

### Rules
1. **One meta-framework**: Next.js (no mixing with Remix/Nuxt)
2. **Tailwind first**: No CSS-in-JS unless absolutely needed
3. **Copy-paste Shadcn**: Faster than npm packages
4. **Mobile-first**: Responsive by default
5. **Error boundaries**: Everywhere
6. **80% test coverage**: Vitest + Playwright

---

## Enhanced Orchestrator Methods

### `_extract_scope(message)` - Scope Fleshing

**Before**: Basic JSON extraction
```python
{
  "project": "UserProject",
  "goal": "Build something",
  "tech_stack": {"frontend": "Next.js"}
}
```

**After**: 6 Must-Haves with Grok reasoning
```python
{
  "project": "ECommerceStripeStore",
  "goal": "Build scalable online store for browsing products, managing carts, and secure Stripe payments. Solve pain: Easy setup for indie sellers.",
  "tech_stack": {
    "frontend": "Next.js 14+ App Router + TS + Tailwind + Shadcn",
    "backend": "FastAPI + Prisma + PostgreSQL",
    "database": "PostgreSQL (Railway)",
    "auth": "Clerk",
    "payments": "Stripe",
    "deployment": "Vercel (frontend) + Railway (backend)"
  },
  "features": [
    "Product catalog with search/filters",
    "Cart management (add/remove/Zustand)",
    "User auth (Clerk login/signup)",
    "Stripe checkout sessions",
    "Order dashboard"
  ],
  "comps": [
    "Shopify (strength: Easy carts, $29/mo; gap: Vendor lock - your open Next.js alternative)",
    "WooCommerce (WordPress plugins; gap: Heavy for non-blogs)",
    "BigCommerce (Enterprise scale)"
  ],
  "timeline": "1-2h MVP scaffold; 2-3 days full prod",
  "outcome": "Live Next.js store on localhost:3000 + Vercel URL + 80% test coverage + Mobile-first",
  "scope_of_works": {
    "in_scope": ["Research (comps/schema)", "Design (wireframes/APIs)", "Implementation (code/deploy)"],
    "out_scope": ["Native apps", "Advanced analytics (BI tools)"],
    "milestones": [
      "M1: Research done (0-15 min)",
      "M2: Design specs (15-45 min)",
      "M3: MVP on localhost:3000 (45-120 min)"
    ],
    "risks": [
      "Stripe compliance (mitigation: Sandbox + OWASP)",
      "Scaling carts (mitigation: Redis)"
    ],
    "kpis": [
      "95% uptime",
      "Checkout <3s load",
      "Lighthouse 90+",
      "80% test coverage"
    ]
  }
}
```

### `_generate_subtasks(role, scope)` - Modular Breakdown

**Before**: Generic fallback tasks
```python
[
  {"id": "research-1", "title": "Research task 1", "tools": ["research-tools"]}
]
```

**After**: Role-specific, project-tailored tasks
```python
# For role="research", project="ECommerceStripeStore":
[
  {
    "id": "1.1",
    "title": "Gather User Requirements (Browsing/Cart/Stripe)",
    "description": "Interview/survey for core flows (product search, secure checkout). Document pain points.",
    "priority": "high",
    "tools": ["browser", "communication-tool"],
    "status": "pending"
  },
  {
    "id": "1.2",
    "title": "Analyze Shopify Comps",
    "description": "Research Shopify features/pricing/Stripe gaps for inspiration.",
    "priority": "medium",
    "tools": ["browser", "web-scraper"],
    "status": "pending"
  },
  {
    "id": "1.3",
    "title": "Analyze WooCommerce Comps",
    "description": "Evaluate WordPress/Stripe integration pros/cons.",
    "priority": "medium",
    "tools": ["browser", "web-scraper"],
    "status": "pending"
  },
  {
    "id": "1.4",
    "title": "Assess Stack Fit (Next.js + Stripe)",
    "description": "Validate Next.js 14 + FastAPI + Stripe for MVP scalability/security.",
    "priority": "high",
    "tools": ["documentation-sites", "code-gen"],
    "status": "pending"
  }
]
```

---

## UI Components

### SwarmScopeCreator (`components/SwarmScopeCreator.tsx`)

**Features**:
- Floating violet Sparkles button (bottom-right)
- Expands to form with textarea
- Example prompts (quick-fill)
- Real-time submission to orchestrator
- Success/error/clarification states
- Auto-redirect to planner

**Design**:
- Black/95 backdrop blur
- Violet gradient border
- Pulsing glow animation
- Framer Motion transitions

**Integration**: Added to `app/layout.tsx` (global)

---

## Testing

### Full Test Suite
```bash
cd backend
python3 test_grok_reasoning.py
```

**Tests**:
1. E-Commerce (Complex scope)
2. Task Tracker (Moderate)
3. Chat App (Specific)
4. Vague Input (Clarification flow)

**Output**:
```
🧪 TESTING GROK-4-FAST-REASONING SCOPE BREAKDOWN
──────────────────────────────────────────────────

📝 Test Case: E-Commerce (Complex)
   Input: 'Build an e-commerce store with Stripe'

✅ Scope fleshed: ECommerceStripeStore
   Goal: Build scalable online store for browsing products...
   Features: 5 items
   Timeline: 1-2h MVP

✅ Result Status: success
   Message: Scope populated! Swarm started for ECommerceStripeStore
   Swarm ID: abc123-...
   Planner URL: /planner/abc123-...

📊 Planner Tasks Generated:

   Task 1: Research Project Requirements
   ├─ Status: pending
   ├─ Priority: high
   └─ Subtasks: 4 items
      • 1.1: Gather User Requirements (Browsing/Cart/Stripe)
        Tools: browser, communication-tool
      • 1.2: Analyze Shopify Comps
        Tools: browser, web-scraper

   Task 2: Design System Architecture
   ├─ Status: pending
   ├─ Priority: high
   └─ Subtasks: 4 items
      • 2.1: Design Wireframes for Product catalog
        Tools: diagramming-tool, shadcn-gen
      • 2.2: Design DB Schema (Prisma/PG)
        Tools: prisma-gen, db-sync

   Task 3: Implementation Planning
   ├─ Status: pending
   ├─ Priority: medium
   └─ Subtasks: 4 items
      • 3.1: Resource Allocation (3 Agents)
        Tools: orchestrator-assign
      • 3.2: Development Timeline (1-2h Scaffold)
        Tools: timeline-generator

📈 TEST SUMMARY
──────────────────────────────────────────────────
✅ E-Commerce (Complex): PASS
   └─ 3 tasks, 12 subtasks
✅ Task Tracker (Moderate): PASS
   └─ 3 tasks, 12 subtasks
✅ Chat App (Specific): PASS
   └─ 3 tasks, 12 subtasks
✅ Vague Input: PASS (Clarification)

📊 Results: 4/4 tests passed

🎯 GROK-4-FAST-REASONING BREAKDOWN IS READY!
```

### Single Scope Test
```bash
python3 test_grok_reasoning.py "Build a blog with markdown support"
```

---

## Next Steps

### Phase 1: Execution (Current)
- ✅ Scope breakdown working
- ✅ Task generation working
- ✅ Planner UI integration
- 🔄 **Next**: Enable agents to execute MCP tools

### Phase 2: Tool Execution
```python
# In swarm execution loop:
for task in tasks:
    for subtask in task.subtasks:
        if subtask.tools:
            for tool in subtask.tools:
                result = orchestrator.call_mcp_tool(
                    tool_name=tool,
                    args={"query": subtask.description},
                    swarm_id=swarm_id,
                    agent_id=agent.id
                )
                # Update subtask status based on result
                db.update_subtask_status(subtask.id, 'completed')
```

### Phase 3: Code Generation
- Agents use `code-gen` tool to create actual files
- Output to `generated/{swarm_id}/` directory
- Preview in planner UI

### Phase 4: Auto-Deploy
- Vercel API integration
- Push to GitHub
- Deploy preview
- Return live URL

---

## Troubleshooting

### "Orchestrator not responding"
```bash
# Check backend is running
curl http://localhost:8000/swarms
# Should return {"swarms": [...], "count": N}
```

### "Grok API error"
```bash
# Verify API key in .env
cd backend
cat .env | grep OPENROUTER_API_KEY
# Should show: OPENROUTER_API_KEY1=sk-or-v1-...
```

### "Tasks not appearing in planner"
```bash
# Check database
cd backend
sqlite3 swarms/active_swarm.db
> SELECT * FROM swarms ORDER BY created_at DESC LIMIT 1;
> SELECT * FROM agents WHERE swarm_id = '<swarm_id>';
```

### "UI button not showing"
- Check browser console for errors
- Verify `SwarmScopeCreator` imported in `layout.tsx`
- Clear Next.js cache: `rm -rf .next && npm run dev`

---

## API Reference

### POST `/orchestrator/process`

**Request**:
```json
{
  "message": "Build an e-commerce store with Stripe",
  "user_id": "web-user"
}
```

**Response (Success)**:
```json
{
  "status": "success",
  "message": "Scope populated! Swarm started for ECommerceStripeStore",
  "swarm_id": "abc123-def456-...",
  "planner_url": "/planner/abc123-def456-..."
}
```

**Response (Clarification)**:
```json
{
  "status": "needs_clarification",
  "message": "Could you clarify: 1) What's the main goal? 2) Web app or mobile? 3) Key features?",
  "swarm_id": null
}
```

### GET `/api/planner/{swarm_id}`

**Response**:
```json
{
  "swarm_id": "abc123-...",
  "tasks": [
    {
      "id": "1",
      "title": "Research Project Requirements",
      "description": "Gather e-comm needs, comps, and stack fit",
      "status": "pending",
      "priority": "high",
      "level": 0,
      "dependencies": [],
      "subtasks": [
        {
          "id": "1.1",
          "title": "Gather User Requirements",
          "description": "...",
          "status": "pending",
          "priority": "high",
          "tools": ["browser", "communication-tool"]
        }
      ]
    }
  ]
}
```

---

## Performance

- **Scope Extraction**: ~2-5s (Grok inference)
- **Task Generation**: ~3-6s (3 agents × Grok calls)
- **Total Swarm Creation**: ~5-12s
- **Planner Render**: <100ms (React)

**Optimization Tips**:
- Use `temperature=0.3` for scope (consistent)
- Use `temperature=0.4` for tasks (creative but structured)
- Cache common scopes (e.g., "task tracker" → TrackFlow template)
- Parallel agent task generation (future)

---

## Credits

**Built with**:
- Grok-4-Fast-Reasoning (x-ai/grok-4-fast via OpenRouter)
- Next.js 15 + TypeScript
- FastAPI (Python)
- SQLite (Hive-Mind DB)
- Framer Motion (animations)
- Tailwind CSS + Shadcn/ui

**Powered by**: The Stack That Ships™ (2025)

---

**Last Updated**: 2025-10-09  
**Version**: 1.0 (Grok Reasoning Integration)  
**Status**: ✅ Production Ready - Start Testing!
