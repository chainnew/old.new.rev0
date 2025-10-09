"""
Dynamic Task Planner - Scale tasks based on project complexity
Simple scope → 6-8 tasks
Monster scope → 50-100+ tasks with phased delivery
"""
from typing import Dict, List, Any
import json


class DynamicTaskPlanner:
    """Smart task planning - right number of tasks for the job"""

    COMPLEXITY_THRESHOLDS = {
        'simple': 20,      # 6-8 tasks, 2 agents
        'medium': 50,      # 12-15 tasks, 3 agents
        'complex': 100,    # 25-35 tasks, 5 agents
        'monster': 999     # 50-100+ tasks, 8-10 agents, phased
    }

    def analyze_scope_complexity(self, scope: Dict[str, Any]) -> tuple[str, int]:
        """
        Analyze scope and return (complexity_level, score)
        """
        # Extract indicators
        features = scope.get('features', [])
        tech_stack = scope.get('tech_stack', {})
        timeline = scope.get('timeline', '1-2h')
        goal = scope.get('goal', '')

        # Calculate complexity score
        score = 0

        # Features weight
        score += len(features) * 3

        # Tech stack complexity
        stack_items = sum(len(v.split('+')) if isinstance(v, str) else 1
                         for v in tech_stack.values())
        score += stack_items * 2

        # Integrations (Stripe, auth, etc)
        integrations = [
            'stripe', 'payment', 'auth', 'oauth', 'webhook',
            'redis', 'queue', 'email', 'sms', 'notification'
        ]
        goal_lower = goal.lower()
        integration_count = sum(1 for i in integrations if i in goal_lower)
        score += integration_count * 5

        # Database complexity
        if 'prisma' in str(tech_stack).lower() or 'database' in goal_lower:
            score += 5

        # API complexity
        if 'api' in goal_lower or 'rest' in goal_lower or 'graphql' in goal_lower:
            score += 3

        # Timeline indicator (longer = more complex)
        if 'day' in timeline or 'week' in timeline:
            score += 10

        # Determine complexity level
        if score < self.COMPLEXITY_THRESHOLDS['simple']:
            return 'simple', score
        elif score < self.COMPLEXITY_THRESHOLDS['medium']:
            return 'medium', score
        elif score < self.COMPLEXITY_THRESHOLDS['complex']:
            return 'complex', score
        else:
            return 'monster', score

    def calculate_optimal_agents_and_tasks(self, complexity: str, score: int) -> Dict:
        """
        Return optimal number of agents and tasks
        """
        configs = {
            'simple': {
                'num_agents': 2,
                'tasks_per_agent': 3,
                'total_tasks': 6,
                'strategy': 'simple',
                'phases': 1
            },
            'medium': {
                'num_agents': 3,
                'tasks_per_agent': 4,
                'total_tasks': 12,
                'strategy': 'standard',
                'phases': 1
            },
            'complex': {
                'num_agents': 5,
                'tasks_per_agent': 6,
                'total_tasks': 30,
                'strategy': 'parallel',
                'phases': 2
            },
            'monster': {
                'num_agents': min(8, score // 15),  # Scale with complexity
                'tasks_per_agent': 12,
                'total_tasks': min(100, score // 3),  # Cap at 100
                'strategy': 'phased',
                'phases': 3
            }
        }

        config = configs[complexity]

        # Adjust for actual complexity score
        if complexity == 'monster':
            config['total_tasks'] = max(50, min(100, score // 2))
            config['num_agents'] = max(5, min(10, config['total_tasks'] // 10))

        return config

    def generate_adaptive_plan(self, scope: Dict[str, Any]) -> Dict:
        """
        Generate right-sized plan based on scope
        """
        complexity, score = self.analyze_scope_complexity(scope)
        config = self.calculate_optimal_agents_and_tasks(complexity, score)

        print(f"📊 Scope Analysis:")
        print(f"   Complexity: {complexity.upper()} (score: {score})")
        print(f"   Agents: {config['num_agents']}")
        print(f"   Tasks: {config['total_tasks']}")
        print(f"   Strategy: {config['strategy']}")

        plan = {
            'complexity': complexity,
            'complexity_score': score,
            'num_agents': config['num_agents'],
            'total_tasks': config['total_tasks'],
            'strategy': config['strategy'],
            'phases': self.generate_phases(scope, config)
        }

        return plan

    def generate_phases(self, scope: Dict[str, Any], config: Dict) -> List[Dict]:
        """
        Generate execution phases based on strategy
        """
        strategy = config['strategy']

        if strategy == 'simple' or strategy == 'standard':
            # Single phase
            return [{
                'name': 'Development',
                'tasks': config['total_tasks'],
                'duration_est': '1-2 hours',
                'deliverable': 'Working MVP at localhost:3000'
            }]

        elif strategy == 'parallel':
            # Two phases: Core + Polish
            core_tasks = int(config['total_tasks'] * 0.7)
            polish_tasks = config['total_tasks'] - core_tasks

            return [
                {
                    'name': 'Phase 1: Core Features',
                    'tasks': core_tasks,
                    'duration_est': '2-3 hours',
                    'deliverable': 'Working MVP with core features'
                },
                {
                    'name': 'Phase 2: Enhancement & Polish',
                    'tasks': polish_tasks,
                    'duration_est': '1-2 hours',
                    'deliverable': 'Production-ready app'
                }
            ]

        elif strategy == 'phased':
            # Three phases: MVP → Enhanced → Production
            mvp_tasks = int(config['total_tasks'] * 0.4)
            enhanced_tasks = int(config['total_tasks'] * 0.4)
            prod_tasks = config['total_tasks'] - mvp_tasks - enhanced_tasks

            return [
                {
                    'name': 'Phase 1: MVP',
                    'tasks': mvp_tasks,
                    'duration_est': '3-4 hours',
                    'deliverable': 'Core features working',
                    'features': self.extract_mvp_features(scope)
                },
                {
                    'name': 'Phase 2: Enhanced',
                    'tasks': enhanced_tasks,
                    'duration_est': '3-4 hours',
                    'deliverable': 'All features implemented',
                    'features': self.extract_enhanced_features(scope)
                },
                {
                    'name': 'Phase 3: Production Ready',
                    'tasks': prod_tasks,
                    'duration_est': '2-3 hours',
                    'deliverable': 'Tested, secured, deployed',
                    'features': ['Testing', 'Security', 'Performance', 'Deployment']
                }
            ]

        return []

    def extract_mvp_features(self, scope: Dict[str, Any]) -> List[str]:
        """Extract core MVP features (first 40%)"""
        features = scope.get('features', [])
        mvp_count = max(2, len(features) // 2)
        return features[:mvp_count]

    def extract_enhanced_features(self, scope: Dict[str, Any]) -> List[str]:
        """Extract enhanced features (remaining 60%)"""
        features = scope.get('features', [])
        mvp_count = max(2, len(features) // 2)
        return features[mvp_count:]

    def should_break_into_smaller_tasks(self, task: Dict, elapsed_time: int, attempts: int) -> bool:
        """
        Detect if task is too complex and needs breaking down
        """
        # Task taking > 15 min
        if elapsed_time > 900:
            return True

        # Failed 2+ times
        if attempts >= 2:
            return True

        # Description super long
        if len(task.get('description', '')) > 500:
            return True

        return False

    def simplify_complex_task(self, task: Dict) -> List[Dict]:
        """
        Break 1 complex task → 3-5 simpler tasks
        Quick and dirty decomposition
        """
        # Simple heuristic breakdown
        base_id = task['id']
        title = task['title']

        # Generic breakdown pattern
        subtasks = [
            {
                'id': f"{base_id}.1",
                'title': f"Setup/Research for {title}",
                'description': f"Gather requirements and setup for: {title}",
                'priority': task.get('priority', 'medium'),
                'status': 'pending'
            },
            {
                'id': f"{base_id}.2",
                'title': f"Core Implementation of {title}",
                'description': f"Implement main functionality for: {title}",
                'priority': task.get('priority', 'medium'),
                'status': 'pending'
            },
            {
                'id': f"{base_id}.3",
                'title': f"Integration & Testing for {title}",
                'description': f"Connect and test: {title}",
                'priority': task.get('priority', 'medium'),
                'status': 'pending'
            }
        ]

        return subtasks


# Global singleton
_planner = None


def get_dynamic_planner() -> DynamicTaskPlanner:
    """Get or create global planner"""
    global _planner
    if _planner is None:
        _planner = DynamicTaskPlanner()
    return _planner
