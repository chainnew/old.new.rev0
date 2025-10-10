"""
FastAPI endpoint for Hive-Mind Swarm integration.
Connects the SQLite swarm database with the TypeScript frontend.
"""
from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
import uvicorn
import json
from hive_mind_db import HiveMindDB
from orchestrator_agent import OrchestratorAgent
from security.auth_middleware import verify_api_key, APIKeyAuth
import os
from dotenv import load_dotenv

# Load environment and API keys
load_dotenv()
load_dotenv(dotenv_path="backend/.env.keys")

app = FastAPI(
    title="Hive-Mind Swarm API",
    version="1.0.0",
    description="Secured AI Swarm Orchestration API"
)

# Global Orchestrator instance
orchestrator = OrchestratorAgent()

# CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global DB instance - use same DB as orchestrator
DB_PATH = os.getenv('SWARM_DB_PATH', 'swarms/active_swarm.db')
os.makedirs('swarms', exist_ok=True)
db = HiveMindDB(db_path=DB_PATH)
db.init_db()

# Request/Response models
class SwarmCreate(BaseModel):
    project: str
    goal: str
    tech_stack: Dict[str, Any]
    features: List[str]
    num_agents: int = 5

class TaskUpdate(BaseModel):
    status: str
    data: Optional[Dict[str, Any]] = None

class AgentStateUpdate(BaseModel):
    state: Dict[str, Any]

class UserMessage(BaseModel):
    message: str
    user_id: str = "default"

@app.get("/")
def root():
    return {
        "message": "Hive-Mind Swarm API",
        "version": "1.0.0",
        "endpoints": {
            "POST /swarms": "Create new swarm from scope",
            "GET /swarms/{swarm_id}": "Get swarm status",
            "GET /swarms/{swarm_id}/agents": "List all agents",
            "GET /agents/{agent_id}/tasks": "Get tasks for agent",
            "PUT /tasks/{task_id}": "Update task status",
            "PUT /agents/{agent_id}/state": "Update agent state",
            "PUT /swarms/{swarm_id}/status": "Update swarm status"
        }
    }

