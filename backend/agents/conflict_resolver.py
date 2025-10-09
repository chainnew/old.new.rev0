"""
Conflict Resolver - Handles file locking, priority arbitration, and failure propagation
Simple and practical implementation for the 3-agent swarm
"""
from typing import Dict, Optional
from datetime import datetime


class ConflictResolver:
    """Lightweight conflict resolver for 3-agent orchestration"""

    def __init__(self):
        # File locks: filepath → (agent_id, timestamp)
        self.file_locks: Dict[str, tuple] = {}

        # Track failed tasks for propagation
        self.failed_tasks: Dict[str, str] = {}  # task_id → error_message

    def acquire_file_lock(self, filepath: str, agent_id: str) -> bool:
        """
        Try to acquire exclusive lock on a file.
        Returns True if lock acquired, False if already locked by another agent.
        """
        if filepath in self.file_locks:
            locked_by, locked_at = self.file_locks[filepath]

            # Same agent can re-acquire its own lock
            if locked_by == agent_id:
                return True

            # Check if lock is stale (> 30 min)
            elapsed = (datetime.now() - locked_at).seconds
            if elapsed > 1800:  # 30 minutes
                print(f"⚠️ Stale lock detected on {filepath} by {locked_by} - breaking lock")
                self.file_locks[filepath] = (agent_id, datetime.now())
                return True

            # Locked by another agent
            print(f"🔒 File {filepath} locked by {locked_by} (agent {agent_id} waiting)")
            return False

        # Lock available
        self.file_locks[filepath] = (agent_id, datetime.now())
        print(f"✅ Agent {agent_id} acquired lock on {filepath}")
        return True

    def release_file_lock(self, filepath: str, agent_id: str) -> None:
        """Release file lock after write completes"""
        if filepath in self.file_locks:
            locked_by, _ = self.file_locks[filepath]
            if locked_by == agent_id:
                del self.file_locks[filepath]
                print(f"🔓 Agent {agent_id} released lock on {filepath}")

    def release_all_locks_for_agent(self, agent_id: str) -> None:
        """Release all locks held by an agent (cleanup on failure)"""
        to_remove = [
            filepath for filepath, (locked_by, _) in self.file_locks.items()
            if locked_by == agent_id
        ]
        for filepath in to_remove:
            del self.file_locks[filepath]
            print(f"🔓 Released lock on {filepath} (agent {agent_id} cleanup)")

    def mark_task_failed(self, task_id: str, error: str) -> None:
        """Mark task as failed for propagation"""
        self.failed_tasks[task_id] = error
        print(f"❌ Task {task_id} marked as failed: {error}")

    def is_task_failed(self, task_id: str) -> bool:
        """Check if task has failed"""
        return task_id in self.failed_tasks

    def get_failure_reason(self, task_id: str) -> Optional[str]:
        """Get failure reason for a task"""
        return self.failed_tasks.get(task_id)

    def should_block_dependent_task(self, task_dependencies: list) -> Optional[str]:
        """
        Check if any dependency has failed.
        Returns blocking reason if should block, None if can proceed.
        """
        for dep_id in task_dependencies:
            if self.is_task_failed(dep_id):
                reason = self.get_failure_reason(dep_id)
                return f"Dependency task {dep_id} failed: {reason}"
        return None

    def clear_failures(self, task_ids: list) -> None:
        """Clear failure markers (for retry attempts)"""
        for task_id in task_ids:
            if task_id in self.failed_tasks:
                del self.failed_tasks[task_id]
                print(f"🔄 Cleared failure marker for task {task_id}")

    def get_stats(self) -> Dict:
        """Get current resolver statistics"""
        return {
            'active_locks': len(self.file_locks),
            'locked_files': list(self.file_locks.keys()),
            'failed_tasks': len(self.failed_tasks),
            'failed_task_ids': list(self.failed_tasks.keys())
        }


# Global singleton instance
_resolver = None


def get_conflict_resolver() -> ConflictResolver:
    """Get or create global resolver instance"""
    global _resolver
    if _resolver is None:
        _resolver = ConflictResolver()
    return _resolver
