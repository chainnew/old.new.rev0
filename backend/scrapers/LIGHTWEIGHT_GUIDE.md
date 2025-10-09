# ⚡ Lightweight UI Scraper - Zero Cost, Maximum Speed

## Why This Version?

**The Problem:**
- AI reasoning is expensive ($$$)
- Embeddings cost money
- Screenshot generation is slow

**The Solution:**
This lightweight scraper uses:
- ✅ **Pure regex** - No AI models
- ✅ **Simple pattern matching** - Deterministic categorization
- ✅ **Fast async requests** - Concurrent downloads
- ✅ **Minimal processing** - Store code, detect features with regex

**Cost: $0.00** (just GitHub API rate limits)

---

## What It Does

### **Scrapes 12 Repos:**
1. shadcn-ui/ui → 50 components
2. saadeghi/daisyui → 40 components
3. tremorlabs/tremor → 50 components
4. magicuidesign/magicui → 30 components
5. radix-ui/primitives → 30 components
6. tailwindlabs/headlessui → 15 components
7. unovue/shadcn-vue → 40 components
8. huntabyte/shadcn-svelte → 35 components
9. pure-admin/vue-pure-admin → 30 components
10. xyflow/xyflow → 15 components
11. vercel/commerce → 25 components
12. vercel/ai-chatbot → 15 components

**Expected Total: ~375 components in ~10-15 minutes**

### **Extracts (NO AI):**
```python
{
    "id": "abc123",
    "name": "Button",
    "category": "buttons",  # Simple keyword matching
    "code": "export function Button() { ... }",
    "framework": "react-ts",

    # Simple regex checks (NOT AI)
    "has_typescript": true,   # Check for ": string"
    "has_tailwind": true,     # Check for "bg-" "text-"
    "has_props": true,        # Check for "{...}"
    "is_responsive": true,    # Check for "sm:" "md:"
    "has_dark_mode": true,    # Check for "dark:"
    "has_animation": false,   # Check for "animate-"

    "repo": "shadcn-ui/ui",
    "github_url": "https://github.com/..."
}
```

---

## Usage

### **Basic Run (No Setup):**

```bash
# Install dependencies (one-time)
pip install aiohttp

# Run scraper
cd "/Users/matto/Documents/AI CHAT/my-app"
python3 backend/scrapers/lightweight_ui_scraper.py

# Expected:
# 🚀 Scraping 12 repos...
# 📦 shadcn-ui/ui
#    📄 Found 120 files
#    ✅ 10/50
#    ✅ 20/50
#    ...
#    💾 Saved 50 components
# ...
# ✅ SCRAPING COMPLETE!
# ⏱️  Duration: 582.3s (~10 min)
# 💾 Components: 375
```

### **With GitHub Token (Higher Rate Limits):**

```bash
# Get token: https://github.com/settings/tokens
# (No scopes needed, just basic read access)

export GITHUB_TOKEN="ghp_YOUR_TOKEN_HERE"
python3 backend/scrapers/lightweight_ui_scraper.py

# Increases rate limit:
# Without token: 60 requests/hour
# With token: 5,000 requests/hour
```

---

## Output

### **Database: `backend/data/ui_components.db`**

**Schema:**
```sql
components:
  - id (unique hash)
  - name (e.g., "Button")
  - category (buttons, forms, navigation, etc.)
  - code (full source code)
  - framework (react-ts, vue, svelte)
  - file_size, line_count
  - has_typescript, has_tailwind, has_props
  - is_responsive, has_dark_mode, has_animation
  - repo, file_path, github_url
  - scraped_at (timestamp)
```

**Indexes:**
- category (fast category queries)
- framework (filter by React/Vue/Svelte)
- repo (see all components from one source)

---

## Simple Queries

### **Get All Buttons:**
```sql
SELECT name, framework, has_tailwind, github_url
FROM components
WHERE category = 'buttons'
LIMIT 10;
```

### **Get Responsive Dark Mode Components:**
```sql
SELECT name, category, repo
FROM components
WHERE is_responsive = 1 AND has_dark_mode = 1;
```

### **Get TypeScript React Components:**
```sql
SELECT name, category, github_url
FROM components
WHERE framework = 'react-ts' AND has_typescript = 1;
```

### **Count by Category:**
```sql
SELECT category, COUNT(*) as count
FROM components
GROUP BY category
ORDER BY count DESC;
```

---

## How It Works (No Magic)

### **1. Category Detection (Keyword Matching)**
```python
def detect_category(name: str, code: str) -> str:
    name_lower = name.lower()

    if 'button' in name_lower or 'btn' in name_lower:
        return 'buttons'
    elif 'input' in name_lower or 'form' in name_lower:
        return 'forms'
    # ... etc
```

