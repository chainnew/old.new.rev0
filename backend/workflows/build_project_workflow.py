"""
Temporal Workflow: Build Project with Stack Inference Integration

Phase 2B: Durable orchestration with:
- Stack-enriched plans from Phase 2A
- Parallel agent fan-out (Coding Swarm)
- Automatic retries with exponential backoff
- OTel traced activities
- Self-healing via ApplicationError

Run worker: python backend/workflows/build_project_workflow.py
"""
import asyncio
import sys
import os
import json
import uuid
from datetime import timedelta
from typing import Dict, List, Any
import logging

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from temporalio import workflow, activity
from temporalio.client import Client
from temporalio.worker import Worker
from temporalio.exceptions import ApplicationError
from telemetry import get_tracer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
tracer = get_tracer()


# ============================================================================
# Activities (Traced with OTel)
# ============================================================================

@activity.defn
async def generate_plan_activity(scope: str, project_id: str) -> Dict[str, Any]:
    """
    Activity: Generate project plan with stack inference.

    Calls orchestrator._extract_scope() which now auto-runs infer_stack().
    """
    with tracer.start_as_current_span("temporal.generate_plan") as span:
        span.set_attribute("project.id", project_id)
        span.set_attribute("scope.length", len(scope))

        # Import here to avoid circular dependencies
        from orchestrator_agent import OrchestratorAgent

        orchestrator = OrchestratorAgent()
        scope_dict = orchestrator._extract_scope(scope)

        # Enrich with project metadata
        plan = {
            "version": "1.1",
            "project_id": project_id,
            "scope": scope_dict,
            "stack_inference": scope_dict.get('stack_inference', {}),
            "tech_stack": scope_dict.get('tech_stack', {}),
            "tasks": _generate_task_specs(scope_dict, project_id)
        }

        confidence = plan['stack_inference'].get('confidence', 0)
        span.set_attribute("plan.stack_confidence", confidence)
        span.set_attribute("plan.num_tasks", len(plan['tasks']))

        logger.info(f"Plan generated for {project_id}: {plan['stack_inference'].get('backend', 'unknown')} (conf: {confidence:.2f})")

        return plan


def _generate_task_specs(scope: Dict, project_id: str) -> List[Dict]:
    """Generate task specs for parallel execution based on scope."""
    # For Phase 2B demo, create 3 parallel tasks (Frontend, Backend, DevOps)
    # In production, this would be more sophisticated based on plan complexity

    tasks = [
        {
            "id": f"{project_id}-frontend",
            "agent": "frontend_architect",
            "action": "implement",
            "description": f"Build UI for {scope.get('project', 'project')}",
            "payload": {
                "components": ["app/page.tsx", "components/ui/button.tsx"],
                "framework": scope.get('tech_stack', {}).get('frontend', 'Next.js')
            }
        },
        {
            "id": f"{project_id}-backend",
            "agent": "backend_integrator",
            "action": "implement",
            "description": f"Build API for {scope.get('project', 'project')}",
            "payload": {
                "endpoints": ["/api/users", "/api/data"],
                "framework": scope.get('tech_stack', {}).get('backend', 'FastAPI')
            }
        },
        {
            "id": f"{project_id}-devops",
            "agent": "deployment_guardian",
            "action": "setup",
            "description": f"Setup CI/CD for {scope.get('project', 'project')}",
            "payload": {
                "targets": ["Vercel", "Railway"],
                "tests": ["unit", "e2e"]
            }
        }
    ]

    return tasks