@app.post("/swarms", dependencies=[Depends(verify_api_key)])
async def create_swarm(request: Request, scope: SwarmCreate):
    """
    Create a new swarm from initial scope.
    🔐 Requires: SWARM_CREATE_KEY, ADMIN_MASTER_KEY, or API_MASTER_KEY
    """
    try:
        initial_scope = {
            'project': scope.project,
            'goal': scope.goal,
            'tech_stack': scope.tech_stack,
            'features': scope.features
        }
        swarm_id = db.start_swarm_from_scope(initial_scope, num_agents=scope.num_agents)
        status = db.get_swarm_status(swarm_id)
        return {
            "success": True,
            "swarm_id": swarm_id,
            "status": status
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/swarms")
def list_swarms():
    """List all swarms in the database."""
    try:
        # Create new connection to avoid threading issues
        import sqlite3
        conn = sqlite3.connect('swarms/active_swarm.db', check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, name, status, num_agents, created_at, metadata 
            FROM swarms 
            ORDER BY created_at DESC
            LIMIT 50
        """)
        rows = cursor.fetchall()
        conn.close()
        
        swarms = []
        for row in rows:
            try:
                # Safely parse metadata
                metadata = {}
                if row[5]:
                    try:
                        metadata = json.loads(row[5])
                    except:
                        metadata = {}
                
                swarm_data = {
                    'swarm_id': row[0],
                    'name': row[1],
                    'status': row[2],
                    'num_agents': row[3],
                    'created_at': row[4],
                    'metadata': metadata
                }
                swarms.append(swarm_data)
            except Exception as e:
                # Skip broken swarms
                print(f"⚠️ Skipping swarm {row[0]}: {e}")
                continue
        
        return {"swarms": swarms, "count": len(swarms)}
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"swarms": [], "count": 0, "error": str(e)}

@app.get("/swarms/{swarm_id}")
def get_swarm(swarm_id: str):
    """Get full swarm status including agents and tasks."""
    try:
        status = db.get_swarm_status(swarm_id)
        if 'error' in status:
            raise HTTPException(status_code=404, detail=status['error'])
        return status
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/swarms/{swarm_id}/agents")
def get_swarm_agents(swarm_id: str):
    """List all agents in a swarm."""
    try:
        status = db.get_swarm_status(swarm_id)
        if 'error' in status:
            raise HTTPException(status_code=404, detail=status['error'])
        return {
            "swarm_id": swarm_id,
            "agents": status['agents']
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/agents/{agent_id}/tasks")
def get_agent_tasks(agent_id: str):
    """Get all pending tasks for an agent."""
    try:
        tasks = db.get_tasks_for_agent(agent_id)
        return {
            "agent_id": agent_id,
            "tasks": tasks
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/tasks/{task_id}")
def update_task(task_id: str, update: TaskUpdate):
    """Update task status and optionally its data."""
    try:
        db.update_task_status(task_id, update.status, update.data)
        return {
            "success": True,
            "task_id": task_id,
            "status": update.status
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/agents/{agent_id}/state")
def update_agent(agent_id: str, update: AgentStateUpdate):
    """Update agent state."""
    try:
        db.update_agent_state(agent_id, update.state)
        return {
            "success": True,
            "agent_id": agent_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/swarms/{swarm_id}/status")
def update_swarm(swarm_id: str, status: str):
    """Update swarm status."""
    try:
        db.update_swarm_status(swarm_id, status)
        return {
            "success": True,
            "swarm_id": swarm_id,
            "status": status
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# Orchestrator & Planner Endpoints
# ============================================================================

@app.post("/orchestrator/process")
def process_user_message(msg: UserMessage):
    """
    Main Orchestrator endpoint: User message → Scope → Swarm → Planner
    """
    try:
        result = orchestrator.handle_user_input(msg.message, msg.user_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/planner/{swarm_id}")
def get_planner_tasks(swarm_id: str):
    """
    Get formatted planner data for agent-planner.tsx component.
    Returns hierarchical tasks/subtasks matching the UI structure.
    """
    try:
        tasks = orchestrator.get_planner_data(swarm_id)
        return {
            "swarm_id": swarm_id,
            "tasks": tasks
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        # Return empty tasks instead of crashing
        return {
            "swarm_id": swarm_id,
            "tasks": [],
            "error": str(e)
        }

@app.get("/api/planner/{swarm_id}/progress")
def get_swarm_progress(swarm_id: str):
    """
    Get swarm progress, scheduling stats, and conflict resolution stats.
    Includes: % complete, ready tasks, active locks, failed tasks, escalations, memory.
    """
    try:
        progress = orchestrator.get_swarm_progress(swarm_id)

        # Add escalation summary
        escalations = orchestrator.escalation_manager.get_escalation_summary(swarm_id)
        progress['escalations'] = escalations

        # Add context memory summary
        memory_summary = orchestrator.context_memory.get_memory_summary(swarm_id)
        progress['memory'] = memory_summary

        return {
            "swarm_id": swarm_id,
            **progress
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {
            "swarm_id": swarm_id,
            "progress": 0,
            "error": str(e)
        }

@app.get("/api/planner/{swarm_id}/escalations")
def get_swarm_escalations(swarm_id: str):
    """
    Get all escalations for a swarm (blockers needing user attention)
    """
    try:
        escalations = orchestrator.escalation_manager.get_escalations_for_swarm(swarm_id)
        return {
            "swarm_id": swarm_id,
            "escalations": escalations,
            "count": len(escalations)
        }
    except Exception as e:
        return {
            "swarm_id": swarm_id,
            "escalations": [],
            "error": str(e)
        }

@app.post("/api/planner/{swarm_id}/escalations/{escalation_id}/resolve")
def resolve_escalation(swarm_id: str, escalation_id: str, resolution: Dict[str, Any]):
    """
    Resolve an escalation (user provided answer/decision)
    """
    try:
        result = orchestrator.escalation_manager.resolve_escalation(escalation_id, resolution)
        return result
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

# ============================================================================
# MCP Tool Proxy Endpoints (Frontend → MCP Server)
# ============================================================================

@app.post("/api/mcp/tools/{tool_name}")
async def mcp_tool_proxy(tool_name: str, payload: Dict[str, Any]):
    """
    Proxy endpoint for frontend to call MCP tools.
    Forwards requests to MCP server with authentication.
    """
    import requests
    import os
    
    mcp_url = os.getenv('MCP_URL', 'http://localhost:8001')
    mcp_api_key = os.getenv('MCP_API_KEY', 'mcp-secret-key')
    
    try:
        response = requests.post(
            f"{mcp_url}/tools/{tool_name}",
            json=payload,
            headers={
                "Authorization": f"Bearer {mcp_api_key}",
                "Content-Type": "application/json"
            },
            timeout=30
        )
        
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"MCP proxy error: {e}")

@app.get("/api/mcp/tools/schemas")
async def mcp_schemas_proxy():
    """Get MCP tool schemas for frontend."""
    import requests
    import os

    mcp_url = os.getenv('MCP_URL', 'http://localhost:8001')

    try:
        response = requests.get(f"{mcp_url}/tools/schemas", timeout=10)
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"MCP schema fetch error: {e}")

@app.get("/api/projects/{swarm_id}/files")
async def list_project_files(swarm_id: str):
    """List all files in a project directory for the code editor."""
    import os
    from pathlib import Path

    # Get swarm details to find project_path
    cursor = db.cursor
    cursor.execute("SELECT project_path, name FROM swarms WHERE id = ?", (swarm_id,))
    row = cursor.fetchone()

    if not row:
        raise HTTPException(status_code=404, detail="Swarm not found")

    project_path = row[0]
    if not project_path or not os.path.exists(project_path):
        return {"files": [], "project_path": None}

    def scan_directory(path: Path, base_path: Path) -> list:
        """Recursively scan directory and build file tree."""
        items = []
        try:
            for item in sorted(path.iterdir()):
                # Skip hidden files and node_modules
                if item.name.startswith('.') or item.name == 'node_modules':
                    continue

                relative_path = str(item.relative_to(base_path))

                if item.is_dir():
                    children = scan_directory(item, base_path)
                    items.append({
                        'id': relative_path,
                        'name': item.name,
                        'type': 'folder',
                        'path': relative_path,
                        'children': children
                    })
                else:
                    # Detect language from extension
                    ext = item.suffix.lower()
                    lang_map = {
                        '.tsx': 'typescript', '.ts': 'typescript',
                        '.jsx': 'javascript', '.js': 'javascript',
                        '.py': 'python', '.css': 'css',
                        '.json': 'json', '.md': 'markdown'
                    }

                    items.append({
                        'id': relative_path,
                        'name': item.name,
                        'type': 'file',
                        'path': relative_path,
                        'language': lang_map.get(ext, 'plaintext')
                    })
        except PermissionError:
            pass

        return items

    base = Path(project_path)
    file_tree = scan_directory(base, base)

    return {
        "swarm_id": swarm_id,
        "project_path": project_path,
        "files": file_tree
    }

@app.get("/api/projects/{swarm_id}/files/{file_path:path}")
async def get_file_content(swarm_id: str, file_path: str):
    """Get content of a specific file."""
    import os
    from pathlib import Path

    # Get project path
    cursor = db.cursor
    cursor.execute("SELECT project_path FROM swarms WHERE id = ?", (swarm_id,))
    row = cursor.fetchone()

    if not row:
        raise HTTPException(status_code=404, detail="Swarm not found")

    project_path = row[0]
    if not project_path:
        raise HTTPException(status_code=404, detail="Project path not set")

    # Construct full file path and validate it's inside project
    full_path = Path(project_path) / file_path

    # Security: Ensure path is within project directory
    try:
        full_path = full_path.resolve()
        if not str(full_path).startswith(str(Path(project_path).resolve())):
            raise HTTPException(status_code=403, detail="Access denied")
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid file path")

    if not full_path.exists() or not full_path.is_file():
        raise HTTPException(status_code=404, detail="File not found")

    try:
        content = full_path.read_text()
        return {
            "file_path": file_path,
            "content": content,
            "size": full_path.stat().st_size
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading file: {e}")

if __name__ == "__main__":
    print("🚀 Starting Hive-Mind Swarm API...")
    print(f"📁 Database: {DB_PATH}")
    print("🌐 API Docs: http://localhost:8000/docs")
    print("🔧 MCP Proxy: /api/mcp/tools/*")
    uvicorn.run(app, host="0.0.0.0", port=8000)
