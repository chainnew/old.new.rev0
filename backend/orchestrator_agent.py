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
        """Extract structured scope from user message using Grok-4-Fast-Reasoning."""
        prompt = f"""You are Grok-4-Fast-Reasoning, an expert AI for full-stack development scoping.

User Request: "{message}"

**Task**: Flesh out a complete project scope using the 6 Must-Haves breakdown approach.

**The Stack That Ships (2025 Defaults)**:
- Frontend (MVP): Next.js 14+ App Router + TypeScript + Tailwind CSS + Shadcn/ui + TanStack Query + Zustand + React Hook Form + Zod + Vercel + Clerk/NextAuth + Sentry
- Backend (Scale-Up): Node.js/Express/FastAPI + TypeScript/Python + Prisma/SQLAlchemy + PostgreSQL + Redis + BullMQ + JWT + Docker + Railway/Fly.io + GitHub Actions + Stripe
- Rules: Pick one meta-framework (Next.js default); Tailwind first; Copy-paste Shadcn; TanStack for server state; RHF+Zod for forms; Mobile-first; Error boundaries

**Output JSON** with these 6 fields:
{{
  "project": "ProjectName (CamelCase, descriptive)",
  "goal": "Clear 2-3 sentence goal with pain point solved",
  "tech_stack": {{
    "frontend": "Next.js 14+ App Router + TS + Tailwind + Shadcn",
    "backend": "FastAPI/Node + Prisma + PostgreSQL",
    "database": "PostgreSQL (Railway)",
    "auth": "Clerk/NextAuth",
    "payments": "Stripe" (if e-comm),
    "deployment": "Vercel (frontend) + Railway (backend)"
  }},
  "features": ["feature1 with details", "feature2", ...],
  "comps": ["Competitor1 (strength/gap)", "Competitor2", ...],
  "timeline": "1-2h MVP" or "1 day prod",
  "outcome": "Live repo on localhost:3000 + Vercel URL + 80% test coverage",
  "scope_of_works": {{
    "in_scope": ["Research", "Design", "Implementation"],
    "out_scope": ["Native apps", "Advanced analytics"],
    "milestones": ["M1: Research done", "M2: Design specs", "M3: MVP on localhost:3000"],
    "risks": ["Risk1 (mitigation)", ...],
    "kpis": ["95% uptime", "Checkout <3s", "Lighthouse 90+"]
  }}
}}

**Special Cases**:
- If task tracking/Trello: Use "TrackFlow" as project name
- If e-commerce/Stripe: Use "ECommerceStripeStore"
- If vague: Assume web app MVP

Return ONLY valid JSON, no markdown code blocks."""
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=2000
        )
        
        try:
            content = response.choices[0].message.content.strip()
            # Clean markdown if present
            if '```json' in content:
                content = content.split('```json')[1].split('```')[0].strip()
            elif '```' in content:
                content = content.split('```')[1].split('```')[0].strip()
            
            scope = json.loads(content)
            print(f"\n✅ Scope fleshed: {scope['project']}")
            print(f"   Goal: {scope['goal'][:80]}...")
            print(f"   Features: {len(scope.get('features', []))} items")
            print(f"   Timeline: {scope.get('timeline', 'N/A')}\n")
            return scope
        except json.JSONDecodeError as e:
            print(f"⚠️ JSON parse error: {e}")
            # Fallback to basic scope
            return {
                "project": "UserProject",
                "goal": message,
                "tech_stack": {
                    "frontend": "Next.js 14 + TS + Tailwind + Shadcn",
                    "backend": "FastAPI",
                    "database": "PostgreSQL"
                },
                "features": ["core functionality"],
                "comps": ["Industry standard"],
                "timeline": "1-2h",
                "outcome": "MVP on localhost:3000",
                "scope_of_works": {
                    "in_scope": ["Research", "Design", "Implementation"],
                    "out_scope": [],
                    "milestones": ["M1: Setup", "M2: MVP", "M3: Deploy"],
                    "risks": [],
                    "kpis": ["Working prototype"]
                }
            }
    
    def _populate_planner_tasks(self, swarm_id: str, scope: Dict[str, Any]) -> None:
        """
        Generate hierarchical tasks/subtasks for the planner using 3 Grok agents.
        Maps to agent-planner.tsx structure.
        """
        # Get agents from DB
        status = self.db.get_swarm_status(swarm_id)
        agents = status['agents']
        
        # Define task templates aligned with agent roles (NEW + LEGACY)
        task_templates = {
            # New specialized agent roles
            'frontend_architect': {
                'title': 'Frontend Architecture & Implementation',
                'description': 'Design UI/UX wireframes and implement Next.js components with Shadcn/TanStack',
                'priority': 'high',
                'level': 0,
                'dependencies': []
            },
            'backend_integrator': {
                'title': 'Backend Integration & APIs',
                'description': 'Design database schema, implement APIs, and integrate Stripe/Redis/queues',
                'priority': 'high',
                'level': 0,
                'dependencies': []
            },
            'deployment_guardian': {
                'title': 'Testing & Deployment',
                'description': 'Setup CI/CD, run E2E tests, and deploy to Vercel/Railway',
                'priority': 'medium',
                'level': 1,
                'dependencies': ['1', '2']  # Depends on frontend and backend
            },
            # Legacy roles for backwards compatibility
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
                'dependencies': ['1', '2']
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
        """Generate role-specific subtasks using Grok-4-Fast-Reasoning with modular breakdown."""
        
        project = scope.get('project', 'Project')
        goal = scope.get('goal', 'Build application')
        features = scope.get('features', [])
        comps = scope.get('comps', [])
        tech_stack = scope.get('tech_stack', {})
        timeline = scope.get('timeline', '1-2h')
        
        prompts = {
            # NEW: Specialized 3-agent prompts with diverse skillsets
            'frontend_architect': f"""You are Frontend Architect with diverse skillsets: Design + Implementation (UI/UX).

Project: "{project}"
Goal: {goal}
Stack: {tech_stack.get('frontend', 'Next.js 14+ + TS + Tailwind + Shadcn')}
Features: {', '.join(features[:3]) if features else 'TBD'}

Generate exactly 4 frontend subtasks as a JSON array. Combine design AND implementation:
1. Design wireframes for main UI (product catalog/cart/dashboard) - Shadcn component specs
2. Implement Next.js pages with App Router (/products, /cart, /profile)
3. Integrate TanStack Query for API calls + Zustand for cart state
4. Add React Hook Form + Zod validation + Clerk auth integration

**Output Format** (ONLY JSON array, no markdown):
[
  {{
    "id": "1.1",
    "title": "Design + Implement Product Catalog UI",
    "description": "Create Shadcn wireframe specs, then code /app/products/page.tsx with filters/search",
    "priority": "high",
    "tools": ["shadcn-gen", "code-gen", "browser"]
  }},
  ... (3 more)
]

Use MCP tools: shadcn-gen, code-gen, api-designer, browser, diagramming-tool.""",

            'backend_integrator': f"""You are Backend Integrator with diverse skillsets: Implementation + Integration (APIs/DB/Payments).

Project: "{project}"
Goal: {goal}
Stack: {tech_stack.get('backend', 'FastAPI/Node + Prisma + PostgreSQL + Redis')}
Features: {', '.join(features[:3]) if features else 'TBD'}

Generate exactly 4 backend subtasks as a JSON array. Combine implementation AND integration:
1. Design Prisma schema (models: Product, User, Order, Cart) + migrations
2. Implement Express/FastAPI routes (/api/products, /api/cart, /api/orders) with Zod validation
3. Integrate Stripe checkout sessions + webhook handlers (/api/stripe/webhook)
4. Setup Redis for cart caching + BullMQ for async email queue (order confirmations)

**Output Format** (ONLY JSON array, no markdown):
[
  {{
    "id": "2.1",
    "title": "Design Prisma Schema + Implement APIs",
    "description": "Create schema.prisma with relations, then code Express routes with validation",
    "priority": "high",
    "tools": ["prisma-gen", "code-gen", "db-sync", "api-designer"]
  }},
  ... (3 more)
]

Use MCP tools: prisma-gen, code-gen, stripe-tool, db-sync, docker-build.""",

            'deployment_guardian': f"""You are Deployment Guardian with diverse skillsets: Testing + Deployment (CI/CD).

Project: "{project}"
Goal: {goal}
Timeline: {timeline}
Target: localhost:3000 → Vercel (frontend) + Railway (backend)

Generate exactly 4 deployment subtasks as a JSON array. Combine testing AND deployment:
1. Write Vitest unit tests (cart logic, API mocks) + Playwright E2E (checkout flow) - 80% coverage
2. Create GitHub Actions CI/CD (.github/workflows/ci.yml: test → build → deploy)
3. Setup Vercel deploy (frontend) + Railway (backend PG/Redis) + Docker Compose (local)
4. Configure Sentry error tracking + Lighthouse CI (90+ scores) + monitoring

**Output Format** (ONLY JSON array, no markdown):
[
  {{
    "id": "3.1",
    "title": "Write Tests (Unit + E2E) for Coverage 80%+",
    "description": "Create Vitest tests for components/logic, Playwright for checkout flow",
    "priority": "medium",
    "tools": ["code-gen", "test-runner", "browser"]
  }},
  ... (3 more)
]

Use MCP tools: code-gen, docker-build, vercel-cli, test-runner, monitoring-setup.""",

            # LEGACY: Old role prompts for backwards compatibility
            'research': f"""You are a Research Specialist agent in a swarm for project "{project}".

Goal: {goal}

Generate exactly 4 research subtasks as a JSON array. Focus on:
1. Gathering user requirements (interviews/surveys for core flows)
2. Analyzing competitor #{1 if comps else 'industry standard'}: {comps[0] if comps else 'N/A'} (features/pricing/gaps)
3. Analyzing competitor #{2 if len(comps) > 1 else 'alternative'}: {comps[1] if len(comps) > 1 else 'N/A'} (pros/cons)
4. Assessing stack fit: {tech_stack.get('frontend', 'Next.js')} + {tech_stack.get('backend', 'FastAPI')} (validate for scalability/security)

**Output Format** (ONLY JSON array, no markdown):
[
  {{
    "id": "1.1",
    "title": "Gather User Requirements (...)",
    "description": "Interview/survey for core flows. Document pain points.",
    "priority": "high",
    "tools": ["browser", "communication-tool"]
  }},
  ... (3 more)
]

Make titles specific to {project}. Use MCP tools: browser, web-scraper, communication-tool, documentation-sites.""",
            
            'design': f"""You are a Design Specialist agent in a swarm for project "{project}".

Stack: {json.dumps(tech_stack)}
Features: {', '.join(features[:3]) if features else 'TBD'}

Generate exactly 4 design subtasks as a JSON array. Focus on:
1. Design wireframes (Figma/Shadcn for UI components)
2. Design database schema (Prisma models with relations)
3. Specify APIs (REST/GraphQL endpoints with validation)
4. Outline integrations (e.g., Stripe sessions/webhooks, Auth flows)

**Output Format** (ONLY JSON array):
[
  {{
    "id": "2.1",
    "title": "Design Wireframes for {features[0] if features else 'Main Features'}",
    "description": "Create Figma mockups or Shadcn component specs.",
    "priority": "high",
    "tools": ["diagramming-tool", "shadcn-gen"]
  }},
  ... (3 more)
]

Use MCP tools: diagramming-tool, prisma-gen, api-designer, stripe-tool, db-sync.""",
            
            'implementation': f"""You are an Implementation Specialist agent in a swarm for project "{project}".

Timeline: {timeline}
Scope: {scope.get('scope_of_works', {}).get('in_scope', ['Research', 'Design', 'Implementation'])}

Generate exactly 4 implementation subtasks as a JSON array. Focus on:
1. Resource allocation (Assign agents: Frontend/Backend/Deploy roles)
2. Development timeline (Gantt chart: Setup → Code → Test → Deploy)
3. Risk assessment (Identify risks like scaling/security + mitigations)
4. Setup localhost:3000 & deploy prep (npx create-next-app; Vercel preview)

**Output Format** (ONLY JSON array):
[
  {{
    "id": "3.1",
    "title": "Resource Allocation (3 Agents)",
    "description": "Assign Frontend/Backend/Deploy roles to swarm agents.",
    "priority": "medium",
    "tools": ["orchestrator-assign"]
  }},
  ... (3 more)
]

Use MCP tools: orchestrator-assign, timeline-generator, risk-analyzer, code-gen, docker-build."""
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
