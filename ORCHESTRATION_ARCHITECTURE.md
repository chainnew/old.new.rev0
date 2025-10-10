# 🎯 ORCHESTRATION ARCHITECTURE ANALYSIS

**Grok-Orc → 3 AI Agents: Work Assignment, Management, Conflict Resolution & Scheduling**

---

## 📋 Executive Summary

This document provides a complete analysis of how **grok-orc** (the master orchestrator) manages the 3 specialized AI agents, including:

- ✅ **Work Assignment Algorithm** - How tasks are routed to agents
- ✅ **Management & Oversight** - Real-time monitoring and coordination
- ⚠️ **Conflict Resolution** - Current gaps and recommendations
- ⚠️ **Scheduling & Dependencies** - Basic implementation, needs enhancement

**Current Status**: Proof-of-concept architecture with solid foundation but **missing advanced conflict resolution and scheduling**.

---

## 🏗️ System Architecture Overview

### The Players

```
┌─────────────────────────────────────────────────────────────┐
│                     GROK-ORC (Orchestrator)                  │
│  - User-facing AI (x-ai/grok-4-fast-reasoning)              │
│  - Scope extraction & clarification                          │
│  - Swarm creation (3 agents)                                 │
│  - Task generation (12 subtasks = 3 agents × 4 each)        │
│  - Status monitoring                                         │
└────────────────────┬────────────────────────────────────────┘
                     │
        ┌────────────┴────────────┐
        │   HIVE-MIND DATABASE    │
        │   (SQLite - swarms/     │
        │    active_swarm.db)     │
        │  - swarms                │
        │  - agents                │
        │  - tasks                 │
        │  - sessions              │
        └────────────┬────────────┘
                     │
     ┌───────────────┼───────────────┐
     │               │               │
┌────▼────┐    ┌────▼────┐    ┌────▼────┐
│Frontend │    │Backend  │    │Deployment│
│Architect│    │Integrator│   │Guardian  │
│         │    │         │    │         │
│Design + │    │Impl +   │    │Test +   │
│Impl     │    │Integration│  │Deploy   │
│(UI/UX)  │    │(APIs/DB)│    │(CI/CD)  │
└────┬────┘    └────┬────┘    └────┬────┘
     │               │               │
     └───────────────┼───────────────┘
                     │
              ┌──────▼──────┐
              │  MCP TOOLS  │
              │  Port 8001  │
              │- browser    │
              │- code-gen   │
              │- db-sync    │
              │- stripe-tool│
              └─────────────┘
```

---

## 🎯 Part 1: Work Assignment Algorithm

### How Grok-Orc Assigns Work to Agents

**File**: `backend/orchestrator_agent.py` (Lines 207-283)

### Step-by-Step Flow

```python
# STEP 1: User message arrives → Grok-Orc receives
handle_user_input(message: str, user_id: str)
  ├─→ Check if vague (< 5 words or greetings)
  │     ├─→ YES: Ask clarifying questions using Grok-4-Fast
  │     └─→ NO: Continue to scope extraction
  │
  ├─→ STEP 2: Extract structured scope using Grok-4-Fast-Reasoning
  │   _extract_scope(message) → Returns JSON:
  │     {
  │       "project": "EcommerceStore",
  │       "goal": "Build online store with Stripe",
  │       "tech_stack": { frontend, backend, database },
  │       "features": ["product catalog", "cart", "checkout"],
  │       "timeline": "1-2h",
  │       "scope_of_works": { in_scope, milestones, risks, kpis }
  │     }
  │
  ├─→ STEP 3: Start swarm with 3 agents (hardcoded optimal number)
  │   db.start_swarm_from_scope(scope, num_agents=3)
  │     └─→ Creates agents with specialized roles:
  │         1. frontend_architect    (Design + Implementation)
  │         2. backend_integrator    (Implementation + Integration)
  │         3. deployment_guardian   (Testing + Deployment)
  │
  └─→ STEP 4: Generate & assign 12 subtasks (4 per agent)
      _populate_planner_tasks(swarm_id, scope)
        ├─→ For each agent:
        │     ├─→ Get role-specific prompt template
        │     ├─→ Call Grok-4-Fast to generate 4 subtasks
        │     └─→ Store in agent state (hive-mind DB)
        │
        └─→ Update swarm status to 'running'
```

### Task Templates (Orchestrator Lines 217-262)

**Frontend Architect** gets:
```json
{
  "title": "Frontend Architecture & Implementation",
  "description": "Design UI/UX wireframes and implement Next.js components with Shadcn/TanStack",
  "priority": "high",
  "level": 0,
  "dependencies": []
}
```

**Backend Integrator** gets:
```json
{
  "title": "Backend Integration & APIs",
  "description": "Design database schema, implement APIs, and integrate Stripe/Redis/queues",
  "priority": "high",
  "level": 0,
  "dependencies": []
}
```

**Deployment Guardian** gets:
```json
{
  "title": "Testing & Deployment",
  "description": "Setup CI/CD, run E2E tests, and deploy to Vercel/Railway",
  "priority": "medium",
  "level": 1,
  "dependencies": ["1", "2"]  // ⚠️ DEPENDS ON FRONTEND & BACKEND
}
```

### Subtask Generation Process (Lines 323-527)

**Orchestrator calls `_generate_subtasks()` for each agent:**

1. **Constructs role-specific prompt** with:
   - Project name, goal, features
   - Tech stack (Next.js, FastAPI, PostgreSQL)
   - Timeline and competitor info
   - Instructions for 4 modular subtasks

2. **Calls Grok-4-Fast-Reasoning** with temperature 0.4:
   ```python
   response = self.client.chat.completions.create(
       model=self.model,  # x-ai/grok-4-fast
       messages=[{"role": "user", "content": prompt}],
       temperature=0.4
   )
   ```

3. **Parses JSON response** (with markdown cleanup):
   ```json
   [
     {
       "id": "1.1",
       "title": "Design + Implement Product Catalog UI",
       "description": "Create Shadcn wireframe specs, then code /app/products/page.tsx",
       "priority": "high",
       "tools": ["shadcn-gen", "code-gen", "browser"],
       "status": "pending"
     },
     { /* 3 more subtasks */ }
   ]
   ```

