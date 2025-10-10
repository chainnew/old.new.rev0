"""
Orchestrator Agent: Main user-facing entry point for scope → swarm → planner pipeline.
Interacts with user, clarifies scope, starts swarms, and populates the agent planner.

NOW WITH: Retry logic, self-validation, dynamic planning, escalations, context memory
"""
import json
import os
import requests
from typing import Dict, Any, List
from openai import OpenAI
from hive_mind_db import HiveMindDB
from agents.conflict_resolver import get_conflict_resolver
from agents.task_scheduler import create_scheduler
from agents.retry_manager import get_retry_manager
from agents.code_validator import get_code_validator
from agents.dynamic_planner import get_dynamic_planner
from agents.escalation_manager import get_escalation_manager
from agents.context_memory import get_context_memory
from agents.project_workspace import get_workspace_manager
from telemetry import get_tracer
from dotenv import load_dotenv
import sys
import os

load_dotenv()

# Import stack inferencer (Phase 2A integration)
try:
    from analyzers.stack_inferencer import infer_stack
    STACK_INFERENCE_AVAILABLE = True
except ImportError:
    print("⚠️ Stack inferencer not available - using fallback stacks")
    STACK_INFERENCE_AVAILABLE = False

class OrchestratorAgent:
    def __init__(self):
        self.db = HiveMindDB('swarms/active_swarm.db')
        self.db.init_db()

        # Core systems (conflict resolution + scheduling)
        self.conflict_resolver = get_conflict_resolver()
        self.scheduler = create_scheduler(self.db)

        # Telemetry (Phase 2A)
        self.tracer = get_tracer()

        # NEW: Intelligence amplification systems
        self.retry_manager = get_retry_manager()
        self.code_validator = get_code_validator()
        self.dynamic_planner = get_dynamic_planner()
        self.escalation_manager = get_escalation_manager(self.db)
        self.context_memory = get_context_memory(self.db)
        self.workspace_manager = get_workspace_manager()

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

        print(f"\n🚀 Orchestrator initialized with {self.model}")
        print(f"🔧 MCP Tools loaded: {len(self.mcp_tools)} tools available")
        print(f"🛡️ Conflict resolver and scheduler active")
        print(f"🔄 Retry manager loaded (intelligent error recovery)")
        print(f"✅ Code validator loaded (syntax + type checking)")
        print(f"📊 Dynamic planner loaded (6-100+ tasks based on complexity)")
        print(f"🚨 Escalation manager loaded (smart blocker handling)")
        print(f"🧠 Context memory loaded (remember decisions & learnings)\n")
    
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

        # NEW: Analyze complexity and generate adaptive plan
        plan = self.dynamic_planner.generate_adaptive_plan(scope)

        # Remember initial scope decision
        self.context_memory.remember_decision(
            swarm_id="pending",
            decision=f"Project complexity: {plan['complexity']}",
            reasoning=f"Score: {plan['complexity_score']}, using {plan['num_agents']} agents with {plan['total_tasks']} tasks"
        )

        # Step 2: Start swarm with DYNAMIC agent count (not hardcoded 3)
        swarm_id = self.db.start_swarm_from_scope(scope, num_agents=plan['num_agents'])
        print(f"🚀 Swarm {swarm_id} started for '{scope['project']}'")
        print(f"   Strategy: {plan['strategy']} with {plan['num_agents']} agents, {plan['total_tasks']} tasks")

        # NEW: Create autonomous project workspace
        project_path = self.workspace_manager.create_workspace(
            project_name=scope.get('project', 'UnnamedProject'),
            swarm_id=swarm_id,
            scope=scope,
            template_type=plan.get('template_type', 'fullstack')
        )

        # Store project path in swarm metadata
        self.db.cursor.execute(
            "UPDATE swarms SET project_path = ? WHERE id = ?",
            (project_path, swarm_id)
        )
        self.db.conn.commit()

        # DEMO: Generate starter files immediately
        self._generate_demo_files(project_path, scope)

        # Load any existing memory for this swarm
        self.context_memory.load_memory_from_db(swarm_id)

        # Step 3: Generate detailed tasks/subtasks using Grok agents
        self._populate_planner_tasks(swarm_id, scope, plan)

        # Step 4: Update swarm to running
        self.db.update_swarm_status(swarm_id, 'running')

        # Step 5: Start agent executor in background to generate code
        import subprocess
        backend_dir = os.path.dirname(__file__)
        venv_python = os.path.join(backend_dir, 'venv/bin/python3')

        # Use venv python if it exists, otherwise system python
        python_exec = venv_python if os.path.exists(venv_python) else 'python3'

        # Start executor and redirect output to a log file
        log_file = open(os.path.join(backend_dir, f'executor_{swarm_id[:8]}.log'), 'w')
        subprocess.Popen([
            python_exec,
            'agent_executor.py',
            swarm_id
        ], cwd=backend_dir, stdout=log_file, stderr=log_file)
        print(f"🤖 Agent executor started for swarm {swarm_id}")
        print(f"   📝 Log: executor_{swarm_id[:8]}.log")

        return {
            "status": "success",
            "message": f"Scope populated! Swarm started for {scope['project']}",
            "swarm_id": swarm_id,
            "planner_url": f"/planner/{swarm_id}",
            "plan": plan,  # Include plan details
            "project_path": project_path  # Autonomous workspace location
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
        """
        Extract structured scope from user message using Grok-4-Fast-Reasoning.
        Phase 2A: Now integrated with stack inference engine for auto-fill.
        """
        with self.tracer.start_as_current_span("extract_scope") as span:
            span.set_attribute("message.length", len(message))

            prompt = f"""You are Grok-4-Fast-Reasoning, an expert AI for full-stack development scoping.

User Request: "{message}"

**Task**: Flesh out a complete project scope using the 6 Must-Haves breakdown approach.

**UI Component Database Available**:
- 218 production-ready components from shadcn/ui, Tremor, Radix UI, Vercel Commerce, HeadlessUI
- Categories: buttons, forms, navigation, cards, modals, data, charts, feedback, loading
- Agents can query via MCP tool or direct SQL (backend/data/ui_components.db)
- Cost: $0 vs $5-10 per generated component
- **Rule**: Agents MUST check database before generating UI from scratch

**The Stack That Ships (2025 Defaults)**:
- Frontend (MVP): Next.js 14+ App Router + TypeScript + Tailwind CSS + Shadcn/ui + TanStack Query + Zustand + React Hook Form + Zod + Vercel + Clerk/NextAuth + Sentry
- Backend (Scale-Up): Node.js/Express/FastAPI + TypeScript/Python + Prisma/SQLAlchemy + PostgreSQL + Redis + BullMQ + JWT + Docker + Railway/Fly.io + GitHub Actions + Stripe
- Rules: Pick one meta-framework (Next.js default); Tailwind first; Copy-paste Shadcn; TanStack for server state; RHF+Zod for forms; Mobile-first; Error boundaries; Use UI component database first

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

            # PHASE 2A: Stack Inference Integration
            # Step 1: Infer technology stack from scope
            stack_inference = None
            if STACK_INFERENCE_AVAILABLE:
                try:
                    print(f"🔍 Running stack inference on: '{message[:60]}...'")
                    stack_inference = infer_stack(message)

                    span.set_attribute("stack.confidence", stack_inference.get('confidence', 0))
                    span.set_attribute("stack.backend", stack_inference.get('backend', 'unknown'))
                    span.set_attribute("stack.template", stack_inference.get('template_title', 'unknown'))

                    conf = stack_inference.get('confidence', 0)
                    if conf >= 0.7:
                        print(f"✅ Stack inferred: {stack_inference['backend']} + {stack_inference['frontend']}")
                        print(f"   Confidence: {conf:.2f} | Template: {stack_inference.get('template_title')}")
                    else:
                        print(f"⚠️ Low confidence ({conf:.2f}) - using Grok fallback in stack")

                except Exception as e:
                    print(f"⚠️ Stack inference failed: {e}")
                    span.set_attribute("stack.error", str(e))
                    stack_inference = None

            # Extract project name from message (simple keyword matching)
            project_name = "UserProject"
            if "taskmaster" in message.lower() or "task" in message.lower():
                project_name = "TaskMasterPro"
            elif "landing" in message.lower() or "website" in message.lower():
                # Extract name from "for X" pattern
                words = message.split()
                for i, word in enumerate(words):
                    if word.lower() in ["for", "called"] and i + 1 < len(words):
                        project_name = words[i+1].replace('"', '').replace("'", "").strip()
                        break

            # DEMO MODE: Fast scope generation with stack inference
            print(f"📋 Generating scope (fast mode with stack inference)")

            # Build tech_stack from inference or use defaults
            if stack_inference and stack_inference.get('confidence', 0) >= 0.5:
                tech_stack = {
                    "frontend": stack_inference.get('frontend', 'Next.js 14 + TS + Tailwind'),
                    "backend": stack_inference.get('backend', 'FastAPI'),
                    "database": stack_inference.get('database', 'PostgreSQL'),
                    "auth": stack_inference.get('auth', 'Clerk/NextAuth'),
                    "deployment": stack_inference.get('deployment', 'Vercel + Railway')
                }
            else:
                # Fallback defaults
                tech_stack = {
                    "frontend": "Next.js 14 + TS + Tailwind + Shadcn",
                    "backend": "FastAPI",
                    "database": "PostgreSQL"
                }

            # NOTE: In production, uncomment this to use Grok AI for full scope generation
            # response = self.client.chat.completions.create(
            #     model=self.model,
            #     messages=[{"role": "user", "content": prompt}],
            #     temperature=0.3,
            #     max_tokens=2000
            # )
            #
            # try:
            #     content = response.choices[0].message.content.strip()
            #     # Clean markdown if present
            #     if '```json' in content:
            #         content = content.split('```json')[1].split('```')[0].strip()
            #     elif '```' in content:
            #         content = content.split('```')[1].split('```')[0].strip()
            #
            #     scope = json.loads(content)
            #     # Enrich with stack inference
            #     if stack_inference:
            #         scope['stack_inference'] = stack_inference
            #     return scope
            # except json.JSONDecodeError as e:
            #     print(f"⚠️ JSON parse error: {e}")

            # Build enriched scope with stack inference
            scope = {
                "project": project_name,
                "goal": message,
                "tech_stack": tech_stack,
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

            # Phase 2A: Add stack inference metadata
            if stack_inference:
                scope['stack_inference'] = stack_inference
                span.set_attribute("stack.inferred", True)

                # Log low confidence for user confirmation gate (Week 3)
                if stack_inference.get('confidence', 0) < 0.7:
                    print(f"   📌 Low confidence stack - may need user confirmation")
            else:
                span.set_attribute("stack.inferred", False)

            span.set_attribute("scope.project", project_name)
            print(f"✅ Scope generated: {project_name}")
            print(f"   Stack: {tech_stack['backend']} + {tech_stack['frontend']}")
            if stack_inference:
                print(f"   Inference: {stack_inference.get('rationale', 'N/A')[:80]}...")

            return scope
    
    def _populate_planner_tasks(self, swarm_id: str, scope: Dict[str, Any], plan: Dict[str, Any] = None) -> None:
        """
        Generate hierarchical tasks/subtasks for the planner using dynamic number of Grok agents.
        Maps to agent-planner.tsx structure.

        Now uses plan from dynamic_planner for optimal task count.
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

        # DEMO MODE: Skip Grok API calls (too slow), use fallback subtasks directly
        print(f"📋 Generating subtasks for {role} (using fallback templates for demo speed)")

        # NOTE: In production, uncomment this to use Grok AI for task generation
        # try:
        #     response = self.client.chat.completions.create(
        #         model=self.model,
        #         messages=[{"role": "user", "content": prompt}],
        #         temperature=0.4
        #     )
        #
        #     content = response.choices[0].message.content
        #     # Extract JSON from markdown if needed
        #     if '```json' in content:
        #         content = content.split('```json')[1].split('```')[0].strip()
        #     elif '```' in content:
        #         content = content.split('```')[1].split('```')[0].strip()
        #
        #     subtasks = json.loads(content)
        #
        #     # Add status field
        #     for subtask in subtasks:
        #         subtask['status'] = 'pending'
        #
        #     return subtasks
        # except Exception as e:
        #     print(f"⚠️ Error generating subtasks for {role}: {e}")

        # Detailed fallback subtasks based on role
        fallback_subtasks = {
            'frontend_architect': [
                {"id": "1.1", "title": f"Design UI wireframes for {project}", "description": "Create responsive layouts with Tailwind + Shadcn", "priority": "high", "status": "pending", "tools": ["shadcn-gen", "browser"]},
                {"id": "1.2", "title": "Implement Next.js pages", "description": "Build App Router pages with TypeScript", "priority": "high", "status": "pending", "tools": ["code-gen"]},
                {"id": "1.3", "title": "Add state management", "description": "Setup TanStack Query + Zustand", "priority": "medium", "status": "pending", "tools": ["code-gen"]},
                {"id": "1.4", "title": "Implement forms & validation", "description": "React Hook Form + Zod schemas", "priority": "medium", "status": "pending", "tools": ["code-gen"]}
            ],
            'backend_integrator': [
                {"id": "2.1", "title": f"Design database schema for {project}", "description": "Create Prisma models with relations", "priority": "high", "status": "pending", "tools": ["db-sync", "prisma-gen"]},
                {"id": "2.2", "title": "Build API endpoints", "description": "Express/FastAPI routes with Zod validation", "priority": "high", "status": "pending", "tools": ["api-designer", "code-gen"]},
                {"id": "2.3", "title": "Integrate third-party services", "description": "Setup Stripe, Redis, email services", "priority": "medium", "status": "pending", "tools": ["stripe-tool", "code-gen"]},
                {"id": "2.4", "title": "Add authentication", "description": "JWT tokens + Clerk integration", "priority": "medium", "status": "pending", "tools": ["code-gen"]}
            ],
            'deployment_guardian': [
                {"id": "3.1", "title": "Write automated tests", "description": "Vitest unit + Playwright E2E tests", "priority": "high", "status": "pending", "tools": ["code-gen"]},
                {"id": "3.2", "title": "Setup CI/CD pipeline", "description": "GitHub Actions for test + deploy", "priority": "high", "status": "pending", "tools": ["code-gen"]},
                {"id": "3.3", "title": f"Deploy {project}", "description": "Vercel frontend + Railway backend", "priority": "medium", "status": "pending", "tools": ["vercel-cli", "docker-build"]},
                {"id": "3.4", "title": "Configure monitoring", "description": "Sentry errors + Lighthouse CI", "priority": "medium", "status": "pending", "tools": ["code-gen"]}
            ]
        }

        return fallback_subtasks.get(role, [
            {"id": f"{role}-1", "title": f"{role.capitalize()} task", "description": "Auto-generated", "priority": "medium", "status": "pending", "tools": []}
        ])
    
    def get_planner_data(self, swarm_id: str) -> List[Dict[str, Any]]:
        """
        Format swarm data for agent-planner.tsx component.
        Returns array of Task objects matching the component's interface.
        """
        status = self.db.get_swarm_status(swarm_id)

        # Agent role display names
        role_names = {
            'frontend_architect': 'Frontend Architect',
            'backend_integrator': 'Backend Integrator',
            'deployment_guardian': 'Deployment Guardian',
            'research': 'Research Agent',
            'design': 'Design Agent',
            'implementation': 'Implementation Agent'
        }

        tasks = []
        for idx, agent in enumerate(status['agents'], 1):
            agent_state = agent['state']
            task_data = agent_state.get('data', {})
            agent_role = agent.get('role', 'agent')
            agent_name = role_names.get(agent_role, agent_role.replace('_', ' ').title())

            task = {
                'id': str(idx),
                'title': task_data.get('task_title', f"{agent_name} Phase"),
                'description': f"Handle {agent_role} tasks for {status['metadata'].get('project', 'project')}",
                'status': agent_state.get('status', 'pending'),
                'priority': 'high' if idx <= 2 else 'medium',
                'level': 0 if idx <= 2 else 1,
                'dependencies': ['1', '2'] if idx == 3 else [],
                'subtasks': task_data.get('subtasks', []),
                'assigned_to': agent_name,  # NEW: Show which agent is working on this
                'agent_role': agent_role    # NEW: Technical role identifier
            }

            tasks.append(task)

        return tasks

    def get_swarm_progress(self, swarm_id: str) -> Dict[str, Any]:
        """Get progress and statistics for a swarm"""
        stats = self.scheduler.get_stats(swarm_id)
        conflict_stats = self.conflict_resolver.get_stats()

        return {
            **stats,
            'conflict_stats': conflict_stats
        }

    def check_task_ready(self, agent_id: str, task_id: str, swarm_id: str) -> tuple[bool, str]:
        """
        Check if agent can start a task (used by agents before execution).
        Returns (can_start, message)
        """
        # Check scheduling (dependencies)
        can_start, reason = self.scheduler.can_agent_start_task(agent_id, task_id, swarm_id)

        if not can_start:
            return False, f"Task blocked: {reason}"

        # Check for failed dependencies
        full_task = self.scheduler._get_full_task(task_id, swarm_id)
        block_reason = self.conflict_resolver.should_block_dependent_task(
            full_task.get('dependencies', [])
        )

        if block_reason:
            return False, block_reason

        return True, "Task ready to start"

    def acquire_file_lock(self, filepath: str, agent_id: str) -> bool:
        """Try to acquire lock on a file for an agent"""
        return self.conflict_resolver.acquire_file_lock(filepath, agent_id)

    def release_file_lock(self, filepath: str, agent_id: str):
        """Release file lock after agent completes write"""
        self.conflict_resolver.release_file_lock(filepath, agent_id)

    def report_task_failure(self, task_id: str, error: str, agent_id: str):
        """Report task failure for propagation to dependent tasks"""
        self.conflict_resolver.mark_task_failed(task_id, error)
        self.conflict_resolver.release_all_locks_for_agent(agent_id)
        print(f"❌ Task {task_id} failed, locks released for agent {agent_id}")

    def _generate_demo_files(self, project_path: str, scope: Dict[str, Any]):
        """Generate demo starter files for immediate preview (NOT production AI generation)"""
        project_name = scope.get('project', 'Project')

        # Create app/page.tsx - Landing page with hero, features, pricing
        page_tsx = f'''import {{ Button }} from '@/components/ui/button';
import {{ Card, CardContent, CardDescription, CardHeader, CardTitle }} from '@/components/ui/card';
import {{ Check }} from 'lucide-react';

export default function Home() {{
  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800">
      {{/* Hero Section */}}
      <section className="container mx-auto px-4 py-20 text-center">
        <h1 className="text-5xl font-bold mb-6">Welcome to {project_name}</h1>
        <p className="text-xl text-gray-600 dark:text-gray-300 mb-8 max-w-2xl mx-auto">
          {scope.get('goal', 'Your amazing project')}
        </p>
        <Button size="lg">Get Started Free</Button>
      </section>

      {{/* Features */}}
      <section className="container mx-auto px-4 py-16">
        <h2 className="text-3xl font-bold text-center mb-12">Key Features</h2>
        <div className="grid md:grid-cols-3 gap-8">
          {{["Fast", "Easy", "Secure"].map((f, i) => (
            <Card key={{i}}>
              <CardHeader><CardTitle>{{f}}</CardTitle></CardHeader>
              <CardContent><CardDescription>Feature description here</CardDescription></CardContent>
            </Card>
          ))}}
        </div>
      </section>
    </div>
  );
}}
'''

        # Create components/ui/button.tsx
        button_tsx = '''import * as React from "react"

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {{
  size?: "sm" | "default" | "lg"
}}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({{ className = "", size = "default", ...props }}, ref) => {{
    const sizes = {{ sm: "h-9 px-3", default: "h-10 px-4 py-2", lg: "h-11 px-8" }}
    return <button className={{`rounded-md font-medium ${{sizes[size]}} ${{className}}`}} ref={{ref}} {{...props}} />
  }}
)
Button.displayName = "Button"
export {{ Button }}
'''

        # Write files
        self.workspace_manager.write_file(project_path, "app/page.tsx", page_tsx)
        self.workspace_manager.write_file(project_path, "components/ui/button.tsx", button_tsx)
        print(f"✅ Demo files created: app/page.tsx, components/ui/button.tsx")

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

    print(f"\n📊 Result: {{json.dumps(result, indent=2)}}")

    if result['swarm_id']:
        print(f"\n📋 Planner Data:")
        planner_data = orchestrator.get_planner_data(result['swarm_id'])
        print(json.dumps(planner_data, indent=2))
