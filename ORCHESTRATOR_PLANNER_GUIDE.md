# 🎯 Orchestrator → Planner Integration Guide

Complete guide for the **Scope → Swarm → Planner** pipeline that dynamically populates your `agent-plan.tsx` component.

## 🏗️ Architecture Overview

```
User Input → Orchestrator Agent → Hive-Mind DB → FastAPI → React UI
    ↓              ↓                    ↓            ↓         ↓
  "Build         Grok-4-Fast         Swarm with    REST      agent-plan.tsx
   task          generates            3 agents     API       (animated UI)
   tracker"      scope + tasks        (SQLite)   endpoints
```

### Components

1. **Orchestrator Agent** (`backend/orchestrator_agent.py`)
   - Main entry point for user requests
   - Clarifies vague inputs ("hey") using Grok-4-Fast
   - Extracts structured scope from natural language
   - Starts swarm with 3 specialized agents
   - Generates hierarchical tasks/subtasks

2. **Hive-Mind Database** (`backend/hive_mind_db.py`)
   - SQLite persistence for swarm state
   - Stores swarms, agents, tasks, sessions
   - WAL mode for concurrent agent access

3. **FastAPI Server** (`backend/swarm_api.py`)
   - REST endpoints for frontend integration
   - CORS enabled for Next.js
   - Real-time swarm status

4. **Agent Planner UI** (`components/ui/agent-plan.tsx`)
   - Dynamic task rendering
   - Auto-polling for swarm updates
   - Animated status changes

## 🚀 Quick Start

### 1. Ensure API is Running

```bash
cd backend

# Check if running
lsof -ti:8000

# If not running, start it
python swarm_api.py
```

### 2. Test Orchestrator

```bash
# Run test pipeline
python test_orchestrator_pipeline.py
```

**Expected output:**
```json
{
  "status": "success",
  "message": "Scope populated! Swarm started for TrackFlow",
  "swarm_id": "abc-123-xyz",
  "planner_url": "/planner/abc-123-xyz"
}
```

### 3. Use in Frontend

#### Option A: Direct Component Usage

```tsx
import Plan from '@/components/ui/agent-plan';

export default function PlannerPage() {
  return (
    <div className="h-screen">
      <Plan swarmId="abc-123-xyz" enablePolling={true} pollingInterval={3000} />
    </div>
  );
}
```

#### Option B: Fetch from User Chat

```tsx
'use client';

import { useState } from 'react';
import Plan from '@/components/ui/agent-plan';

export default function ChatInterface() {
  const [swarmId, setSwarmId] = useState<string | null>(null);
  
  const handleUserMessage = async (message: string) => {
    const response = await fetch('http://localhost:8000/orchestrator/process', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message, user_id: 'user123' })
    });
    
    const result = await response.json();
    
    if (result.status === 'success') {
      setSwarmId(result.swarm_id);
    } else if (result.status === 'needs_clarification') {
      alert(result.message); // Or show in chat
    }
  };
  
  return (
    <div className="grid grid-cols-2 h-screen">
      <div className="border-r">
        {/* Chat UI */}
        <input 
          type="text" 
          placeholder="Tell me what to build..."
          onKeyPress={(e) => {
            if (e.key === 'Enter') {
              handleUserMessage(e.currentTarget.value);
              e.currentTarget.value = '';
            }
          }}
        />
      </div>
      
      <div>
        {swarmId ? (
          <Plan swarmId={swarmId} />
        ) : (
          <div className="flex items-center justify-center h-full text-white/40">
            Enter a project idea to start planning...
          </div>
        )}
      </div>
    </div>
  );
}
```

## 📋 API Reference

### POST /orchestrator/process

Process user input and create swarm.

**Request:**
```json
{
  "message": "Build a task tracker with Next.js",
  "user_id": "user123"
}
```

**Response (Success):**
```json
{
  "status": "success",
  "message": "Scope populated! Swarm started for TaskTracker",
  "swarm_id": "550e8400-e29b-41d4-a716-446655440000",
  "planner_url": "/planner/550e8400-e29b-41d4-a716-446655440000"
}
```