4. **Stores in hive-mind DB**:
   ```python
   db.update_agent_state(agent['id'], {
       'status': 'assigned',
       'data': {
           'task_id': str(idx),
           'task_title': template['title'],
           'subtasks': subtasks
       }
   })
   ```

### Assignment Algorithm Summary

| Step | Action | File | Lines |
|------|--------|------|-------|
| 1 | Receive user message | orchestrator_agent.py | 58-71 |
| 2 | Extract scope using Grok | orchestrator_agent.py | 117-205 |
| 3 | Create 3 specialized agents | hive_mind_db.py | 194-214 |
| 4 | Generate 4 subtasks per agent | orchestrator_agent.py | 323-527 |
| 5 | Store in agent state | hive_mind_db.py | 267-272 |

**✅ STRENGTHS:**
- Clean separation of concerns (3 specialized roles)
- AI-powered task generation (context-aware)
- Structured JSON output for frontend consumption
- Hardcoded 3-agent optimal configuration (prevents over-complexity)

**⚠️ GAPS:**
- No dynamic agent selection (always creates 3 agents)
- No load balancing (all agents get 4 tasks regardless of complexity)
- No task splitting/merging based on scope size

---

## 👁️ Part 2: Management & Oversight

### How Grok-Orc Monitors Agents

**Files**: `backend/agents/swarm_coordinator.py` + `backend/hive_mind_db.py`

### SwarmCoordinator Architecture

**File**: `swarm_coordinator.py` (Lines 43-293)

```python
class SwarmCoordinator:
    def __init__(self):
        self.queues: Dict[str, asyncio.Queue] = {}      # Message passing
        self.agent_health: Dict[str, AgentHealth] = {}  # Health tracking
        self.active_tasks: Dict[str, Dict[str, Any]] = {}
        self.results_cache: Dict[str, Any] = {}
```

### Management Features

#### 1. Agent Registration (Lines 67-86)

```python
def register_agent(self, agent_id: str) -> asyncio.Queue:
    """Each agent registers with coordinator and gets message queue"""
    if agent_id not in self.queues:
        self.queues[agent_id] = asyncio.Queue()
        self.agent_health[agent_id] = AgentHealth(
            agent_id=agent_id,
            status=AgentStatus.IDLE,
            last_heartbeat=datetime.now()
        )
    return self.queues[agent_id]
```

**Agent Status Enum** (Lines 12-18):
- `IDLE` - Ready for work
- `WORKING` - Currently executing
- `COMPLETED` - Task finished
- `FAILED` - Error occurred
- `WAITING` - Blocked/dependency not met

#### 2. Health Monitoring (Lines 112-121)

```python
def update_agent_status(self, agent_id: str, status: AgentStatus):
    """Update agent status with automatic heartbeat"""
    if agent_id in self.agent_health:
        self.agent_health[agent_id].status = status
        self.agent_health[agent_id].last_heartbeat = datetime.now()

def heartbeat(self, agent_id: str):
    """Agent sends periodic heartbeat"""
    if agent_id in self.agent_health:
        self.agent_health[agent_id].last_heartbeat = datetime.now()
```

**Health Tracking** (Lines 33-40):
```python
@dataclass
class AgentHealth:
    agent_id: str
    status: AgentStatus
    last_heartbeat: datetime
    tasks_completed: int = 0
    tasks_failed: int = 0
    avg_execution_time_ms: float = 0.0
```

#### 3. Message Passing System (Lines 88-110)

**Agent-to-Agent Communication:**

```python
@dataclass
class AgentMessage:
    from_agent: str
    to_agent: str
    message_type: str  # 'task', 'result', 'query', 'handshake'
    payload: Dict[str, Any]
    timestamp: datetime
    conversation_id: str = ""

async def send_message(self, message: AgentMessage):
    """Send message to specific agent"""
    await self.queues[message.to_agent].put(message)

async def broadcast_message(self, from_agent: str, message_type: str, payload: Dict):
    """Send to all agents (except sender)"""
    for agent_id in self.queues.keys():
        if agent_id != from_agent:
            msg = AgentMessage(from_agent, agent_id, message_type, payload)
            await self.send_message(msg)
```

**Message Types:**
- `task` - New work assignment
- `result` - Task completion output
- `query` - Request clarification from orchestrator
- `handshake` - Agent announces capabilities on startup

#### 4. Task Routing (Lines 151-186)

**Simple routing based on task type:**

```python
async def route_task(self, task: Dict[str, Any]) -> str:
    """Route task to best available agent"""
    task_type = task.get('type', 'code')

    # Task type → Agent mapping
    agent_mapping = {
        'code': 'code_agent',
        'port': 'eterna_port_agent',
        'debug': 'debug_agent',
        'research': 'research_agent'
    }

    selected_agent = agent_mapping.get(task_type, 'code_agent')

    # Check if agent is IDLE
    if self.agent_health[selected_agent].status == AgentStatus.IDLE:
        self.update_agent_status(selected_agent, AgentStatus.WORKING)
        return selected_agent

    # Fallback: Find any idle agent
    for agent_id, health in self.agent_health.items():
        if health.status == AgentStatus.IDLE:
            self.update_agent_status(agent_id, AgentStatus.WORKING)
            return agent_id

    # All busy - return first agent (will queue)
    return selected_agent
```

**⚠️ LIMITATION:** This routing logic is basic and not actively used in the 3-agent orchestration (agents are pre-assigned by role).

#### 5. Task Execution with Stats (Lines 188-242)

