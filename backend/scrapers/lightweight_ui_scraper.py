"""
Lightweight UI Component Scraper - Zero AI/Reasoning Required
Pure pattern matching and deterministic code extraction

NO EXPENSIVE OPERATIONS:
- No AI models
- No embeddings
- No reasoning
- No screenshot generation (optional, separate script)
Just fast, efficient scraping with regex and simple rules

Usage:
    python3 lightweight_ui_scraper.py
"""

import asyncio
import aiohttp
import sqlite3
import json
import hashlib
import re
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass
import time


@dataclass
class ScrapingConfig:
    """Simple configuration for scraping."""
    # Database
    db_path: str = "backend/data/ui_components.db"

    # GitHub API
    github_token: Optional[str] = None  # Set to increase rate limits
    timeout: int = 10
    rate_limit: float = 1.5  # Seconds between requests

    # Limits
    max_files_per_repo: int = 50
    min_file_size: int = 100
    max_file_size: int = 100000  # 100KB

    # File patterns
    component_extensions: List[str] = None
    exclude_patterns: List[str] = None

    def __post_init__(self):
        if self.component_extensions is None:
            self.component_extensions = ['.tsx', '.jsx', '.vue', '.svelte']
        if self.exclude_patterns is None:
            self.exclude_patterns = [
                '.test.', '.spec.', '.stories.',
                '__tests__', '__mocks__', 'node_modules'
            ]


