import json
import aiohttp
import asyncio
import random
import time
import os
from typing import List
from dotenv import load_dotenv
from improved_grok_agent_v2 import run_grok_agent_async  # Or copy in if standalone
from collections import defaultdict

load_dotenv()
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN', '')
GITHUB_SEARCH_URL = "https://api.github.com/search/repositories"

# Expanded repo list + dynamic search (e.g., for "tailwind ui" topics)
BASE_REPO_LIST = [
    "shadcn-ui/ui", "tailwindlabs/tailwindcss", "saadeghi/daisyui", "aceternity/ui", "magicuidesign/magicui",
    "yeun/open-color", "colorhunt/colorhunt", "coolors/coolors-palette-generator", "flatuicolors/flatuicolors",
    "markmead/hyperui", "themesberg/flowbite", "merakiui/merakiui", "tremorlabs/tremor",
    "cruip/open-react-template", "vercel/next.js", "goabstract/Awesome-Design-Tools",
    "bradtraversy/design-resources-for-developers", "ripienaar/free-for-dev",
    "lucide-icons/lucide", "tailwindlabs/heroicons", "tabler/tabler-icons", "framer/motion"
    # Add more; this covers your "list" focus
]

async def search_github_topics(session: aiohttp.ClientSession, query: str = "tailwind ui", max_results: int = 20, min_stars: int = 500) -> List[str]:
    """Dynamic repo discovery via GitHub search (topics + stars)."""
    params = {
        "q": f"{query} stars:>{min_stars}",
        "sort": "stars",
        "order": "desc",
        "per_page": 100
    }
    async with session.get(GITHUB_SEARCH_URL, params=params, headers={'Authorization': f'token {GITHUB_TOKEN}' if GITHUB_TOKEN else {}}) as resp:
        if resp.status == 200:
            data = await resp.json()
            repos = [item['full_name'] for item in data.get('items', [])[:max_results]]
            print(f"Found {len(repos)} repos via search: {query}")
            return repos
        return []

async def scrape_repo_async(session: aiohttp.ClientSession, repo: str, target_paths: List[str] = ['components', 'styles', 'css', 'ui', 'src', 'examples', 'icons'], max_files: int = 10) -> Dict:
    """Async scrape: Info + filtered tree + contents (v2: full fetch for top files)."""
    # Info (same as v1)
    info_url = f"https://api.github.com/repos/{repo}"
    async with session.get(info_url) as resp:
        if resp.status != 200:
            return {"error": f"Repo fetch failed: {resp.status}"}
        info = await resp.json()
        stars = info.get('stargazers_count', 0)
        desc = info.get('description', '')
    
    # Tree + contents (parallel fetch)
    tree_url = f"https://api.github.com/repos/{repo}/git/trees/main?recursive=1"
    async with session.get(tree_url) as tree_resp:
        tree = await tree_resp.json() if tree_resp.status == 200 else {"error": "Tree failed"}
    
    contents = []
    fetch_tasks = []
    if 'tree' in tree:
        for item in tree['tree']:
            if item['type'] == 'blob' and any(target in item['path'].lower() for target in target_paths):
                contents.append({
                    "path": item['path'],
                    "name": item['path'].split('/')[-1],
                    "type": "file",
                    "url": item.get('url', '')
                })
                if len(fetch_tasks) < max_files:  # Limit fetches
                    raw_url = f"https://raw.githubusercontent.com/{repo}/main/{item['path']}"
                    if len(item['path']) < 256 and item['path'].endswith(('.css', '.jsx', '.tsx', '.js', '.html', '.md')):  # UI focus
                        fetch_tasks.append(fetch_github_content_async(session, repo, item['path']))  # From v2 agent
        contents = contents[:max_files * 2]  # Paths buffer
    
    # Await fetches
    raw_contents = await asyncio.gather(*fetch_tasks, return_exceptions=True)
    content_map = {contents[i]['path']: raw_contents[i] for i in range(len(contents)) if isinstance(raw_contents[i], str) else None}
    
    return {
        "full_name": repo,
        "description": desc,
        "stars": stars,
        "contents": contents,  # Paths
        "raw_contents": content_map,  # Actual code
        "url": f"https://github.com/{repo}"
    }

async def curate_goods_library(results: List[Dict]) -> Dict:
    """Curate scraped results into a goods library (dedup/categorize)."""
    library = defaultdict(list)
    for res in results:
        if 'goods' in res:
            for good in res['goods']:
                good['source_repo'] = res['repo']
                lib_type = good['type']
                # Dedup: Simple hash for uniqueness
                key = f"{lib_type}:{good.get('name', '')}:{hash(good.get('code', '')) % 10000}"
                if key not in [g['key'] for g in library[lib_type]]:
                    good['key'] = key
                    library[lib_type].append(good)
    
    # Add stencils as separate cat
    stencils = [{"stencil": res.get('stencil_example'), "source": res['repo']} for res in results if res.get('stencil_example')]
    library['stencils'] = stencils[:20]  # Top 20
    
    return {"library": dict(library), "total_goods": sum(len(v) for v in library.values()), "recommendations": "Prioritize high-stars for Tailwind components."}

async def main_async(batch_size=5, search_query="tailwind ui components", search_limit=15, min_stars_search=1000):
    """Main: Search + Scrape + Analyze + Curate Goods."""
    connector = aiohttp.TCPConnector(limit=20)
    timeout = aiohttp.ClientTimeout(total=60)
    
    async with aiohttp.ClientSession(connector=connector, timeout=timeout, headers={'Authorization': f'token {GITHUB_TOKEN}' if GITHUB_TOKEN else {}}) as session:
        # Dynamic repos
        dynamic_repos = await search_github_topics(session, search_query, search_limit, min_stars_search)
        all_repos = BASE_REPO_LIST + dynamic_repos[:10]  # Blend base + new (dedup)
        all_repos = list(set(all_repos))[:30]  # Cap 30 total
        
        print(f"Total repos to scrape: {len(all_repos)} (base + search '{search_query}')")
        
        # Parallel scrape
        scrape_tasks = [scrape_repo_async(session, repo) for repo in all_repos]
        raw_data = await asyncio.gather(*scrape_tasks, return_exceptions=True)
        raw_data = [d for d in raw_data if isinstance(d, dict) and 'error' not in d]
        
        with open('ui_raw_scrape_v2.json', 'w') as f:
            json.dump(raw_data, f, indent=2)
        print(f"Scraped {len(raw_data)} repos to ui_raw_scrape_v2.json (with raw contents!)")
        
        # Enrich (batched)
        goal = "Extract reusable UI goods: Tailwind components (HTML/JSX), color palettes (CSS/JSON), stencils (Mermaid/HTML templates). Gen 4-6 per repo, focus on modern/shadcn-style."
        enriched_results = []
        for i in range(0, len(raw_data), batch_size):
            chunk = raw_data[i:i+batch_size]
            chunk_results = await run_grok_agent_async(goal, chunk)
            enriched_results.extend(chunk_results)
            await asyncio.sleep(5)  # Grok cooldown
        
        with open('ui_grok_enriched_v2.json', 'w') as f:
            json.dump(enriched_results, f, indent=2)
        
        # Curate library
        library = await curate_goods_library(enriched_results)
        with open('ui_goods_library.json', 'w') as f:
            json.dump(library, f, indent=2)
        print(f"Curated library: ui_goods_library.json ({library['total_goods']} goods across categories).")

if __name__ == "__main__":
    asyncio.run(main_async(batch_size=3, search_query="tailwind react ui", search_limit=10, min_stars_search=800))