```python
async def execute_swarm_task(self, task: Dict, agents: Dict) -> Dict:
    """Execute task and track metrics"""
    selected_agent_id = await self.route_task(task)

    try:
        agent = agents[selected_agent_id]
        result = await agent.execute(task)

        # Update success/failure counts
        if result.get('status') == 'completed':
            self.agent_health[selected_agent_id].tasks_completed += 1
        else:
            self.agent_health[selected_agent_id].tasks_failed += 1

        self.update_agent_status(selected_agent_id, AgentStatus.COMPLETED)
        self.results_cache[task_id] = result

        return result
    except Exception as e:
        self.update_agent_status(selected_agent_id, AgentStatus.FAILED)
        return {'status': 'failed', 'error': str(e)}
```

#### 6. Swarm Health Dashboard (Lines 244-258)

```python
def get_swarm_stats(self) -> Dict[str, Any]:
    """Get real-time swarm statistics"""
    return {
        'total_agents': len(self.agent_health),
        'agents': {
            agent_id: {
                'status': health.status.value,
                'tasks_completed': health.tasks_completed,
                'tasks_failed': health.tasks_failed,
                'last_heartbeat': health.last_heartbeat.isoformat()
            }
            for agent_id, health in self.agent_health.items()
        }
    }
```

#### 7. Agent Handshake Protocol (Lines 123-149)

**When agents start, they announce capabilities:**

```python
async def handshake(self, agent_id: str, capabilities: Dict) -> bool:
    """Agent announces capabilities to swarm"""
    if agent_id not in self.queues:
        self.register_agent(agent_id)

    # Broadcast to other agents
    await self.broadcast_message(
        from_agent=agent_id,
        message_type="handshake",
        payload={
            "agent_id": agent_id,
            "capabilities": capabilities,
            "timestamp": datetime.now().isoformat()
        }
    )
    return True
```

**Example Capabilities:**
```json
{
  "agent_id": "frontend_architect",
  "capabilities": {
    "skills": ["Design", "Implementation", "UI/UX"],
    "tools": ["shadcn-gen", "code-gen", "browser"],
    "models": ["x-ai/grok-4-fast-reasoning"],
    "max_parallel_tasks": 4
  }
}
```

### Hive-Mind Database State Management

**File**: `hive_mind_db.py`

#### Database Schema (Lines 80-142)

```sql
-- Swarms table: Top-level orchestration
CREATE TABLE swarms (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'idle',  -- idle/running/paused/completed/error
    num_agents INTEGER NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    metadata TEXT  -- JSON: full scope, features, timeline
);

-- Agents table: Individual agents
CREATE TABLE agents (
    id TEXT PRIMARY KEY,
    swarm_id TEXT NOT NULL,
    role TEXT NOT NULL,  -- frontend_architect/backend_integrator/deployment_guardian
    state TEXT NOT NULL,  -- JSON: {status: 'executing', data: {...}}
    assigned_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (swarm_id) REFERENCES swarms (id) ON DELETE CASCADE
);

-- Tasks table: Granular work units
CREATE TABLE tasks (
    id TEXT PRIMARY KEY,
    agent_id TEXT NOT NULL,
    swarm_id TEXT NOT NULL,
    description TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',  -- pending/in-progress/completed/failed
    priority INTEGER DEFAULT 5,
    data TEXT NOT NULL,  -- JSON: inputs/outputs
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT (datetime('now')),
    FOREIGN KEY (agent_id) REFERENCES agents (id) ON DELETE CASCADE
);

-- Sessions table: Persistent hive-mind memory
CREATE TABLE sessions (
    id TEXT PRIMARY KEY,
    swarm_id TEXT NOT NULL,
    data TEXT NOT NULL,  -- JSON: {scope, progress: 75, learned: {...}}
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

#### State Update Methods (Lines 267-337)

```python
def update_agent_state(self, agent_id: str, new_state: Dict[str, Any]):
    """Agents update their own state during execution"""
    self.cursor.execute(
        "UPDATE agents SET state = ? WHERE id = ?",
        (json.dumps(new_state), agent_id)
    )
    self.conn.commit()

def update_task_status(self, task_id: str, status: str, data: Optional[Dict] = None):
    """Update task progress"""
    if data:
        self.cursor.execute(
            "UPDATE tasks SET status = ?, data = ?, updated_at = datetime('now') WHERE id = ?",
            (status, json.dumps(data), task_id)
        )
    else:
        self.cursor.execute(
            "UPDATE tasks SET status = ?, updated_at = datetime('now') WHERE id = ?",
            (status, task_id)
        )
    self.conn.commit()

def get_swarm_status(self, swarm_id: str) -> Dict[str, Any]:
    """Full swarm status for monitoring"""
    # Get swarm + agents + tasks
    return {
        'swarm_id': swarm_id,
        'name': swarm_name,
        'status': swarm_status,
        'agents': [
            {'id': agent_id, 'role': role, 'state': json.loads(state)}
            for agent in agents
        ],
        'tasks': [
            {'id': task_id, 'description': desc, 'status': status, 'priority': priority}
            for task in tasks
        ],
        'metadata': full_scope_json
    }
```

### Management Summary

**✅ STRENGTHS:**
- Async message queues for agent communication
- Health tracking with heartbeats (30-second timeout)
- Success/failure metrics per agent
- Handshake protocol for capability discovery
- Persistent state in SQLite (survives restarts)
- Real-time status via API endpoints

**⚠️ GAPS:**
- No active monitoring dashboard (stats endpoint exists but no frontend)
- No alerting system (agents fail silently)
- No automatic recovery/retry logic
- Heartbeat timeout not enforced (ping function exists but not used)

---

## ⚖️ Part 3: Conflict Resolution

### **CRITICAL FINDING: NO CONFLICT RESOLUTION IMPLEMENTED** ⚠️

After thorough code review, **conflict resolution is completely missing** from the current implementation. Here's what exists vs. what's needed:

### What Currently Exists

**1. Basic Task Dependencies** (orchestrator_agent.py Lines 236-239)

```python
'deployment_guardian': {
    'dependencies': ['1', '2']  # Depends on frontend + backend
}
```

**Problem**: Dependencies are **declared but never enforced**. No code checks if tasks 1 and 2 are completed before starting deployment tasks.

**2. Task Priority Field** (hive_mind_db.py Line 51)

```python
class TaskSchema(BaseModel):
    priority: int = 5  # 1-10 scale
