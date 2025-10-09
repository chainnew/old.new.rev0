"""
Escalation Manager - Handle blockers gracefully
When agents get stuck, escalate with clear actions
"""
from typing import Dict, List, Any, Optional
from datetime import datetime
import uuid
import json


class EscalationManager:
    """Escalate blockers to user with actionable options"""

    BLOCKER_TYPES = {
        'config': {
            'icon': '⚙️',
            'title': 'Configuration Required',
            'actions': [
                'Provide the required configuration',
                'Use test/mock values for now',
                'Skip this feature'
            ]
        },
        'design_decision': {
            'icon': '🤔',
            'title': 'Design Decision Needed',
            'actions': [
                'Choose recommended option',
                'Choose alternative option',
                'Let AI decide based on best practices'
            ]
        },
        'external_service': {
            'icon': '🌐',
            'title': 'External Service Issue',
            'actions': [
                'Wait for service to recover',
                'Use alternative service',
                'Mock this feature for now'
            ]
        },
        'unclear_requirement': {
            'icon': '❓',
            'title': 'Requirement Clarification Needed',
            'actions': [
                'Provide more details',
                'Accept AI interpretation',
                'Skip for now, revisit later'
            ]
        },
        'technical_limitation': {
            'icon': '⚠️',
            'title': 'Technical Limitation',
            'actions': [
                'Adjust requirements',
                'Use workaround approach',
                'Mark as known limitation'
            ]
        }
    }

    def __init__(self, db):
        self.db = db
        self.escalations = {}  # In-memory cache

    def classify_blocker(self, error: str, task: Dict) -> str:
        """Figure out what type of blocker this is"""
        error_lower = error.lower()

        # Config issues
        if any(k in error_lower for k in ['env', 'api key', 'api_key', 'config', 'credential']):
            return 'config'

        # Service issues
        if any(k in error_lower for k in ['unavailable', 'not found', 'timeout', 'connection']):
            return 'external_service'

        # Design decisions
        if any(k in error_lower for k in ['choose', 'decide', 'which', 'or', 'should i']):
            return 'design_decision'

        # Unclear requirements
        if any(k in error_lower for k in ['unclear', 'ambiguous', 'dont understand', "don't know"]):
            return 'unclear_requirement'

        # Technical limitations
        return 'technical_limitation'

    def create_escalation(
        self,
        blocker_error: str,
        task: Dict,
        agent_id: str,
        swarm_id: str,
        context: Optional[Dict] = None
    ) -> Dict:
        """
        Create user-friendly escalation with clear options
        """
        blocker_type = self.classify_blocker(blocker_error, task)
        blocker_config = self.BLOCKER_TYPES.get(blocker_type, self.BLOCKER_TYPES['technical_limitation'])

        escalation = {
            'id': str(uuid.uuid4()),
            'swarm_id': swarm_id,
            'agent_id': agent_id,
            'task_id': task.get('id'),
            'task_title': task.get('title', 'Unknown task'),
            'blocker_type': blocker_type,
            'blocker_error': blocker_error,
            'severity': self.assess_severity(blocker_type, task),
            'icon': blocker_config['icon'],
            'title': blocker_config['title'],
            'description': self.generate_description(blocker_error, task, blocker_type),
            'suggested_actions': blocker_config['actions'],
            'can_continue_without': self.can_work_around(task, swarm_id),
            'affected_tasks': self.get_affected_tasks(task, swarm_id),
            'context': context or {},
            'created_at': datetime.now().isoformat(),
            'status': 'pending',
            'resolution': None
        }

        # Store escalation
        self.escalations[escalation['id']] = escalation

        # Save to database in sessions table
        self.save_escalation_to_db(escalation)

        print(f"\n🚨 ESCALATION CREATED: {blocker_config['icon']} {blocker_config['title']}")
        print(f"   Task: {task.get('title')}")
        print(f"   Blocker: {blocker_error[:100]}")
        print(f"   Can continue: {escalation['can_continue_without']}")

        return escalation

    def assess_severity(self, blocker_type: str, task: Dict) -> str:
        """
        Determine severity: critical, high, medium, low
        """
        # Config issues are usually high severity
        if blocker_type == 'config':
            return 'high'

        # External service issues depend on task priority
        if blocker_type == 'external_service':
            priority = task.get('priority', 'medium')
            return 'high' if priority == 'high' else 'medium'

        # Design decisions are medium (can usually proceed with default)
        if blocker_type == 'design_decision':
            return 'medium'

        # Unclear requirements are medium-low
        if blocker_type == 'unclear_requirement':
            return 'medium'

        # Technical limitations are low (work around exists)
        return 'low'

    def generate_description(self, error: str, task: Dict, blocker_type: str) -> str:
        """
        Human-friendly description of the blocker
        """
        descriptions = {
            'config': f"Missing configuration needed to complete '{task.get('title')}'. Error: {error}",
            'design_decision': f"Need to make a design decision for '{task.get('title')}'. Question: {error}",
            'external_service': f"External service issue while working on '{task.get('title')}'. Error: {error}",
            'unclear_requirement': f"Requirements unclear for '{task.get('title')}'. Need clarification: {error}",
            'technical_limitation': f"Technical challenge with '{task.get('title')}'. Issue: {error}"
        }

        return descriptions.get(blocker_type, error)

    def can_work_around(self, task: Dict, swarm_id: str) -> bool:
        """
        Can other agents continue while this is blocked?
        """
        # Check if other tasks depend on this one
        from agents.task_scheduler import create_scheduler

        scheduler = create_scheduler(self.db)
        swarm_status = self.db.get_swarm_status(swarm_id)

        # Find dependent tasks
        dependent_count = 0
        for agent in swarm_status['agents']:
            for subtask in agent['state'].get('data', {}).get('subtasks', []):
                deps = subtask.get('dependencies', [])
                if task['id'] in deps:
                    dependent_count += 1

        # If few dependents, can work around
        return dependent_count <= 2

    def get_affected_tasks(self, blocked_task: Dict, swarm_id: str) -> List[str]:
        """
        Get list of task IDs that are blocked by this escalation
        """
        affected = [blocked_task['id']]

        # Find all tasks that depend on blocked task
        swarm_status = self.db.get_swarm_status(swarm_id)

        for agent in swarm_status['agents']:
            for subtask in agent['state'].get('data', {}).get('subtasks', []):
                deps = subtask.get('dependencies', [])
                if blocked_task['id'] in deps:
                    affected.append(subtask['id'])

        return affected

    def save_escalation_to_db(self, escalation: Dict):
        """Save escalation to database"""
        try:
            # Save in sessions table as escalation record
            self.db.cursor.execute("""
                INSERT INTO sessions (id, swarm_id, data)
                VALUES (?, ?, ?)
            """, (
                escalation['id'],
                escalation['swarm_id'],
                json.dumps({
                    'type': 'escalation',
                    'escalation': escalation
                })
            ))
            self.db.conn.commit()
        except Exception as e:
            print(f"⚠️ Failed to save escalation to DB: {e}")

    def get_escalations_for_swarm(self, swarm_id: str, status: str = 'pending') -> List[Dict]:
        """Get all escalations for a swarm"""
        return [
            esc for esc in self.escalations.values()
            if esc['swarm_id'] == swarm_id and esc['status'] == status
        ]

    def resolve_escalation(self, escalation_id: str, resolution: Dict) -> Dict:
        """
        User resolved escalation - apply resolution and resume
        """
        if escalation_id not in self.escalations:
            return {'success': False, 'error': 'Escalation not found'}

        escalation = self.escalations[escalation_id]
        escalation['status'] = 'resolved'
        escalation['resolution'] = resolution
        escalation['resolved_at'] = datetime.now().isoformat()

        print(f"✅ Escalation resolved: {escalation['title']}")
        print(f"   Action taken: {resolution.get('action')}")

        return {
            'success': True,
            'escalation': escalation,
            'message': 'Escalation resolved, resuming work'
        }

    def cancel_escalation(self, escalation_id: str, reason: str = None) -> Dict:
        """
        Cancel escalation (user chose to skip feature)
        """
        if escalation_id not in self.escalations:
            return {'success': False, 'error': 'Escalation not found'}

        escalation = self.escalations[escalation_id]
        escalation['status'] = 'cancelled'
        escalation['cancellation_reason'] = reason
        escalation['cancelled_at'] = datetime.now().isoformat()

        # Mark affected tasks as skipped
        for task_id in escalation['affected_tasks']:
            self.db.update_task_status(task_id, 'skipped', {
                'reason': f'Escalation cancelled: {reason}'
            })

        print(f"🚫 Escalation cancelled: {escalation['title']}")

        return {
            'success': True,
            'escalation': escalation,
            'message': 'Feature skipped, continuing with other tasks'
        }

    def get_escalation_summary(self, swarm_id: str) -> Dict:
        """
        Get summary of escalations for dashboard
        """
        escalations = self.get_escalations_for_swarm(swarm_id)

        summary = {
            'total': len(escalations),
            'by_type': {},
            'by_severity': {},
            'pending': len([e for e in escalations if e['status'] == 'pending']),
            'resolved': len([e for e in escalations if e['status'] == 'resolved']),
            'escalations': escalations
        }

        # Count by type
        for esc in escalations:
            t = esc['blocker_type']
            summary['by_type'][t] = summary['by_type'].get(t, 0) + 1

            s = esc['severity']
            summary['by_severity'][s] = summary['by_severity'].get(s, 0) + 1

        return summary


# Global singleton
_escalation_manager = None


def get_escalation_manager(db) -> EscalationManager:
    """Get or create global escalation manager"""
    global _escalation_manager
    if _escalation_manager is None:
        _escalation_manager = EscalationManager(db)
    return _escalation_manager
