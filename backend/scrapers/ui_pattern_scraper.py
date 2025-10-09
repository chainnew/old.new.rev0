"""
UI Pattern Scraper - Collects production-quality UI components and patterns
Scrapes: shadcn/ui, DaisyUI, Tailwind UI, and design inspiration sites
"""
import asyncio
import aiohttp
import sqlite3
import json
import hashlib
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import re
from bs4 import BeautifulSoup
import base64

class UIPatternScraper:
    """
    Scrapes production UI patterns from multiple sources.
    Extracts code, screenshots, and metadata.
    """

    def __init__(self, db_path: str = "backend/data/ui_patterns.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.init_database()

    def init_database(self):
        """Create database schema for UI patterns."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ui_patterns (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                subcategory TEXT,
                code_tsx TEXT,
                code_css TEXT,
                code_html TEXT,
                screenshot_url TEXT,
                live_demo_url TEXT,
                tags TEXT,  -- JSON array
                framework TEXT,  -- react, vue, svelte
                styling TEXT,  -- tailwind, css, styled-components
                dependencies TEXT,  -- JSON array
                quality_score INTEGER DEFAULT 0,
                accessibility_score INTEGER DEFAULT 0,
                responsive BOOLEAN DEFAULT 1,
                dark_mode BOOLEAN DEFAULT 0,
                source_url TEXT,
                source_repo TEXT,
                used_in_production BOOLEAN DEFAULT 0,
                production_sites TEXT,  -- JSON array
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS scrape_jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_name TEXT NOT NULL,
                source_url TEXT NOT NULL,
                status TEXT DEFAULT 'pending',  -- pending, running, completed, failed
                patterns_extracted INTEGER DEFAULT 0,
                started_at TIMESTAMP,
                completed_at TIMESTAMP,
                error_message TEXT
            )
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_category ON ui_patterns(category)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_quality ON ui_patterns(quality_score DESC)
        """)

        conn.commit()
        conn.close()

    async def scrape_shadcn_ui(self) -> List[Dict[str, Any]]:
        """
        Scrape shadcn/ui examples and components.
        Target: https://ui.shadcn.com/examples
        """
        patterns = []

        # shadcn/ui example pages
        examples = [
            {
                "name": "Dashboard",
                "url": "https://ui.shadcn.com/examples/dashboard",
                "category": "dashboard",
                "tags": ["analytics", "charts", "cards", "modern"]
            },
            {
                "name": "Cards",
                "url": "https://ui.shadcn.com/examples/cards",
                "category": "components",
                "subcategory": "cards",
                "tags": ["card", "container", "layout"]
            },
            {
                "name": "Forms",
                "url": "https://ui.shadcn.com/examples/forms",
                "category": "forms",
                "tags": ["form", "input", "validation"]
            },
            {
                "name": "Authentication",
                "url": "https://ui.shadcn.com/examples/authentication",
                "category": "auth",
                "tags": ["login", "signup", "form"]
            },
            {
                "name": "Music",
                "url": "https://ui.shadcn.com/examples/music",
                "category": "complex",
                "tags": ["sidebar", "navigation", "player"]
            }
        ]

        print(f"🎨 Scraping shadcn/ui examples...")

        for example in examples:
            try:
                # For now, we'll use the GitHub source
                github_url = f"https://raw.githubusercontent.com/shadcn-ui/ui/main/apps/www/app/examples/{example['name'].lower()}/page.tsx"

                async with aiohttp.ClientSession() as session:
                    async with session.get(github_url, timeout=10) as response:
                        if response.status == 200:
                            code = await response.text()

                            pattern = {
                                "id": hashlib.md5(f"shadcn-{example['name']}".encode()).hexdigest(),
                                "name": f"shadcn/ui - {example['name']}",
                                "category": example["category"],
                                "subcategory": example.get("subcategory", ""),
                                "code_tsx": code,
                                "tags": json.dumps(example["tags"]),
                                "framework": "react",
                                "styling": "tailwind",
                                "dependencies": json.dumps(["@radix-ui/react", "class-variance-authority", "lucide-react"]),
                                "source_url": example["url"],
                                "source_repo": "shadcn-ui/ui",
                                "used_in_production": True,
                                "production_sites": json.dumps(["ui.shadcn.com", "vercel.com"])
                            }

                            patterns.append(pattern)
                            print(f"  ✅ Extracted: {pattern['name']}")

            except Exception as e:
                print(f"  ❌ Failed to scrape {example['name']}: {e}")

        return patterns

    async def scrape_github_components(self, repo: str) -> List[Dict[str, Any]]:
        """
        Scrape components from a GitHub repository.

        Args:
            repo: GitHub repo in format "owner/repo"

        Returns:
            List of extracted component patterns
        """
        patterns = []

        try:
            # Get file tree from GitHub API
            api_url = f"https://api.github.com/repos/{repo}/git/trees/main?recursive=1"

            async with aiohttp.ClientSession() as session:
                async with session.get(api_url, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()

                        # Find component files
                        component_files = [
                            f for f in data.get("tree", [])
                            if f["path"].startswith(("components/", "src/components/"))
                            and f["path"].endswith((".tsx", ".jsx", ".vue", ".svelte"))
                        ]

                        print(f"📦 Found {len(component_files)} component files in {repo}")

                        # Extract up to 20 components
                        for file in component_files[:20]:
                            try:
                                raw_url = f"https://raw.githubusercontent.com/{repo}/main/{file['path']}"

                                async with session.get(raw_url, timeout=10) as file_response:
                                    if file_response.status == 200:
                                        code = await file_response.text()

                                        # Extract component name
                                        component_name = Path(file["path"]).stem

                                        # Detect framework
                                        framework = "react"
                                        if file["path"].endswith(".vue"):
                                            framework = "vue"
                                        elif file["path"].endswith(".svelte"):
                                            framework = "svelte"

                                        pattern = {
                                            "id": hashlib.md5(f"{repo}-{file['path']}".encode()).hexdigest(),
                                            "name": f"{repo.split('/')[1]} - {component_name}",
                                            "category": self._detect_category(component_name, code),
                                            "code_tsx": code if framework == "react" else "",
                                            "code_html": code if framework != "react" else "",
                                            "tags": json.dumps(self._extract_tags(component_name, code)),
                                            "framework": framework,
                                            "styling": self._detect_styling(code),
                                            "dependencies": json.dumps(self._extract_dependencies(code)),
                                            "source_url": f"https://github.com/{repo}/blob/main/{file['path']}",
                                            "source_repo": repo
                                        }

                                        patterns.append(pattern)
                                        print(f"  ✅ {component_name}")

                            except Exception as e:
                                print(f"  ⚠️ Failed to extract {file['path']}: {e}")

        except Exception as e:
            print(f"❌ Failed to scrape {repo}: {e}")

        return patterns

    def _detect_category(self, name: str, code: str) -> str:
        """Detect component category from name and code."""
        name_lower = name.lower()
        code_lower = code.lower()

        # Category detection logic
        if any(word in name_lower for word in ["button", "btn"]):
            return "buttons"
        elif any(word in name_lower for word in ["card", "panel"]):
            return "cards"
        elif any(word in name_lower for word in ["nav", "menu", "sidebar"]):
            return "navigation"
        elif any(word in name_lower for word in ["form", "input", "field"]):
            return "forms"
        elif any(word in name_lower for word in ["modal", "dialog"]):
            return "modals"
        elif any(word in name_lower for word in ["table", "grid", "list"]):
            return "data_display"
        elif any(word in name_lower for word in ["hero", "header"]):
            return "hero_sections"
        elif any(word in name_lower for word in ["dashboard"]):
            return "dashboards"
        else:
            return "other"

    def _extract_tags(self, name: str, code: str) -> List[str]:
        """Extract relevant tags from component."""
        tags = []

        # Add name-based tags
        name_words = re.findall(r'[A-Z][a-z]+', name)
        tags.extend([w.lower() for w in name_words])

        # Add feature tags
        if "className" in code or "class:" in code:
            if "dark:" in code:
                tags.append("dark-mode")
            if "md:" in code or "lg:" in code:
                tags.append("responsive")
            if "animate-" in code or "transition-" in code:
                tags.append("animated")

        return list(set(tags))

    def _detect_styling(self, code: str) -> str:
        """Detect styling approach."""
        if "className" in code and ("bg-" in code or "text-" in code):
            return "tailwind"
        elif "styled" in code or "css`" in code:
            return "styled-components"
        elif "<style" in code:
            return "css"
        else:
            return "unknown"

    def _extract_dependencies(self, code: str) -> List[str]:
        """Extract import dependencies."""
        deps = []

        # Find import statements
        imports = re.findall(r'from ["\']([^"\']+)["\']', code)
        deps.extend([imp for imp in imports if not imp.startswith((".", "/"))])

        return list(set(deps))[:10]  # Limit to 10 deps

    def save_patterns(self, patterns: List[Dict[str, Any]]):
        """Save extracted patterns to database."""
        if not patterns:
            print("⚠️  No patterns to save")
            return

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        for pattern in patterns:
            cursor.execute("""
                INSERT OR REPLACE INTO ui_patterns (
                    id, name, category, subcategory, code_tsx, code_html,
                    tags, framework, styling, dependencies, source_url,
                    source_repo, used_in_production, production_sites
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                pattern.get("id"),
                pattern.get("name"),
                pattern.get("category"),
                pattern.get("subcategory", ""),
                pattern.get("code_tsx"),
                pattern.get("code_html"),
                pattern.get("tags"),
                pattern.get("framework"),
                pattern.get("styling"),
                pattern.get("dependencies"),
                pattern.get("source_url"),
                pattern.get("source_repo"),
                pattern.get("used_in_production", False),
                pattern.get("production_sites")
            ))

        conn.commit()
        conn.close()

        print(f"💾 Saved {len(patterns)} patterns to database")

    async def run_scraping_job(self, sources: List[str] = None):
        """
        Run complete scraping job.

        Args:
            sources: List of source repos to scrape (default: top repos)
        """
        if sources is None:
            # Default: Our top UI repos from ui_catalog
            sources = [
                "shadcn-ui/ui",
                "saadeghi/daisyui",
                "magicuidesign/magicui",
                "tremorlabs/tremor",
                "unovue/shadcn-vue"
            ]

        all_patterns = []

        print(f"\n🚀 Starting UI pattern scraping job...")
        print(f"📋 Sources: {len(sources)}")

        # Scrape shadcn/ui first (special handling)
        shadcn_patterns = await self.scrape_shadcn_ui()
        all_patterns.extend(shadcn_patterns)

        # Scrape GitHub repos
        for repo in sources:
            if repo == "shadcn-ui/ui":
                continue  # Already scraped

            print(f"\n📦 Scraping {repo}...")
            patterns = await self.scrape_github_components(repo)
            all_patterns.extend(patterns)

            # Rate limiting
            await asyncio.sleep(1)

        # Save all patterns
        self.save_patterns(all_patterns)

        print(f"\n✅ Scraping complete! Extracted {len(all_patterns)} patterns")

        return all_patterns


async def main():
    """Run scraping job."""
    import os
    os.chdir("/Users/matto/Documents/AI CHAT/my-app")

    scraper = UIPatternScraper()

    # Run scraping
    patterns = await scraper.run_scraping_job()

    print(f"\n📊 Summary:")
    print(f"   Total patterns: {len(patterns)}")

    # Count by category
    categories = {}
    for p in patterns:
        cat = p.get("category", "unknown")
        categories[cat] = categories.get(cat, 0) + 1

    print(f"\n   By category:")
    for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
        print(f"     {cat}: {count}")


if __name__ == "__main__":
    asyncio.run(main())
