"""
MCP (Multi-Agent Control Platform) Servers
Provides tool APIs for swarm agents: browser, code-gen, db-sync, communication
"""
from fastapi import FastAPI, HTTPException, Depends, Header
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import requests
from openai import OpenAI
from hive_mind_db import HiveMindDB
from agents.ui_component_manager import get_ui_component_manager
import uuid
import json
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Initialize UI Component Manager
ui_manager = get_ui_component_manager()

# Auth dependency (API key based)
MCP_API_KEY = os.getenv('MCP_API_KEY', 'mcp-secret-key')

def get_api_key(authorization: Optional[str] = Header(None)):
    """Validate MCP API key from header."""
    expected = f"Bearer {MCP_API_KEY}"
    if not authorization or authorization != expected:
        raise HTTPException(401, "Invalid MCP API key")
    return authorization

app = FastAPI(title="MCP Servers", version="1.0", description="Tool APIs for AI Swarm Agents")

# Ensure swarms directory exists
os.makedirs('swarms', exist_ok=True)

# Hive-Mind DB integration
db = HiveMindDB('swarms/mcp_swarm.db')
db.init_db()

# Grok client for code generation (optional - only needed for code-gen tool)
# Try OPENROUTER_API_KEY first, then fall back to numbered keys
OPENROUTER_API_KEY = (
    os.getenv('OPENROUTER_API_KEY') or 
    os.getenv('OPENROUTER_API_KEY1') or 
    os.getenv('OPENROUTER_API_KEY2') or 
    os.getenv('OPENROUTER_API_KEY3')
)
GROK_MODEL = os.getenv('OPENROUTER_MODEL', 'x-ai/grok-4-fast')

if OPENROUTER_API_KEY:
    grok_client = OpenAI(
        api_key=OPENROUTER_API_KEY,
        base_url="https://openrouter.ai/api/v1"
    )
    print(f"✅ Code-gen tool enabled with {GROK_MODEL}")
else:
    grok_client = None
    print("⚠️  Code-gen tool disabled (OPENROUTER_API_KEY not set)")

# ============================================================================
# Pydantic Models
# ============================================================================

class ToolCall(BaseModel):
    """Standard tool call format for MCP."""
    tool_name: str = Field(..., description="MCP tool to call")
    args: Dict[str, Any] = Field(..., description="Tool arguments")
    swarm_id: str = Field(..., description="Current swarm for DB update")
    agent_id: str = Field(..., description="Calling agent ID")

class ToolResponse(BaseModel):
    """Standard tool response format."""
    success: bool
    output: Any
    updated_task_id: Optional[str] = None
    error: Optional[str] = None

# ============================================================================
# Tool Implementations
# ============================================================================

def browser_tool(query: str, num_results: int = 5) -> Dict[str, List[str]]:
    """
    Web research tool for market comps and information gathering.
    Uses DuckDuckGo Instant Answer API (no key required).
    """
    try:
        # DuckDuckGo Instant Answer API
        response = requests.get(
            "https://api.duckduckgo.com/",
            params={"q": query, "format": "json", "no_html": 1},
            timeout=10
        )
        
        if response.status_code != 200:
            return {"results": [], "error": f"Search failed with status {response.status_code}"}
        
        data = response.json()
        
        # Extract results from RelatedTopics
        results = []
        for topic in data.get('RelatedTopics', [])[:num_results]:
            if isinstance(topic, dict):
                text = topic.get('Text', '')
                url = topic.get('FirstURL', '')
                if text:
                    results.append({"text": text, "url": url})
        
        # If no related topics, try abstract
        if not results and data.get('Abstract'):
            results.append({
                "text": data['Abstract'],
                "url": data.get('AbstractURL', '')
            })
        
        return {
            "query": query,
            "results": results,
            "count": len(results)
        }
    except Exception as e:
        return {"results": [], "error": str(e)}

