import json
import requests
import time
import os
from dotenv import load_dotenv
from improved_grok_agent import run_grok_agent  # Import the improved agent (or copy-paste if running standalone)
from functools import lru_cache

load_dotenv()
GITHUB_HEADERS = {'Authorization': f'token {os.getenv("GITHUB_TOKEN", "")}'} if os.getenv('GITHUB_TOKEN') else {}

# Your repo list (GitHub only)
REPO_LIST = [
    "shadcn-ui/ui", "tailwindlabs/tailwindcss", "saadeghi/daisyui", "aceternity/ui", "magicuidesign/magicui",
    "yeun/open-color", "colorhunt/colorhunt", "coolors/coolors-palette-generator", "flatuicolors/flatuicolors",
    "markmead/hyperui", "themesberg/flowbite", "merakiui/merakiui", "tremorlabs/tremor",
    "cruip/open-react-template", "vercel/next.js", "goabstract/Awesome-Design-Tools",
    "bradtraversy/design-resources-for-developers", "ripienaar/free-for-dev",
    "lucide-icons/lucide", "tailwindlabs/heroicons", "tabler/tabler-icons", "framer/motion"
    # Add more from your list; vercel/next.js examples are in /examples subtree
]

@lru_cache(maxsize=50)
def scrape_repo(repo, target_paths=['components', 'styles', 'css', 'ui', 'src', 'examples']):
    """Scrape repo: Description, stars, filtered tree contents."""
    # Repo info
    info_url = f"https://api.github.com/repos/{repo}"
    resp = requests.get(info_url, headers=GITHUB_HEADERS)
    if resp.status_code != 200:
        return {"error": f"Repo fetch failed: {resp.status_code}"}
    
    info = resp.json()
    stars = info.get('stargazers_count', 0)
    desc = info.get('description', '')
    
    # Tree (recursive, filter for UI paths)
    tree_url = f"https://api.github.com/repos/{repo}/git/trees/main?recursive=1"
    tree_resp = requests.get(tree_url, headers=GITHUB_HEADERS)
    tree = tree_resp.json() if tree_resp.status_code == 200 else {"error": "Tree fetch failed"}
    
    contents = []
    if 'tree' in tree:
        for item in tree['tree']:
            path_lower = item['path'].lower()
            if any(target in path_lower for target in target_paths) and item['type'] == 'blob':  # Files only
                contents.append({
                    "path": item['path'],
                    "name": item['path'].split('/')[-1],
                    "type": item['type'],
                    "url": item.get('url', '')  # Raw content URL if needed
                })
    
    return {
        "full_name": repo,
        "description": desc,
        "stars": stars,
        "contents": contents[:50],  # Limit to top 50 UI files
        "url": f"https://github.com/{repo}"
    }

def main(batch_size=5, sleep_time=2):
    """Scrape repos, then analyze with Grok."""
    raw_data = []
    for i, repo in enumerate(REPO_LIST):
        print(f"Scraping {repo} ({i+1}/{len(REPO_LIST)})")
        entry = scrape_repo(repo)
        if 'error' not in entry:
            raw_data.append(entry)
        time.sleep(sleep_time)  # Rate limit
    
    # Save raw scrape (like your export)
    with open('ui_raw_scrape.json', 'w') as f:
        json.dump(raw_data, f, indent=2)
    print(f"Scraped {len(raw_data)} repos to ui_raw_scrape.json")
    
    # Enrich with Grok (batch in chunks to avoid token overload)
    goal = "Extract UI/Tailwind components, color palettes, and generate a stencil (HTML or Mermaid for web patterns)."
    enriched_results = []
    for i in range(0, len(raw_data), batch_size):
        chunk = raw_data[i:i+batch_size]
        chunk_results = run_grok_agent(goal, chunk)
        enriched_results.extend(chunk_results)
        time.sleep(5)  # Grok cooldown
    
    # Save enriched
    with open('ui_grok_enriched.json', 'w') as f:
        json.dump(enriched_results, f, indent=2)
    print("Enrichment complete: ui_grok_enriched.json (includes stencils, components, recs).")

if __name__ == "__main__":
    main(batch_size=3)  # Start small; increase for full run

