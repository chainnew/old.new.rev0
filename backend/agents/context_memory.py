"""
Context Memory - Remember decisions, constraints, learnings
Agents don't repeat mistakes or forget what was already decided
"""
from typing import Dict, List, Any, Optional
from datetime import datetime
import json


class ContextMemory:
    """Remember context across agent executions"""

    def __init__(self, db):
        self.db = db
        self.memory_categories = {
            'decisions': {},      # Architectural decisions
            'constraints': {},    # User constraints
            'learnings': {},      # Lessons from errors
            'preferences': {},    # User preferences
            'completed': {}       # What's already done
        }

    def remember_decision(self, swarm_id: str, decision: str, reasoning: str, agent_id: str = None):
        """
        Store architectural decision with reasoning
        Example: "Chose Next.js because user wanted React + SSR"
        """
        key = f"{swarm_id}:{decision}"

        self.memory_categories['decisions'][key] = {
            'decision': decision,
            'reasoning': reasoning,
            'agent_id': agent_id,
            'timestamp': datetime.now().isoformat(),
            'swarm_id': swarm_id
        }

        # Persist to DB
        self._save_to_db(swarm_id, 'decision', {
            'decision': decision,
            'reasoning': reasoning,
            'agent_id': agent_id
        })

        print(f"💭 Remembered decision: {decision}")

    def remember_constraint(self, swarm_id: str, constraint: str, source: str = 'user'):
        """
        Store user constraints
        Example: "Don't use MongoDB", "Must support IE11"
        """
        key = f"{swarm_id}:{constraint}"

        self.memory_categories['constraints'][key] = {
            'constraint': constraint,
            'source': source,
            'timestamp': datetime.now().isoformat(),
            'swarm_id': swarm_id
        }

        self._save_to_db(swarm_id, 'constraint', {
            'constraint': constraint,
            'source': source
        })

        print(f"🚫 Remembered constraint: {constraint}")

    def remember_learning(self, swarm_id: str, mistake: str, solution: str, context: str = None):
        """
        Store lessons learned from errors
        Example: "Stripe webhook needs /api prefix, not root path"
        """
        key = f"{swarm_id}:{mistake}"

        self.memory_categories['learnings'][key] = {
            'mistake': mistake,
            'solution': solution,
            'context': context,
            'timestamp': datetime.now().isoformat(),
            'swarm_id': swarm_id
        }

        self._save_to_db(swarm_id, 'learning', {
            'mistake': mistake,
            'solution': solution,
            'context': context
        })

        print(f"📚 Learned: {mistake} → {solution}")

    def remember_preference(self, swarm_id: str, preference: str, value: Any):
        """
        Store user preferences
        Example: "Code style: functional", "Prefer TypeScript over JavaScript"
        """
        key = f"{swarm_id}:{preference}"

        self.memory_categories['preferences'][key] = {
            'preference': preference,
            'value': value,
            'timestamp': datetime.now().isoformat(),
            'swarm_id': swarm_id
        }

        self._save_to_db(swarm_id, 'preference', {
            'preference': preference,
            'value': value
        })

        print(f"⚡ Remembered preference: {preference} = {value}")

    def mark_completed(self, swarm_id: str, item: str, output: Any = None):
        """
        Mark something as already done (avoid duplication)
        Example: "Generated Button component", "Created database schema"
        """
        key = f"{swarm_id}:{item}"

        self.memory_categories['completed'][key] = {
            'item': item,
            'output': output,
            'timestamp': datetime.now().isoformat(),
            'swarm_id': swarm_id
        }

        print(f"✅ Marked complete: {item}")

    def get_relevant_context(self, swarm_id: str, task: Dict, agent_role: str = None) -> Dict:
        """
        Retrieve all context relevant to current task
        Returns structured context to inject into agent prompt
        """
        context = {
            'decisions': [],
            'constraints': [],
            'learnings': [],
            'preferences': [],
            'completed': []
        }

        task_title = task.get('title', '').lower()
        task_desc = task.get('description', '').lower()
        combined = f"{task_title} {task_desc}"

        # Find relevant decisions
        for key, data in self.memory_categories['decisions'].items():
            if swarm_id in key:
                decision = data['decision'].lower()
                # Check if decision is relevant to this task
                if self._is_relevant(decision, combined):
                    context['decisions'].append(data)

        # Get all constraints (always relevant)
        for key, data in self.memory_categories['constraints'].items():
            if swarm_id in key:
                context['constraints'].append(data)

        # Find relevant learnings
        for key, data in self.memory_categories['learnings'].items():
            if swarm_id in key:
                mistake = data['mistake'].lower()
                if self._is_relevant(mistake, combined):
                    context['learnings'].append(data)

        # Get preferences
        for key, data in self.memory_categories['preferences'].items():
            if swarm_id in key:
                context['preferences'].append(data)

        # Check completed items (avoid duplication)
        for key, data in self.memory_categories['completed'].items():
            if swarm_id in key:
                item = data['item'].lower()
                if self._is_relevant(item, combined):
                    context['completed'].append(data)

        return context

    def _is_relevant(self, item: str, context: str) -> bool:
        """
        Check if an item is relevant to current context
        Simple keyword matching
        """
        # Extract key terms
        item_terms = set(item.split())
        context_terms = set(context.split())

        # Check for overlap
        overlap = item_terms & context_terms

        # Relevant if 2+ common words (or 1 significant word)
        significant_words = ['auth', 'database', 'api', 'stripe', 'payment', 'user', 'admin']

        has_significant = any(w in item_terms and w in context_terms for w in significant_words)

        return len(overlap) >= 2 or has_significant

    def inject_context_into_prompt(self, base_prompt: str, context: Dict) -> str:
        """
        Enhance agent prompt with relevant context
        This is the magic - agents remember everything
        """
        if not any(context.values()):
            return base_prompt  # No context to add

        context_sections = []

        # Add decisions
        if context['decisions']:
            decisions_text = "\n".join([
                f"- {d['decision']} (Reason: {d['reasoning']})"
                for d in context['decisions']
            ])
            context_sections.append(f"**Previous Decisions**:\n{decisions_text}")

        # Add constraints
        if context['constraints']:
            constraints_text = "\n".join([
                f"- {c['constraint']}"
                for c in context['constraints']
            ])
            context_sections.append(f"**Constraints (MUST follow)**:\n{constraints_text}")

        # Add learnings
        if context['learnings']:
            learnings_text = "\n".join([
                f"- {l['mistake']} → Solution: {l['solution']}"
                for l in context['learnings']
            ])
            context_sections.append(f"**Learnings from Previous Errors**:\n{learnings_text}")

        # Add preferences
        if context['preferences']:
            prefs_text = "\n".join([
                f"- {p['preference']}: {p['value']}"
                for p in context['preferences']
            ])
            context_sections.append(f"**User Preferences**:\n{prefs_text}")

        # Add completed items
        if context['completed']:
            completed_text = "\n".join([
                f"- {c['item']}"
                for c in context['completed']
            ])
            context_sections.append(f"**Already Completed (don't duplicate)**:\n{completed_text}")

        # Inject context
        context_block = "\n\n".join(context_sections)

        enhanced_prompt = f"""
{base_prompt}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🧠 CONTEXT FROM PREVIOUS WORK (Remember these!)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{context_block}

Use this context to inform your implementation. Stay consistent with previous decisions and don't repeat mistakes.
"""

        return enhanced_prompt

    def _save_to_db(self, swarm_id: str, memory_type: str, data: Dict):
        """Persist memory to database"""
        try:
            self.db.cursor.execute("""
                INSERT INTO sessions (id, swarm_id, data)
                VALUES (?, ?, ?)
            """, (
                f"memory_{datetime.now().timestamp()}",
                swarm_id,
                json.dumps({
                    'type': 'memory',
                    'memory_type': memory_type,
                    'data': data,
                    'timestamp': datetime.now().isoformat()
                })
            ))
            self.db.conn.commit()
        except Exception as e:
            print(f"⚠️ Failed to save memory to DB: {e}")

    def load_memory_from_db(self, swarm_id: str):
        """Load all memory for a swarm from database"""
        try:
            self.db.cursor.execute("""
                SELECT data FROM sessions
                WHERE swarm_id = ? AND data LIKE '%"type": "memory"%'
            """, (swarm_id,))

            rows = self.db.cursor.fetchall()

            for row in rows:
                try:
                    session_data = json.loads(row[0])
                    if session_data.get('type') == 'memory':
                        memory_type = session_data.get('memory_type')
                        data = session_data.get('data')

                        # Restore to memory categories
                        if memory_type == 'decision':
                            key = f"{swarm_id}:{data['decision']}"
                            self.memory_categories['decisions'][key] = data

                        elif memory_type == 'constraint':
                            key = f"{swarm_id}:{data['constraint']}"
                            self.memory_categories['constraints'][key] = data

                        elif memory_type == 'learning':
                            key = f"{swarm_id}:{data['mistake']}"
                            self.memory_categories['learnings'][key] = data

                        elif memory_type == 'preference':
                            key = f"{swarm_id}:{data['preference']}"
                            self.memory_categories['preferences'][key] = data

                except Exception as e:
                    print(f"⚠️ Failed to parse memory row: {e}")

            print(f"🧠 Loaded memory for swarm {swarm_id}")

        except Exception as e:
            print(f"⚠️ Failed to load memory from DB: {e}")

    def get_memory_summary(self, swarm_id: str) -> Dict:
        """Get summary of what's in memory"""
        summary = {
            'decisions': len([k for k in self.memory_categories['decisions'].keys() if swarm_id in k]),
            'constraints': len([k for k in self.memory_categories['constraints'].keys() if swarm_id in k]),
            'learnings': len([k for k in self.memory_categories['learnings'].keys() if swarm_id in k]),
            'preferences': len([k for k in self.memory_categories['preferences'].keys() if swarm_id in k]),
            'completed': len([k for k in self.memory_categories['completed'].keys() if swarm_id in k])
        }

        return summary


# Global singleton
_context_memory = None


def get_context_memory(db) -> ContextMemory:
    """Get or create global context memory"""
    global _context_memory
    if _context_memory is None:
        _context_memory = ContextMemory(db)
    return _context_memory