def code_gen_tool(framework: str, component: str, scope_data: Dict[str, Any]) -> str:
    """
    Code generation tool using Grok-4-Fast.
    Generates framework-specific code (Next.js, React, etc.)
    """
    if grok_client is None:
        return "// Error: Code generation disabled. Set OPENROUTER_API_KEY environment variable."
    
    try:
        prompt = f"""Generate production-ready {framework} code for a {component} component.

Scope/Requirements:
{json.dumps(scope_data, indent=2)}

Requirements:
- Use TypeScript
- Use Tailwind CSS for styling
- Use Shadcn/UI components if applicable
- Include proper error handling
- Add comments for complex logic
- Make it responsive and accessible

Return ONLY the code, no markdown or explanations."""

        response = grok_client.chat.completions.create(
            model=GROK_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=2000
        )
        
        code = response.choices[0].message.content
        
        # Clean markdown if present
        if '```' in code:
            code = code.split('```')[1]
            if code.startswith('tsx') or code.startswith('typescript'):
                code = '\n'.join(code.split('\n')[1:])
        
        return code.strip()
    except Exception as e:
        return f"// Error generating code: {e}"

def db_sync_tool(operation: str, data: Dict[str, Any], swarm_id: str) -> str:
    """
    Database sync tool for hive-mind operations.
    Updates tasks, sessions, and agent states.
    """
    try:
        if operation == "update_task":
            task_id = data.get('task_id')
            status = data.get('status', 'completed')
            output = data.get('output', {})
            
            db.cursor.execute("""
                UPDATE tasks 
                SET status = ?, data = ?, updated_at = datetime('now')
                WHERE id = ?
            """, (status, json.dumps(output), task_id))
            db.conn.commit()
            
            return f"Task {task_id} updated to {status}"
            
        elif operation == "update_session":
            session_data = data.get('session_data', {})
            
            db.cursor.execute("""
                INSERT INTO sessions (id, swarm_id, data)
                VALUES (?, ?, ?)
            """, (str(uuid.uuid4()), swarm_id, json.dumps(session_data)))
            db.conn.commit()
            
            return "Session data saved"
            
        elif operation == "get_progress":
            db.cursor.execute("""
                SELECT COUNT(*) as total,
                       SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as done
                FROM tasks
                WHERE swarm_id = ?
            """, (swarm_id,))
            row = db.cursor.fetchone()
            total, done = row[0], row[1]
            progress = (done / total * 100) if total > 0 else 0
            
            return f"Progress: {done}/{total} tasks ({progress:.1f}%)"
            
        else:
            raise ValueError(f"Unknown operation: {operation}")
            
    except Exception as e:
        raise HTTPException(500, f"DB sync failed: {e}")

def communication_tool(message: str, recipient: str = "user", action: str = "notify") -> str:
    """
    Communication tool for agent-user interactions.
    Handles notifications, clarifications, and updates.
    """
    timestamp = datetime.now().isoformat()
    
    actions = {
        "notify": f"[{timestamp}] Notification to {recipient}: {message}",
        "clarify": f"[{timestamp}] Clarification request to {recipient}: {message}",
        "update": f"[{timestamp}] Update for {recipient}: {message}",
        "error": f"[{timestamp}] Error reported to {recipient}: {message}"
    }
    
    return actions.get(action, actions["notify"])

def ui_component_tool(query: str, component_type: Optional[str] = None, limit: int = 5) -> Dict[str, Any]:
    """
    Search scraped GitHub UI themes database for components.
    Agents use this to discover pre-built UI components matching requirements.

    Args:
        query: Component search term (e.g., "button", "navbar", "dashboard", "card")
        component_type: Optional filter ("react", "vue", "tailwind")
        limit: Max results to return

    Returns:
        List of matching UI components with code samples
    """
    try:
        components = ui_manager.search_components(query, component_type, limit)

        return {
            "query": query,
            "found": len(components),
            "components": components[:limit]
        }
    except Exception as e:
        return {
            "query": query,
            "found": 0,
            "components": [],
            "error": str(e)
        }

# ============================================================================
# API Endpoints
# ============================================================================

@app.get("/")
def root():
    return {
        "service": "MCP Servers",
        "version": "1.0",
        "tools": ["browser", "code-gen", "db-sync", "communication", "ui-component"],
        "endpoints": {
            "GET /tools/schemas": "Get OpenAI-compatible tool schemas",
            "POST /tools/browser": "Web research tool",
            "POST /tools/code-gen": "Code generation tool",
            "POST /tools/db-sync": "Database sync tool",
            "POST /tools/communication": "Communication tool",
            "POST /tools/ui-component": "UI component discovery tool (142 themes)"
        }
    }

