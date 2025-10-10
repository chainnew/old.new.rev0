import sqlite3
import json
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, validator  # For schema validation (like Zod)

# Pydantic schemas for validation (ensures type-safe scope ingestion; mirrors RHF+Zod stack)
class SwarmSchema(BaseModel):
    id: str
    name: str
    status: str  # 'idle', 'running', 'paused', 'completed', 'error'
    num_agents: int  # e.g., 3-5 for mini-swarms
    created_at: datetime
    metadata: Dict[str, Any] = {}  # e.g., {'project': 'TrackFlow', 'timeline': '1-2h'}

    @validator('status')
    def validate_status(cls, v):
        valid = ['idle', 'running', 'paused', 'completed', 'error']
        if v not in valid:
            raise ValueError(f'Status must be one of {valid}')
        return v

class AgentSchema(BaseModel):
    id: str
    swarm_id: str
    role: str  # New: 'frontend_architect', 'backend_integrator', 'deployment_guardian' | Legacy: 'research', 'design', 'implementation'
    state: Dict[str, Any] = {}  # e.g., {'status': 'executing', 'data': {'outputs': [...]}}
    assigned_at: datetime

    @validator('role')
    def validate_role(cls, v):
        # Updated roles: 3 specialized agents with diverse skillsets
        valid = [
            'frontend_architect',    # Design + Implementation (UI/UX)
            'backend_integrator',    # Implementation + Integration (APIs/DB)
            'deployment_guardian',   # Testing + Deployment (CI/CD)
            # Legacy support for old swarms
            'research', 'design', 'implementation', 'test', 'deploy', 'quality'
        ]
        if v not in valid:
            raise ValueError(f'Role must be one of {valid}')
        return v

class TaskSchema(BaseModel):
    id: str
    agent_id: str
    swarm_id: str
    description: str  # e.g., "Gen Shadcn dashboard wireframe"
    status: str  # 'pending', 'in-progress', 'completed', 'failed'
    priority: int = 5
    data: Dict[str, Any] = {}  # JSON: inputs/outputs (e.g., {'code': '...', 'errors': []})
    created_at: datetime
    updated_at: datetime

    @validator('status')
    def validate_status(cls, v):
        valid = ['pending', 'in-progress', 'completed', 'failed']
        if v not in valid:
            raise ValueError(f'Status must be one of {valid}')
        return v

class SessionSchema(BaseModel):
    id: str
    swarm_id: str
    data: Dict[str, Any] = {}  # JSON: full scope, progress, learned states
    timestamp: datetime

