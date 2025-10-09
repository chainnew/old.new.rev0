"""
Code Agent - Specialist for hypervisor code migration (x86 → ARM64)
Part of HECTIC SWARM
"""
import os
from typing import Dict, Any, List
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from utils.openrouter_client import get_openrouter_client

# Optional: Database support
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    DB_AVAILABLE = True
except ImportError:
    DB_AVAILABLE = False
    print("⚠️  psycopg2 not installed - running without database support")


class CodeAgent:
    """
    Code migration specialist
    - Ports x86 → ARM64 hypervisor code
    - Generates git-style diffs
    - Uses RAG for context
    """
    
    def __init__(self):
        self.client = get_openrouter_client()
        self.model = "x-ai/grok-4-fast"
        
        # System prompt
        self.system_prompt = """You are a Code Specialist in HECTIC SWARM.
Your role: Port x86 hypervisor code to ARM64 for Xen.

Focus on:
- Architecture-specific changes (registers, instructions, memory model)
- Generate clean git-style diffs (+/- format)
- Preserve hypervisor logic, only change arch bits
- Comment complex ARM changes

Output format: Git diff with context lines."""
    
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute code migration task
        
        Args:
            task: {
                'id': str,
                'conversation_id': str,
                'description': str (e.g., "Port arch/x86/traps.c"),
                'file_path': str,
                'code_snippet': str (optional)
            }
        
        Returns:
            {
                'task_id': str,
                'output': {'diff': str, 'summary': str},
                'status': 'completed' | 'failed'
            }
        """
        try:
            # 1. Get RAG context from PostgreSQL
            context = await self._get_rag_context(
                task['conversation_id'], 
                'hypervisor_code'
            )
            
            # 2. Build prompt
            user_prompt = f"""
Task: {task['description']}
File: {task.get('file_path', 'N/A')}

Relevant context (from previous work):
{context}

Code to migrate:
```c
{task.get('code_snippet', task['description'])}
```

Generate:
1. ARM64 diff
2. Brief summary of key changes
"""
            
            # 3. Call Grok via OpenRouter
            response = await self.client.chat_completion(
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                model=self.model,
                max_tokens=8192,  # Large diffs
                temperature=0.3  # Precise code
            )
            
            diff_output = response.choices[0].message.content
            
            # 4. Store artifact in DB
            await self._store_artifact(
                task['conversation_id'],
                diff_output,
                task.get('file_path', 'generated')
            )
            
            # 5. Extract summary (simple parse)
            summary = self._extract_summary(diff_output)
            
            return {
                "task_id": task['id'],
                "output": {
                    "diff": diff_output,
                    "summary": summary
                },
                "status": "completed"
            }
            
        except Exception as e:
            print(f"❌ Code Agent error: {e}")
            return {
                "task_id": task['id'],
                "output": {"error": str(e)},
                "status": "failed"
            }
    
    async def _get_rag_context(self, conversation_id: str, type_filter: str) -> str:
        """Query PostgreSQL for relevant memories (RAG)"""
        if not DB_AVAILABLE:
            return "Database not configured - using fresh context."
        
        try:
            conn = psycopg2.connect(os.getenv('DATABASE_URL'))
            cur = conn.cursor(cursor_factory=RealDictCursor)
            
            # Get recent memories related to hypervisor code
            cur.execute("""
                SELECT content, memory_type 
                FROM agent_memory 
                WHERE conversation_id = %s 
                  AND memory_type ILIKE %s
                ORDER BY created_at DESC 
                LIMIT 5
            """, (conversation_id, f'%{type_filter}%'))
            
            memories = cur.fetchall()
            cur.close()
            conn.close()
            
            if not memories:
                return "No previous context available."
            
            context_parts = [
                f"[{mem['memory_type']}]: {mem['content']}" 
                for mem in memories
            ]
            return "\n\n".join(context_parts)
            
        except Exception as e:
            print(f"⚠️ RAG context fetch failed: {e}")
            return "Context unavailable."
    
    async def _store_artifact(self, conversation_id: str, content: str, file_path: str):
        """Store generated code artifact in PostgreSQL"""
        if not DB_AVAILABLE:
            print(f"⚠️ Database not available - artifact not persisted: {file_path}")
            return
        
        try:
            conn = psycopg2.connect(os.getenv('DATABASE_URL'))
            cur = conn.cursor()
            
            cur.execute("""
                INSERT INTO code_artifacts (conversation_id, file_path, content, artifact_type)
                VALUES (%s, %s, %s, %s)
            """, (conversation_id, file_path, content, 'diff'))
            
            conn.commit()
            cur.close()
            conn.close()
            
            print(f"✅ Stored artifact: {file_path}")
            
        except Exception as e:
            print(f"⚠️ Artifact storage failed: {e}")
    
    def _extract_summary(self, diff_output: str) -> str:
        """Extract summary from diff (simple heuristic)"""
        lines = diff_output.split('\n')
        
        # Look for summary lines (agent usually adds context)
        summary_lines = [
            line for line in lines[:10] 
            if not line.startswith(('diff', '---', '+++', '@@'))
        ]
        
        if summary_lines:
            return ' '.join(summary_lines[:3])
        
        return "Code migration diff generated"
