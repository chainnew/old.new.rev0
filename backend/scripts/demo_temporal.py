#!/usr/bin/env python3
"""
Temporal Workflow Demo Script

Demonstrates Phase 2B integration:
- Stack inference in workflow
- Parallel task execution
- OTel traced activities
- Automatic retries

Usage: python demo_temporal.py "scope" "project_id"
"""
import asyncio
import sys
import uuid
from datetime import timedelta

from temporalio.client import Client


async def run_workflow_demo(scope: str, project_id: str):
    """Start and monitor a BuildProjectWorkflow."""
    print("🎯 Temporal Workflow Demo: Phase 2B")
    print("=" * 60)
    print(f"Scope: {scope}")
    print(f"Project ID: {project_id}")
    print("=" * 60)
    print("")

    # Connect to Temporal
    print("🔌 Connecting to Temporal server...")
    client = await Client.connect("localhost:7233")
    print("✅ Connected")
    print("")

    # Start workflow
    workflow_id = f"build-project-{project_id}-{uuid.uuid4().hex[:8]}"

    print(f"🚀 Starting workflow (ID: {workflow_id})...")
    print("   This will:")
    print("   1. Generate plan with stack inference")
    print("   2. Dispatch 3 tasks in parallel")
    print("   3. Run test gate validation")
    print("")

    handle = await client.start_workflow(
        "BuildProjectWorkflow",
        args=[scope, project_id],
        id=workflow_id,
        task_queue="grok-orc-queue",
        execution_timeout=timedelta(minutes=5)
    )

    print(f"✅ Workflow started!")
    print(f"   Watch progress at: http://localhost:8233/namespaces/default/workflows/{workflow_id}")
    print("")
    print("⏳ Waiting for completion...")
    print("")

    # Wait for result
    try:
        result = await handle.result()

        print("=" * 60)
        print("🎉 Workflow Completed Successfully!")
        print("=" * 60)
        print("")
        print(f"Status: {result['status']}")
        print("")
        print("📊 Plan:")
        print(f"   Backend: {result['plan']['stack_backend']}")
        print(f"   Frontend: {result['plan']['stack_frontend']}")
        print(f"   Confidence: {result['plan']['stack_confidence']:.2f}")
        print("")
        print("⚡ Execution:")
        print(f"   Tasks Completed: {result['execution']['tasks_completed']}/{result['execution']['tasks_total']}")
        print(f"   Coverage: {result['execution']['coverage']:.1f}%")
        print("")
        print("✅ Project ready for deployment!")
        print("")

        return result

    except Exception as e:
        print("=" * 60)
        print("❌ Workflow Failed")
        print("=" * 60)
        print(f"Error: {e}")
        print("")
        print("Check:")
        print("1. Worker is running: python backend/workflows/build_project_workflow.py")
        print("2. Temporal server is up: docker ps | grep temporal-server")
        print("3. Logs: docker logs temporal-server")
        print("")
        raise


def main():
    """CLI entry point."""
    if len(sys.argv) < 2:
        scope = "Build a task management app with Python backend and modern UI"
        project_id = str(uuid.uuid4())[:8]
        print(f"ℹ️  Using default scope and project ID")
    else:
        scope = sys.argv[1]
        project_id = sys.argv[2] if len(sys.argv) > 2 else str(uuid.uuid4())[:8]

    asyncio.run(run_workflow_demo(scope, project_id))


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 Demo cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        sys.exit(1)