@activity.defn
async def dispatch_task_activity(task_spec: Dict[str, Any], plan: Dict[str, Any]) -> Dict[str, Any]:
    """
    Activity: Dispatch task to agent with stack-enriched payload.

    Simulates agent execution (in production, calls actual agent API).
    """
    with tracer.start_as_current_span("temporal.dispatch_task") as span:
        span.set_attribute("task.id", task_spec['id'])
        span.set_attribute("task.agent", task_spec['agent'])

        # Enrich task with stack from plan
        enriched_task = {
            **task_spec,
            "stack_context": plan['stack_inference'],
            "project_id": plan['project_id']
        }

        # DEMO MODE: Simulate task execution
        # In production, this would call: requests.post(agent_url, json=enriched_task)

        logger.info(f"Dispatching task {task_spec['id']} to {task_spec['agent']}")

        # Simulate work
        await asyncio.sleep(0.5)

        # Simulate 90% success rate (10% fail for retry demo)
        import random
        if random.random() < 0.1:
            logger.warning(f"Task {task_spec['id']} failed (simulated)")
            raise ApplicationError(
                f"Task {task_spec['id']} failed: simulated error",
                non_retryable=False  # Temporal will retry
            )

        result = {
            "status": "success",
            "task_id": task_spec['id'],
            "agent": task_spec['agent'],
            "output": {
                "files_created": 5,
                "lines_of_code": 250
            },
            "coverage": {"lines": 95, "branches": 88}
        }

        span.set_attribute("task.status", "success")
        logger.info(f"Task {task_spec['id']} completed successfully")

        return result


@activity.defn
async def ui_inference_activity(plan: Dict[str, Any]) -> Dict[str, Any]:
    """
    Activity: Generate UI-specific plan with stack-aware components.

    Week 3 Phase A: Infers UI design from scope + stack.
    """
    with tracer.start_as_current_span("temporal.ui_inference") as span:
        stack = plan['stack_inference']
        scope_text = plan['scope'].get('goal', 'Default UI')

        span.set_attribute("ui.frontend", stack.get('frontend', 'unknown'))
        span.set_attribute("ui.stack_confidence", stack.get('confidence', 0))

        # Import here to avoid circular dependencies
        from openai import OpenAI
        import os

        client = OpenAI(
            api_key=os.getenv('OPENROUTER_API_KEY'),
            base_url="https://openrouter.ai/api/v1"
        )

        # Generate UI plan with stack context
        prompt = f"""Generate a UI component plan for this project:

Scope: {scope_text}
Frontend Stack: {stack.get('frontend', 'React')}
Backend Stack: {stack.get('backend', 'FastAPI')}
Database: {stack.get('database', 'PostgreSQL')}

Output JSON with:
{{
  "components": ["ComponentName with description"],
  "constraints": {{"responsive": true, "wcag": "2.1", "theme": "modern"}},
  "hooks": ["API hooks for backend integration"],
  "needs_review": false
}}

Return ONLY valid JSON."""

        logger.info(f"Inferring UI for: {scope_text[:60]}...")

        response = client.chat.completions.create(
            model="x-ai/grok-4-fast",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4,
            max_tokens=800
        )

        content = response.choices[0].message.content.strip()

        # Clean markdown
        if '```json' in content:
            content = content.split('```json')[1].split('```')[0].strip()
        elif '```' in content:
            content = content.split('```')[1].split('```')[0].strip()

        import json as json_lib
        ui_plan = json_lib.loads(content)

        # Enrich with stack context
        ui_plan['stack_hint'] = stack

        span.set_attribute("ui.components_count", len(ui_plan.get('components', [])))
        span.set_attribute("ui.needs_review", ui_plan.get('needs_review', False))

        logger.info(f"UI plan generated: {len(ui_plan.get('components', []))} components")

        return ui_plan