**Response (Needs Clarification):**
```json
{
  "status": "needs_clarification",
  "message": "I'd be happy to help! To build something great, I need a bit more info:\n\n1. What's the main goal or purpose of your project?\n2. What type of application are you thinking? (web app, mobile app, API, dashboard, etc.)\n3. Any specific features or requirements you have in mind?",
  "swarm_id": null
}
```

### GET /api/planner/{swarm_id}

Get formatted planner data for UI.

**Response:**
```json
{
  "swarm_id": "550e8400-e29b-41d4-a716-446655440000",
  "tasks": [
    {
      "id": "1",
      "title": "Research Project Requirements",
      "description": "Handle research tasks for TrackFlow",
      "status": "assigned",
      "priority": "high",
      "level": 0,
      "dependencies": [],
      "subtasks": [
        {
          "id": "1.1",
          "title": "Analyze Trello's core task management features",
          "description": "Research how Trello handles boards, lists, and cards...",
          "priority": "high",
          "status": "pending",
          "tools": ["browser", "web-scraper"]
        }
      ]
    }
  ]
}
```

## 🎨 UI Component Props

### Plan Component

```typescript
interface PlanProps {
  swarmId?: string;           // Optional: Swarm ID to load (if not provided, shows mock data)
  enablePolling?: boolean;    // Default: true - Auto-refresh every pollingInterval
  pollingInterval?: number;   // Default: 3000ms - How often to fetch updates
}
```

**Examples:**

```tsx
// Static mock data (no swarm)
<Plan />

// Load from swarm, no polling
<Plan swarmId="abc-123" enablePolling={false} />

// Load with fast polling (1s)
<Plan swarmId="abc-123" pollingInterval={1000} />
```

## 🔄 Workflow Examples

### Example 1: TrackFlow (Task Tracker)

**User Input:**
```
"Build a task tracking dashboard like Trello with Next.js, authentication, and analytics"
```

**Orchestrator Actions:**
1. Extracts scope using Grok-4-Fast:
   ```json
   {
     "project": "TrackFlow",
     "goal": "SaaS task tracking dashboard similar to Trello",
     "tech_stack": {
       "frontend": "Next.js + Tailwind",
       "backend": "FastAPI",
       "database": "PostgreSQL"
     },
     "features": ["boards", "tasks", "auth", "analytics"],
     "comps": ["Trello", "Asana"],
     "timeline": "1-2h"
   }
   ```

2. Creates swarm with 3 agents:
   - **Research Agent**: Analyze Trello/Asana, identify gaps
   - **Design Agent**: Create wireframes, DB schema, API specs
   - **Implementation Agent**: Plan resources, timeline, risks

3. Generates subtasks per agent:
   - Research: "Analyze Trello's board system", "Compare auth flows"
   - Design: "Design dashboard wireframe", "Define Prisma schema"
   - Implementation: "Allocate 3 agents", "Create 2h timeline"

4. Returns swarm_id → Frontend polls → UI updates

### Example 2: E-Commerce Store

**User Input:**
```
"E-commerce store with product catalog and checkout"
```

**Generated Tasks:**
- Research: Product management systems, payment gateways
- Design: Product catalog UI, checkout flow, DB schema
- Implementation: Stripe integration plan, inventory management

## 🧪 Testing

### Test Orchestrator Locally

```bash
# Run comprehensive tests
python backend/test_orchestrator_pipeline.py
```

### Test via cURL

```bash
# Create swarm
curl -X POST http://localhost:8000/orchestrator/process \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Build a blog with Next.js and MDX",
    "user_id": "test"
  }'

# Get planner data (use swarm_id from above)
curl http://localhost:8000/api/planner/YOUR_SWARM_ID
```

### Test in Browser

1. Open http://localhost:8000/docs (FastAPI Swagger UI)
2. Try `/orchestrator/process` endpoint
3. Copy `swarm_id` from response
4. Try `/api/planner/{swarm_id}` endpoint
5. See formatted task data

## 🎯 Integration with Your Stack

### With Grok-4-Fast (OpenRouter)

Already configured! The Orchestrator uses:
```python
model = 'x-ai/grok-4-fast'  # From .env
```

