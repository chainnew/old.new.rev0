"""
Primary Agent - Coordinator for HECTIC SWARM
Decomposes tasks and routes to specialist agents
"""
import os
from typing import Dict, Any, List
import json
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from utils.openrouter_client import get_openrouter_client


class PrimaryAgent:
    """
    Swarm coordinator
    - Decomposes user requests into subtasks
    - Routes to specialist agents
    - Integrates results
    """
    
    def __init__(self):
        self.client = get_openrouter_client()
        self.model = "x-ai/grok-4-fast"
        
        self.system_prompt = """You are the Primary Coordinator in HECTIC SWARM for hypervisor porting.

Available specialist agents:
- CODE: Migrates x86 → ARM64 code
- DEBUG: Analyzes hypervisor errors/traps
- RESEARCH: Finds arch-specific documentation

Your job:
1. Decompose user requests into agent tasks
2. Return JSON array of tasks

Output format:
```json
[
  {
    "type": "code",
    "description": "Port arch/x86/traps.c to ARM64",
    "priority": 1,
    "file_path": "arch/x86/traps.c"
  }
]
```

Rules:
- Break complex ports into file-level tasks
- Use "code" for migration, "debug" for errors, "research" for docs
- Max 5 parallel tasks
"""
    
    async def decompose(self, user_message: str, conversation_id: str) -> List[Dict[str, Any]]:
        """
        Decompose user request into agent tasks
        
        Args:
            user_message: User's request (e.g., "Port Xen x86 trap handling to ARM")
            conversation_id: UUID for context
        
        Returns:
            List of task dicts for specialist agents
        """
        try:
            response = await self.client.chat_completion(
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": f"Request: {user_message}\nConversation: {conversation_id}"}
                ],
                model=self.model,
                max_tokens=2048,
                temperature=0.5
            )
            
            content = response.choices[0].message.content
            
            # Extract JSON from markdown code blocks
            tasks = self._parse_tasks(content)
            
            # Add conversation_id to each task
            for i, task in enumerate(tasks):
                task['id'] = f"{conversation_id}-task-{i}"
                task['conversation_id'] = conversation_id
            
            print(f"✅ Decomposed into {len(tasks)} tasks")
            return tasks
            
        except Exception as e:
            print(f"❌ Decomposition failed: {e}")
            # Fallback: single code task
            return [{
                'id': f"{conversation_id}-task-0",
                'type': 'code',
                'description': user_message,
                'conversation_id': conversation_id,
                'priority': 1
            }]
    
    async def integrate(self, results: List[Dict[str, Any]], conversation_id: str) -> str:
        """
        Integrate specialist results into final response
        
        Args:
            results: List of agent outputs
            conversation_id: UUID
        
        Returns:
            Human-readable summary
        """
        try:
            # Build summary of results
            summary_parts = []
            for i, result in enumerate(results):
                if result['status'] == 'completed':
                    output = result.get('output', {})
                    summary = output.get('summary', 'Task completed')
                    summary_parts.append(f"{i+1}. ✅ {summary}")
                else:
                    summary_parts.append(f"{i+1}. ❌ Task failed: {result.get('output', {}).get('error', 'Unknown')}")
            
            combined = "\n".join(summary_parts)
            
            # Ask Grok to write a nice summary
            response = await self.client.chat_completion(
                messages=[
                    {"role": "system", "content": "You integrate specialist agent results into a clear summary for the user."},
                    {"role": "user", "content": f"Agent results:\n{combined}\n\nWrite a brief summary."}
                ],
                model=self.model,
                max_tokens=512,
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"❌ Integration failed: {e}")
            return "✅ Tasks completed. Check artifacts for details."
    
    def _parse_tasks(self, content: str) -> List[Dict[str, Any]]:
        """Extract JSON tasks from LLM response"""
        # Try to find JSON in markdown code blocks
        if '```json' in content:
            start = content.find('```json') + 7
            end = content.find('```', start)
            json_str = content[start:end].strip()
        elif '```' in content:
            start = content.find('```') + 3
            end = content.find('```', start)
            json_str = content[start:end].strip()
        else:
            json_str = content
        
        try:
            tasks = json.loads(json_str)
            if isinstance(tasks, list):
                return tasks
            return [tasks]
        except json.JSONDecodeError:
            print(f"⚠️ Failed to parse tasks JSON, using fallback")
            return []