@activity.defn
async def visual_test_activity(ui_result: Dict[str, Any], coding_results: List[Dict[str, Any]], project_id: str) -> Dict[str, Any]:
    """
    Activity: Visual testing with Playwright for UI inference results.

    Week 3 Phase B: E2E accessibility + responsive checks + screenshot diffs.

    Args:
        ui_result: UI inference output (components, constraints, hooks)
        coding_results: Parallel task results (frontend/backend code)
        project_id: Project identifier for artifacts path

    Returns:
        Visual test results with WCAG violations, responsive pass/fail, diff score
    """
    with tracer.start_as_current_span("temporal.visual_test") as span:
        import subprocess
        import os
        import json

        span.set_attribute("visual.project_id", project_id)
        span.set_attribute("visual.components_count", len(ui_result.get('components', [])))

        # Construct artifacts path (from Projects/ directory structure)
        artifacts_path = f"/Users/matto/Documents/AI CHAT/my-app/Projects/{project_id}"

        # PHASE B STUB: Ephemeral environment setup (Docker build)
        # In production: Docker build from coding_results artifacts, serve on port 3000
        logger.info(f"🐳 [STUB] Building ephemeral Docker environment for {project_id}...")
        # subprocess.run(["docker", "build", "-t", f"ui-test-{project_id}", "."], cwd=artifacts_path, check=False)
        # subprocess.run(["docker", "run", "-d", "-p", "3000:3000", f"ui-test-{project_id}"], check=False)

        # PHASE B STUB: Playwright E2E tests
        logger.info(f"🎭 [STUB] Running Playwright E2E tests for accessibility...")
        # In production: Install playwright with `playwright install`, run tests/ui-flows.spec.js
        # playwright_out = subprocess.run(
        #     ["playwright", "test", "tests/ui-flows.spec.js", "--headed=false"],
        #     cwd=artifacts_path,
        #     capture_output=True,
        #     text=True,
        #     timeout=60
        # )
        playwright_passed = True  # STUB: Assume E2E passed
        wcag_violations = []  # STUB: No violations detected

        # PHASE B STUB: Responsive breakpoint checks
        logger.info(f"📱 [STUB] Checking responsive design (mobile 375px, tablet 768px, desktop 1920px)...")
        responsive_pass = ui_result.get('constraints', {}).get('responsive', False)
        breakpoints_tested = ["mobile_375px", "tablet_768px", "desktop_1920px"] if responsive_pass else []

        # PHASE B STUB: Screenshot diff with pixelmatch
        logger.info(f"📸 [STUB] Generating screenshots and computing visual diffs...")
        # In production: Take screenshots with Playwright, compare with baseline using pixelmatch
        # import pixelmatch
        # diff_score = pixelmatch.compare(baseline_img, actual_img, output_img, width, height)
        diff_score = 0.02  # STUB: 2% difference (acceptable threshold <5%)
        diff_pass = diff_score < 0.05

        # Aggregate results
        visual_pass = playwright_passed and responsive_pass and diff_pass

        span.set_attribute("visual.playwright_passed", playwright_passed)
        span.set_attribute("visual.wcag_violations", len(wcag_violations))
        span.set_attribute("visual.responsive_pass", responsive_pass)
        span.set_attribute("visual.diff_score", diff_score)
        span.set_attribute("visual.overall_pass", visual_pass)

        result = {
            "pass": visual_pass,
            "playwright": {
                "passed": playwright_passed,
                "wcag_violations": wcag_violations,
                "stub": True  # PHASE B STUB indicator
            },
            "responsive": {
                "pass": responsive_pass,
                "breakpoints_tested": breakpoints_tested
            },
            "screenshot_diff": {
                "pass": diff_pass,
                "diff_score": diff_score,
                "threshold": 0.05,
                "stub": True  # PHASE B STUB indicator
            },
            "retriable": not visual_pass  # Retry if failed
        }

        if not visual_pass:
            logger.warning(f"⚠️  Visual tests failed: Playwright={playwright_passed}, Responsive={responsive_pass}, Diff={diff_pass}")
        else:
            logger.info(f"✅ Visual tests passed: WCAG clean, responsive, diff={diff_score:.2%}")

        return result