Ensure `.env` has:
```env
OPENROUTER_API_KEY=your_key
OPENROUTER_MODEL=x-ai/grok-4-fast
```

### With Your ARM Hypervisor Agents

The swarm system is extensible:

```python
# Add custom agent role
# In hive_mind_db.py, update AgentSchema validator:
valid = ['research', 'design', 'implementation', 'test', 'deploy', 'quality', 'arm-port']

# In orchestrator_agent.py:
task_templates['arm-port'] = {
    'title': 'ARM→x86 Hypervisor Port',
    'description': 'Port Xen hypervisor components to ARM64',
    'priority': 'critical'
}
```

### With Your Xen Port Diff

The planner can track porting tasks:

```python
# Generate subtasks from your arm-p2m.diff
subtasks = [
    {
        "id": "port-1",
        "title": "Port p2m_lookup from x86 to ARM64",
        "description": "Implement IPA→PA translation in arch/arm/mm/p2m.c",
        "data": {
            "file": "xen/arch/arm/mm/p2m.c",
            "changes": "+47 lines",
            "status": "in-progress"
        }
    }
]
```

## 📊 Real-Time Updates

The planner polls every 3 seconds by default. Swarm agents can update task status:

```python
# In your agent execution code
from hive_mind_db import HiveMindDB

db = HiveMindDB('swarms/active_swarm.db')

# Agent completes a subtask
db.update_task_status(
    task_id='1.1',
    status='completed',
    data={
        'output': 'Trello analysis complete',
        'findings': ['Drag-drop UI', 'Real-time sync', 'Team collaboration']
    }
)

# Frontend polls → Sees status change → Animates checkmark ✅
```

## 🐛 Troubleshooting

### Planner shows "Loading..." forever

**Check:**
1. API is running: `curl http://localhost:8000`
2. Swarm ID is valid: `curl http://localhost:8000/swarms/{swarm_id}`
3. Browser console for errors
4. CORS is enabled (check API logs)

### "Failed to load planner data"

**Check:**
1. Orchestrator initialized: Look for "🎯 Orchestrator initialized" in API logs
2. Database exists: `ls -la swarms/*.db`
3. OpenRouter API key set: `echo $OPENROUTER_API_KEY`

### Tasks not updating

**Verify polling:**
```tsx
// Add debug logging
useEffect(() => {
  console.log('Polling swarm:', swarmId);
  // ...
}, [swarmId]);
```

Check network tab for `/api/planner/{id}` requests every 3s.

## 🚢 Production Deployment

### Environment Variables

```env
# .env.production
NEXT_PUBLIC_SWARM_API_URL=https://api.yourapp.com
OPENROUTER_API_KEY=your_key
OPENROUTER_MODEL=x-ai/grok-4-fast
SWARM_DB_PATH=/var/data/swarms/production.db
```

### API Deployment

```bash
# Using Docker
docker build -t swarm-api backend/
docker run -p 8000:8000 -e OPENROUTER_API_KEY=$KEY swarm-api

# Or Render/Railway/Fly.io
# Point to backend/swarm_api.py as entry point
```

### Frontend Deployment

```bash
# Vercel/Netlify
# Set NEXT_PUBLIC_SWARM_API_URL in dashboard

# Build check
npm run build
```

## 📚 Additional Resources

- **Hive-Mind DB Docs**: `backend/HIVE_MIND_README.md`
- **Agent Coordination**: Integration with Swarms.ai, LangChain, CrewAI
- **Swarm Client (TS)**: `lib/swarm-client.ts`

## ✅ Success Checklist

- [ ] API running on :8000
- [ ] Test pipeline passes (`python test_orchestrator_pipeline.py`)
- [ ] OpenRouter API key configured
- [ ] Frontend fetches planner data
- [ ] Polling works (status updates every 3s)
- [ ] Error states handled (loading, failed)
- [ ] Ready to process user inputs! 🚀

---

**You're ready to "Go TrackFlow Planner"!** 🎯

Test it: Type "Build a task tracker" → Watch the planner populate → Swarm executes → UI updates live!
