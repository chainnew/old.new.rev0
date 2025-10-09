"""
Orchestrator Agent: Main user-facing entry point for scope → swarm → planner pipeline.
Interacts with user, clarifies scope, starts swarms, and populates the agent planner.
"""
import json
import os
import requests
from typing import Dict, Any, List
from openai import OpenAI
from hive_mind_db import HiveMindDB
from dotenv import load_dotenv

load_dotenv()

class OrchestratorAgent:
    def __init__(self):
        self.db = HiveMindDB('swarms/active_swarm.db')
        self.db.init_db()
        
        # OpenRouter client for Grok-4-Fast (try numbered keys as fallback)
        api_key = (
            os.getenv('OPENROUTER_API_KEY') or 
            os.getenv('OPENROUTER_API_KEY1') or 
            os.getenv('OPENROUTER_API_KEY2') or 
            os.getenv('OPENROUTER_API_KEY3')
        )
        
        if not api_key:
            raise ValueError("OPENROUTER_API_KEY not found in environment. Please set it in .env file.")
        
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1"
        )
        self.model = os.getenv('OPENROUTER_MODEL', 'x-ai/grok-4-fast')
        
        # MCP integration
        self.mcp_url = os.getenv('MCP_URL', 'http://localhost:8001')
        self.mcp_api_key = os.getenv('MCP_API_KEY', 'mcp-secret-key')
        self.mcp_tools = self._load_mcp_tools()
        
        print(f"🎯 Orchestrator initialized with {self.model}")
        print(f"🔧 MCP Tools loaded: {len(self.mcp_tools)} tools available")
    
    def _load_mcp_tools(self) -> List[Dict[str, Any]]:
        """Load MCP tool schemas from MCP server."""
        try:
            response = requests.get(f"{self.mcp_url}/tools/schemas", timeout=5)
            if response.status_code == 200:
                return response.json().get('tools', [])
            else:
                print(f"⚠️ Could not load MCP tools: {response.status_code}")
                return []
        except Exception as e:
            print(f"⚠️ MCP server not available: {e}")
            return []
    
    def handle_user_input(self, message: str, user_id: str = "default") -> Dict[str, Any]:
        """
        Main entry point: User message → Scope fleshing → Swarm start → Planner population
        """
        print(f"📨 Received: '{message}' from user {user_id}")
        
        # Step 1: Flesh scope (clarify if vague like "hey")
        if self._is_vague(message):
            clarification = self._clarify_scope(message)
            return {
                "status": "needs_clarification",
                "message": clarification,
                "swarm_id": None
            }
        
        # Extract or generate scope
        scope = self._extract_scope(message)
        
        # Step 2: Start swarm with 3 agents (optimal for reasoning)
        swarm_id = self.db.start_swarm_from_scope(scope, num_agents=3)
        print(f"🚀 Swarm {swarm_id} started for '{scope['project']}'")
        
        # Step 3: Generate detailed tasks/subtasks using Grok agents
        self._populate_planner_tasks(swarm_id, scope)
        
        # Step 4: Update swarm to running
        self.db.update_swarm_status(swarm_id, 'running')
        
        return {
            "status": "success",
            "message": f"Scope populated! Swarm started for {scope['project']}",
            "swarm_id": swarm_id,
            "planner_url": f"/planner/{swarm_id}"
        }
    
    def _is_vague(self, message: str) -> bool:
        """Check if message is too vague and needs clarification."""
        vague_keywords = ['hey', 'hello', 'hi', 'build something', 'help me']
        return len(message.split()) < 5 or any(kw in message.lower() for kw in vague_keywords)
    
    def _clarify_scope(self, message: str) -> str:
        """Use Grok to ask clarifying questions."""
        prompt = f"""User said: "{message}"
        
This is vague. Ask 2-3 targeted questions to clarify:
1. What's the project goal/idea?
2. What type of application? (web app, mobile, API, dashboard, etc.)
3. Any specific features or requirements?

Keep it conversational and helpful."""
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        
        return response.choices[0].message.content
    
    def _extract_scope(self, message: str) -> Dict[str, Any]:
        """Extract structured scope from user message using Grok."""
        prompt = f"""User request: "{message}"

Extract a structured project scope in JSON format:
{{
  "project": "ProjectName",
  "goal": "Clear 1-2 sentence goal",
  "tech_stack": {{
    "frontend": "Framework",
    "backend": "Framework",
    "database": "DB"
  }},
  "features": ["feature1", "feature2", ...],
  "comps": ["competitor1", "competitor2"],
  "timeline": "1-2h" or "1 day" etc
}}

If user mentioned task tracking/dashboard similar to Trello, use TrackFlow as project name.
Return ONLY valid JSON, no markdown."""
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        
        try:
            scope = json.loads(response.choices[0].message.content)
            return scope
        except json.JSONDecodeError:
            # Fallback to basic scope
            return {
                "project": "UserProject",
                "goal": message,
                "tech_stack": {"frontend": "Next.js", "backend": "FastAPI"},
                "features": ["core functionality"],
                "timeline": "1-2h"
            }
    
    def _populate_planner_tasks(self, swarm_id: str, scope: Dict[str, Any]) -> None:
        """
        Generate hierarchical tasks/subtasks for the planner using 3 Grok agents.
        Maps to agent-planner.tsx structure.
        """
        # Get agents from DB
        status = self.db.get_swarm_status(swarm_id)
        agents = status['agents']
        
        # Define task templates aligned with agent roles
        task_templates = {
            'research': {
                'title': 'Research Project Requirements',
                'description': 'Gather information about project scope, competitors, and market',
                'priority': 'high',
                'level': 0,
                'dependencies': []
            },
            'design': {
                'title': 'Design System Architecture',
                'description': 'Create architecture, wireframes, and technical specifications',
                'priority': 'high',
                'level': 0,
                'dependencies': []
            },
            'implementation': {
                'title': 'Implementation Planning',
                'description': 'Plan resource allocation, timeline, and execution strategy',
                'priority': 'medium',
                'level': 1,
                'dependencies': ['1', '2']  # Depends on research and design
            }
        }
        
        # Generate subtasks for each agent using Grok
        for idx, agent in enumerate(agents, 1):
            role = agent['role']
            template = task_templates.get(role, task_templates['implementation'])
            
            # Use Grok to generate specific subtasks
            subtasks = self._generate_subtasks(role, scope)
            
            # Store in agent state
            self.db.update_agent_state(agent['id'], {
                'status': 'assigned',
                'data': {
                    'task_id': str(idx),
                    'task_title': template['title'],
                    'subtasks': subtasks
                }
            })
            
            print(f"✅ Agent {agent['id']} ({role}): {len(subtasks)} subtasks generated")
    
    def call_mcp_tool(self, tool_name: str, args: Dict[str, Any], swarm_id: str, agent_id: str) -> Dict[str, Any]:
        """
        Call an MCP tool and get results.
        """
        try:
            payload = {
                "tool_name": tool_name,
                "args": args,
                "swarm_id": swarm_id,
                "agent_id": agent_id
            }
            
            headers = {
                "Authorization": f"Bearer {self.mcp_api_key}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(
                f"{self.mcp_url}/tools/{tool_name}",
                json=payload,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "success": False,
                    "error": f"MCP call failed: {response.status_code}",
                    "output": None
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "output": None
            }
    
    def _generate_subtasks(self, role: str, scope: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate role-specific subtasks using Grok."""
        prompts = {
            'research': f"""For project "{scope['project']}" with goal: {scope['goal']}

Generate 3-4 research subtasks focusing on:
- Understanding user requirements
- Analyzing competitors: {', '.join(scope.get('comps', ['Trello', 'Asana']))}
- Identifying tech stack fit for {scope.get('tech_stack', {}).get('frontend', 'Next.js')}

Return JSON array of subtasks:
[
  {{"id": "1.1", "title": "...", "description": "...", "priority": "high|medium|low", "tools": ["browser", "web-scraper"]}}
]""",
            
            'design': f"""For project "{scope['project']}" using stack: {json.dumps(scope.get('tech_stack', {}))}

Generate 3-4 design subtasks focusing on:
- Wireframes for features: {', '.join(scope.get('features', []))}
- Database schema design
- API specifications

Return JSON array.""",
            
            'implementation': f"""For project "{scope['project']}" in timeline: {scope.get('timeline', '1-2h')}

Generate 3-4 implementation subtasks focusing on:
- Resource allocation
- Development timeline
- Risk assessment

Return JSON array."""
        }
        
        prompt = prompts.get(role, prompts['implementation'])
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.4
            )
            
            content = response.choices[0].message.content
            # Extract JSON from markdown if needed
            if '```json' in content:
                content = content.split('```json')[1].split('```')[0].strip()
            elif '```' in content:
                content = content.split('```')[1].split('```')[0].strip()
            
            subtasks = json.loads(content)
            
            # Add status field
            for subtask in subtasks:
                subtask['status'] = 'pending'
            
            return subtasks
        except Exception as e:
            print(f"⚠️ Error generating subtasks for {role}: {e}")
            # Fallback subtasks
            return [
                {
                    "id": f"{role}-1",
                    "title": f"{role.capitalize()} task 1",
                    "description": "Auto-generated task",
                    "priority": "medium",
                    "status": "pending",
                    "tools": [f"{role}-tools"]
                }
            ]
    
    def get_planner_data(self, swarm_id: str) -> List[Dict[str, Any]]:
        """
        Format swarm data for agent-planner.tsx component.
        Returns array of Task objects matching the component's interface.
        """
        status = self.db.get_swarm_status(swarm_id)
        
        tasks = []
        for idx, agent in enumerate(status['agents'], 1):
            agent_state = agent['state']
            task_data = agent_state.get('data', {})
            
            task = {
                'id': str(idx),
                'title': task_data.get('task_title', f"{agent['role'].capitalize()} Phase"),
                'description': f"Handle {agent['role']} tasks for {status['metadata'].get('project', 'project')}",
                'status': agent_state.get('status', 'pending'),
                'priority': 'high' if idx <= 2 else 'medium',
                'level': 0 if idx <= 2 else 1,
                'dependencies': ['1', '2'] if idx == 3 else [],
                'subtasks': task_data.get('subtasks', [])
            }
            
            tasks.append(task)
        
        return tasks

# CLI for testing
if __name__ == "__main__":
    orchestrator = OrchestratorAgent()
    
    # Test with TrackFlow example
    print("\n" + "="*60)
    print("Testing Orchestrator with 'Build a task tracker like Trello'")
    print("="*60 + "\n")
    
    result = orchestrator.handle_user_input(
        "Build a task tracking dashboard like Trello with Next.js and Tailwind",
        user_id="test_user"
    )
    
    print(f"\n📊 Result: {json.dumps(result, indent=2)}")
    
    if result['swarm_id']:
        print(f"\n📋 Planner Data:")
        planner_data = orchestrator.get_planner_data(result['swarm_id'])
        print(json.dumps(planner_data, indent=2))