```

**Problem**: Priority is **stored but never used**. Tasks are not sorted or executed in priority order.

**3. Agent Status Tracking** (swarm_coordinator.py Lines 112-116)

```python
def update_agent_status(self, agent_id: str, status: AgentStatus):
    self.agent_health[agent_id].status = status
```

**Problem**: Status is **tracked but not acted upon**. No logic handles status transitions or blocked states.

### Conflict Scenarios (Currently Unhandled)

#### Scenario 1: Resource Contention
**Problem**: Both Frontend Architect and Backend Integrator try to modify the same file (e.g., `lib/types.ts`).

**Current Behavior**: ⚠️ **Last write wins** - No file locking, no merge strategy, potential data loss.

**Needed**:
- File-level locking mechanism
- Merge conflict detection
- Orchestrator arbitration ("Backend owns lib/types.ts")

#### Scenario 2: Dependency Deadlock
**Problem**: Frontend needs API schema from Backend, but Backend is waiting for UI wireframes from Frontend.

**Current Behavior**: ⚠️ **Both agents wait forever** - No deadlock detection.

**Needed**:
- Dependency graph validation (detect cycles)
- Deadlock resolution (prioritize one path)
- Timeout with escalation to orchestrator

#### Scenario 3: API Contract Mismatch
**Problem**: Frontend expects `GET /api/products` to return `{ products: [] }`, but Backend implements `{ data: { products: [] } }`.

**Current Behavior**: ⚠️ **Integration fails at runtime** - No contract validation.

**Needed**:
- Shared API schema (OpenAPI/Swagger)
- Contract validation before task completion
- Orchestrator-enforced schema registry

#### Scenario 4: Task Failure Cascade
**Problem**: Backend's database migration fails, blocking all dependent Frontend tasks.

**Current Behavior**: ⚠️ **Frontend tasks silently wait** - No failure propagation.

**Needed**:
- Task status propagation (failed parent → mark children as blocked)
- Automatic retry with exponential backoff
- Escalation to orchestrator after 3 retries

#### Scenario 5: Parallel Task Race Condition
**Problem**: Both Frontend and Deployment Guardian try to update `package.json` simultaneously (adding dependencies).

**Current Behavior**: ⚠️ **Race condition** - Overwrites likely.

**Needed**:
- Critical section locks for shared files
- Merge strategy (combine package.json changes)
- Orchestrator-managed write queue

### Recommended Conflict Resolution Architecture

**Minimal Viable Implementation (2-4 hours):**

```python
# NEW FILE: backend/agents/conflict_resolver.py

class ConflictResolver:
    def __init__(self, coordinator: SwarmCoordinator, db: HiveMindDB):
        self.coordinator = coordinator
        self.db = db
        self.file_locks: Dict[str, str] = {}  # filepath → agent_id
        self.dependency_graph: Dict[str, List[str]] = {}

    def check_dependencies(self, task_id: str) -> bool:
        """Ensure all dependency tasks are completed"""
        task = self.db.get_task(task_id)
        deps = task.get('dependencies', [])

        for dep_id in deps:
            dep_task = self.db.get_task(dep_id)
            if dep_task['status'] != 'completed':
                return False  # Block this task
        return True

    def acquire_file_lock(self, filepath: str, agent_id: str) -> bool:
        """Lock file for exclusive write access"""
        if filepath in self.file_locks:
            current_owner = self.file_locks[filepath]
            if current_owner != agent_id:
                return False  # Locked by another agent

        self.file_locks[filepath] = agent_id
        return True

    def release_file_lock(self, filepath: str, agent_id: str):
        """Release lock after write"""
        if self.file_locks.get(filepath) == agent_id:
            del self.file_locks[filepath]

    def detect_deadlock(self) -> Optional[List[str]]:
        """Detect circular dependencies using DFS"""
        # Build dependency graph
        for task_id, task in self.db.get_all_pending_tasks().items():
            self.dependency_graph[task_id] = task.get('dependencies', [])

        # Run cycle detection algorithm
        visited = set()
        stack = set()

        def dfs(node):
            visited.add(node)
            stack.add(node)

            for neighbor in self.dependency_graph.get(node, []):
                if neighbor not in visited:
                    if dfs(neighbor):
                        return True
                elif neighbor in stack:
                    return True  # Cycle detected!

            stack.remove(node)
            return False

        for task_id in self.dependency_graph:
            if task_id not in visited:
                if dfs(task_id):
                    return list(stack)  # Return cycle
        return None

    async def resolve_conflict(self, conflict_type: str, data: Dict) -> Dict:
        """Central conflict resolution dispatcher"""
        if conflict_type == 'file_contention':
            return await self._resolve_file_contention(data)
        elif conflict_type == 'dependency_deadlock':
            return await self._resolve_deadlock(data)
        elif conflict_type == 'api_mismatch':
            return await self._resolve_api_mismatch(data)
        elif conflict_type == 'task_failure':
            return await self._propagate_failure(data)
        else:
            return {'status': 'unhandled', 'escalate': True}

    async def _resolve_file_contention(self, data: Dict) -> Dict:
        """Strategy: Orchestrator decides priority based on task dependencies"""
        file = data['filepath']
        agent1 = data['agent1']
        agent2 = data['agent2']

        # Check which agent's task has higher priority
        task1 = self.db.get_current_task_for_agent(agent1)
        task2 = self.db.get_current_task_for_agent(agent2)

        if task1['priority'] > task2['priority']:
            winner = agent1
            loser = agent2
        else:
            winner = agent2
            loser = agent1

        # Winner gets lock, loser waits
        self.acquire_file_lock(file, winner)
        await self.coordinator.send_message(AgentMessage(
            from_agent='orchestrator',
            to_agent=loser,
            message_type='wait',
            payload={'reason': f'File {file} locked by {winner}', 'retry_after': 30}
        ))

        return {'winner': winner, 'loser': loser, 'status': 'resolved'}

    async def _resolve_deadlock(self, data: Dict) -> Dict:
        """Strategy: Break cycle by prioritizing critical path"""
        cycle = self.detect_deadlock()
        if not cycle:
            return {'status': 'no_deadlock'}

        # Choose task with highest priority in cycle
        priorities = {tid: self.db.get_task(tid)['priority'] for tid in cycle}
        critical_task = max(priorities, key=priorities.get)

        # Remove dependencies for critical task (force it to proceed)
        self.db.update_task(critical_task, {'dependencies': []})

        # Notify orchestrator
        await self.coordinator.broadcast_message(
            from_agent='orchestrator',
            message_type='deadlock_resolved',
            payload={'cycle': cycle, 'forced_task': critical_task}
        )

        return {'status': 'resolved', 'cycle': cycle, 'forced': critical_task}