# Hive-Mind DB Class: Manages SQLite for Python swarm agents
class HiveMindDB:
    def __init__(self, db_path: str = ':memory:') -> None:
        """Init DB connection. Use ':memory:' for tests; file path for persistence."""
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)  # Allow threading for agents
        self.cursor = self.conn.cursor()
        self.conn.execute('PRAGMA journal_mode = WAL;')  # Concurrency for parallel agents
        self.conn.execute('PRAGMA synchronous = NORMAL;')  # Speed/safety balance
        self.conn.commit()

    def init_db(self) -> None:
        """Create tables (inspired by Swarms.ai/LangGraph checkpoints; Claude-Flow sessions)."""
        # Swarms table: Top-level orchestration
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS swarms (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'idle',
                num_agents INTEGER NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                metadata TEXT,  -- JSON stringified
                project_path TEXT  -- Autonomous workspace path: Projects/ProjectName_swarmId/
            )
        """)

        # Agents table: Individual agents in hive-mind (narrow roles for parallelism)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS agents (
                id TEXT PRIMARY KEY,
                swarm_id TEXT NOT NULL,
                role TEXT NOT NULL,
                state TEXT NOT NULL,  -- JSON: {'status': 'executing', 'data': {...}}
                assigned_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (swarm_id) REFERENCES swarms (id) ON DELETE CASCADE
            )
        """)

        # Tasks table: Granular work (agents execute in 1-2h bursts)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id TEXT PRIMARY KEY,
                agent_id TEXT NOT NULL,
                swarm_id TEXT NOT NULL,
                description TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                priority INTEGER DEFAULT 5,
                data TEXT NOT NULL,  -- JSON: inputs/outputs
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT (datetime('now')),
                FOREIGN KEY (agent_id) REFERENCES agents (id) ON DELETE CASCADE,
                FOREIGN KEY (swarm_id) REFERENCES swarms (id) ON DELETE CASCADE
            )
        """)

        # Sessions table: Persistent hive-mind memory (resume swarms across runs)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                swarm_id TEXT NOT NULL,
                data TEXT NOT NULL,  -- JSON: {'scope': {...}, 'progress': 75, 'learned': {...}}
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (swarm_id) REFERENCES swarms (id) ON DELETE CASCADE
            )
        """)

        # Indexes for query speed during agent execution
        self.cursor.executescript("""
            CREATE INDEX IF NOT EXISTS idx_swarm_status ON swarms(status);
            CREATE INDEX IF NOT EXISTS idx_agent_swarm ON agents(swarm_id);
            CREATE INDEX IF NOT EXISTS idx_task_status ON tasks(status);
            CREATE INDEX IF NOT EXISTS idx_session_swarm ON sessions(swarm_id);
        """)

        self.conn.commit()
        print(f"✅ Hive-Mind DB initialized at {self.db_path}")

    def start_swarm_from_scope(self, initial_scope: Dict[str, Any], num_agents: int = 5) -> str:
        """
        Ingest initial scope from PostgreSQL (e.g., via SQLAlchemy).
        Example PG fetch (uncomment/integrate):
        from sqlalchemy import create_engine, text
        engine = create_engine('postgresql://user:pass@host/db')
        with engine.connect() as conn:
            result = conn.execute(text("SELECT scope_json FROM scopes WHERE project = :project"),
                                  {'project': initial_scope.get('project', 'TrackFlow')})
            initial_scope = result.fetchone()[0] if result.fetchone() else initial_scope
        """
        # Validate scope (minimal schema; uses Pydantic)
        scope_model = SwarmSchema.model_validate({
            'name': initial_scope.get('project', 'DefaultSwarm'),
            'num_agents': num_agents,
            'metadata': initial_scope,
            'status': 'idle',
            'created_at': datetime.now(),
            'id': str(uuid.uuid4())
        })
        validated_scope = scope_model.model_dump()

        # Generate IDs
        swarm_id = validated_scope['id']
        session_id = str(uuid.uuid4())

        # Insert swarm
        self.cursor.execute("""
            INSERT INTO swarms (id, name, num_agents, metadata, status)
            VALUES (?, ?, ?, ?, ?)
        """, (
            swarm_id,
            validated_scope['name'],
            validated_scope['num_agents'],
            json.dumps(validated_scope['metadata']),
            validated_scope['status']
        ))

        # Create initial session for persistence (e.g., progress tracking)
        self.cursor.execute("""
            INSERT INTO sessions (id, swarm_id, data)
            VALUES (?, ?, ?)
        """, (
            session_id,
            swarm_id,
            json.dumps({'progress': 0, 'scope': validated_scope['metadata'], 'learned': {}})
        ))

        # Assign agents - ALWAYS use specialized 3-agent roles (Frontend Architect, Backend Integrator, Deployment Guardian)
        # This is the new standard for all swarms
        roles = ['frontend_architect', 'backend_integrator', 'deployment_guardian'][:num_agents]
        
        agent_ids = []
        for i, role in enumerate(roles):
            agent_id = f"agent-{role.replace('_', '-')}-{str(uuid.uuid4())[:8]}"
            agent_ids.append((agent_id, role))
            agent_state = {'status': 'idle', 'data': {'role_inputs': []}}
            self.cursor.execute("""
                INSERT INTO agents (id, swarm_id, role, state)
                VALUES (?, ?, ?, ?)
            """, (
                agent_id,
                swarm_id,
                role,
                json.dumps(agent_state)
            ))

        # Seed initial tasks from scope (auto-breakdown; customizable)
        tasks_from_scope = self._generate_tasks_from_scope(validated_scope, swarm_id, agent_ids)
        for task in tasks_from_scope:
            self.cursor.execute("""
                INSERT INTO tasks (id, swarm_id, agent_id, description, data, priority, status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                task['id'],
                swarm_id,
                task['agent_id'],
                task['description'],
                json.dumps(task['data']),
                task['priority'],
                task['status']
            ))

        self.conn.commit()
        print(f"🚀 Swarm '{swarm_id}' started from scope for {num_agents} agents.")
        return swarm_id

    def _generate_tasks_from_scope(self, scope: Dict[str, Any], swarm_id: str, agent_ids: List[tuple]) -> List[Dict[str, Any]]:
        """Auto-generate tasks based on scope (e.g., for TrackFlow: break into phases)."""
        project = scope['metadata'].get('project', 'Generic')
        tasks = []
        # Create agent_id lookup
        agent_map = {role: aid for aid, role in agent_ids}
        
        # Example breakdown (customize via scope features/goal)
        task_defs = [
            {'role': 'research', 'desc': f"Research comps for {project}", 'data': {'comps': ['Trello']}, 'priority': 10},
            {'role': 'design', 'desc': f"Design wireframes/DB schema for {project}", 'data': {'stack': scope['metadata'].get('tech_stack')}, 'priority': 9},
            {'role': 'implementation', 'desc': f"Impl core features (e.g., dashboard) for {project}", 'data': {'features': scope['metadata'].get('features', [])}, 'priority': 8},
            {'role': 'test', 'desc': f"Run E2E tests for {project}", 'data': {'coverage_target': 80}, 'priority': 7},
            {'role': 'deploy', 'desc': f"Deploy MVP for {project}", 'data': {'url': 'vercel.app'}, 'priority': 6}
        ]
        
        for td in task_defs[:len(agent_ids)]:  # Limit to num_agents
            agent_id = agent_map.get(td['role'], agent_ids[0][0])
            tasks.append({
                'id': str(uuid.uuid4()),
                'agent_id': agent_id,
                'description': td['desc'],
                'data': td['data'],
                'priority': td['priority'],
                'status': 'pending',
                'created_at': datetime.now(),
                'updated_at': datetime.now()
            })
        return tasks

    # Helper methods for agent interactions
    def update_agent_state(self, agent_id: str, new_state: Dict[str, Any]) -> None:
        """Agent calls this during execution (e.g., from LangChain tool)."""
        self.cursor.execute("""
            UPDATE agents SET state = ? WHERE id = ?
        """, (json.dumps(new_state), agent_id))
        self.conn.commit()

    def update_task_status(self, task_id: str, status: str, data: Optional[Dict[str, Any]] = None) -> None:
        """Update task status and optionally its data."""
        if data:
            self.cursor.execute("""
                UPDATE tasks SET status = ?, data = ?, updated_at = datetime('now') WHERE id = ?
            """, (status, json.dumps(data), task_id))
        else:
            self.cursor.execute("""
                UPDATE tasks SET status = ?, updated_at = datetime('now') WHERE id = ?
            """, (status, task_id))
        self.conn.commit()

    def get_tasks_for_agent(self, agent_id: str) -> List[Dict[str, Any]]:
        """Query pending tasks for an agent."""
        self.cursor.execute("""
            SELECT * FROM tasks WHERE agent_id = ? AND status = 'pending' ORDER BY priority DESC
        """, (agent_id,))
        rows = self.cursor.fetchall()
        tasks = []
        for row in rows:
            tasks.append({
                'id': row[0],
                'agent_id': row[1],
                'swarm_id': row[2],
                'description': row[3],
                'status': row[4],
                'priority': row[5],
                'data': json.loads(row[6]),
                'created_at': row[7],
                'updated_at': row[8]
            })
        return tasks

    def get_swarm_status(self, swarm_id: str) -> Dict[str, Any]:
        """Get full swarm status including all agents and tasks."""
        # Get swarm info
        self.cursor.execute("SELECT * FROM swarms WHERE id = ?", (swarm_id,))
        swarm_row = self.cursor.fetchone()
        if not swarm_row:
            return {'error': 'Swarm not found'}
        
        # Get agents
        self.cursor.execute("SELECT * FROM agents WHERE swarm_id = ?", (swarm_id,))
        agents = [{'id': row[0], 'role': row[2], 'state': json.loads(row[3])} for row in self.cursor.fetchall()]
        
        # Get tasks
        self.cursor.execute("SELECT * FROM tasks WHERE swarm_id = ?", (swarm_id,))
        tasks = [{'id': row[0], 'description': row[3], 'status': row[4], 'priority': row[5]} for row in self.cursor.fetchall()]
        
        return {
            'swarm_id': swarm_id,
            'name': swarm_row[1],
            'status': swarm_row[2],
            'agents': agents,
            'tasks': tasks,
            'metadata': json.loads(swarm_row[5]) if swarm_row[5] else {}
        }

    def update_swarm_status(self, swarm_id: str, status: str) -> None:
        """Update swarm status."""
        self.cursor.execute("""
            UPDATE swarms SET status = ? WHERE id = ?
        """, (status, swarm_id))
        self.conn.commit()

    def close(self) -> None:
        """Cleanup connection."""
        self.conn.close()

# Example Usage Script (run with `python hive_mind_db.py`)
if __name__ == "__main__":
    # Sample initial scope (in prod: fetch from PG as noted in start_swarm_from_scope)
    initial_scope = {
        'project': 'TrackFlow',
        'goal': 'SaaS dashboard for task tracking',
        'tech_stack': {'frontend': 'Next.js + Tailwind', 'backend': 'Node + Prisma'},
        'features': ['dashboard', 'auth', 'tasks']
    }

    import os
    os.makedirs('swarms', exist_ok=True)
    
    db = HiveMindDB(db_path='swarms/trackflow_swarm.db')
    db.init_db()
    swarm_id = db.start_swarm_from_scope(initial_scope, num_agents=5)

    # Simulate agent query (e.g., from your Python swarm code)
    print(f"\n📋 Swarm Status:")
    status = db.get_swarm_status(swarm_id)
    print(json.dumps(status, indent=2))

    db.close()
