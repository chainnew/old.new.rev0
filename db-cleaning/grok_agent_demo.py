import json
import requests
import os
from dotenv import load_dotenv

load_dotenv()

# Config from .env
API_KEY = os.getenv('XAI_API_KEY')
ENDPOINT = os.getenv('XAI_API_ENDPOINT')
MODEL = os.getenv('XAI_MODEL')

# Load your enriched data
with open('enriched_entry.json', 'r') as f:  # Or 'super_themes.json' for full 142
    data = json.load(f)  # Single entry; for array, pick first: data = data[0]

def grok_chat(messages, max_tokens=500, temperature=0.7):
    """Helper: Send to Grok API."""
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
        return response.json()['choices'][0]['message']['content']
    else:
        raise ValueError(f"Grok API error: {response.status_code} - {response.text}")

def fetch_github_dir(repo, dir_path):
    """Tool: Fetch dir contents (reuse from before)."""
    url = f"https://api.github.com/repos/{repo}/git/trees/main?recursive=1"  # Recursive for depth
    # Or contents: f"https://api.github.com/repos/{repo}/contents/{dir_path}?ref=main"
    resp = requests.get(url)
    return resp.json() if resp.status_code == 200 else {"error": "Fetch failed"}

# Agent loop: Plan → Act → Synthesize (Grok handles reasoning)
def run_grok_agent(goal, data):
    # Step 1: Plan with Grok (reason over JSON data)
    system_msg = "You are Grok, an expert agent for GitHub theme/system design analysis. Use structured reasoning."
    user_msg = f"""
    Data: {json.dumps(data, indent=2)}  # Enriched repo entry
    Goal: {goal}
    
    Step-by-step plan:
    1. Analyze files/diagrams for system design patterns.
    2. Act: Simulate fetching diagrams dir (use provided data or tool).
    3. Output: JSON with resources summary, a Mermaid stencil (e.g., for URL shortener), and recs.
    """
    messages = [
        {"role": "system", "content": system_msg},
        {"role": "user", "content": user_msg}
    ]
    plan = grok_chat(messages, max_tokens=300)
    print("Grok's Plan:\n", plan)
    
    # Step 2: Act (fetch diagrams if needed; fallback to data)
    repo = data['full_name']
    diagrams_data = fetch_github_dir(repo, 'diagrams')
    if 'error' in diagrams_data:
        diagrams_data = next((f for f in data['files'] if f['name'] == 'diagrams'), {})  # From JSON
    
    # Step 3: Synthesize with Grok
    synth_msg = f"""
    Plan: {plan}
    Fetched diagrams: {json.dumps(diagrams_data[:5], indent=2)}  # Top 5 items
    Goal continues: {goal}. Extract 3 key resources from README/contents. Generate Mermaid for a load balancer pattern.
    Output strictly as JSON: {{"resources": [{{...}}], "mermaid_code": "...", "recommendation": "..."}}.
    """
    messages.append({"role": "assistant", "content": plan})
    messages.append({"role": "user", "content": synth_msg})
    output = grok_chat(messages, max_tokens=400)
    
    # Parse JSON from output
    try:
        result = json.loads(output)
    except json.JSONDecodeError:
        result = {"raw_output": output, "note": "Non-JSON; manual parse needed"}
    
    return result

# Demo
goal = "Analyze this awesome system design repo for interview prep: Summarize resources and generate a diagram stencil."
result = run_grok_agent(goal, data)
print("\nGrok Agent Output:\n", json.dumps(result, indent=2))