@app.get("/tools/schemas")
async def get_tool_schemas():
    """Get OpenAI-compatible tool schemas for agent prompts."""
    return {
        "tools": [
            {
                "type": "function",
                "function": {
                    "name": "browser_tool",
                    "description": "Research competitors, market data, and web information. Returns structured search results.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Search query (e.g., 'task tracking SaaS competitors')"
                            },
                            "num_results": {
                                "type": "integer",
                                "description": "Number of results to return (default: 5)",
                                "default": 5
                            }
                        },
                        "required": ["query"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "code_gen_tool",
                    "description": "Generate production-ready code using Grok-4-Fast. Supports Next.js, React, TypeScript.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "framework": {
                                "type": "string",
                                "description": "Framework/library (e.g., 'Next.js', 'React')"
                            },
                            "component": {
                                "type": "string",
                                "description": "Component to generate (e.g., 'dashboard', 'auth-form')"
                            },
                            "scope_data": {
                                "type": "object",
                                "description": "Project scope and requirements"
                            }
                        },
                        "required": ["framework", "component"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "db_sync_tool",
                    "description": "Sync data with hive-mind database. Update tasks, sessions, and progress.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "operation": {
                                "type": "string",
                                "enum": ["update_task", "update_session", "get_progress"],
                                "description": "Operation to perform"
                            },
                            "data": {
                                "type": "object",
                                "description": "Operation-specific data"
                            },
                            "swarm_id": {
                                "type": "string",
                                "description": "Target swarm ID"
                            }
                        },
                        "required": ["operation", "swarm_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "communication_tool",
                    "description": "Communicate with users or stakeholders. Send notifications, clarifications, updates.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "message": {
                                "type": "string",
                                "description": "Message content"
                            },
                            "recipient": {
                                "type": "string",
                                "description": "Recipient (default: 'user')",
                                "default": "user"
                            },
                            "action": {
                                "type": "string",
                                "enum": ["notify", "clarify", "update", "error"],
                                "description": "Communication action type",
                                "default": "notify"
                            }
                        },
                        "required": ["message"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "ui_component_tool",
                    "description": "Search 142 scraped GitHub UI theme repositories for components. Find buttons, navbars, dashboards, cards, forms, etc. Returns code samples and stencil patterns.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Component search term (e.g., 'button', 'navbar', 'dashboard', 'card', 'form', 'modal')"
                            },
                            "component_type": {
                                "type": "string",
                                "description": "Optional filter: 'react', 'vue', 'tailwind', 'css'",
                                "default": None
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Max results (default: 5)",
                                "default": 5
                            }
                        },
                        "required": ["query"]
                    }
                }
            }
        ]
    }

@app.post("/tools/browser", response_model=ToolResponse)
async def call_browser(call: ToolCall, _: str = Depends(get_api_key)):
    """Execute browser tool for web research."""
    if call.tool_name != "browser":
        raise HTTPException(400, f"Invalid tool: expected 'browser', got '{call.tool_name}'")
    
    try:
        output = browser_tool(
            call.args.get("query", ""),
            call.args.get("num_results", 5)
        )
        
        # Update swarm task with results
        db.cursor.execute("""
            UPDATE tasks 
            SET status = 'completed', 
                data = json_set(data, '$.browser_results', ?),
                updated_at = datetime('now')
            WHERE id = (
                SELECT id FROM tasks 
                WHERE swarm_id = ? 
                  AND agent_id = ?
                  AND status != 'completed'
                LIMIT 1
            )
        """, (json.dumps(output), call.swarm_id, call.agent_id))
        db.conn.commit()
        
        return ToolResponse(
            success=True,
            output=output,
            updated_task_id=call.agent_id
        )
    except Exception as e:
        return ToolResponse(
            success=False,
            output=None,
            error=str(e)
        )