### **2. Feature Detection (Regex)**
```python
def extract_features(code: str) -> dict:
    return {
        'has_typescript': bool(re.search(r':\s*(string|number)', code)),
        'has_tailwind': bool(re.search(r'bg-|text-|flex', code)),
        'is_responsive': bool(re.search(r'sm:|md:|lg:', code)),
        'has_dark_mode': 'dark:' in code,
        'has_animation': 'animate-' in code
    }
```

### **3. Framework Detection (File Extension)**
```python
def detect_framework(file_path: str) -> str:
    if file_path.endswith('.tsx'):
        return 'react-ts'
    elif file_path.endswith('.jsx'):
        return 'react-js'
    elif file_path.endswith('.vue'):
        return 'vue'
    # ...
```

**That's it! No AI, no models, no reasoning.**

---

## Comparison to Production Scraper

| Feature | Production Scraper | Lightweight Scraper |
|---------|-------------------|---------------------|
| **Repos** | 18 | 12 |
| **Components** | 500+ | 375 |
| **Speed** | ~30 min | **~10 min** ✅ |
| **AI/Reasoning** | Optional | **ZERO** ✅ |
| **Embeddings** | Optional | **ZERO** ✅ |
| **Screenshots** | Optional | **ZERO** ✅ |
| **Cost** | Low | **$0** ✅ |
| **Quality Scoring** | Advanced (4 metrics) | Simple (regex flags) |
| **Database Size** | Large (embeddings, etc.) | **Small** ✅ |

---

## When to Use Each

### **Use Lightweight Scraper When:**
- ✅ You want fast results
- ✅ You don't need quality scores
- ✅ Simple categorization is enough
- ✅ You're testing/prototyping
- ✅ You want zero cost

### **Use Production Scraper When:**
- You need quality scores (0-100)
- You want semantic search (later)
- You need screenshots
- You want advanced categorization
- Production deployment

---

## Cost Comparison

### **Lightweight Scraper:**
```
GitHub API calls: FREE (with token: 5,000/hour)
Processing: Pure Python regex (FREE)
Storage: SQLite (FREE)
Total: $0.00
```

### **With AI Reasoning (expensive):**
```
Grok-4-Fast-Reasoning: $5/1M tokens
375 components × 2,000 tokens each = 750K tokens
Cost: ~$3.75 per scrape
Monthly (daily scrapes): ~$112.50
```

### **With Embeddings (cheap but still costs):**
```
OpenAI text-embedding-3-small: $0.02/1M tokens
375 components × 500 tokens = 187K tokens
Cost: ~$0.004 per scrape
Monthly: ~$0.12 (basically free)
```

**Lightweight = $0.00** 🎉

---

## Next Steps

After scraping, you can:

### **1. Query the Database**
```bash
sqlite3 backend/data/ui_components.db
sqlite> SELECT COUNT(*) FROM components;
sqlite> SELECT * FROM components WHERE category='buttons' LIMIT 5;
```

### **2. Use in Agent Prompts**
```python
# Tell agents about the component database
prompt = f"""
You have access to {component_count} UI components:
- {button_count} buttons
- {form_count} forms
- {nav_count} navigation components

Query database: SELECT * FROM components WHERE category=?
"""
```

### **3. Build Simple Search API**
```python
@app.get("/api/components/search")
def search_components(category: str, framework: str):
    return db.query("""
        SELECT * FROM components
        WHERE category = ? AND framework = ?
        LIMIT 20
    """, (category, framework))
```

---

## Troubleshooting

### **Rate Limiting**
```
Error: API rate limit exceeded
```
**Solution:** Get GitHub token (free)
```bash
export GITHUB_TOKEN="ghp_..."
```

### **Slow Scraping**
Current: 1.5s between requests

**Speed it up:**
```python
# In lightweight_ui_scraper.py
config = ScrapingConfig(
    rate_limit=0.5  # Faster but riskier
)
```

### **Missing Dependencies**
```bash
pip install aiohttp
```

---

## Summary

**Lightweight Scraper:**
- ⚡ **Fast** - 10-15 minutes
- 💰 **Free** - $0.00 cost
- 🎯 **Simple** - No AI, just regex
- 📦 **375 components** from 12 repos
- 🔍 **Searchable** - SQLite with indexes
- ✅ **Production ready** - Use today

**Perfect for:**
- Testing the system
- Building proof-of-concept
- Avoiding AI costs
- Quick iterations

**Run it now:**
```bash
python3 backend/scrapers/lightweight_ui_scraper.py
```

🚀 Get 375 components in 10 minutes with ZERO cost!
