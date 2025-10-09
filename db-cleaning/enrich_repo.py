import requests
import json
import sys
import argparse

def fetch_github_contents(repo, ref='main'):
    """Fetch full root contents from GitHub API."""
    url = f"https://api.github.com/repos/{repo}/contents?ref={ref}"
    headers = {'Accept': 'application/vnd.github.v3+json'}  # Rate limit friendly
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching contents: {response.status_code}")
        return []

def fetch_file_content(download_url):
    """Download raw file content (e.g., README)."""
    if not download_url:
        return ""
    response = requests.get(download_url)
    return response.text if response.status_code == 200 else ""

def enrich_entry(base_data, api_key=None):  # base_data is your sample dict
    """Enrich with live data."""
    if api_key:
        headers = {'Authorization': f'token {api_key}'}
    else:
        headers = {}
    
    contents = fetch_github_contents(base_data['full_name'])
    base_data['files'] = contents  # Update with fresh API data
    
    # Extract README if present
    readme_file = next((f for f in contents if f['name'] == 'README.md'), None)
    if readme_file:
        base_data['readme'] = fetch_file_content(readme_file['download_url'])
    
    # Example AI-like enrichment: Score based on stars + size, add patterns
    base_data['ui_mods_score'] = min(100, base_data['stars'] / 1000 + len(contents) * 0.5)  # Simple formula
    base_data['stencil_patterns'].append({
        "name": "Resource Curator Pattern",
        "description": "Awesome list structure for aggregating free learning resources.",
        "code_snippet": "Use Markdown links to organize: ## Books\n- [Grokking...](url)",
        "framework": "documentation"
    })
    
    # Live stars update (from repo API)
    repo_url = f"https://api.github.com/repos/{base_data['full_name']}"
    repo_resp = requests.get(repo_url, headers=headers)
    if repo_resp.status_code == 200:
        base_data['stars'] = repo_resp.json()['stargazers_count']
    
    base_data['last_enriched'] = '2025-10-07'  # Or datetime.now().isoformat()
    return base_data

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--repo', default='ashishps1/awesome-system-design-resources')
    parser.add_argument('--api_key', help='GitHub token for higher rate limits')
    parser.add_argument('--output', default='enriched_entry.json')
    args = parser.parse_args()
    
    # Your sample as base (paste the dict here or load from file)
    sample_data = {  # From your message
        "full_name": args.repo,  # Or "repo" if using old key
        "description": "Learn System Design concepts and prepare for interviews using free resources.",
        "stars": 26558,
        "files": [],  # Will be populated
        "readme": "",
        "images": [],
        "category": "system-design",
        "ai_description": "Curated free resources for system design interviews.",
        "ui_mods_score": 0.0,
        "stencil_patterns": [],
        "tweaked_variants": [],
        "processing_status": "enriched",
        "github_url": f"https://github.com/{args.repo}"
    }
    
    enriched = enrich_entry(sample_data, args.api_key)
    with open(args.output, 'w') as f:
        json.dump(enriched, f, indent=2, ensure_ascii=False)
    print(f"Enriched {args.repo} saved to {args.output}. Stars now: {enriched['stars']}")
