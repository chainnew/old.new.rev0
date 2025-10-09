"""
HECTIC SWARM - FastAPI Backend
Main orchestrator for AI agent swarm
"""
import asyncio
import os
from typing import Dict, Any
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables from backend/.env or parent .env.local
backend_env = Path(__file__).parent / '.env'
parent_env = Path(__file__).parent.parent / '.env.local'

if backend_env.exists():
    load_dotenv(backend_env)
    print(f"📄 Loaded env from: {backend_env}")
elif parent_env.exists():
    load_dotenv(parent_env)
    print(f"📄 Loaded env from: {parent_env}")
else:
    load_dotenv()  # Try default locations

from agents.primary_agent import PrimaryAgent
from agents.code_agent import CodeAgent
from agents.eterna_port_agent import EternaPortAgent
from agents.swarm_coordinator import get_coordinator

# Import routers
from routes.eterna_port import router as eterna_router

# Initialize FastAPI
app = FastAPI(
    title="HECTIC SWARM API",
    description="Multi-agent system for hypervisor porting",
    version="0.1.0"
)

# CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(eterna_router)

# Initialize agents
primary_agent = PrimaryAgent()
code_agent = CodeAgent()
eterna_port_agent = EternaPortAgent()

# Initialize swarm coordinator
coordinator = get_coordinator()

# Agent registry
AGENTS = {
    'code': code_agent,
    'port': eterna_port_agent,
    'eterna_port': eterna_port_agent,
    # Add more agents here as you build them:
    # 'debug': DebugAgent(),
    # 'research': ResearchAgent(),
}

# Register agents with coordinator
coordinator.register_agent('primary')
coordinator.register_agent('code')
coordinator.register_agent('eterna_port')


class SwarmRequest(BaseModel):
    """Request model for swarm orchestration"""
    userMessage: str
    conversationId: str


class SwarmResponse(BaseModel):
    """Response model"""
    response: str
    tasks: list[Dict[str, Any]]
    swarm_stats: Dict[str, Any] = {}


@app.get("/")
async def root():
    """Health check with full system status"""
    # Check OpenRouter connectivity
    try:
        test_keys = sum(1 for key in [
            os.getenv('OPENROUTER_API_KEY1'),
            os.getenv('OPENROUTER_API_KEY2'),
            os.getenv('OPENROUTER_API_KEY3')
        ] if key)
    except:
        test_keys = 0
    
    # Check database
    db_status = "connected" if os.getenv('DATABASE_URL') else "not configured"
    
    # Get swarm stats
    swarm_stats = coordinator.get_swarm_stats()
    
    return {
        "status": "🚀 HECTIC SWARM v1.0 - Grok 4 Fast Powered",
        "model": "x-ai/grok-4-fast",
        "agents": list(AGENTS.keys()),
        "api_keys_loaded": test_keys,
        "database": db_status,
        "swarm_coordinator": swarm_stats,
        "version": "1.0.0",
        "endpoints": {
            "orchestrate": "POST /swarm/orchestrate",
            "single_agent": "POST /agent/{type}/execute",
            "swarm_health": "GET /swarm/health",
            "eterna_port": "POST /eterna/port",
            "eterna_bulk": "POST /eterna/port/bulk",
            "eterna_analyze": "GET /eterna/analyze/{file_path}",
            "docs": "GET /docs"
        }
    }


@app.post("/swarm/orchestrate", response_model=SwarmResponse)
async def orchestrate(request: SwarmRequest):
    """
    Main swarm orchestration endpoint
    
    Flow:
    1. Primary agent decomposes request
    2. Specialist agents execute in parallel
    3. Primary integrates results
    """
    import time
    start_time = time.time()
    
    try:
        # Step 1: Decompose
        print(f"📥 Request: {request.userMessage[:100]}...")
        tasks = await primary_agent.decompose(
            request.userMessage,
            request.conversationId
        )
        
        if not tasks:
            return SwarmResponse(
                response="No tasks generated. Try being more specific.",
                tasks=[]
            )
        
        # Step 2: Execute in parallel with swarm coordination
        print(f"🔄 Executing {len(tasks)} tasks in parallel...")
        agent_coroutines = []
        
        for task in tasks:
            # Use coordinator to route tasks
            agent_coroutines.append(
                coordinator.execute_swarm_task(task, AGENTS)
            )
        
        # Run all agents concurrently
        results = await asyncio.gather(*agent_coroutines, return_exceptions=True)
        
        # Handle exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append({
                    'task_id': tasks[i]['id'],
                    'status': 'failed',
                    'output': {'error': str(result)}
                })
            else:
                processed_results.append(result)
        
        # Step 3: Integrate
        print("🔗 Integrating results...")
        integrated_response = await primary_agent.integrate(
            processed_results,
            request.conversationId
        )
        
        # Calculate stats
        end_time = time.time()
        completion_time_ms = int((end_time - start_time) * 1000)
        failures = sum(1 for r in processed_results if r.get('status') == 'failed')
        
        return SwarmResponse(
            response=integrated_response,
            tasks=processed_results,
            swarm_stats={
                "completion_time_ms": completion_time_ms,
                "total_tasks": len(processed_results),
                "failures": failures,
                "model": "x-ai/grok-4-fast"
            }
        )
        
    except Exception as e:
        print(f"❌ Orchestration error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/agent/{agent_type}/execute")
