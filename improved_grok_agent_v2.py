import json
import aiohttp
import asyncio
import os
import time
from dotenv import load_dotenv
import logging
from functools import lru_cache
from typing import List, Dict, Any

load_dotenv()

# Config (same as before)
API_KEY = os.getenv('XAI_API_KEY')
ENDPOINT = os.getenv('XAI_API_ENDPOINT', 'https://api.x.ai/v1/chat/completions')  # Default Grok endpoint
MODEL = os.getenv('XAI_MODEL', 'grok-beta')  # Or grok-4-fast
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN', '')

# Logging (same)
logging.basicConfig(filename='grok_agent_log.txt', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

@lru_cache(maxsize=256)
async def grok_chat_async(session: aiohttp.ClientSession, messages: List[Dict], max_tokens=800, temperature=0.3, retries=5):
    """Async Grok chat with advanced retry (429/5xx) and token logging."""
    payload = {
        "model": MODEL,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature
    }
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    for attempt in range(retries):
        async with session.post(ENDPOINT, json=payload, headers=headers) as response:
            if response.status == 200:
                full_resp = await response.json()
                content = full_resp['choices'][0]['message']['content']
                usage = full_resp.get('usage', {})
                logging.info(f"Grok tokens: {usage} for goal: {messages[-1]['content'][:50]}...")
                print(f"Tokens used: {usage.get('total_tokens', 0)}")
                return content
            elif response.status == 429:
                wait = 2 ** attempt + random.uniform(0, 1)  # Jittered backoff
                logging.warning(f"Rate limit (attempt {attempt+1}): Wait {wait}s")
                await asyncio.sleep(wait)
            else:
                text = await response.text()
                logging.warning(f"Grok error (attempt {attempt+1}): {response.status} - {text[:100]}")
                if attempt == retries - 1:
                    raise ValueError(f"Grok API failed: {response.status} - {text}")
                await asyncio.sleep(2 ** attempt)
    return ""

async def fetch_github_content_async(session: aiohttp.ClientSession, repo: str, file_path: str) -> str:
    """Async fetch raw file content from GitHub."""
    url = f"https://raw.githubusercontent.com/{repo}/main/{file_path}"
    async with session.get(url) as resp:
        if resp.status == 200:
            return await resp.text()
        logging.warning(f"Content fetch failed for {repo}/{file_path}: {resp.status}")
        return ""

async def run_grok_agent_async(goal: str, data: List[Dict], target_dirs: List[str] = ['components', 'styles', 'css', 'ui', 'diagrams'], max_files_per_dir: int = 5) -> List[Dict]:
    """
    Async Grok UI analysis: Fetch contents, analyze for goods (components, stencils).
    
    Args:
        ... (same)
        target_dirs: Dirs to scrape contents from.
        max_files_per_dir: Limit files fetched (API-friendly).
    """
    if isinstance(data, dict):
        data = [data]
    results = []
    connector = aiohttp.TCPConnector(limit=10, limit_per_host=5)  # Concurrency
    timeout = aiohttp.ClientTimeout(total=30)
    
    async with aiohttp.ClientSession(connector=connector, timeout=timeout, headers={'Authorization': f'token {GITHUB_TOKEN}' if GITHUB_TOKEN else {}}) as session:
        for entry in data:
            repo = entry.get('full_name') or entry.get('repo')
            if not repo:
                logging.warning("Skipping entry: No repo name")
                continue
            
            # Step 1: Plan (same as v1, but async)
            system_msg = "You are Grok, UI/web dev expert. Extract goods: Tailwind components (HTML/JSX snippets), color palettes (JSON/CSS), stencils (Mermaid/HTML templates). Prioritize reusable, high-stars repos."
            user_msg = f"""
            Repo: {repo} | Stars: {entry.get('stars', 0)} | Desc: {entry.get('description', '')}
            Goal: {goal}
            
            Plan JSON: {{"steps": ["fetch UI files", "extract patterns", "gen 3-5 goods + stencil"]}}.
            Focus: Target dirs {target_dirs}. Limit to modern Tailwind/Shadcn/DaisyUI.
            """
            messages = [{"role": "system", "content": system_msg}, {"role": "user", "content": user_msg}]
            plan = await grok_chat_async(session, messages, max_tokens=300)
            print(f"\nGrok Plan for {repo}:\n{plan}")
            
            # Step 2: Act - Async fetch contents from target dirs (parallel)
            fetched_contents = {}
            fetch_tasks = []
            tree_data = await fetch_github_dir_tree_async(session, repo)  # See below helper
            if 'error' not in tree_data:
                for dir_path in target_dirs:
                    dir_files = [item for item in tree_data.get('tree', []) if item['path'].startswith(dir_path + '/') and item['type'] == 'blob']
                    dir_files = dir_files[:max_files_per_dir]  # Limit
                    for item in dir_files:
                        fetch_tasks.append(fetch_github_content_async(session, repo, item['path']))
                        fetched_contents[item['path']] = item['path']  # Placeholder
            if fetch_tasks:
                contents_list = await asyncio.gather(*fetch_tasks, return_exceptions=True)
                # Assign contents (simplified; zip with paths in prod)
                content_idx = 0
                for path in fetched_contents:
                    if content_idx < len(contents_list) and isinstance(contents_list[content_idx], str):
                        fetched_contents[path] = contents_list[content_idx]
                    content_idx += 1
            
            print(f"Fetched contents for {repo}: {len([c for c in fetched_contents.values() if isinstance(c, str)])} files")
            
            # Step 3: Synthesize (enhanced for goods)
            synth_msg = f"""
            Plan: {plan}
            Fetched UI contents (sample paths + content snippets): {json.dumps({k: v[:200] + '...' if isinstance(v, str) else v for k, v in list(fetched_contents.items())[:3]}, indent=2)}
            Goal: {goal}. Extract 4-6 goods: 
            - Components: Tailwind HTML/JSX (e.g., button, card).
            - Palettes: JSON/CSS vars (colors from .css).
            - Stencils: Mermaid flow or full HTML template (<30 lines).
            Output strict JSON: {{"goods": [{{"type": "component"|"palette"|"stencil", "name": "...", "code": "...", "why": "From shadcn/ui, accessible variant", "repo": "{repo}"}}], "recommendation": "Top picks for dashboard UI", "stencil_example": {{"type": "html"|"mermaid", "code": "..."}}}}.
            Ensure code is copy-paste ready (no external deps).
            """
            messages.append({"role": "assistant", "content": plan})
            messages.append({"role": "user", "content": synth_msg})
            output = await grok_chat_async(session, messages, max_tokens=1000)
            
            # Parse (enhanced: fallback to raw if not JSON)
            try:
                result = json.loads(output)
                result['repo'] = repo
                result['goods'] = result.get('goods', [])  # Ensure list
            except json.JSONDecodeError:
                result = {"raw_output": output, "note": "Non-JSON; manual review needed", "repo": repo, "goods": []}
            
            results.append(result)
            await asyncio.sleep(2)  # Rate buffer
    
    return results

# Helper: Async GitHub tree fetch (new for v2)
async def fetch_github_dir_tree_async(session: aiohttp.ClientSession, repo: str):
    url = f"https://api.github.com/repos/{repo}/git/trees/main?recursive=1"
    async with session.get(url) as resp:
        if resp.status == 200:
            return await resp.json()
        return {"error": f"Tree fetch failed: {resp.status}"}

# Main (async)
async def main_async(input_file='ui_raw_scrape.json', goal='Extract UI components and stencils for web dev library.'):
    with open(input_file, 'r') as f:
        data = json.load(f)
    results = await run_grok_agent_async(goal, data)
    
    output_file = input_file.replace('.json', '_enriched_v2.json')
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"v2 Enrichment complete: {output_file} (with full contents + categorized goods).")

if __name__ == "__main__":
    asyncio.run(main_async())
