# 🐝 Hive-Mind Swarm Agent Database

Complete Python implementation for orchestrating AI agent swarms with SQLite persistence. Designed for 1-2 hour turn-key builds with 3-5 specialized agents.

## 🎯 Features

- **Lightweight & Fast**: SQLite with WAL mode for concurrent agent access
- **Pydantic Validation**: Type-safe scope ingestion (like Zod in TypeScript)
- **Multi-Agent Orchestration**: Research, Design, Implementation, Test, Deploy agents
- **Task Queue System**: Priority-based task assignment and execution
- **Session Persistence**: Resume swarms across runs
- **RESTful API**: FastAPI endpoints for frontend integration
- **Framework Agnostic**: Works with Swarms.ai, LangChain, CrewAI, OpenAI Swarm

## 📦 Installation

```bash
# Navigate to backend directory
cd backend

# Install dependencies
pip install pydantic fastapi uvicorn sqlite3

# Optional: For PostgreSQL integration
pip install sqlalchemy psycopg2-binary
```

## 🚀 Quick Start

### 1. Initialize Database

```python
from hive_mind_db import HiveMindDB

# Create database
db = HiveMindDB(db_path='swarms/my_project.db')
db.init_db()
```

### 2. Create a Swarm

```python
# Define initial scope
scope = {
    'project': 'TrackFlow',
    'goal': 'Build SaaS task tracking dashboard',
    'tech_stack': {
        'frontend': 'Next.js + Tailwind + Shadcn',
        'backend': 'FastAPI + Prisma',
        'database': 'PostgreSQL'
    },
    'features': ['dashboard', 'auth', 'task-board', 'analytics']
}

# Start swarm with 5 agents
swarm_id = db.start_swarm_from_scope(scope, num_agents=5)
print(f"✅ Swarm created: {swarm_id}")
```

### 3. Query Swarm Status

```python
# Get full swarm status
status = db.get_swarm_status(swarm_id)
print(f"Swarm: {status['name']}")
print(f"Agents: {len(status['agents'])}")
print(f"Tasks: {len(status['tasks'])}")
```

### 4. Agent Execution Loop

```python
# Get tasks for a specific agent
agent_id = "agent-implementation-abc123"
tasks = db.get_tasks_for_agent(agent_id)

for task in tasks:
    print(f"Executing: {task['description']}")
    
    # Agent does work here...
    # (e.g., LangChain tool calls, code generation, API requests)
    
    # Update task status
    db.update_task_status(
        task['id'], 
        'completed', 
        {'output': 'Generated dashboard component'}
    )
```

## 🌐 FastAPI Server

### Start the API

```bash
python swarm_api.py
```

Server runs on http://localhost:8000

API Docs: http://localhost:8000/docs

### Available Endpoints

#### Create Swarm
```bash
curl -X POST http://localhost:8000/swarms \
  -H "Content-Type: application/json" \
  -d '{
    "project": "TrackFlow",
    "goal": "Build task tracker",
    "tech_stack": {"frontend": "Next.js"},
    "features": ["dashboard"],
    "num_agents": 5
  }'
```

#### Get Swarm Status
```bash
curl http://localhost:8000/swarms/{swarm_id}
```

#### Get Agent Tasks
```bash
curl http://localhost:8000/agents/{agent_id}/tasks
```

#### Update Task
```bash
curl -X PUT http://localhost:8000/tasks/{task_id} \
  -H "Content-Type: application/json" \
  -d '{"status": "completed", "data": {"output": "Done"}}'
```

## 🏗️ Architecture

### Database Schema

```
swarms/
├── id (PK)
├── name
├── status (idle|running|paused|completed|error)
├── num_agents
├── created_at
└── metadata (JSON)

agents/
├── id (PK)
├── swarm_id (FK)
├── role (research|design|implementation|test|deploy)
├── state (JSON)
└── assigned_at

tasks/
├── id (PK)
├── agent_id (FK)
├── swarm_id (FK)
├── description
├── status (pending|in-progress|completed|failed)
├── priority
├── data (JSON)
├── created_at
└── updated_at

sessions/
├── id (PK)
├── swarm_id (FK)
├── data (JSON: scope, progress, learned states)
└── timestamp
```

### Agent Roles

1. **Research Agent**: Analyzes requirements, researches competitors
2. **Design Agent**: Creates wireframes, DB schemas, architecture
3. **Implementation Agent**: Generates code, builds features
4. **Test Agent**: Runs tests, validates functionality
5. **Deploy Agent**: Handles deployment, monitoring setup

## 🔌 Integration Examples

### With LangChain

```python
from langchain.agents import AgentExecutor
from langchain.tools import Tool
from hive_mind_db import HiveMindDB

db = HiveMindDB('swarms/project.db')

def get_next_task(agent_id: str) -> str:
    """LangChain tool to fetch next task."""
    tasks = db.get_tasks_for_agent(agent_id)
    return tasks[0]['description'] if tasks else "No tasks"

task_tool = Tool(
    name="GetNextTask",
    func=get_next_task,
    description="Fetch the next pending task for this agent"
)

# Add to your LangChain agent...
```

### With OpenAI Swarm

```python
from swarm import Swarm, Agent
from hive_mind_db import HiveMindDB

db = HiveMindDB('swarms/project.db')
swarm_id = db.start_swarm_from_scope(scope, num_agents=3)

# Create OpenAI agents
research_agent = Agent(
    name="Research",
    instructions="Research competitors and requirements"
)

design_agent = Agent(
    name="Design", 
    instructions="Create wireframes and architecture"
)

# Execute swarm...
client = Swarm()
```