async def execute_single_agent(agent_type: str, task: Dict[str, Any]):
    """
    Execute a single agent directly (for testing)
    
    Example:
    POST /agent/code/execute
    {
        "id": "test-1",
        "conversation_id": "uuid",
        "description": "Port x86 code",
        "code_snippet": "void foo() { ... }"
    }
    """
    if agent_type not in AGENTS:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_type}' not found")
    
    agent = AGENTS[agent_type]
    result = await agent.execute(task)
    return result


@app.get("/swarm/health")
async def swarm_health():
    """
    Get swarm coordinator health and statistics
    
    Returns:
        Agent health, task stats, and ping results
    """
    stats = coordinator.get_swarm_stats()
    ping_results = await coordinator.ping_all_agents()
    
    return {
        "status": "healthy",
        "coordinator": stats,
        "ping_results": ping_results,
        "timestamp": "now"
    }


# ============================================================================
# Orchestrator & Planner Endpoints
# ============================================================================

from orchestrator_agent import OrchestratorAgent
import json

# Initialize orchestrator
try:
    orchestrator = OrchestratorAgent()
except Exception as e:
    print(f"⚠️ Orchestrator not available: {e}")
    orchestrator = None

class UserMessage(BaseModel):
    message: str
    user_id: str = "default"

@app.post("/orchestrator/process")
async def process_user_message(msg: UserMessage):
    """Orchestrator endpoint for swarm creation"""
    if not orchestrator:
        raise HTTPException(500, "Orchestrator not initialized")
    try:
        result = orchestrator.handle_user_input(msg.message, msg.user_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/swarms")
async def list_swarms():
    """List all swarms"""
    if not orchestrator:
        return {"swarms": [], "count": 0}
    try:
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
                metadata = {}
                if row[5]:
                    try:
                        metadata = json.loads(row[5])
                    except:
                        metadata = {}
                
                swarms.append({
                    'swarm_id': row[0],
                    'name': row[1],
                    'status': row[2],
                    'num_agents': row[3],
                    'created_at': row[4],
                    'metadata': metadata
                })
            except:
                continue
        
        return {"swarms": swarms, "count": len(swarms)}
    except Exception as e:
        return {"swarms": [], "count": 0, "error": str(e)}

@app.get("/api/planner/{swarm_id}")
async def get_planner_tasks(swarm_id: str):
    """Get planner data for a swarm"""
    if not orchestrator:
        raise HTTPException(500, "Orchestrator not initialized")
    try:
        tasks = orchestrator.get_planner_data(swarm_id)
        return {"swarm_id": swarm_id, "tasks": tasks}
    except Exception as e:
        return {"swarm_id": swarm_id, "tasks": [], "error": str(e)}

if __name__ == "__main__":
    import uvicorn
    
    print("""
    ╔═══════════════════════════════════╗
    ║   🚀 HECTIC SWARM STARTING 🚀     ║
    ╚═══════════════════════════════════╝
    """)
    
    # Check environment
    required_env = ['OPENROUTER_API_KEY1']
    missing = [var for var in required_env if not os.getenv(var)]
    
    if missing:
        print(f"❌ Missing environment variables: {missing}")
        print("💡 Add API keys to backend/.env")
        exit(1)
    
    # Optional: Database
    if not os.getenv('DATABASE_URL'):
        print("⚠️  DATABASE_URL not set - running without persistence")
    
    print("✅ Environment configured")
    print(f"✅ Agents loaded: {list(AGENTS.keys())}")
    print("\n🌐 Server starting on http://localhost:8000")
    print("📚 API docs: http://localhost:8000/docs\n")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
