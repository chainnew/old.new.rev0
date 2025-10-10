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

            # Step 3: Test Gate
            workflow.logger.info("🧪 Step 3: Running test gate...")

            gate_result = await workflow.execute_activity(
                test_gate_activity,
                args=[successful_results],
                start_to_close_timeout=timedelta(seconds=30)
            )

            workflow.logger.info(f"   ✅ Test gate passed: {gate_result['coverage']:.1f}% coverage")

            # Step 4: Return Results
            final_result = {
                "status": "success",
                "project_id": project_id,
                "plan": {
                    "stack_backend": stack_backend,
                    "stack_frontend": plan['stack_inference'].get('frontend', 'unknown'),
                    "stack_confidence": stack_conf
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
            test_gate_activity
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
