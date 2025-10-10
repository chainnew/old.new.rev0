#!/usr/bin/env python3
"""
Agent Executor - Picks up pending tasks and executes them with real code generation.
Runs as a background worker, processing tasks from the database.
"""

import os
import json
import time
import asyncio
from typing import Dict, Any, List
from openai import OpenAI
from hive_mind_db import HiveMindDB
from agents.project_workspace import ProjectWorkspace

class AgentExecutor:
    def __init__(self):
        self.db = HiveMindDB(db_path='swarms/active_swarm.db')
        self.db.init_db()  # Ensure DB is initialized
        self.workspace_manager = ProjectWorkspace()

        # Initialize Grok client
        api_key = os.getenv('OPENROUTER_API_KEY1') or os.getenv('OPENROUTER_API_KEY')
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1"
        )
        self.model = os.getenv('OPENROUTER_MODEL', 'x-ai/grok-code-fast-1')

    def get_pending_tasks(self, swarm_id: str) -> List[Dict[str, Any]]:
        """Get all pending subtasks for a swarm"""
        status = self.db.get_swarm_status(swarm_id)
        pending_tasks = []

        for agent in status['agents']:
            agent_state = agent['state']
            task_data = agent_state.get('data', {})
            subtasks = task_data.get('subtasks', [])

            for subtask in subtasks:
                if subtask.get('status') == 'pending':
                    pending_tasks.append({
                        'agent_id': agent['id'],
                        'agent_role': agent['role'],
                        'subtask': subtask,
                        'swarm_id': swarm_id
                    })

        return pending_tasks

    def generate_code_for_task(self, task: Dict[str, Any], project_name: str) -> str:
        """Use Grok to generate code for a specific subtask"""
        subtask = task['subtask']
        role = task['agent_role']

        prompt = f"""You are a {role} working on project "{project_name}".

Task: {subtask['title']}
Description: {subtask['description']}
Priority: {subtask['priority']}

Generate the complete, production-ready code for this task. Output ONLY the code with filename comments.

Example format:
```tsx
// File: components/ui/Button.tsx
export function Button() {{ ... }}
```

Generate the code now:"""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=4000
        )

        return response.choices[0].message.content

    def extract_files_from_code(self, code_response: str) -> List[Dict[str, str]]:
        """Extract individual files from Grok's response"""
        files = []

        # Match code blocks with file comments
        import re
        pattern = r'(?:```[\w]*\s*)?(?://|#)\s*File:\s*([^\n]+)\n(.*?)(?:```|(?=(?://|#)\s*File:|$))'
        matches = re.findall(pattern, code_response, re.DOTALL)

        for filepath, code in matches:
            filepath = filepath.strip()
            code = code.strip()

            # Remove markdown code fence if present
            if code.startswith('```'):
                code = '\n'.join(code.split('\n')[1:])
            if code.endswith('```'):
                code = '\n'.join(code.split('\n')[:-1])

            files.append({
                'path': filepath,
                'content': code.strip()
            })

        return files if files else [{'path': 'index.tsx', 'content': code_response}]

    def execute_task(self, task: Dict[str, Any], project_path: str, project_name: str):
        """Execute a single task - generate code and write files"""
        print(f"\n🔧 Executing: {task['subtask']['title']}")

        # Update task status to in_progress
        self.update_subtask_status(task, 'in-progress')

        try:
            # Generate code using Grok
            code_response = self.generate_code_for_task(task, project_name)

            # Extract individual files
            files = self.extract_files_from_code(code_response)

            # Write files to project
            for file in files:
                file_path = os.path.join(project_path, file['path'])
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                with open(file_path, 'w') as f:
                    f.write(file['content'])
                print(f"   ✅ Created: {file['path']}")

            # Update task status to completed
            self.update_subtask_status(task, 'completed')

        except Exception as e:
            print(f"   ❌ Error: {e}")
            self.update_subtask_status(task, 'failed')

    def update_subtask_status(self, task: Dict[str, Any], status: str):
        """Update subtask status in database"""
        agent_id = task['agent_id']
        subtask_id = task['subtask']['id']

        # Get current agent state
        cursor = self.db.cursor
        cursor.execute("SELECT state FROM agents WHERE id = ?", (agent_id,))
        row = cursor.fetchone()

        if row:
            state = json.loads(row[0])
            subtasks = state.get('data', {}).get('subtasks', [])

            # Update the specific subtask
            for subtask in subtasks:
                if subtask['id'] == subtask_id:
                    subtask['status'] = status
                    break

            # Save back to DB
            state['data']['subtasks'] = subtasks
            cursor.execute(
                "UPDATE agents SET state = ? WHERE id = ?",
                (json.dumps(state), agent_id)
            )
            self.db.conn.commit()
            print(f"   📊 Status: {status}")

    def run_swarm(self, swarm_id: str):
        """Execute all tasks for a swarm"""
        print(f"\n🚀 Starting agent executor for swarm {swarm_id}")

        # Get swarm details
        status = self.db.get_swarm_status(swarm_id)
        project_name = status['metadata'].get('project', 'Project')

        # Get project path
        cursor = self.db.cursor
        cursor.execute("SELECT project_path FROM swarms WHERE id = ?", (swarm_id,))
        row = cursor.fetchone()
        project_path = row[0] if row and row[0] else f"Projects/{project_name}"

        # Get pending tasks
        tasks = self.get_pending_tasks(swarm_id)
        print(f"📋 Found {len(tasks)} pending tasks")

        # Execute tasks sequentially (can parallelize later)
        for i, task in enumerate(tasks, 1):
            print(f"\n[{i}/{len(tasks)}] Processing task...")
            self.execute_task(task, project_path, project_name)
            time.sleep(1)  # Brief pause between tasks

        # Update swarm status
        cursor.execute(
            "UPDATE swarms SET status = ? WHERE id = ?",
            ('completed', swarm_id)
        )
        self.db.conn.commit()

        print(f"\n✅ Swarm {swarm_id} completed! All tasks done.")

def main():
    """Main entry point for agent executor"""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python agent_executor.py <swarm_id>")
        sys.exit(1)

    swarm_id = sys.argv[1]
    executor = AgentExecutor()
    executor.run_swarm(swarm_id)

if __name__ == "__main__":
    main()