```

**Integration Points:**

```python
# In orchestrator_agent.py - Add to handle_user_input()
from agents.conflict_resolver import ConflictResolver

class OrchestratorAgent:
    def __init__(self):
        # ... existing code ...
        self.conflict_resolver = ConflictResolver(self.coordinator, self.db)

    async def monitor_swarm(self, swarm_id: str):
        """Periodic monitoring loop (every 5 seconds)"""
        while True:
            await asyncio.sleep(5)

            # Check for deadlocks
            deadlock = self.conflict_resolver.detect_deadlock()
            if deadlock:
                await self.conflict_resolver.resolve_conflict('dependency_deadlock', {})

            # Check agent health
            stats = self.coordinator.get_swarm_stats()
            for agent_id, health in stats['agents'].items():
                if health['status'] == 'FAILED':
                    # Trigger retry or escalation
                    await self.handle_agent_failure(agent_id)
```

### Conflict Resolution Summary

| Conflict Type | Current State | Needed | Priority |
|---------------|---------------|--------|----------|
| File contention | ⚠️ None | File locking + priority arbitration | 🔴 HIGH |
| Dependency deadlock | ⚠️ None | Cycle detection + critical path forcing | 🔴 HIGH |
| API contract mismatch | ⚠️ None | Shared schema registry + validation | 🟡 MEDIUM |
| Task failure cascade | ⚠️ None | Status propagation + auto-retry | 🔴 HIGH |
| Race conditions | ⚠️ None | Critical section locks | 🟡 MEDIUM |

**Recommendation**: Implement file locking and deadlock detection as **Phase 1 (2-4 hours)** before production use.

---

## 📅 Part 4: Scheduling & Dependencies

### Current Dependency Implementation

**Declaration** (orchestrator_agent.py Lines 217-239):

```python
task_templates = {
    'frontend_architect': {
        'dependencies': []  # No dependencies - starts immediately
    },
    'backend_integrator': {
        'dependencies': []  # No dependencies - starts immediately
    },
    'deployment_guardian': {
        'dependencies': ['1', '2']  # ⚠️ DECLARED BUT NOT ENFORCED
    }
}
```

**Problem**: Dependencies are **metadata-only**. No code enforces them.

### What's Missing: Dependency Enforcement Engine

**Needed Implementation:**

```python
# NEW: backend/agents/scheduler.py

class TaskScheduler:
    def __init__(self, db: HiveMindDB, coordinator: SwarmCoordinator):
        self.db = db
        self.coordinator = coordinator

    def get_ready_tasks(self, swarm_id: str) -> List[Dict]:
        """Get tasks whose dependencies are satisfied"""
        pending_tasks = self.db.get_tasks_by_status(swarm_id, 'pending')
        ready = []

        for task in pending_tasks:
            if self.are_dependencies_met(task):
                ready.append(task)

        return ready

    def are_dependencies_met(self, task: Dict) -> bool:
        """Check if all dependency tasks are completed"""
        dep_ids = task.get('dependencies', [])

        for dep_id in dep_ids:
            dep_task = self.db.get_task(dep_id)
            if dep_task['status'] != 'completed':
                return False  # Dependency not done yet

        return True

    def schedule_next_batch(self, swarm_id: str) -> List[str]:
        """Get next batch of tasks to execute (respects dependencies)"""
        ready_tasks = self.get_ready_tasks(swarm_id)

        # Sort by priority
        ready_tasks.sort(key=lambda t: t['priority'], reverse=True)

        # Return up to N tasks (parallel execution limit)
        return ready_tasks[:3]  # Max 3 parallel (one per agent)

    def build_execution_timeline(self, swarm_id: str) -> Dict:
        """Generate Gantt chart data for UI"""
        tasks = self.db.get_all_tasks(swarm_id)

        # Build dependency graph
        graph = {}
        for task in tasks:
            graph[task['id']] = {
                'task': task,
                'deps': task.get('dependencies', []),
                'level': 0,  # Will be calculated
                'start_time': None,
                'duration': self.estimate_duration(task)
            }

        # Calculate levels (topological sort)
        for task_id in graph:
            graph[task_id]['level'] = self._calculate_level(graph, task_id)

        # Calculate start times
        for task_id in sorted(graph, key=lambda tid: graph[tid]['level']):
            task_data = graph[task_id]
            dep_end_times = [
                graph[dep]['start_time'] + graph[dep]['duration']
                for dep in task_data['deps']
            ]
            task_data['start_time'] = max(dep_end_times) if dep_end_times else 0

        return graph

    def estimate_duration(self, task: Dict) -> int:
        """Estimate task duration in minutes (ML model could enhance this)"""
        # Simple heuristic based on task type
        role = task.get('role', 'unknown')
        complexity = len(task.get('description', ''))

        base_duration = {
            'frontend_architect': 30,
            'backend_integrator': 45,
            'deployment_guardian': 20
        }.get(role, 30)

        # Adjust for complexity (longer descriptions = more complex)
        complexity_factor = 1 + (complexity / 500)

        return int(base_duration * complexity_factor)

    def _calculate_level(self, graph: Dict, task_id: str, visited: set = None) -> int:
        """Calculate task level in dependency graph (for Gantt chart)"""
        if visited is None:
            visited = set()

        if task_id in visited:
            return 0  # Cycle detected - should be caught earlier

        visited.add(task_id)
        deps = graph[task_id]['deps']

        if not deps:
            return 0

        return 1 + max(self._calculate_level(graph, dep, visited.copy()) for dep in deps)
