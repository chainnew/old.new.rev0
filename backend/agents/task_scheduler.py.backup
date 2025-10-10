"""
Task Scheduler - Enforces task dependencies and manages execution order
Simple dependency checking for 3-agent orchestration
"""
from typing import Dict, List, Optional, Set
from hive_mind_db import HiveMindDB


class TaskScheduler:
    """Lightweight task scheduler with dependency enforcement"""

    def __init__(self, db: HiveMindDB):
        self.db = db

        # Track tasks currently being checked (for cycle detection)
        self._checking: Set[str] = set()

    def are_dependencies_met(self, task_id: str, task_data: Dict) -> bool:
        """
        Check if all dependencies for a task are completed.
        Returns True if can start, False if blocked.
        """
        dependencies = task_data.get('dependencies', [])

        if not dependencies:
            return True  # No dependencies, can start immediately

        # Get all tasks in this swarm
        swarm_id = task_data['swarm_id']
        swarm_status = self.db.get_swarm_status(swarm_id)

        # Build task status map
        task_status_map = {}
        for task in swarm_status['tasks']:
            task_status_map[task['id']] = task['status']

        # Check each dependency
        for dep_id in dependencies:
            dep_status = task_status_map.get(dep_id, 'pending')

            if dep_status == 'failed':
                print(f"⚠️ Task {task_id} blocked: dependency {dep_id} failed")
                return False

            if dep_status != 'completed':
                print(f"⏳ Task {task_id} waiting: dependency {dep_id} is {dep_status}")
                return False

        print(f"✅ Task {task_id} ready: all dependencies met")
        return True

    def get_ready_tasks(self, swarm_id: str) -> List[Dict]:
        """
        Get all pending tasks whose dependencies are satisfied.
        Returns list of tasks ready to execute, sorted by priority.
        """
        swarm_status = self.db.get_swarm_status(swarm_id)
        ready_tasks = []

        for task in swarm_status['tasks']:
            if task['status'] == 'pending':
                # Need full task data for dependency check
                full_task = self._get_full_task(task['id'], swarm_id)
                if self.are_dependencies_met(task['id'], full_task):
                    ready_tasks.append(full_task)

        # Sort by priority (higher = more important)
        ready_tasks.sort(key=lambda t: t.get('priority', 5), reverse=True)

        return ready_tasks

    def _get_full_task(self, task_id: str, swarm_id: str) -> Dict:
        """Get full task data including dependencies from agent state"""
        # Query agents to find which one has this task
        swarm_status = self.db.get_swarm_status(swarm_id)

        for agent in swarm_status['agents']:
            agent_state = agent.get('state', {})
            agent_data = agent_state.get('data', {})
            subtasks = agent_data.get('subtasks', [])

            for subtask in subtasks:
                if subtask.get('id') == task_id:
                    # Return full subtask with swarm context
                    return {
                        **subtask,
                        'swarm_id': swarm_id,
                        'agent_id': agent['id']
                    }

        # Fallback: return minimal task data
        for task in swarm_status['tasks']:
            if task['id'] == task_id:
                return {
                    **task,
                    'swarm_id': swarm_id,
                    'dependencies': []
                }

        return {'id': task_id, 'swarm_id': swarm_id, 'status': 'pending', 'dependencies': []}

    def detect_dependency_cycle(self, swarm_id: str) -> Optional[List[str]]:
        """
        Detect circular dependencies using DFS.
        Returns list of task IDs in cycle if found, None otherwise.
        """
        swarm_status = self.db.get_swarm_status(swarm_id)

        # Build dependency graph
        graph: Dict[str, List[str]] = {}
        for task in swarm_status['tasks']:
            full_task = self._get_full_task(task['id'], swarm_id)
            graph[task['id']] = full_task.get('dependencies', [])

        # DFS cycle detection
        visited: Set[str] = set()
        rec_stack: Set[str] = set()
        cycle_path: List[str] = []

        def dfs(node: str, path: List[str]) -> bool:
            visited.add(node)
            rec_stack.add(node)
            path.append(node)

            for neighbor in graph.get(node, []):
                if neighbor not in visited:
                    if dfs(neighbor, path):
                        return True
                elif neighbor in rec_stack:
                    # Cycle detected! Find where it starts
                    cycle_start_idx = path.index(neighbor)
                    cycle_path.extend(path[cycle_start_idx:])
                    return True

            path.pop()
            rec_stack.remove(node)
            return False

        for task_id in graph:
            if task_id not in visited:
                if dfs(task_id, []):
                    return cycle_path

        return None

    def calculate_progress(self, swarm_id: str) -> Dict:
        """Calculate swarm progress percentage"""
        swarm_status = self.db.get_swarm_status(swarm_id)
        tasks = swarm_status['tasks']

        if not tasks:
            return {'progress': 0, 'completed': 0, 'total': 0}

        total = len(tasks)
        completed = sum(1 for t in tasks if t['status'] == 'completed')
        in_progress = sum(1 for t in tasks if t['status'] == 'in-progress')
        pending = sum(1 for t in tasks if t['status'] == 'pending')
        failed = sum(1 for t in tasks if t['status'] == 'failed')

        progress = (completed / total) * 100 if total > 0 else 0

        return {
            'progress': round(progress, 1),
            'completed': completed,
            'in_progress': in_progress,
            'pending': pending,
            'failed': failed,
            'total': total
        }

    def can_agent_start_task(self, agent_id: str, task_id: str, swarm_id: str) -> tuple[bool, Optional[str]]:
        """
        Check if an agent can start a specific task.
        Returns (can_start, reason_if_blocked)
        """
        full_task = self._get_full_task(task_id, swarm_id)

        # Check if task belongs to this agent
        if full_task.get('agent_id') != agent_id:
            return False, f"Task {task_id} not assigned to agent {agent_id}"

        # Check if dependencies are met
        if not self.are_dependencies_met(task_id, full_task):
            deps = full_task.get('dependencies', [])
            return False, f"Dependencies not met: {deps}"

        return True, None

    def get_stats(self, swarm_id: str) -> Dict:
        """Get scheduler statistics"""
        ready = self.get_ready_tasks(swarm_id)
        progress = self.calculate_progress(swarm_id)
        cycle = self.detect_dependency_cycle(swarm_id)

        return {
            **progress,
            'ready_tasks': len(ready),
            'has_cycle': cycle is not None,
            'cycle': cycle
        }


# Helper function for easy import
def create_scheduler(db: HiveMindDB) -> TaskScheduler:
    """Create a new scheduler instance"""
    return TaskScheduler(db)
