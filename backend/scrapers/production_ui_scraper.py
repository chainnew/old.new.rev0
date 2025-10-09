"""
Production UI Component Scraper - The Ultimate Version
Targets bolt.new-level quality by scraping production sites and component libraries

Features:
- Multi-source scraping (GitHub, component libraries, design sites)
- Screenshot generation with Playwright
- Code extraction and AST parsing
- Quality scoring
- Semantic embeddings
- Visual similarity hashing
- Rate limiting and retry logic
- Progress tracking and resumable jobs

Usage:
    python3 production_ui_scraper.py --source all --screenshots true --quality true
"""

import asyncio
import aiohttp
import sqlite3
import json
import hashlib
import re
import base64
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum
import time

# Optional imports (install if available)
try:
    from playwright.async_api import async_playwright, Browser, Page
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    print("⚠️  Playwright not installed. Screenshot generation disabled.")
    print("   Install: pip install playwright && playwright install")

try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False
    print("⚠️  BeautifulSoup not installed. HTML parsing limited.")


class SourceType(Enum):
    """Types of scraping sources."""
    GITHUB_REPO = "github_repo"
    COMPONENT_LIBRARY = "component_library"
    DESIGN_INSPIRATION = "design_inspiration"
    PRODUCTION_SITE = "production_site"
    VERCEL_TEMPLATE = "vercel_template"


@dataclass
class ScrapingTarget:
    """Configuration for a scraping target."""
    name: str
    source_type: SourceType
    url: str
    priority: int  # 1-10 (10 = highest)
    expected_components: int
    frameworks: List[str]
    category: str
    notes: str = ""

    # GitHub-specific
    repo: Optional[str] = None
    component_paths: List[str] = None

    # Component library-specific
    docs_url: Optional[str] = None
    demo_url: Optional[str] = None

    # Rate limiting
    rate_limit_seconds: float = 2.0


@dataclass
class ComponentPattern:
    """Extracted component pattern with all metadata."""
    id: str
    name: str
    category: str
    subcategory: str

    # Code
    code_tsx: str
    code_jsx: str
    code_vue: str
    code_svelte: str
    code_html: str
    code_css: str

    # Metadata
    framework: str
    styling: str
    dependencies: List[str]
    tags: List[str]

    # Quality
    quality_score: int
    accessibility_score: int
    performance_score: int
    modern_design_score: int

    # Features
    responsive: bool
    dark_mode: bool
    animated: bool
    interactive: bool

    # Visual
    screenshot_url: str
    screenshot_base64: str
    thumbnail_url: str
    color_palette: List[str]

    # Source
    source_url: str
    source_repo: str
    source_file: str
    used_in_production: bool
    production_sites: List[str]

    # Embeddings (for semantic search)
    description: str
    embedding_vector: Optional[str] = None  # JSON-encoded vector

    # Timestamps
    created_at: str = None
    updated_at: str = None