### With CrewAI

```python
from crewai import Agent, Task, Crew
from hive_mind_db import HiveMindDB

db = HiveMindDB('swarms/project.db')
swarm_id = db.start_swarm_from_scope(scope, num_agents=4)

# Define agents
researcher = Agent(
    role='Research Specialist',
    goal='Gather requirements and analyze competitors',
    backstory='Expert at market research'
)

# Fetch tasks from DB and execute...
tasks = db.get_tasks_for_agent('agent-research-xyz')
crew = Crew(agents=[researcher], tasks=tasks)
```

## 🔄 Workflow Example

```python
# 1. Initialize
db = HiveMindDB('swarms/trackflow.db')
db.init_db()

# 2. Create swarm from scope
scope = {
    'project': 'TrackFlow',
    'goal': 'Build MVP in 2 hours',
    'tech_stack': {'frontend': 'Next.js'},
    'features': ['dashboard', 'auth']
}
swarm_id = db.start_swarm_from_scope(scope, num_agents=5)

# 3. Update swarm to running
db.update_swarm_status(swarm_id, 'running')

# 4. Agents execute tasks
for agent in ['research', 'design', 'implementation']:
    agent_id = f"agent-{agent}-xxx"
    tasks = db.get_tasks_for_agent(agent_id)
    
    for task in tasks:
        # Agent executes...
        db.update_task_status(task['id'], 'in-progress')
        # ... work happens ...
        db.update_task_status(task['id'], 'completed', {'output': '...'})

# 5. Complete swarm
db.update_swarm_status(swarm_id, 'completed')

# 6. Review results
final_status = db.get_swarm_status(swarm_id)
print(f"✅ Swarm complete! {len(final_status['tasks'])} tasks done")
```

## 📊 Frontend Integration (TypeScript)

### Fetch Swarm Status

```typescript
// In your Next.js component
async function getSwarmStatus(swarmId: string) {
  const res = await fetch(`http://localhost:8000/swarms/${swarmId}`);
  const data = await res.json();
  
  return {
    swarmId: data.swarm_id,
    name: data.name,
    status: data.status,
    agents: data.agents,
    tasks: data.tasks
  };
}
```

### Create New Swarm

```typescript
async function createSwarm(scope: SwarmScope) {
  const res = await fetch('http://localhost:8000/swarms', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      project: scope.project,
      goal: scope.goal,
      tech_stack: scope.techStack,
      features: scope.features,
      num_agents: 5
    })
  });
  
  const data = await res.json();
  return data.swarm_id;
}
```

### Update Agent Plan Component

```typescript
// In agent-plan.tsx
useEffect(() => {
  const interval = setInterval(async () => {
    const status = await getSwarmStatus(currentSwarmId);
    setTasks(status.tasks.map(task => ({
      id: task.id,
      title: task.description,
      status: task.status,
      priority: task.priority
    })));
  }, 2000); // Poll every 2s
  
  return () => clearInterval(interval);
}, [currentSwarmId]);
```

## 🧪 Testing

```bash
# Run the example
python hive_mind_db.py

# Expected output:
# ✅ Hive-Mind DB initialized at swarms/trackflow_swarm.db
# 🚀 Swarm 'abc-123-xyz' started from scope for 5 agents.
# 📋 Swarm Status: {...}
```

## 🔒 Security

- **Local SQLite**: No external network access required
- **Encryption**: Add `pysqlcipher3` for encrypted databases
- **API Auth**: Add JWT/API keys to FastAPI endpoints
- **Input Validation**: Pydantic schemas validate all inputs

## 📈 Scaling

### For Production

1. **PostgreSQL Sync**: Export swarm data to PG for long-term storage
2. **Redis Queue**: Add task queue for distributed agents
3. **Async**: Use `aiosqlite` for async operations
4. **Monitoring**: Add logging, metrics (Prometheus/Grafana)

### Performance Tips

- One DB file per swarm/project (isolation)
- WAL mode enabled (concurrent reads)
- Index on status fields (fast queries)
- Clean up completed swarms periodically

## 🛠️ Customization

### Add Custom Agent Roles

```python
# Modify validator in AgentSchema
@validator('role')
def validate_role(cls, v):
    valid = ['research', 'design', 'implementation', 'test', 'deploy', 'quality', 'security', 'docs']
    if v not in valid:
        raise ValueError(f'Role must be one of {valid}')
    return v
```

### Custom Task Generation

```python
def _generate_tasks_from_scope(self, scope, swarm_id, agent_ids):
    # Your custom logic based on scope.features, scope.goal, etc.
    tasks = []
    if 'auth' in scope['metadata'].get('features', []):
        tasks.append({
            'description': 'Implement OAuth2 authentication',
            'agent_id': agent_map['implementation'],
            'priority': 10
        })
    return tasks
```

## 📚 References

- **Swarms.ai**: https://github.com/kyegomez/swarms
- **LangGraph**: https://github.com/langchain-ai/langgraph
- **CrewAI**: https://github.com/joaomdmoura/crewai
- **OpenAI Swarm**: https://github.com/openai/swarm

## 🤝 Contributing

This is a production-ready starting point. Extend with:
- Vector stores for neural memory
- Tool integrations (GitHub, Slack, etc.)
- Advanced scheduling algorithms
- Multi-swarm orchestration

## 📄 License

MIT - Use freely in your projects!

---

**Ready to build with AI swarms? Start your hive! 🐝**