class LightweightUIScraper:
    """
    Simple, fast UI component scraper.

    What it does:
    1. Fetches component files from GitHub repos
    2. Extracts basic metadata (NO AI)
    3. Stores in SQLite database
    4. Simple category detection (regex only)
    """

    def __init__(self, config: Optional[ScrapingConfig] = None):
        self.config = config or ScrapingConfig()
        self.db_path = Path(self.config.db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        self.stats = {
            "repos_scraped": 0,
            "files_processed": 0,
            "components_saved": 0,
            "errors": 0
        }

        self.init_database()

    def init_database(self):
        """Create simple database schema."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS components (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                category TEXT,

                -- Code
                code TEXT NOT NULL,
                framework TEXT NOT NULL,

                -- Simple metadata (NO AI)
                file_size INTEGER,
                line_count INTEGER,
                has_typescript BOOLEAN DEFAULT 0,
                has_tailwind BOOLEAN DEFAULT 0,
                has_props BOOLEAN DEFAULT 0,

                -- Simple feature flags
                is_responsive BOOLEAN DEFAULT 0,
                has_dark_mode BOOLEAN DEFAULT 0,
                has_animation BOOLEAN DEFAULT 0,

                -- Source
                repo TEXT NOT NULL,
                file_path TEXT NOT NULL,
                github_url TEXT,

                -- Timestamps
                scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Simple indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_category ON components(category)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_framework ON components(framework)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_repo ON components(repo)")

        conn.commit()
        conn.close()

    # ========================================================================
    # SCRAPING TARGETS - Simple list of repos
    # ========================================================================

    def get_repos_to_scrape(self) -> List[Dict[str, Any]]:
        """
        Simple list of repos to scrape.
        No complex priority system - just a flat list.
        """
        return [
            # Component Libraries (HIGH VALUE)
            {"repo": "shadcn-ui/ui", "paths": ["apps/www/registry/new-york"], "limit": 50},
            {"repo": "saadeghi/daisyui", "paths": ["src/components"], "limit": 40},
            {"repo": "tremorlabs/tremor", "paths": ["src/components"], "limit": 50},
            {"repo": "magicuidesign/magicui", "paths": ["registry/components"], "limit": 30},
            {"repo": "radix-ui/primitives", "paths": ["packages/react"], "limit": 30},

            # Specialized (MEDIUM VALUE)
            {"repo": "tailwindlabs/headlessui", "paths": ["packages/@headlessui-react/src/components"], "limit": 15},
            {"repo": "unovue/shadcn-vue", "paths": ["apps/www/src/lib/registry"], "limit": 40},
            {"repo": "huntabyte/shadcn-svelte", "paths": ["apps/www/src/lib/registry"], "limit": 35},

            # Dashboard/Charts
            {"repo": "pure-admin/vue-pure-admin", "paths": ["src/components"], "limit": 30},
            {"repo": "xyflow/xyflow", "paths": ["packages/react/src/components"], "limit": 15},

            # Templates (BONUS)
            {"repo": "vercel/commerce", "paths": ["components", "site/components"], "limit": 25},
            {"repo": "vercel/ai-chatbot", "paths": ["components"], "limit": 15},
        ]

    # ========================================================================
    # GITHUB API - Simple fetching
    # ========================================================================

    async def fetch_repo_tree(
        self,
        repo: str,
        session: aiohttp.ClientSession
    ) -> List[Dict[str, str]]:
        """Fetch file tree from GitHub API."""
        url = f"https://api.github.com/repos/{repo}/git/trees/main?recursive=1"
        headers = {}

        if self.config.github_token:
            headers["Authorization"] = f"token {self.config.github_token}"

        try:
            async with session.get(url, headers=headers, timeout=self.config.timeout) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("tree", [])
                else:
                    print(f"   ❌ Failed to fetch tree: {response.status}")
                    return []
        except Exception as e:
            print(f"   ❌ Error fetching tree: {e}")
            return []

    async def fetch_file_content(
        self,
        repo: str,
        file_path: str,
        session: aiohttp.ClientSession
    ) -> Optional[str]:
        """Fetch raw file content from GitHub."""
        url = f"https://raw.githubusercontent.com/{repo}/main/{file_path}"

        try:
            async with session.get(url, timeout=self.config.timeout) as response:
                if response.status == 200:
                    return await response.text()
                return None
        except:
            return None

    # ========================================================================
    # SIMPLE PATTERN MATCHING - No AI required
    # ========================================================================

    def detect_framework(self, file_path: str) -> str:
        """Simple file extension check."""
        if file_path.endswith('.tsx'):
            return 'react-ts'
        elif file_path.endswith('.jsx'):
            return 'react-js'
        elif file_path.endswith('.vue'):
            return 'vue'
        elif file_path.endswith('.svelte'):
            return 'svelte'
        return 'unknown'

    def detect_category(self, name: str, code: str) -> str:
        """Simple keyword matching for categories."""
        name_lower = name.lower()

        # Simple dictionary lookup (NO REASONING)
        if any(w in name_lower for w in ['button', 'btn']):
            return 'buttons'
        elif any(w in name_lower for w in ['input', 'field', 'form', 'select', 'textarea']):
            return 'forms'
        elif any(w in name_lower for w in ['nav', 'menu', 'sidebar', 'header', 'footer']):
            return 'navigation'
        elif any(w in name_lower for w in ['card', 'panel']):
            return 'cards'
        elif any(w in name_lower for w in ['modal', 'dialog', 'popup', 'drawer']):
            return 'modals'
        elif any(w in name_lower for w in ['table', 'grid', 'list']):
            return 'data'
        elif any(w in name_lower for w in ['chart', 'graph', 'plot']):
            return 'charts'
        elif any(w in name_lower for w in ['alert', 'toast', 'notification']):
            return 'feedback'
        elif any(w in name_lower for w in ['spinner', 'loader', 'skeleton', 'progress']):
            return 'loading'
        else:
            return 'other'

    def extract_simple_features(self, code: str) -> Dict[str, bool]:
        """Extract features using simple regex (NO AI)."""
        return {
            'has_typescript': bool(re.search(r':\s*(string|number|boolean|any)', code)),
            'has_tailwind': bool(re.search(r'className.*\b(bg-|text-|flex|grid)', code)),
            'has_props': 'props' in code.lower() or bool(re.search(r'\{.*\}.*=', code)),
            'is_responsive': bool(re.search(r'(sm:|md:|lg:|@media)', code)),
            'has_dark_mode': 'dark:' in code,
            'has_animation': bool(re.search(r'(animate-|transition-|motion\.)', code))
        }

    # ========================================================================
    # MAIN SCRAPING LOGIC
    # ========================================================================

    async def scrape_repo(
        self,
        repo_config: Dict[str, Any],
        session: aiohttp.ClientSession
    ) -> int:
        """
        Scrape a single repository.
        Returns number of components saved.
        """
        repo = repo_config["repo"]
        component_paths = repo_config.get("paths", [])
        limit = repo_config.get("limit", 50)

        print(f"\n📦 {repo}")

        # Get file tree
        tree = await self.fetch_repo_tree(repo, session)

        if not tree:
            print(f"   ⚠️  No files found")
            return 0

        # Filter component files
        component_files = []
        for file in tree:
            path = file.get("path", "")

            # Check if in component paths
            in_path = any(path.startswith(p) for p in component_paths) if component_paths else True

            # Check extension
            has_ext = any(path.endswith(ext) for ext in self.config.component_extensions)

            # Check exclusions
            excluded = any(pattern in path for pattern in self.config.exclude_patterns)

            if in_path and has_ext and not excluded:
                component_files.append(file)

        print(f"   📄 Found {len(component_files)} files")

        # Process files (up to limit)
        saved_count = 0
        for i, file in enumerate(component_files[:limit], 1):
            try:
                file_path = file["path"]

                # Fetch content
                code = await self.fetch_file_content(repo, file_path, session)

                if not code:
                    continue

                # Check size
                if len(code) < self.config.min_file_size or len(code) > self.config.max_file_size:
                    continue

                # Extract metadata (SIMPLE - NO AI)
                component_name = Path(file_path).stem
                framework = self.detect_framework(file_path)
                category = self.detect_category(component_name, code)
                features = self.extract_simple_features(code)

                # Create component record
                component_id = hashlib.md5(f"{repo}/{file_path}".encode()).hexdigest()

                component = {
                    'id': component_id,
                    'name': component_name,
                    'category': category,
                    'code': code,
                    'framework': framework,
                    'file_size': len(code),
                    'line_count': code.count('\n'),
                    'repo': repo,
                    'file_path': file_path,
                    'github_url': f"https://github.com/{repo}/blob/main/{file_path}",
                    **features
                }

                # Save to database
                self.save_component(component)
                saved_count += 1

                if i % 10 == 0:
                    print(f"   ✅ {i}/{len(component_files[:limit])}")

                # Rate limiting
                await asyncio.sleep(self.config.rate_limit)

            except Exception as e:
                self.stats["errors"] += 1
                continue

        print(f"   💾 Saved {saved_count} components")
        self.stats["repos_scraped"] += 1
        self.stats["components_saved"] += saved_count

        return saved_count

    def save_component(self, component: Dict[str, Any]):
        """Save component to database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT OR REPLACE INTO components (
                id, name, category, code, framework,
                file_size, line_count,
                has_typescript, has_tailwind, has_props,
                is_responsive, has_dark_mode, has_animation,
                repo, file_path, github_url
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            component['id'],
            component['name'],
            component['category'],
            component['code'],
            component['framework'],
            component['file_size'],
            component['line_count'],
            component['has_typescript'],
            component['has_tailwind'],
            component['has_props'],
            component['is_responsive'],
            component['has_dark_mode'],
            component['has_animation'],
            component['repo'],
            component['file_path'],
            component['github_url']
        ))

        conn.commit()
        conn.close()

    # ========================================================================
    # RUN SCRAPING JOB
    # ========================================================================

    async def run(self):
        """Run the complete scraping job."""
        repos = self.get_repos_to_scrape()

        print("🚀 LIGHTWEIGHT UI SCRAPER")
        print("=" * 60)
        print(f"📋 Repos to scrape: {len(repos)}")
        print(f"⚡ Mode: FAST (no AI, no reasoning)")
        print(f"💾 Database: {self.db_path}")
        print()

        start_time = time.time()

        # Create session
        async with aiohttp.ClientSession() as session:
            for repo_config in repos:
                await self.scrape_repo(repo_config, session)

                # Cooldown between repos
                await asyncio.sleep(2)

        # Summary
        duration = time.time() - start_time

        print("\n" + "=" * 60)
        print("✅ SCRAPING COMPLETE!")
        print("=" * 60)
        print(f"⏱️  Duration: {duration:.1f}s")
        print(f"📦 Repos: {self.stats['repos_scraped']}")
        print(f"💾 Components: {self.stats['components_saved']}")
        print(f"❌ Errors: {self.stats['errors']}")
        print()

        # Show breakdown
        self.print_database_stats()

    def print_database_stats(self):
        """Print simple database statistics."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # By category
        cursor.execute("""
            SELECT category, COUNT(*) as count
            FROM components
            GROUP BY category
            ORDER BY count DESC
        """)

        print("📊 By Category:")
        for category, count in cursor.fetchall():
            print(f"   {category}: {count}")

        print()

        # By framework
        cursor.execute("""
            SELECT framework, COUNT(*) as count
            FROM components
            GROUP BY framework
            ORDER BY count DESC
        """)

        print("🎯 By Framework:")
        for framework, count in cursor.fetchall():
            print(f"   {framework}: {count}")

        print()

        # Feature stats
        cursor.execute("""
            SELECT
                SUM(has_tailwind) as tailwind,
                SUM(has_typescript) as typescript,
                SUM(is_responsive) as responsive,
                SUM(has_dark_mode) as dark_mode,
                SUM(has_animation) as animated
            FROM components
        """)

        stats = cursor.fetchone()
        print("✨ Features:")
        print(f"   Tailwind CSS: {stats[0]}")
        print(f"   TypeScript: {stats[1]}")
        print(f"   Responsive: {stats[2]}")
        print(f"   Dark Mode: {stats[3]}")
        print(f"   Animated: {stats[4]}")

        conn.close()


# ============================================================================
# MAIN
# ============================================================================

async def main():
    """Run the scraper."""

    # Optional: Set GitHub token for higher rate limits
    # Get token: https://github.com/settings/tokens
    # export GITHUB_TOKEN="ghp_..."

    import os
    github_token = os.getenv("GITHUB_TOKEN")

    config = ScrapingConfig(
        github_token=github_token,
        rate_limit=1.5,  # Fast but safe
        max_files_per_repo=50
    )

    scraper = LightweightUIScraper(config)
    await scraper.run()


if __name__ == "__main__":
    import os
    os.chdir("/Users/matto/Documents/AI CHAT/my-app")

    asyncio.run(main())