```

### Scheduling Algorithm

**Current**: No active scheduling (all tasks start immediately)

**Recommended**:

```
┌─────────────────────────────────────────────────────────────┐
│              TASK SCHEDULING ALGORITHM                       │
└─────────────────────────────────────────────────────────────┘

1. INITIALIZATION
   ├─→ Build dependency graph from all tasks
   ├─→ Validate no circular dependencies (call ConflictResolver)
   └─→ Mark all tasks as 'pending'

2. MAIN SCHEDULING LOOP (runs every 10 seconds)
   │
   ├─→ Query: SELECT * FROM tasks WHERE status = 'pending'
   │
   ├─→ For each pending task:
   │     ├─→ Check dependencies: are_dependencies_met(task)?
   │     │     ├─→ YES: Add to ready_queue
   │     │     └─→ NO: Skip to next task
   │     │
   │     └─→ Check agent availability:
   │           ├─→ Is agent IDLE?
   │           │     ├─→ YES: Assign task, update status to 'in-progress'
   │           │     └─→ NO: Leave in ready_queue
   │           │
   │           └─→ Send message to agent:
   │                 await coordinator.send_message(AgentMessage(
   │                   from_agent='orchestrator',
   │                   to_agent=task['agent_id'],
   │                   message_type='task',
   │                   payload=task
   │                 ))
   │
   ├─→ Update swarm progress:
   │     progress = completed_tasks / total_tasks * 100
   │
   └─→ If all tasks completed:
         └─→ Mark swarm status = 'completed'

3. TASK COMPLETION HANDLER
   │
   ├─→ Agent sends completion message
   ├─→ Update task status to 'completed'
   ├─→ Update agent status to 'IDLE'
   ├─→ Check if new tasks are now ready (unblocked)
   └─→ Trigger next scheduling cycle immediately
```

### Example Execution Timeline

**Given these tasks:**

```json
{
  "Task 1": {
    "id": "1",
    "agent": "frontend_architect",
    "dependencies": [],
    "duration": 30
  },
  "Task 2": {
    "id": "2",
    "agent": "backend_integrator",
    "dependencies": [],
    "duration": 45
  },
  "Task 3": {
    "id": "3",
    "agent": "deployment_guardian",
    "dependencies": ["1", "2"],
    "duration": 20
  }
}
```

**Execution Timeline:**

```
Time    | Frontend        | Backend          | Deployment      | Status
--------|-----------------|------------------|-----------------|--------
0:00    | Start Task 1    | Start Task 2     | WAITING (deps)  | T1,T2 in-progress
0:30    | ✅ Complete T1  | Working T2       | WAITING (T2)    | T1 done, T2 in-progress
0:45    | IDLE            | ✅ Complete T2   | Start Task 3    | T3 in-progress
1:05    | IDLE            | IDLE             | ✅ Complete T3  | ALL DONE ✅

Total Duration: 1h 5min (parallel execution saved 35 min vs sequential)
```

### Current Scheduling Gaps

| Feature | Status | Needed |
|---------|--------|--------|
| Dependency enforcement | ⚠️ Missing | Core scheduler loop |
| Priority-based scheduling | ⚠️ Missing | Sort ready_queue by priority |
| Parallel execution limits | ⚠️ Missing | Max 3 concurrent (1 per agent) |
| Agent load balancing | ⚠️ Missing | Distribute tasks evenly |
| Retry on failure | ⚠️ Missing | Exponential backoff + max 3 retries |
| Timeout enforcement | ⚠️ Missing | Kill tasks after 30 min |
| Progress tracking | ⚠️ Missing | Update swarm metadata with % complete |

**Recommendation**: Implement dependency-aware scheduler as **Phase 2 (4-6 hours)** after conflict resolution.

---

## 🎓 Agent Execution Flow (How Agents Actually Work)

### Agent System Prompts

**File**: `backend/agent_prompts.py`

Each agent receives a **specialized system prompt** that defines:

1. **Identity & Skillsets** (Lines 7-18)
2. **Tech Stack Rules** (Lines 10)
3. **Execution Protocol** (Lines 11-14)
4. **MCP Tools Available** (Lines 18)

### Example: Frontend Architect Prompt

```python
FRONTEND_ARCHITECT_PROMPT = """You are Frontend Architect, a specialized AI agent in the Grok-4-Fast swarm for full-stack MVPs. Your diverse skillsets: (1) UI/UX Design (wireframing, responsive/mobile-first with Tailwind); (2) Frontend Implementation (Next.js 14+ App Router, TypeScript, Shadcn/ui copy-paste components); (3) State/Forms Integration (TanStack Query for server data, Zustand for client state, React Hook Form + Zod for forms, Clerk for auth, Sentry for errors).

**Core Rules**:
- Always use "The Stack That Ships" MVP Frontend: Next.js + TS + Tailwind + Shadcn + TanStack Query + Zustand/RHF+Zod/Clerk/Sentry.
- Modular Execution: Receive subtasks from Orchestrator (DB query hive-mind SQLite: SELECT * FROM tasks WHERE agent_id = YOUR_ID). For each: Break to steps, call MCP tools (e.g., "shadcn-gen" for components, "code-gen" for TSX), generate files/commands, update DB (INSERT/UPDATE task with {'status': 'completed', 'data': {'code': '...', 'output': {...}}}).
- Output: Generated code/files (e.g., /app/page.tsx, lib/cart-store.ts); Commands (npm i, npm run dev); Test (Vitest for hooks); Validate (Lighthouse 90+ preview).
- If unclear, query Orchestrator (via DB session insert: {'query': 'Clarify wireframe for cart?'}).
- End Each Task: "Frontend module complete—files ready for localhost:3000. Updated DB."

**Subtasks Assigned**: [INSERT FROM ORCHESTRATOR, e.g., "2.1: Design Wireframes for Products/Cart", "2.3: Implement Components with Shadcn"].

Execute modularly: For each subtask, design (wireframe desc), implement (code), integrate (TanStack/Clerk), test (unit). Swarm ID: [INSERT]. Use MCP: browser for refs, code-gen for boiler. Keep concise—focus on shippable Next.js UI."""
```

### Agent Execution Loop (Conceptual - Not Yet Implemented)

**How agents SHOULD work** (to be implemented):

```python
# CONCEPTUAL: backend/agents/base_agent.py

