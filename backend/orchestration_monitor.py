"""
Orchestration Monitor: Self-healing feedback loop for Grok-orc Swarm Synergy.

Phase 1B: Implements A1 (Synergy Dynamics) with:
- 10s polling for failed tasks
- Exponential backoff retry (3 attempts)
- Orchestration event logging
- OpenTelemetry traces for interventions

Run as background service: python orchestration_monitor.py
"""
import time
import math
import sqlite3
import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional
from telemetry import get_tracer
from opentelemetry import trace
import os

# Configuration
DB_PATH = os.getenv('SWARM_DB_PATH', 'swarms/active_swarm.db')
POLL_INTERVAL = 10  # seconds
MAX_RETRIES = 3
BACKOFF_BASE = 10  # seconds (10s, 20s, 40s)

class OrchestrationMonitor:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self.tracer = get_tracer()
        self.retry_counts = {}  # In-memory: {task_id: retry_count}

        # Initialize DB tables if needed
        self._init_events_table()

        print(f"🔄 Orchestration Monitor initialized")
        print(f"   📁 Database: {self.db_path}")
        print(f"   ⏱️  Poll interval: {POLL_INTERVAL}s")
        print(f"   🔁 Max retries: {MAX_RETRIES} with exponential backoff\n")

    def _init_events_table(self):
        """Create orchestration_events table for intervention logging."""
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS orchestration_events (
                id TEXT PRIMARY KEY,
                task_id TEXT NOT NULL,
                swarm_id TEXT,
                event_type TEXT NOT NULL,
                details TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_events_task ON orchestration_events(task_id)
        """)

        conn.commit()
        conn.close()
        print("✅ orchestration_events table ready")

    def _log_event(self, task_id: str, swarm_id: str, event_type: str, details: str):
        """Log orchestration intervention event."""
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        cursor = conn.cursor()

        event_id = str(uuid.uuid4())
        cursor.execute("""
            INSERT INTO orchestration_events (id, task_id, swarm_id, event_type, details)
            VALUES (?, ?, ?, ?, ?)
        """, (event_id, task_id, swarm_id, event_type, details))

        conn.commit()
        conn.close()

    def _get_failed_tasks(self) -> List[Dict]:
        """Query tasks with status='failed' from last 5 minutes."""
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        cursor = conn.cursor()

        # Query failed tasks (within 5min window to avoid stale retries)
        cursor.execute("""
            SELECT id, agent_id, swarm_id, description, data, priority
            FROM tasks
            WHERE status = 'failed'
              AND updated_at > datetime('now', '-5 minutes')
            ORDER BY priority DESC
        """)

        rows = cursor.fetchall()
        conn.close()

        tasks = []
        for row in rows:
            tasks.append({
                'id': row[0],
                'agent_id': row[1],
                'swarm_id': row[2],
                'description': row[3],
                'data': json.loads(row[4]) if row[4] else {},
                'priority': row[5]
            })

        return tasks

    def _retry_task(self, task: Dict) -> bool:
        """
        Retry a failed task with exponential backoff.

        Returns:
            True if retry succeeded, False if max retries exceeded
        """
        task_id = task['id']
        retry_count = self.retry_counts.get(task_id, 0)

        # Check max retries
        if retry_count >= MAX_RETRIES:
            print(f"❌ Task {task_id[:8]} exceeded max retries ({MAX_RETRIES})")
            self._log_event(
                task_id,
                task['swarm_id'],
                'max_retries_exceeded',
                f"Failed after {MAX_RETRIES} attempts"
            )
            return False

        # Calculate backoff delay
        backoff_delay = BACKOFF_BASE * math.pow(2, retry_count)

        with self.tracer.start_as_current_span("monitor.retry_task") as span:
            span.set_attribute("task.id", task_id)
            span.set_attribute("retry.count", retry_count + 1)
            span.set_attribute("backoff.delay", backoff_delay)

            print(f"🔁 Retrying task {task_id[:8]} (attempt {retry_count + 1}/{MAX_RETRIES})")
            print(f"   ⏳ Backoff: {backoff_delay}s")
            print(f"   📝 {task['description'][:60]}...")

            # Wait for backoff
            time.sleep(backoff_delay)

            # Update task status to 'queued' for re-execution
            conn = sqlite3.connect(self.db_path, check_same_thread=False)
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE tasks
                SET status = 'queued',
                    updated_at = datetime('now')
                WHERE id = ?
            """, (task_id,))

            conn.commit()
            conn.close()

            # Increment retry counter
            self.retry_counts[task_id] = retry_count + 1

            # Log intervention
            self._log_event(
                task_id,
                task['swarm_id'],
                'retry',
                f"Retry #{retry_count + 1} after {backoff_delay}s backoff"
            )

            span.set_attribute("retry.success", True)
            print(f"✅ Task {task_id[:8]} re-queued for execution\n")

        return True

    def _check_swarm_health(self) -> Dict:
        """Get swarm health statistics."""
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        cursor = conn.cursor()

        # Count tasks by status
        cursor.execute("""
            SELECT status, COUNT(*) as count
            FROM tasks
            GROUP BY status
        """)

        status_counts = {row[0]: row[1] for row in cursor.fetchall()}

        # Count recent interventions (last 10 min)
        cursor.execute("""
            SELECT COUNT(*)
            FROM orchestration_events
            WHERE timestamp > datetime('now', '-10 minutes')
              AND event_type = 'retry'
        """)

        recent_interventions = cursor.fetchone()[0]

        conn.close()

        return {
            'status_counts': status_counts,
            'recent_interventions': recent_interventions,
            'retry_success_rate': self._calculate_retry_success_rate()
        }

    def _calculate_retry_success_rate(self) -> float:
        """Calculate percentage of retries that led to task completion."""
        if not self.retry_counts:
            return 100.0

        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        cursor = conn.cursor()

        # Count completed tasks that were retried
        retried_task_ids = list(self.retry_counts.keys())
        placeholders = ','.join(['?' for _ in retried_task_ids])

        cursor.execute(f"""
            SELECT COUNT(*)
            FROM tasks
            WHERE id IN ({placeholders})
              AND status = 'completed'
        """, retried_task_ids)

        completed_count = cursor.fetchone()[0]
        conn.close()

        return (completed_count / len(retried_task_ids)) * 100 if retried_task_ids else 100.0

    def monitor_loop(self):
        """
        Main monitoring loop: Poll DB every 10s for failed tasks and retry.

        Run this as a background service or daemon.
        """
        print("🚀 Starting orchestration monitor loop...\n")

        iteration = 0
        while True:
            iteration += 1

            with self.tracer.start_as_current_span("monitor.poll_cycle") as span:
                span.set_attribute("iteration", iteration)

                # Query failed tasks
                failed_tasks = self._get_failed_tasks()
                span.set_attribute("failed_tasks.count", len(failed_tasks))

                if failed_tasks:
                    print(f"🔍 Found {len(failed_tasks)} failed tasks (iteration {iteration})")

                    for task in failed_tasks:
                        self._retry_task(task)

                # Log health stats every 10 iterations (~100s)
                if iteration % 10 == 0:
                    health = self._check_swarm_health()
                    print(f"\n📊 Swarm Health (iteration {iteration}):")
                    print(f"   Tasks by status: {health['status_counts']}")
                    print(f"   Recent interventions: {health['recent_interventions']}")
                    print(f"   Retry success rate: {health['retry_success_rate']:.1f}%\n")

            # Sleep until next poll
            time.sleep(POLL_INTERVAL)


def main():
    """Entry point for running monitor as standalone service."""
    monitor = OrchestrationMonitor()

    try:
        monitor.monitor_loop()
    except KeyboardInterrupt:
        print("\n\n⏹️  Monitor stopped by user")
    except Exception as e:
        print(f"\n❌ Monitor crashed: {e}")
        raise


if __name__ == "__main__":
    main()
