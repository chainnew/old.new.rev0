import json
import requests
import os
from dotenv import load_dotenv

load_dotenv()

# Config from .env
API_KEY = os.getenv('XAI_API_KEY')
ENDPOINT = os.getenv('XAI_API_ENDPOINT')
MODEL = os.getenv('XAI_MODEL')

# Load your enriched data (single entry; for array, adjust below)
with open('enriched_entry.json', 'r') as f:
    data = json.load(f)

def grok_chat(messages, max_tokens=500, temperature=0.7):
    """Helper: Send to Grok API, return full response for usage logging."""
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
    response = requests.post(ENDPOINT, json=payload, headers=headers)
    if response.status_code == 200:
        full_resp = response.json()
        content = full_resp['choices'][0]['message']['content']
        usage = full_resp.get('usage', {})
        print(f"Tokens used: {usage}")  # Log for monitoring
        return content
    else:
        raise ValueError(f"Grok API error: {response.status_code} - {response.text}")

def fetch_github_dir(repo, dir_path):
    """Tool: Fetch GitHub dir contents (recursive tree for depth)."""
    url = f"https://api.github.com/repos/{repo}/git/trees/main?recursive=1"
    resp = requests.get(url)
    if resp.status_code == 200:
        return resp.json()
    return {"error": f"Fetch failed: {resp.status_code}"}

# Agent loop: Plan → Act → Synthesize (Grok handles reasoning)
def run_grok_agent(goal, data):
    # Step 1: Plan with Grok (reason over JSON data)
    system_msg = "You are Grok, an expert agent for GitHub theme/system design analysis. Use structured reasoning and output JSON where specified."
    user_msg = f"""
    Data: {json.dumps(data, indent=2)}  # Enriched repo entry
    Goal: {goal}
    
    Step-by-step plan (output as structured JSON):
    1. Analyze files/diagrams for system design patterns.
    2. Act: Simulate fetching diagrams dir (use provided data or tool).
    3. Output: JSON with resources summary, a Mermaid stencil (e.g., for URL shortener), and recs.
    """
    messages = [
        {"role": "system", "content": system_msg},
        {"role": "user", "content": user_msg}
    ]
    plan = grok_chat(messages, max_tokens=400)
    print("\nGrok's Plan:\n", plan)
    
    # Step 2: Act (fetch diagrams if needed; fallback to data)
    repo = data['full_name']
    fetch_result = fetch_github_dir(repo, 'diagrams')  # This returns full tree; filter for 'diagrams'
    if 'error' in fetch_result:
        # Fallback: Use JSON data
        diagrams_entry = next((f for f in data['files'] if f['name'] == 'diagrams'), None)
        if diagrams_entry is None:
            diagrams_data = []
        else:
            diagrams_data = [diagrams_entry]  # Wrap as list
    else:
        # From live fetch: Extract subtree for 'diagrams' (filter tree by path)
        tree_items = fetch_result.get('tree', [])
        diagrams_data = [item for item in tree_items if item['path'].startswith('diagrams/')]
    
    # Safely get top 5 items as list (handle dict/list/empty)
    if isinstance(diagrams_data, list):
        items = diagrams_data[:5]
    elif isinstance(diagrams_data, dict):
        if 'tree' in diagrams_data:
            items = diagrams_data['tree'][:5]
        else:
            items = []
    else:
        items = []  # Ultimate fallback
    
    print(f"\nFetched diagrams items: {len(items)} (top 5 preview: {json.dumps(items[:3], indent=2)})")  # Debug
    
    # Step 3: Synthesize with Grok
    synth_msg = f"""
    Plan: {plan}
    Fetched diagrams: {json.dumps(items, indent=2)}  # Top 5 items
    Goal continues: {goal}. Extract 3 key resources from README/contents. Generate Mermaid for a load balancer pattern (keep it simple, 10-15 lines).
    Output strictly as JSON: {{"resources": [{{"type": "...", "name": "...", "description": "...", "why": "..."}}], "mermaid_code": "graph ...", "recommendation": "..."}}.
    """
    messages.append({"role": "assistant", "content": plan})
    messages.append({"role": "user", "content": synth_msg})
    output = grok_chat(messages, max_tokens=600)
    
    # Parse JSON from output
    try:
        result = json.loads(output)
    except json.JSONDecodeError:
        result = {"raw_output": output, "note": "Grok output was text; manual parsing suggested."}
    
    return result

# Demo run
if __name__ == "__main__":
    goal = "Analyze this awesome system design repo for interview prep: Summarize resources and generate a diagram stencil."
    result = run_grok_agent(goal, data)
    print("\nGrok Agent Output:\n", json.dumps(result, indent=2))
    
    # Optional: Batch mode for full themes (uncomment to run over super_themes.json)
    # with open('super_themes.json', 'r') as f:
    #     themes = json.load(f)
    # results = []
    # for theme in themes[:3]:  # Test first 3; remove [:3] for all
    #     if 'system' in (theme.get('description', '') + theme.get('ai_description', '')).lower():
    #         res = run_grok_agent("Quick pattern analysis", theme)
    #         results.append({"theme": theme['full_name'], "result": res})
    # with open('batch_results.json', 'w') as f:
    #     json.dump(results, f, indent=2)
    # print("Batch complete: See batch_results.json")