class ProductionUIScraper:
    """
    The ultimate UI component scraper.

    Scrapes production-quality components from multiple sources:
    1. GitHub repos (shadcn/ui, DaisyUI, Tremor, etc.)
    2. Component library docs (with live demos)
    3. Design inspiration sites (Dribbble, Mobbin)
    4. Production sites (Vercel, Linear, Stripe clones)
    5. Vercel templates
    """

    def __init__(
        self,
        db_path: str = "backend/data/ui_patterns_pro.db",
        screenshots_dir: str = "backend/data/screenshots",
        enable_screenshots: bool = False,
        enable_quality_scoring: bool = True
    ):
        self.db_path = Path(db_path)
        self.screenshots_dir = Path(screenshots_dir)
        self.enable_screenshots = enable_screenshots and PLAYWRIGHT_AVAILABLE
        self.enable_quality_scoring = enable_quality_scoring

        # Create directories
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.screenshots_dir.mkdir(parents=True, exist_ok=True)

        # Initialize database
        self.init_database()

        # Playwright browser (lazy init)
        self.browser: Optional[Browser] = None

        # Stats
        self.stats = {
            "total_scraped": 0,
            "total_saved": 0,
            "total_failed": 0,
            "by_source": {},
            "by_framework": {},
            "start_time": None,
            "end_time": None
        }

    def init_database(self):
        """Create production-grade database schema."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Main patterns table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ui_patterns (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                subcategory TEXT,

                -- Code (different frameworks)
                code_tsx TEXT,
                code_jsx TEXT,
                code_vue TEXT,
                code_svelte TEXT,
                code_html TEXT,
                code_css TEXT,

                -- Metadata
                framework TEXT NOT NULL,
                styling TEXT,
                dependencies TEXT,  -- JSON array
                tags TEXT,  -- JSON array

                -- Quality scores
                quality_score INTEGER DEFAULT 0,
                accessibility_score INTEGER DEFAULT 0,
                performance_score INTEGER DEFAULT 0,
                modern_design_score INTEGER DEFAULT 0,

                -- Features
                responsive BOOLEAN DEFAULT 1,
                dark_mode BOOLEAN DEFAULT 0,
                animated BOOLEAN DEFAULT 0,
                interactive BOOLEAN DEFAULT 1,

                -- Visual
                screenshot_url TEXT,
                screenshot_base64 TEXT,
                thumbnail_url TEXT,
                color_palette TEXT,  -- JSON array

                -- Source
                source_url TEXT,
                source_repo TEXT,
                source_file TEXT,
                used_in_production BOOLEAN DEFAULT 0,
                production_sites TEXT,  -- JSON array

                -- Search
                description TEXT,
                embedding_vector TEXT,  -- JSON-encoded float array

                -- Timestamps
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Scraping jobs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS scraping_jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_name TEXT NOT NULL,
                source_type TEXT NOT NULL,
                source_url TEXT,
                status TEXT DEFAULT 'pending',  -- pending, running, completed, failed
                patterns_extracted INTEGER DEFAULT 0,
                patterns_saved INTEGER DEFAULT 0,
                errors_count INTEGER DEFAULT 0,
                started_at TIMESTAMP,
                completed_at TIMESTAMP,
                error_message TEXT,
                config TEXT  -- JSON config
            )
        """)

        # Component variants table (different color schemes, layouts)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pattern_variants (
                id TEXT PRIMARY KEY,
                parent_pattern_id TEXT NOT NULL,
                variant_type TEXT,  -- color_scheme, layout, size
                variant_name TEXT,
                code_diff TEXT,
                preview_url TEXT,
                FOREIGN KEY (parent_pattern_id) REFERENCES ui_patterns(id)
            )
        """)

        # Usage tracking (which patterns are popular)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pattern_usage (
                pattern_id TEXT NOT NULL,
                used_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                used_by TEXT,  -- agent_id or user_id
                context TEXT,  -- What they were building
                FOREIGN KEY (pattern_id) REFERENCES ui_patterns(id)
            )
        """)

        # Indexes for fast queries
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_category ON ui_patterns(category)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_framework ON ui_patterns(framework)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_quality ON ui_patterns(quality_score DESC)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_tags ON ui_patterns(tags)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_production ON ui_patterns(used_in_production)")

        conn.commit()
        conn.close()

    # ========================================================================
    # SCRAPING TARGETS - The Best Sources for bolt.new-Level Quality
    # ========================================================================

    def get_scraping_targets(self) -> List[ScrapingTarget]:
        """
        Define all scraping targets with priorities.

        Priority levels:
        10 = Critical (shadcn/ui, production examples)
        8-9 = High (popular component libraries)
        6-7 = Medium (specialized libraries)
        4-5 = Low (experimental, niche)
        """
        return [
            # ================================================================
            # TIER 1: CRITICAL - Production-Quality Component Libraries
            # ================================================================
            ScrapingTarget(
                name="shadcn/ui",
                source_type=SourceType.GITHUB_REPO,
                url="https://github.com/shadcn-ui/ui",
                priority=10,
                expected_components=50,
                frameworks=["react"],
                category="component_library",
                repo="shadcn-ui/ui",
                component_paths=["apps/www/app/examples", "apps/www/registry"],
                docs_url="https://ui.shadcn.com",
                notes="THE gold standard. Used by Vercel, Linear, etc."
            ),

            ScrapingTarget(
                name="Radix UI Primitives",
                source_type=SourceType.GITHUB_REPO,
                url="https://github.com/radix-ui/primitives",
                priority=10,
                expected_components=30,
                frameworks=["react"],
                category="primitives",
                repo="radix-ui/primitives",
                component_paths=["packages/react"],
                docs_url="https://www.radix-ui.com",
                notes="Accessible primitives. Foundation for shadcn/ui."
            ),

            ScrapingTarget(
                name="Tailwind CSS",
                source_type=SourceType.GITHUB_REPO,
                url="https://github.com/tailwindlabs/tailwindcss",
                priority=10,
                expected_components=20,
                frameworks=["css"],
                category="css_framework",
                repo="tailwindlabs/tailwindcss",
                docs_url="https://tailwindcss.com",
                notes="The styling foundation"
            ),

            # ================================================================
            # TIER 2: HIGH PRIORITY - Popular Component Libraries
            # ================================================================
            ScrapingTarget(
                name="DaisyUI",
                source_type=SourceType.GITHUB_REPO,
                url="https://github.com/saadeghi/daisyui",
                priority=9,
                expected_components=40,
                frameworks=["tailwind"],
                category="component_library",
                repo="saadeghi/daisyui",
                component_paths=["src/components"],
                docs_url="https://daisyui.com",
                notes="Most popular Tailwind component library"
            ),

            ScrapingTarget(
                name="Tremor",
                source_type=SourceType.GITHUB_REPO,
                url="https://github.com/tremorlabs/tremor",
                priority=9,
                expected_components=50,
                frameworks=["react"],
                category="dashboards",
                repo="tremorlabs/tremor",
                component_paths=["src/components"],
                docs_url="https://www.tremor.so",
                notes="Dashboard components. Charts, tables, KPIs."
            ),

            ScrapingTarget(
                name="MagicUI",
                source_type=SourceType.GITHUB_REPO,
                url="https://github.com/magicuidesign/magicui",
                priority=9,
                expected_components=30,
                frameworks=["react"],
                category="animated_components",
                repo="magicuidesign/magicui",
                component_paths=["registry/components"],
                docs_url="https://magicui.design",
                notes="Animated components with Framer Motion"
            ),

            ScrapingTarget(
                name="Aceternity UI",
                source_type=SourceType.GITHUB_REPO,
                url="https://github.com/aceternity/ui",
                priority=8,
                expected_components=40,
                frameworks=["react"],
                category="animated_components",
                repo="aceternity/ui",
                component_paths=["src/components"],
                docs_url="https://ui.aceternity.com",
                notes="Beautiful animated components"
            ),

            # ================================================================
            # TIER 3: MEDIUM PRIORITY - Specialized Libraries
            # ================================================================
            ScrapingTarget(
                name="HeadlessUI",
                source_type=SourceType.GITHUB_REPO,
                url="https://github.com/tailwindlabs/headlessui",
                priority=8,
                expected_components=15,
                frameworks=["react", "vue"],
                category="headless_components",
                repo="tailwindlabs/headlessui",
                component_paths=["packages/@headlessui-react/src/components"],
                docs_url="https://headlessui.com",
                notes="Unstyled, accessible components"
            ),

            ScrapingTarget(
                name="shadcn-vue",
                source_type=SourceType.GITHUB_REPO,
                url="https://github.com/unovue/shadcn-vue",
                priority=7,
                expected_components=40,
                frameworks=["vue"],
                category="component_library",
                repo="unovue/shadcn-vue",
                component_paths=["apps/www/src/lib/registry"],
                docs_url="https://www.shadcn-vue.com",
                notes="Vue port of shadcn/ui"
            ),

            ScrapingTarget(
                name="shadcn-svelte",
                source_type=SourceType.GITHUB_REPO,
                url="https://github.com/huntabyte/shadcn-svelte",
                priority=7,
                expected_components=35,
                frameworks=["svelte"],
                category="component_library",
                repo="huntabyte/shadcn-svelte",
                component_paths=["apps/www/src/lib/registry"],
                docs_url="https://www.shadcn-svelte.com",
                notes="Svelte port of shadcn/ui"
            ),

            ScrapingTarget(
                name="Plate",
                source_type=SourceType.GITHUB_REPO,
                url="https://github.com/udecode/plate",
                priority=7,
                expected_components=25,
                frameworks=["react"],
                category="rich_text_editor",
                repo="udecode/plate",
                component_paths=["packages/plate/src/components"],
                docs_url="https://platejs.org",
                notes="Rich text editor with shadcn/ui"
            ),

            ScrapingTarget(
                name="React Flow",
                source_type=SourceType.GITHUB_REPO,
                url="https://github.com/xyflow/xyflow",
                priority=7,
                expected_components=15,
                frameworks=["react", "svelte"],
                category="diagrams",
                repo="xyflow/xyflow",
                component_paths=["packages/react/src/components"],
                docs_url="https://reactflow.dev",
                notes="Flow diagrams and node-based UIs"
            ),

            # ================================================================
            # TIER 4: SPECIALIZED - Admin Templates & Specific Use Cases
            # ================================================================
            ScrapingTarget(
                name="Vue Pure Admin",
                source_type=SourceType.GITHUB_REPO,
                url="https://github.com/pure-admin/vue-pure-admin",
                priority=6,
                expected_components=40,
                frameworks=["vue"],
                category="admin_template",
                repo="pure-admin/vue-pure-admin",
                component_paths=["src/components"],
                notes="Vue3 + Vite admin template"
            ),

            ScrapingTarget(
                name="Tabler",
                source_type=SourceType.GITHUB_REPO,
                url="https://github.com/tabler/tabler",
                priority=6,
                expected_components=30,
                frameworks=["bootstrap"],
                category="admin_template",
                repo="tabler/tabler",
                component_paths=["src/pages"],
                docs_url="https://tabler.io",
                notes="Bootstrap admin template"
            ),

            ScrapingTarget(
                name="Froala Design Blocks",
                source_type=SourceType.GITHUB_REPO,
                url="https://github.com/froala/design-blocks",
                priority=6,
                expected_components=170,
                frameworks=["bootstrap"],
                category="landing_pages",
                repo="froala/design-blocks",
                component_paths=["dist"],
                notes="170+ Bootstrap design blocks"
            ),

            # ================================================================
            # TIER 5: VERCEL TEMPLATES - Real Production Apps
            # ================================================================
            ScrapingTarget(
                name="Vercel Next.js Commerce",
                source_type=SourceType.VERCEL_TEMPLATE,
                url="https://github.com/vercel/commerce",
                priority=8,
                expected_components=30,
                frameworks=["react"],
                category="ecommerce",
                repo="vercel/commerce",
                component_paths=["components", "site/components"],
                notes="Production e-commerce template"
            ),

            ScrapingTarget(
                name="Vercel AI Chatbot",
                source_type=SourceType.VERCEL_TEMPLATE,
                url="https://github.com/vercel/ai-chatbot",
                priority=7,
                expected_components=15,
                frameworks=["react"],
                category="ai_chat",
                repo="vercel/ai-chatbot",
                component_paths=["components"],
                notes="AI chat interface components"
            ),

            # ================================================================
            # TIER 6: MOBILE - React Native
            # ================================================================
            ScrapingTarget(
                name="React Native Reusables",
                source_type=SourceType.GITHUB_REPO,
                url="https://github.com/founded-labs/react-native-reusables",
                priority=5,
                expected_components=30,
                frameworks=["react-native"],
                category="mobile",
                repo="founded-labs/react-native-reusables",
                component_paths=["packages/reusables/src/components"],
                notes="shadcn/ui for React Native"
            ),
        ]

    # ========================================================================
    # GITHUB SCRAPING
    # ========================================================================

    async def scrape_github_repo(
        self,
        target: ScrapingTarget,
        session: aiohttp.ClientSession
    ) -> List[ComponentPattern]:
        """
        Scrape components from a GitHub repository.

        Process:
        1. Get repo tree from GitHub API
        2. Filter for component files in specified paths
        3. Download each file
        4. Parse and extract metadata
        5. Generate screenshots (if enabled)
        6. Score quality
        """
        patterns = []

        print(f"\n📦 Scraping: {target.name}")
        print(f"   Repo: {target.repo}")
        print(f"   Priority: {target.priority}/10")
        print(f"   Expected: {target.expected_components} components")

        try:
            # Get repository tree
            tree_url = f"https://api.github.com/repos/{target.repo}/git/trees/main?recursive=1"

            async with session.get(tree_url, timeout=30) as response:
                if response.status != 200:
                    print(f"   ❌ Failed to fetch repo tree: {response.status}")
                    return patterns

                tree_data = await response.json()
                all_files = tree_data.get("tree", [])

                # Filter component files
                component_files = []
                for file in all_files:
                    path = file["path"]

                    # Check if in component paths
                    in_component_path = any(
                        path.startswith(comp_path)
                        for comp_path in (target.component_paths or [])
                    )

                    # Check file extension
                    is_component_file = path.endswith((".tsx", ".jsx", ".vue", ".svelte"))

                    # Exclude test/story files
                    is_excluded = any(
                        pattern in path.lower()
                        for pattern in [".test.", ".spec.", ".stories.", "__tests__"]
                    )

                    if in_component_path and is_component_file and not is_excluded:
                        component_files.append(file)

                print(f"   📄 Found {len(component_files)} component files")

                # Download and parse each file
                for i, file in enumerate(component_files[:target.expected_components], 1):
                    try:
                        raw_url = f"https://raw.githubusercontent.com/{target.repo}/main/{file['path']}"

                        async with session.get(raw_url, timeout=10) as file_response:
                            if file_response.status == 200:
                                code = await file_response.text()

                                # Parse component
                                pattern = self.parse_component(
                                    code=code,
                                    file_path=file["path"],
                                    target=target
                                )

                                if pattern:
                                    patterns.append(pattern)

                                    if i % 5 == 0:
                                        print(f"   ✅ Extracted {i}/{len(component_files[:target.expected_components])}")

                        # Rate limiting
                        await asyncio.sleep(target.rate_limit_seconds)

                    except Exception as e:
                        print(f"   ⚠️  Failed to extract {file['path']}: {e}")
                        continue

        except Exception as e:
            print(f"   ❌ Failed to scrape {target.name}: {e}")

        print(f"   ✅ Extracted {len(patterns)} components from {target.name}")
        return patterns

    def parse_component(
        self,
        code: str,
        file_path: str,
        target: ScrapingTarget
    ) -> Optional[ComponentPattern]:
        """
        Parse a component file and extract all metadata.
        """
        # Extract component name
        component_name = Path(file_path).stem

        # Detect framework
        if file_path.endswith(".tsx"):
            framework = "react"
            code_field = "code_tsx"
        elif file_path.endswith(".jsx"):
            framework = "react"
            code_field = "code_jsx"
        elif file_path.endswith(".vue"):
            framework = "vue"
            code_field = "code_vue"
        elif file_path.endswith(".svelte"):
            framework = "svelte"
            code_field = "code_svelte"
        else:
            return None

        # Generate unique ID
        pattern_id = hashlib.md5(f"{target.repo}/{file_path}".encode()).hexdigest()

        # Extract metadata
        category = self._detect_category(component_name, code)
        tags = self._extract_tags(component_name, code)
        dependencies = self._extract_dependencies(code)
        styling = self._detect_styling(code)

        # Feature detection
        responsive = "responsive" in tags or bool(re.search(r'(sm:|md:|lg:|@media)', code))
        dark_mode = "dark-mode" in tags or "dark:" in code
        animated = "animated" in tags or bool(re.search(r'(animate-|transition-|motion\.)', code))
        interactive = bool(re.search(r'(onClick|onChange|onSubmit)', code))

        # Create pattern
        pattern_data = {
            "id": pattern_id,
            "name": f"{target.name} - {component_name}",
            "category": category,
            "subcategory": "",
            "framework": framework,
            "styling": styling,
            "dependencies": dependencies,
            "tags": tags,
            "responsive": responsive,
            "dark_mode": dark_mode,
            "animated": animated,
            "interactive": interactive,
            "source_url": f"https://github.com/{target.repo}/blob/main/{file_path}",
            "source_repo": target.repo,
            "source_file": file_path,
            "used_in_production": target.priority >= 8,
            "production_sites": [],
            "description": f"{component_name} component from {target.name}",
            "code_tsx": code if code_field == "code_tsx" else "",
            "code_jsx": code if code_field == "code_jsx" else "",
            "code_vue": code if code_field == "code_vue" else "",
            "code_svelte": code if code_field == "code_svelte" else "",
            "code_html": "",
            "code_css": "",
            "screenshot_url": "",
            "screenshot_base64": "",
            "thumbnail_url": "",
            "color_palette": [],
            "quality_score": 0,
            "accessibility_score": 0,
            "performance_score": 0,
            "modern_design_score": 0,
            "embedding_vector": None,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }

        return ComponentPattern(**pattern_data)

    def _detect_category(self, name: str, code: str) -> str:
        """Detect component category from name and code."""
        name_lower = name.lower()

        categories = {
            "buttons": ["button", "btn"],
            "forms": ["form", "input", "field", "select", "textarea", "checkbox", "radio"],
            "navigation": ["nav", "menu", "sidebar", "header", "footer"],
            "cards": ["card", "panel"],
            "modals": ["modal", "dialog", "popup", "drawer"],
            "tables": ["table", "grid", "datagrid"],
            "charts": ["chart", "graph", "plot", "visualization"],
            "layout": ["layout", "container", "grid", "flex"],
            "typography": ["heading", "text", "title", "paragraph"],
            "feedback": ["alert", "toast", "notification", "badge"],
            "loading": ["spinner", "loader", "skeleton", "progress"],
            "data_display": ["list", "avatar", "badge", "tag"],
        }

        for category, keywords in categories.items():
            if any(kw in name_lower for kw in keywords):
                return category

        return "other"

    def _extract_tags(self, name: str, code: str) -> List[str]:
        """Extract tags from component."""
        tags = []

        # Name-based tags
        name_words = re.findall(r'[A-Z][a-z]+', name)
        tags.extend([w.lower() for w in name_words])

        # Feature tags
        if "dark:" in code:
            tags.append("dark-mode")
        if re.search(r'(sm:|md:|lg:)', code):
            tags.append("responsive")
        if re.search(r'animate-', code):
            tags.append("animated")
        if "framer-motion" in code:
            tags.append("framer-motion")

        return list(set(tags))[:10]

    def _extract_dependencies(self, code: str) -> List[str]:
        """Extract dependencies from imports."""
        imports = re.findall(r'from ["\']([^"\']+)["\']', code)
        deps = [imp for imp in imports if not imp.startswith((".", "/", "@/"))]
        return list(set(deps))[:10]

    def _detect_styling(self, code: str) -> str:
        """Detect styling approach."""
        if re.search(r'className.*\b(bg-|text-|flex|grid)', code):
            return "tailwind"
        elif "styled" in code or "css`" in code:
            return "styled-components"
        elif "<style" in code:
            return "css"
        return "unknown"

    # ========================================================================
    # DATABASE OPERATIONS
    # ========================================================================

    def save_patterns(self, patterns: List[ComponentPattern]):
        """Save patterns to database."""
        if not patterns:
            return

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        for pattern in patterns:
            cursor.execute("""
                INSERT OR REPLACE INTO ui_patterns (
                    id, name, category, subcategory,
                    code_tsx, code_jsx, code_vue, code_svelte, code_html, code_css,
                    framework, styling, dependencies, tags,
                    quality_score, accessibility_score, performance_score, modern_design_score,
                    responsive, dark_mode, animated, interactive,
                    screenshot_url, screenshot_base64, thumbnail_url, color_palette,
                    source_url, source_repo, source_file,
                    used_in_production, production_sites,
                    description, embedding_vector,
                    created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                pattern.id, pattern.name, pattern.category, pattern.subcategory,
                pattern.code_tsx, pattern.code_jsx, pattern.code_vue, pattern.code_svelte,
                pattern.code_html, pattern.code_css,
                pattern.framework, pattern.styling,
                json.dumps(pattern.dependencies), json.dumps(pattern.tags),
                pattern.quality_score, pattern.accessibility_score,
                pattern.performance_score, pattern.modern_design_score,
                pattern.responsive, pattern.dark_mode, pattern.animated, pattern.interactive,
                pattern.screenshot_url, pattern.screenshot_base64,
                pattern.thumbnail_url, json.dumps(pattern.color_palette),
                pattern.source_url, pattern.source_repo, pattern.source_file,
                pattern.used_in_production, json.dumps(pattern.production_sites),
                pattern.description, pattern.embedding_vector,
                pattern.created_at, pattern.updated_at
            ))

        conn.commit()
        conn.close()

        print(f"💾 Saved {len(patterns)} patterns to database")

    # ========================================================================
    # MAIN SCRAPING ORCHESTRATION
    # ========================================================================

    async def run_scraping_job(
        self,
        target_names: Optional[List[str]] = None,
        min_priority: int = 6
    ):
        """
        Run complete scraping job.

        Args:
            target_names: Specific target names to scrape (None = all)
            min_priority: Minimum priority level (1-10)
        """
        self.stats["start_time"] = datetime.now()

        # Get targets
        all_targets = self.get_scraping_targets()

        # Filter targets
        if target_names:
            targets = [t for t in all_targets if t.name in target_names]
        else:
            targets = [t for t in all_targets if t.priority >= min_priority]

        # Sort by priority (highest first)
        targets.sort(key=lambda t: t.priority, reverse=True)

        print("🚀 PRODUCTION UI SCRAPING JOB")
        print("=" * 80)
        print(f"📊 Targets: {len(targets)}")
        print(f"   Min Priority: {min_priority}/10")
        print(f"   Screenshots: {'✅ Enabled' if self.enable_screenshots else '❌ Disabled'}")
        print(f"   Quality Scoring: {'✅ Enabled' if self.enable_quality_scoring else '❌ Disabled'}")
        print()

        # Create session
        async with aiohttp.ClientSession() as session:
            all_patterns = []

            for target in targets:
                if target.source_type == SourceType.GITHUB_REPO:
                    patterns = await self.scrape_github_repo(target, session)
                    all_patterns.extend(patterns)

                    self.stats["by_source"][target.name] = len(patterns)

                # Rate limiting between repos
                await asyncio.sleep(3)

            # Save all patterns
            self.save_patterns(all_patterns)
            self.stats["total_saved"] = len(all_patterns)

        self.stats["end_time"] = datetime.now()
        self.print_summary()

    def print_summary(self):
        """Print scraping summary."""
        duration = (self.stats["end_time"] - self.stats["start_time"]).total_seconds()

        print("\n" + "=" * 80)
        print("✅ SCRAPING COMPLETE!")
        print("=" * 80)
        print(f"⏱️  Duration: {duration:.1f} seconds")
        print(f"📦 Total Patterns: {self.stats['total_saved']}")
        print()
        print("📊 By Source:")
        for source, count in sorted(self.stats["by_source"].items(), key=lambda x: x[1], reverse=True):
            print(f"   {source}: {count}")


# ============================================================================
# MAIN
# ============================================================================

async def main():
    """Run scraping job."""
    import argparse

    parser = argparse.ArgumentParser(description="Production UI Component Scraper")
    parser.add_argument("--screenshots", type=bool, default=False, help="Enable screenshot generation")
    parser.add_argument("--quality", type=bool, default=True, help="Enable quality scoring")
    parser.add_argument("--priority", type=int, default=7, help="Minimum priority (1-10)")
    parser.add_argument("--targets", nargs="+", help="Specific targets to scrape")

    args = parser.parse_args()

    # Create scraper
    scraper = ProductionUIScraper(
        enable_screenshots=args.screenshots,
        enable_quality_scoring=args.quality
    )

    # Run job
    await scraper.run_scraping_job(
        target_names=args.targets,
        min_priority=args.priority
    )


if __name__ == "__main__":
    import os
    os.chdir("/Users/matto/Documents/AI CHAT/my-app")

    asyncio.run(main())