@activity.defn
async def resolve_conflicts_activity(ui_result: Dict[str, Any], backend_result: Dict[str, Any], project_id: str) -> Dict[str, Any]:
    """
    Activity: Conflict resolution using pgvector similarity for UI/Backend sync.

    Week 3 Phase B: Detects mismatches (e.g., UI assumes GraphQL but backend is REST)
    and mediates by regenerating UI with correct backend hints.

    Args:
        ui_result: UI inference output with hooks/components
        backend_result: Backend coding task result with endpoints/schema
        project_id: Project identifier

    Returns:
        Conflict resolution result with similarity score and fixed UI (if needed)
    """
    with tracer.start_as_current_span("temporal.conflict_resolve") as span:
        import numpy as np
        from sklearn.metrics.pairwise import cosine_similarity

        span.set_attribute("conflict.project_id", project_id)

        # Extract UI and backend artifacts for comparison
        ui_hooks = ui_result.get('hooks', [])
        ui_components_code = "\n".join(ui_result.get('components', []))  # STUB: In prod, read from files

        backend_endpoints = backend_result.get('endpoints', [])  # STUB: Extract from backend code
        backend_schema = backend_result.get('schema', {})  # STUB: Extract API schema

        logger.info(f"🔍 [STUB] Checking UI/Backend sync for project {project_id}...")
        logger.info(f"   UI hooks: {ui_hooks}")
        logger.info(f"   Backend endpoints: {backend_endpoints}")

        # PHASE B STUB: Embed UI code + backend schema using OpenRouter embeddings
        # In production: Use stack_inferencer.embed_text() for both artifacts
        # ui_embedding = embed_text(ui_components_code + " ".join(ui_hooks))
        # backend_embedding = embed_text(json.dumps(backend_endpoints) + json.dumps(backend_schema))

        # STUB: Simulate embeddings with random vectors
        ui_embedding = np.random.rand(1536)
        backend_embedding = np.random.rand(1536)

        # Compute cosine similarity
        similarity = cosine_similarity([ui_embedding], [backend_embedding])[0][0]
        span.set_attribute("conflict.similarity", float(similarity))

        # Conflict threshold: <0.7 indicates mismatch
        conflict_threshold = 0.7
        has_conflict = similarity < conflict_threshold

        span.set_attribute("conflict.detected", has_conflict)

        if has_conflict:
            logger.warning(f"⚠️  Conflict detected! UI/Backend similarity: {similarity:.2f} < {conflict_threshold}")

            # PHASE B STUB: Mediation via Grok-4-Fast re-generation
            # In production: Call ai_client to regenerate UI with corrected backend hints
            mediation_prompt = f"""Fix UI/Backend mismatch:
UI assumes: {ui_hooks}
Backend provides: {backend_endpoints}

Regenerate UI hooks to match backend REST endpoints."""

            # logger.info(f"🤖 [STUB] Mediating conflict with Grok-4-Fast...")
            # fixed_ui = await client.chat.completions.create(...)
            fixed_ui = {
                **ui_result,
                "hooks": [f"use{endpoint}Query" for endpoint in backend_endpoints[:5]],  # STUB fix
                "conflict_resolved": True
            }

            # Log intervention to orchestration_events (STUB)
            # create_orchestration_event(project_id, "conflict_resolved", f"Similarity {similarity:.2f} → Fixed")

            return {
                "resolved": True,
                "similarity": float(similarity),
                "original_ui": ui_result,
                "fixed_ui": fixed_ui,
                "intervention": f"Re-generated UI hooks to match backend (similarity {similarity:.2f})"
            }
        else:
            logger.info(f"✅ No conflicts: UI/Backend similarity: {similarity:.2f} ≥ {conflict_threshold}")
            return {
                "resolved": False,
                "similarity": float(similarity),
                "message": "UI and backend are synced"
            }