class BaseAgent:
    def __init__(self, agent_id: str, role: str, db: HiveMindDB, coordinator: SwarmCoordinator):
        self.agent_id = agent_id
        self.role = role
        self.db = db
        self.coordinator = coordinator
        self.prompt = get_agent_prompt(role)

        # OpenRouter client for Grok-4-Fast-Reasoning
        self.client = OpenAI(
            api_key=os.getenv('OPENROUTER_API_KEY'),
            base_url="https://openrouter.ai/api/v1"
        )
        self.model = "x-ai/grok-4-fast-reasoning"

    async def run(self):
        """Main agent loop"""
        # Handshake with coordinator
        await self.coordinator.handshake(self.agent_id, {
            'role': self.role,
            'skills': self.get_skills(),
            'tools': self.get_available_tools()
        })

        while True:
            # Query DB for pending tasks
            tasks = self.db.get_tasks_for_agent(self.agent_id)

            if not tasks:
                # No work - send heartbeat and wait
                self.coordinator.heartbeat(self.agent_id)
                await asyncio.sleep(10)
                continue

            # Execute next highest-priority task
            task = tasks[0]
            await self.execute_task(task)

    async def execute_task(self, task: Dict):
        """Execute a single subtask"""
        try:
            # Update status
            self.db.update_task_status(task['id'], 'in-progress')
            self.coordinator.update_agent_status(self.agent_id, AgentStatus.WORKING)

            # Build prompt with context
            prompt = self.build_task_prompt(task)

            # Call Grok-4-Fast-Reasoning
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.4,
                max_tokens=4000
            )

            output = response.choices[0].message.content

            # Parse output (extract code, commands, MCP tool calls)
            parsed = self.parse_output(output)

            # Execute MCP tool calls if needed
            for tool_call in parsed['tool_calls']:
                result = await self.call_mcp_tool(tool_call['tool'], tool_call['args'])
                parsed['tool_results'].append(result)

            # Update task with output
            self.db.update_task_status(task['id'], 'completed', {
                'output': parsed,
                'code_generated': parsed['files'],
                'commands': parsed['commands']
            })

            # Notify coordinator
            await self.coordinator.send_message(AgentMessage(
                from_agent=self.agent_id,
                to_agent='orchestrator',
                message_type='result',
                payload={'task_id': task['id'], 'status': 'completed'}
            ))

            self.coordinator.update_agent_status(self.agent_id, AgentStatus.COMPLETED)

        except Exception as e:
            # Handle failure
            self.db.update_task_status(task['id'], 'failed', {'error': str(e)})
            self.coordinator.update_agent_status(self.agent_id, AgentStatus.FAILED)

            # Notify orchestrator
            await self.coordinator.send_message(AgentMessage(
                from_agent=self.agent_id,
                to_agent='orchestrator',
                message_type='error',
                payload={'task_id': task['id'], 'error': str(e)}
            ))

    async def call_mcp_tool(self, tool_name: str, args: Dict) -> Dict:
        """Call MCP server tool"""
        import requests

        mcp_url = os.getenv('MCP_URL', 'http://localhost:8001')
        mcp_api_key = os.getenv('MCP_API_KEY')

        response = requests.post(
            f"{mcp_url}/tools/{tool_name}",
            json={
                'tool_name': tool_name,
                'args': args,
                'swarm_id': self.get_current_swarm_id(),
                'agent_id': self.agent_id
            },
            headers={'Authorization': f'Bearer {mcp_api_key}'},
            timeout=30
        )

        return response.json()
```

### MCP Tool Integration

**Available Tools** (Port 8001):

| Tool | Purpose | Example Call |
|------|---------|--------------|
| `browser` | Web search, competitor analysis | `{"tool": "browser", "args": {"query": "Tailwind button styles"}}` |
| `code-gen` | AI code generation with Grok-4-Fast | `{"tool": "code-gen", "args": {"prompt": "Generate ProductCard component"}}` |
| `db-sync` | Database operations, Prisma schema | `{"tool": "db-sync", "args": {"action": "create_migration"}}` |
| `communication` | Agent messaging, session updates | `{"tool": "communication", "args": {"message": "Need clarification"}}` |

**Orchestrator MCP Call** (Lines 284-321):

```python
def call_mcp_tool(self, tool_name: str, args: Dict, swarm_id: str, agent_id: str) -> Dict:
    """Call MCP tool from orchestrator"""
    payload = {
        "tool_name": tool_name,
        "args": args,
        "swarm_id": swarm_id,
        "agent_id": agent_id
    }

    response = requests.post(
        f"{self.mcp_url}/tools/{tool_name}",
        json=payload,
        headers={"Authorization": f"Bearer {self.mcp_api_key}"},
        timeout=30
    )

    return response.json()