@app.post("/tools/code-gen", response_model=ToolResponse)
async def call_code_gen(call: ToolCall, _: str = Depends(get_api_key)):
    """Execute code generation tool."""
    if call.tool_name != "code-gen":
        raise HTTPException(400, f"Invalid tool: expected 'code-gen', got '{call.tool_name}'")
    
    try:
        output = code_gen_tool(
            call.args.get("framework", "Next.js"),
            call.args.get("component", "component"),
            call.args.get("scope_data", {})
        )
        
        # Update swarm task with generated code
        db.cursor.execute("""
            UPDATE tasks 
            SET status = 'in-progress',
                data = json_set(data, '$.generated_code', ?),
                updated_at = datetime('now')
            WHERE id = (
                SELECT id FROM tasks 
                WHERE swarm_id = ? AND agent_id = ?
                LIMIT 1
            )
        """, (output, call.swarm_id, call.agent_id))
        db.conn.commit()
        
        return ToolResponse(
            success=True,
            output={"code": output},
            updated_task_id=call.agent_id
        )
    except Exception as e:
        return ToolResponse(
            success=False,
            output=None,
            error=str(e)
        )

@app.post("/tools/db-sync", response_model=ToolResponse)
async def call_db_sync(call: ToolCall, _: str = Depends(get_api_key)):
    """Execute database sync tool."""
    if call.tool_name != "db-sync":
        raise HTTPException(400, f"Invalid tool: expected 'db-sync', got '{call.tool_name}'")
    
    try:
        output = db_sync_tool(
            call.args.get("operation", "get_progress"),
            call.args.get("data", {}),
            call.swarm_id
        )
        
        # Log tool call
        session_id = str(uuid.uuid4())
        db.cursor.execute("""
            INSERT INTO sessions (id, swarm_id, data)
            VALUES (?, ?, ?)
        """, (session_id, call.swarm_id, json.dumps({
            "tool_call": "db-sync",
            "operation": call.args.get("operation"),
            "result": output,
            "timestamp": datetime.now().isoformat()
        })))
        db.conn.commit()
        
        return ToolResponse(
            success=True,
            output=output,
            updated_task_id=session_id
        )
    except Exception as e:
        return ToolResponse(
            success=False,
            output=None,
            error=str(e)
        )

@app.post("/tools/communication", response_model=ToolResponse)
async def call_communication(call: ToolCall, _: str = Depends(get_api_key)):
    """Execute communication tool."""
    if call.tool_name != "communication":
        raise HTTPException(400, f"Invalid tool: expected 'communication', got '{call.tool_name}'")
    
    try:
        output = communication_tool(
            call.args.get("message", ""),
            call.args.get("recipient", "user"),
            call.args.get("action", "notify")
        )
        
        # Log communication
        db.cursor.execute("""
            UPDATE sessions 
            SET data = json_insert(data, '$.communications', json_array(?))
            WHERE swarm_id = ?
            ORDER BY timestamp DESC
            LIMIT 1
        """, (output, call.swarm_id))
        db.conn.commit()
        
        return ToolResponse(
            success=True,
            output=output
        )
    except Exception as e:
        return ToolResponse(
            success=False,
            output=None,
            error=str(e)
        )

@app.post("/tools/ui-component", response_model=ToolResponse)
async def call_ui_component(call: ToolCall, _: str = Depends(get_api_key)):
    """Execute UI component search tool."""
    if call.tool_name != "ui-component":
        raise HTTPException(400, f"Invalid tool: expected 'ui-component', got '{call.tool_name}'")

    try:
        output = ui_component_tool(
            call.args.get("query", ""),
            call.args.get("component_type"),
            call.args.get("limit", 5)
        )

        # Log tool call
        session_id = str(uuid.uuid4())
        db.cursor.execute("""
            INSERT INTO sessions (id, swarm_id, data)
            VALUES (?, ?, ?)
        """, (session_id, call.swarm_id, json.dumps({
            "tool_call": "ui-component",
            "query": call.args.get("query"),
            "found": output.get("found", 0),
            "timestamp": datetime.now().isoformat()
        })))
        db.conn.commit()

        return ToolResponse(
            success=True,
            output=output,
            updated_task_id=session_id
        )
    except Exception as e:
        return ToolResponse(
            success=False,
            output=None,
            error=str(e)
        )

# Run: uvicorn mcp_servers:app --host 0.0.0.0 --port 8001
if __name__ == "__main__":
    import uvicorn
    print("🔧 Starting MCP Servers on port 8001...")
    print("📋 Tools: browser, code-gen, db-sync, communication, ui-component")
    print("🎨 UI Component Database: 142 GitHub repos loaded")
    print("🔑 API Key required: Bearer {MCP_API_KEY}")
    uvicorn.run(app, host="0.0.0.0", port=8001)