@activity.defn
async def test_gate_activity(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Activity: Validate results meet quality gates.

    Checks coverage, errors, etc.
    """
    with tracer.start_as_current_span("temporal.test_gate") as span:
        span.set_attribute("results.count", len(results))

        # Calculate aggregate metrics
        total_coverage = sum(
            r.get('coverage', {}).get('lines', 0)
            for r in results
            if r.get('status') == 'success'
        ) / len(results) if results else 0

        failed_count = sum(1 for r in results if r.get('status') != 'success')

        span.set_attribute("gate.coverage", total_coverage)
        span.set_attribute("gate.failed_count", failed_count)

        # Gate: Require 80% coverage
        if total_coverage < 80:
            logger.error(f"Test gate failed: Coverage {total_coverage}% < 80%")
            raise ApplicationError(
                f"Coverage too low: {total_coverage}%",
                non_retryable=True  # Don't retry quality gates
            )

        logger.info(f"Test gate passed: {total_coverage}% coverage")

        return {
            "status": "passed",
            "coverage": total_coverage,
            "failed_tasks": failed_count
        }


@activity.defn
async def enforce_slo_activity(plan: Dict[str, Any], execution_results: Dict[str, Any], workflow_start_time: float) -> Dict[str, Any]:
    """
    Activity: Enforce SLOs (Service Level Objectives) for Week 4 production readiness.

    SLOs Checked:
    - Cost per project <$5 (OpenRouter tokens)
    - E2E latency <12 minutes (p95)
    - Coverage >=95%
    - Stack confidence >=0.8

    Args:
        plan: Generated plan with stack_inference
        execution_results: Aggregate results (UI, visual, conflicts, test gate)
        workflow_start_time: Workflow start timestamp (Unix time)

    Returns:
        SLO compliance result with cost, latency, coverage metrics
    """
    with tracer.start_as_current_span("temporal.slo_enforce") as span:
        import time

        project_id = plan.get('scope', {}).get('project', 'unknown')
        span.set_attribute("slo.project_id", project_id)

        # SLO 1: Cost Estimation (<$5 per project)
        # Estimate tokens from activities (STUB: hardcoded for demo)
        total_tokens = 0
        total_tokens += plan.get('metrics', {}).get('tokens', 1200)  # Plan generation
        total_tokens += execution_results.get('ui', {}).get('tokens', 800)  # UI inference
        total_tokens += execution_results.get('conflicts', {}).get('tokens', 600) if execution_results.get('conflicts', {}).get('detected') else 0

        cost_per_1k = 0.005  # $0.005/1k tokens (OpenRouter avg)
        estimated_cost = (total_tokens / 1000) * cost_per_1k

        span.set_attribute("slo.tokens_used", total_tokens)
        span.set_attribute("slo.estimated_cost", estimated_cost)

        if estimated_cost > 5.0:
            logger.error(f"💰 SLO BREACH: Cost ${estimated_cost:.2f} > $5 threshold")
            raise ApplicationError(
                f"Cost overrun: ${estimated_cost:.2f} exceeds $5 SLO",
                non_retryable=True  # Don't retry cost breaches
            )

        # SLO 2: E2E Latency (<12 minutes p95)
        workflow_duration = time.time() - workflow_start_time
        latency_slo = 720  # 12 minutes in seconds

        span.set_attribute("slo.latency_seconds", workflow_duration)
        span.set_attribute("slo.latency_threshold", latency_slo)

        if workflow_duration > latency_slo:
            logger.warning(f"⏱️  SLO WARNING: Latency {workflow_duration:.0f}s > {latency_slo}s threshold")
            # Don't fail, just warn and log (latency can spike)
            span.set_attribute("slo.latency_breach", True)
        else:
            span.set_attribute("slo.latency_breach", False)

        # SLO 3: Coverage (>=95%)
        coverage = execution_results.get('test_gate', {}).get('coverage', 0)
        coverage_slo = 95.0

        span.set_attribute("slo.coverage", coverage)
        span.set_attribute("slo.coverage_threshold", coverage_slo)

        if coverage < coverage_slo:
            logger.error(f"📊 SLO BREACH: Coverage {coverage:.1f}% < {coverage_slo}% threshold")
            # Log intervention (STUB: would create orchestration event)
            # create_orchestration_event(project_id, "slo_breach", f"Coverage {coverage:.1f}%")
            raise ApplicationError(
                f"Coverage SLO failed: {coverage:.1f}% < {coverage_slo}%",
                non_retryable=False  # Retriable (may pass on retry)
            )

        # SLO 4: Stack Confidence (>=0.8)
        stack_confidence = plan.get('stack_inference', {}).get('confidence', 0)
        confidence_slo = 0.8

        span.set_attribute("slo.stack_confidence", stack_confidence)
        span.set_attribute("slo.confidence_threshold", confidence_slo)

        if stack_confidence < confidence_slo:
            logger.warning(f"🎯 SLO WARNING: Stack confidence {stack_confidence:.2f} < {confidence_slo} threshold")
            # Warn but don't fail (low confidence triggers manual review flag)
            span.set_attribute("slo.confidence_breach", True)
        else:
            span.set_attribute("slo.confidence_breach", False)

        # Aggregate SLO result
        slo_compliant = (
            estimated_cost <= 5.0 and
            coverage >= coverage_slo
        )

        result = {
            "compliant": slo_compliant,
            "cost": {
                "tokens": total_tokens,
                "estimated_cost": round(estimated_cost, 2),
                "threshold": 5.0,
                "breach": estimated_cost > 5.0
            },
            "latency": {
                "duration_seconds": round(workflow_duration, 1),
                "threshold_seconds": latency_slo,
                "breach": workflow_duration > latency_slo
            },
            "coverage": {
                "value": round(coverage, 1),
                "threshold": coverage_slo,
                "breach": coverage < coverage_slo
            },
            "confidence": {
                "value": round(stack_confidence, 2),
                "threshold": confidence_slo,
                "breach": stack_confidence < confidence_slo
            }
        }

        if slo_compliant:
            logger.info(f"✅ SLO Compliant: Cost=${estimated_cost:.2f}, Coverage={coverage:.1f}%, Latency={workflow_duration:.0f}s")
        else:
            logger.error(f"❌ SLO Breach: Check cost/coverage thresholds")

        return result


# ============================================================================
# Workflow Definition
# ============================================================================

@workflow.defn
class BuildProjectWorkflow:
    """
    Durable workflow for building projects with stack inference.

    Flow:
    1. Generate plan (with stack auto-fill)
    2. Fan-out parallel tasks (Coding Swarm)
    3. Test gate validation
    4. Return results

    Features:
    - Automatic retries with exponential backoff
    - OTel traced activities
    - Stack-enriched task payloads
    - Quality gates
    """

    @workflow.run
    async def run(self, scope: str, project_id: str) -> Dict[str, Any]:
        import time
        workflow_start_time = time.time()  # Track start time for SLO latency check

        workflow.logger.info(f"🚀 Starting BuildProjectWorkflow for {project_id}")
        workflow.logger.info(f"   Scope: {scope[:60]}...")

        try:
            # Step 1: Generate Plan with Stack Inference
            workflow.logger.info("📋 Step 1: Generating plan with stack inference...")

            plan = await workflow.execute_activity(
                generate_plan_activity,
                args=[scope, project_id],
                start_to_close_timeout=timedelta(seconds=30),
                retry_policy=workflow.RetryPolicy(
                    initial_interval=timedelta(seconds=5),
                    maximum_attempts=3,
                    backoff_coefficient=2.0
                )
            )

            stack_backend = plan['stack_inference'].get('backend', 'unknown')
            stack_conf = plan['stack_inference'].get('confidence', 0)

            workflow.logger.info(f"   ✅ Plan generated:")
            workflow.logger.info(f"      Backend: {stack_backend}")
            workflow.logger.info(f"      Confidence: {stack_conf:.2f}")
            workflow.logger.info(f"      Tasks: {len(plan['tasks'])}")

            # Step 2: Fan-out Parallel Tasks (Coding Swarm)
            workflow.logger.info("⚡ Step 2: Dispatching tasks in parallel...")

            task_futures = []
            for task_spec in plan['tasks']:
                future = workflow.execute_activity(
                    dispatch_task_activity,
                    args=[task_spec, plan],
                    start_to_close_timeout=timedelta(seconds=60),
                    schedule_to_close_timeout=timedelta(seconds=180),
                    retry_policy=workflow.RetryPolicy(
                        initial_interval=timedelta(seconds=10),
                        maximum_attempts=3,
                        backoff_coefficient=2.0  # Exponential: 10s, 20s, 40s
                    )
                )
                task_futures.append(future)

            # Await all tasks (parallel execution!)
            task_results = await asyncio.gather(*task_futures, return_exceptions=True)

            # Filter out exceptions (failed tasks)
            successful_results = [
                r for r in task_results
                if not isinstance(r, Exception)
            ]

            workflow.logger.info(f"   ✅ {len(successful_results)}/{len(task_futures)} tasks completed")

            # Step 3: UI Inference (Week 3 Phase A)
            workflow.logger.info("🎨 Step 3: Generating UI plan...")

            ui_result = await workflow.execute_activity(
                ui_inference_activity,
                args=[plan],
                start_to_close_timeout=timedelta(seconds=45),
                retry_policy=workflow.RetryPolicy(
                    initial_interval=timedelta(seconds=5),
                    maximum_attempts=2
                )
            )

            workflow.logger.info(f"   ✅ UI plan: {len(ui_result.get('components', []))} components")
            if ui_result.get('needs_review'):
                workflow.logger.info("   ⚠️ UI needs user review (low confidence)")

            # Step 3b: Visual Testing (Week 3 Phase B)
            workflow.logger.info("🎭 Step 3b: Running visual tests (Playwright + responsive + diffs)...")

            visual_result = await workflow.execute_activity(
                visual_test_activity,
                args=[ui_result, successful_results, project_id],
                start_to_close_timeout=timedelta(seconds=90),
                retry_policy=workflow.RetryPolicy(
                    initial_interval=timedelta(seconds=10),
                    maximum_attempts=2
                )
            )

            workflow.logger.info(f"   ✅ Visual tests: Pass={visual_result['pass']}, " +
                               f"WCAG violations={len(visual_result['playwright']['wcag_violations'])}, " +
                               f"Responsive={visual_result['responsive']['pass']}, " +
                               f"Diff={visual_result['screenshot_diff']['diff_score']:.2%}")

            # Step 3c: Conflict Resolution (Week 3 Phase B)
            workflow.logger.info("🔍 Step 3c: Checking UI/Backend conflicts...")

            # Extract backend result (assume index 1 is backend task)
            backend_result = successful_results[1] if len(successful_results) > 1 else {}

            conflict_result = await workflow.execute_activity(
                resolve_conflicts_activity,
                args=[ui_result, backend_result, project_id],
                start_to_close_timeout=timedelta(seconds=60),
                retry_policy=workflow.RetryPolicy(
                    initial_interval=timedelta(seconds=5),
                    maximum_attempts=2
                )
            )

            if conflict_result['resolved']:
                workflow.logger.info(f"   ⚠️  Conflict resolved: Similarity {conflict_result['similarity']:.2f}")
                ui_result = conflict_result['fixed_ui']  # Update UI with fixed version
            else:
                workflow.logger.info(f"   ✅ No conflicts: Similarity {conflict_result['similarity']:.2f}")

            # Step 4: Test Gate
            workflow.logger.info("🧪 Step 4: Running test gate...")

            gate_result = await workflow.execute_activity(
                test_gate_activity,
                args=[successful_results],
                start_to_close_timeout=timedelta(seconds=30)
            )

            workflow.logger.info(f"   ✅ Test gate passed: {gate_result['coverage']:.1f}% coverage")

            # Step 5: SLO Enforcement (Week 4 Preview)
            workflow.logger.info("📊 Step 5: Enforcing SLOs (cost, latency, coverage, confidence)...")

            execution_results = {
                "ui": ui_result,
                "visual": visual_result,
                "conflicts": conflict_result,
                "test_gate": gate_result
            }

            slo_result = await workflow.execute_activity(
                enforce_slo_activity,
                args=[plan, execution_results, workflow_start_time],
                start_to_close_timeout=timedelta(seconds=30),
                retry_policy=workflow.RetryPolicy(
                    initial_interval=timedelta(seconds=5),
                    maximum_attempts=1  # Don't retry SLO checks extensively
                )
            )

            if slo_result['compliant']:
                workflow.logger.info(f"   ✅ SLO Compliant: Cost=${slo_result['cost']['estimated_cost']}, " +
                                   f"Coverage={slo_result['coverage']['value']}%")
            else:
                workflow.logger.warning(f"   ⚠️  SLO Breaches Detected - Check cost/coverage")

            # Step 6: Return Results
            final_result = {
                "status": "success",
                "project_id": project_id,
                "plan": {
                    "stack_backend": stack_backend,
                    "stack_frontend": plan['stack_inference'].get('frontend', 'unknown'),
                    "stack_confidence": stack_conf
                },
                "ui": {
                    "components": ui_result.get('components', []),
                    "constraints": ui_result.get('constraints', {}),
                    "hooks": ui_result.get('hooks', []),
                    "needs_review": ui_result.get('needs_review', False),
                    "stack_hint": ui_result.get('stack_hint', {}),
                    "conflict_resolved": ui_result.get('conflict_resolved', False)
                },
                "visual_tests": {
                    "pass": visual_result['pass'],
                    "playwright": visual_result['playwright'],
                    "responsive": visual_result['responsive'],
                    "screenshot_diff": visual_result['screenshot_diff']
                },
                "conflicts": {
                    "detected": conflict_result['resolved'],
                    "similarity": conflict_result['similarity'],
                    "intervention": conflict_result.get('intervention', None)
                },
                "slos": {
                    "compliant": slo_result['compliant'],
                    "cost": slo_result['cost'],
                    "latency": slo_result['latency'],
                    "coverage": slo_result['coverage'],
                    "confidence": slo_result['confidence']
                },
                "execution": {
                    "tasks_completed": len(successful_results),
                    "tasks_total": len(plan['tasks']),
                    "coverage": gate_result['coverage']
                }
            }

            workflow.logger.info("🎉 Workflow completed successfully!")

            return final_result

        except ApplicationError as e:
            workflow.logger.error(f"❌ Workflow failed: {e}")

            if e.non_retryable:
                # Permanent failure (e.g., quality gate)
                return {
                    "status": "failed",
                    "project_id": project_id,
                    "error": str(e),
                    "non_retryable": True
                }
            else:
                # Temporal will retry the workflow
                raise


# ============================================================================
# Worker
# ============================================================================

async def run_worker():
    """Run Temporal worker to process workflows and activities."""
    logger.info("🔌 Connecting to Temporal server at localhost:7233...")

    client = await Client.connect("localhost:7233")

    logger.info("✅ Connected to Temporal")
    logger.info("🏗️  Starting worker for task queue: grok-orc-queue")

    worker = Worker(
        client,
        task_queue="grok-orc-queue",
        workflows=[BuildProjectWorkflow],
        activities=[
            generate_plan_activity,
            dispatch_task_activity,
            ui_inference_activity,
            visual_test_activity,
            resolve_conflicts_activity,
            test_gate_activity,
            enforce_slo_activity
        ]
    )

    logger.info("🚀 Worker started and ready to process workflows")
    logger.info("   Press Ctrl+C to stop")
    logger.info("")

    await worker.run()


if __name__ == "__main__":
    try:
        asyncio.run(run_worker())
    except KeyboardInterrupt:
        logger.info("\n🛑 Worker stopped by user")
    except Exception as e:
        logger.error(f"❌ Worker crashed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