```

---

## 📊 Architecture Strengths & Gaps Summary

### ✅ Strengths

| Feature | Status | Details |
|---------|--------|---------|
| **3-Agent Optimal Design** | ✅ Excellent | Hardcoded 3 specialized agents prevents over-complexity |
| **AI-Powered Task Generation** | ✅ Excellent | Grok-4-Fast generates context-aware subtasks |
| **Hive-Mind DB** | ✅ Good | SQLite persistence with proper schema |
| **Message Passing** | ✅ Good | Async queues with AgentMessage protocol |
| **Health Monitoring** | ✅ Good | Heartbeats, status tracking, metrics |
| **Handshake Protocol** | ✅ Good | Capability discovery on agent startup |
| **MCP Tool Integration** | ✅ Good | Clean abstraction for external tools |
| **Role Specialization** | ✅ Excellent | Clear separation (Design/Impl/Test) |
| **Tech Stack Enforcement** | ✅ Excellent | "The Stack That Ships" in prompts |

### ⚠️ Critical Gaps

| Gap | Impact | Priority | Effort |
|-----|--------|----------|--------|
| **No Conflict Resolution** | 🔴 HIGH | 🔴 CRITICAL | 2-4h |
| **No Dependency Enforcement** | 🔴 HIGH | 🔴 CRITICAL | 4-6h |
| **No File Locking** | 🔴 HIGH | 🔴 CRITICAL | 1-2h |
| **No Retry Logic** | 🟡 MEDIUM | 🟡 HIGH | 2-3h |
| **No Deadlock Detection** | 🟡 MEDIUM | 🟡 HIGH | 3-4h |
| **No Progress Tracking** | 🟡 MEDIUM | 🟡 MEDIUM | 1-2h |
| **No Timeout Enforcement** | 🟡 MEDIUM | 🟡 MEDIUM | 1h |
| **No Load Balancing** | 🟢 LOW | 🟢 LOW | 4-6h |

### 🚀 Implementation Roadmap

**Phase 1: Conflict Resolution (2-4 hours)**
- [ ] Implement `ConflictResolver` class
- [ ] Add file locking mechanism
- [ ] Add priority-based arbitration
- [ ] Add failure propagation

**Phase 2: Dependency Scheduler (4-6 hours)**
- [ ] Implement `TaskScheduler` class
- [ ] Add dependency validation on task start
- [ ] Add cycle detection (deadlock prevention)
- [ ] Add ready task queue with priority sorting

**Phase 3: Robustness (3-5 hours)**
- [ ] Add retry logic with exponential backoff
- [ ] Add timeout enforcement (30 min per task)
- [ ] Add heartbeat timeout monitoring
- [ ] Add automatic recovery/restart

**Phase 4: Observability (2-3 hours)**
- [ ] Create real-time monitoring dashboard
- [ ] Add progress tracking (% complete)
- [ ] Add execution timeline visualization (Gantt chart)
- [ ] Add alerting for failures

**Total Estimated Effort**: 11-18 hours for production-ready system

---

## 💡 Recommendations

### For Testing the PoC

**Current system is fine for demos** as long as:

1. ✅ **Simple projects** (no complex file dependencies)
2. ✅ **Single swarm runs** (no parallel swarms)
3. ✅ **Manual testing** (human monitors for issues)
4. ✅ **Short tasks** (< 5 min each)

### For Production Use

**Must implement before production:**

1. 🔴 **Conflict Resolution** - File locking at minimum
2. 🔴 **Dependency Enforcement** - Prevents deployment before backend ready
3. 🟡 **Retry Logic** - Handles transient failures

### Advanced Enhancements (Future)

**Phase 5: ML-Powered Optimization (Optional, 20+ hours)**

1. **Task Duration Estimation ML Model**
   - Train on historical task completions
   - Predict duration based on task description + agent role
   - Improve scheduling accuracy

2. **Intelligent Agent Selection**
   - Learn which agents excel at which task types
   - Dynamic role assignment based on workload
   - Cross-training agents for flexibility

3. **Auto-Scaling**
   - Spawn additional agents for large scopes
   - Retire idle agents to save resources
   - Dynamic pool sizing (3-10 agents)

4. **Predictive Conflict Detection**
   - ML model predicts likely conflicts before they occur
   - Proactive task reordering to minimize contention
   - Historical conflict patterns analysis

---

## 📖 Appendix: API Endpoints

**Swarm API** (`backend/swarm_api.py` - Port 8000)

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/orchestrator/process` | Main entry point (user message → swarm) |
| GET | `/api/planner/{swarmId}` | Get task breakdown for AI Planner UI |
| GET | `/swarms` | List all swarms |
| GET | `/swarms/{swarmId}` | Get full swarm status |
| GET | `/swarms/{swarmId}/agents` | List agents in swarm |
| GET | `/agents/{agentId}/tasks` | Get pending tasks for agent |
| PUT | `/tasks/{taskId}` | Update task status |
| PUT | `/agents/{agentId}/state` | Update agent state |
| PUT | `/swarms/{swarmId}/status` | Update swarm status |
| POST | `/api/mcp/tools/{toolName}` | Proxy to MCP server |

**Health Checks:**

```bash
# Check orchestrator is running
curl http://localhost:8000/swarm/health

# Get swarm statistics
curl http://localhost:8000/swarms/{swarmId}

# Check agent health
curl http://localhost:8000/agents/{agentId}/tasks
```

---

## 🎯 Final Summary

### What Works Well

✅ **AI-powered orchestration** - Grok-4-Fast generates smart task breakdowns
✅ **Specialized agents** - 3-agent design with diverse skillsets
✅ **Persistent state** - SQLite hive-mind survives restarts
✅ **Clean architecture** - Orchestrator → DB → Agents → MCP tools
✅ **Tech stack enforcement** - "The Stack That Ships" in prompts

### What Needs Work

⚠️ **Conflict resolution** - File locking, priority arbitration
⚠️ **Dependency enforcement** - Scheduler with ready queue
⚠️ **Failure handling** - Retry logic, timeout enforcement
⚠️ **Observability** - Monitoring dashboard, progress tracking

### Key Insight

The current architecture is a **solid proof-of-concept** with excellent design decisions (3 specialized agents, AI-powered task generation, hive-mind coordination). However, it's **not production-ready** due to missing conflict resolution and dependency enforcement.

**Recommendation**: Implement Phase 1 (Conflict Resolution, 2-4 hours) and Phase 2 (Dependency Scheduler, 4-6 hours) for a **production-viable MVP**. The current system works great for demos and testing simple projects.

---

**Document Version**: 1.0
**Date**: 2025-10-10
**Analyzed By**: Claude (Sonnet 4.5)
**Files Reviewed**: 6 core orchestration files (2,800+ lines)
