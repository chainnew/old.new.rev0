import json
import requests
import os
from openai import OpenAI  # pip install openai
from dotenv import load_dotenv

load_dotenv()

# Load enriched data (or super_themes.json)
with open('enriched_entry.json', 'r') as f:  # Start with single; scale to full list
    data = json.load(f)

# OpenRouter client (supports grok-4-fast and other models)
client = OpenAI(
    api_key=os.getenv('OPENROUTER_API_KEY'),
    base_url="https://openrouter.ai/api/v1"
)
MODEL = os.getenv('OPENROUTER_MODEL', 'x-ai/grok-4-fast')  # x-ai/grok-4-fast, x-ai/grok-2-1212, openai/gpt-4-turbo, etc.

def agent_tool_fetch_dir(repo, dir_path):
    """Agent tool: Recursively fetch GitHub dir contents."""
    url = f"https://api.github.com/repos/{repo}/contents/{dir_path}?ref=main"
    resp = requests.get(url)
    if resp.status_code == 200:
        return resp.json()
    return {"error": resp.status_code}

# Agent reasoning loop (simple: plan → act → output)
def run_agent(goal):
    # Step 1: Plan (LLM reasons over data)
    plan_prompt = f"""
    You are an agent for system design prep using this repo data: {json.dumps(data, indent=2)}.
    Goal: {goal}
    
    Plan steps:
    - Filter: Focus on diagrams/implementations dirs.
    - Act: Use tools to fetch details (simulate with provided data).
    - Output: JSON with summaries, Mermaid code for a pattern (e.g., URL shortener), and resources.
    """
    plan_resp = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": plan_prompt}],
        temperature=0.3  # Precise
    )
    plan = plan_resp.choices[0].message.content
    print("Agent Plan:\n", plan)
    
    # Step 2: Act (tool calls)
    repo = data['full_name']
    diagrams = agent_tool_fetch_dir(repo, 'diagrams')  # Live fetch
    if not isinstance(diagrams, list):  # Handle error
        diagrams = [data['files'][2]]  # Fallback to your snippet
    
    # Step 3: Generate output (LLM synthesizes)
    act_prompt = f"""
    Based on plan and fetched diagrams: {json.dumps(diagrams[:3], indent=2)}, {goal}.
    Extract top 3 resources from README (assume: videos/books/implementations).
    Generate Mermaid stencil for URL shortener (load balancer + DB).
    Output as JSON: {{"resources": [...], "mermaid_code": "...", "recommendation": "..."}}.
    """
    output_resp = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": act_prompt}],
        temperature=0.5
    )
    output = json.loads(output_resp.choices[0].message.content)  # Assume JSON
    return output

# Demo goal
goal = "Prepare interview resources from this awesome list, including a diagram pattern."
result = run_agent(goal)
print("\nAgent Output:\n", json.dumps(result, indent=2))

# Example output snippet:
# {
#   "resources": [
#     {"type": "Book", "name": "Grokking the System Design Interview", "why": "Covers URL shortener basics"},
#     {"type": "Video", "name": "ByteByteGo YouTube series"},
#     {"type": "Implementation", "path": "implementations/url-shortener"}
#   ],
#   "mermaid_code": "graph TD\nA[Client] --> LB[Load Balancer]\nLB --> DB[Redis Cache]\nDB --> ShortDB[Database]",
#   "recommendation": "Start with videos for intuition, implement URL shortener using patterns from this repo."
# }
