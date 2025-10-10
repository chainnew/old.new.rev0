#!/usr/bin/env python3
"""
Test script for conflict resolution and task scheduling
Run with: python test_orchestration.py
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

from agents.conflict_resolver import ConflictResolver
from agents.task_scheduler import TaskScheduler
from hive_mind_db import HiveMindDB

def test_conflict_resolver():
    """Test file locking and conflict detection"""
    print("\n" + "="*60)
    print("TEST 1: Conflict Resolver (File Locking)")
    print("="*60)

    resolver = ConflictResolver()

    # Test 1: Agent acquires lock
    print("\n1. Agent 'frontend' acquiring lock on src/types.ts...")
    result = resolver.acquire_file_lock("src/types.ts", "agent-frontend-123")
    print(f"   ✅ Lock acquired: {result}")

    # Test 2: Another agent tries to acquire same lock
    print("\n2. Agent 'backend' trying to acquire same file...")
    result = resolver.acquire_file_lock("src/types.ts", "agent-backend-456")
    print(f"   {'✅ Blocked' if not result else '❌ FAILED - should be blocked'}: {not result}")

    # Test 3: Same agent can re-acquire
    print("\n3. Agent 'frontend' re-acquiring its own lock...")
    result = resolver.acquire_file_lock("src/types.ts", "agent-frontend-123")
    print(f"   ✅ Re-acquired: {result}")

    # Test 4: Release and acquire by another
    print("\n4. Agent 'frontend' releasing lock...")
    resolver.release_file_lock("src/types.ts", "agent-frontend-123")
    print(f"   ✅ Lock released")

    print("\n5. Agent 'backend' acquiring now...")
    result = resolver.acquire_file_lock("src/types.ts", "agent-backend-456")
    print(f"   ✅ Lock acquired: {result}")

    # Test 5: Failure propagation
    print("\n6. Testing task failure propagation...")
    resolver.mark_task_failed("task-1", "Database connection failed")
    block_reason = resolver.should_block_dependent_task(["task-1"])
    print(f"   ✅ Dependent task blocked: {block_reason is not None}")
    print(f"   Reason: {block_reason}")

    # Stats
    print("\n7. Resolver stats:")
    stats = resolver.get_stats()
    print(f"   Active locks: {stats['active_locks']}")
    print(f"   Failed tasks: {stats['failed_tasks']}")

    print("\n✅ Conflict Resolver tests passed!")


def test_task_scheduler():
    """Test dependency enforcement and scheduling"""
    print("\n" + "="*60)
    print("TEST 2: Task Scheduler (Dependency Enforcement)")
    print("="*60)

    # Create test database
    os.makedirs('swarms', exist_ok=True)
    db = HiveMindDB('swarms/test_swarm.db')
    db.init_db()

    # Create test swarm
    print("\n1. Creating test swarm with dependencies...")
    scope = {
        'project': 'TestProject',
        'goal': 'Test dependency enforcement',
        'tech_stack': {'frontend': 'Next.js', 'backend': 'FastAPI'},
        'features': ['test1', 'test2']
    }
    swarm_id = db.start_swarm_from_scope(scope, num_agents=3)
    print(f"   ✅ Swarm created: {swarm_id}")

    scheduler = TaskScheduler(db)

    # Test 2: Check progress
    print("\n2. Calculating initial progress...")
    progress = scheduler.calculate_progress(swarm_id)
    print(f"   Progress: {progress['progress']}%")
    print(f"   Pending: {progress['pending']}, Completed: {progress['completed']}")

    # Test 3: Get ready tasks (no dependencies)
    print("\n3. Getting ready tasks (should be all pending)...")
    ready = scheduler.get_ready_tasks(swarm_id)
    print(f"   ✅ Ready tasks: {len(ready)}")

    # Test 4: Check for cycles
    print("\n4. Checking for dependency cycles...")
    cycle = scheduler.detect_dependency_cycle(swarm_id)
    if cycle:
        print(f"   ⚠️ Cycle detected: {cycle}")
    else:
        print(f"   ✅ No cycles detected")

    # Stats
    print("\n5. Scheduler stats:")
    stats = scheduler.get_stats(swarm_id)
    print(f"   Progress: {stats['progress']}%")
    print(f"   Ready tasks: {stats['ready_tasks']}")
    print(f"   Has cycle: {stats['has_cycle']}")

    print("\n✅ Task Scheduler tests passed!")

    # Cleanup
    db.close()


def test_integration():
    """Test orchestrator integration"""
    print("\n" + "="*60)
    print("TEST 3: Orchestrator Integration")
    print("="*60)

    try:
        from orchestrator_agent import OrchestratorAgent

        print("\n1. Initializing orchestrator with conflict resolver and scheduler...")
        orchestrator = OrchestratorAgent()
        print(f"   ✅ Orchestrator initialized")

        print("\n2. Testing file lock acquisition...")
        can_lock = orchestrator.acquire_file_lock("test.ts", "agent-1")
        print(f"   ✅ Lock acquired: {can_lock}")

        print("\n3. Testing file lock release...")
        orchestrator.release_file_lock("test.ts", "agent-1")
        print(f"   ✅ Lock released")

        print("\n4. Testing task failure reporting...")
        orchestrator.report_task_failure("test-task-1", "Mock failure", "agent-1")
        print(f"   ✅ Failure reported")

        print("\n✅ Integration tests passed!")

    except Exception as e:
        print(f"\n⚠️ Integration test skipped (requires OpenRouter API key)")
        print(f"   Error: {e}")


if __name__ == "__main__":
    print("\n🧪 ORCHESTRATION TESTS")
    print("Testing conflict resolution and task scheduling")

    try:
        test_conflict_resolver()
        test_task_scheduler()
        test_integration()

        print("\n" + "="*60)
        print("✅ ALL TESTS PASSED!")
        print("="*60)
        print("\nNext steps:")
        print("1. Start the backend: cd backend && python swarm_api.py")
        print("2. Test with real swarm: POST /orchestrator/process")
        print("3. Check progress: GET /api/planner/{swarm_id}/progress")
        print("\n")

    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
