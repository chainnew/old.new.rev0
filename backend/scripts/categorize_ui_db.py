"""
UI Component Database Categorization Script
Analyzes raw_themes.db and creates a categorized catalog for AI agents
"""
import sqlite3
import json
from pathlib import Path
from typing import Dict, List, Any

class UIComponentCatalog:
    """Categorize and analyze UI components from scraped GitHub repos."""

    CATEGORIES = {
        "component_libraries": {
            "keywords": ["shadcn", "daisyui", "radix", "headless", "primitive", "magicui", "kokonut"],
            "description": "Pre-built component libraries (shadcn/ui, DaisyUI, Radix, etc.)"
        },
        "css_frameworks": {
            "keywords": ["tailwind", "bootstrap", "css framework", "utility-first"],
            "description": "CSS frameworks (Tailwind, Bootstrap, etc.)"
        },
        "react_ui": {
            "keywords": ["react component", "react ui", "react native"],
            "description": "React component libraries and UI kits"
        },
        "vue_ui": {
            "keywords": ["vue component", "vue ui", "vue.js"],
            "description": "Vue.js component libraries and UI kits"
        },
        "dashboards": {
            "keywords": ["dashboard", "admin", "template", "boilerplate"],
            "description": "Dashboard templates and admin panels"
        },
        "animation": {
            "keywords": ["animation", "motion", "framer", "animate", "transition"],
            "description": "Animation libraries and effects"
        },
        "charts_graphs": {
            "keywords": ["chart", "graph", "diagram", "flow", "visualization", "d3"],
            "description": "Data visualization, charts, and diagrams"
        },
        "design_systems": {
            "keywords": ["design system", "design token", "figma", "sketch"],
            "description": "Design systems and design tools"
        },
        "icons_assets": {
            "keywords": ["icon", "emoji", "svg", "illustration", "asset"],
            "description": "Icon sets and visual assets"
        },
        "forms_inputs": {
            "keywords": ["form", "input", "validation", "schema"],
            "description": "Form builders and input components"
        }
    }

    def __init__(self, db_path: str = "db-cleaning/raw_themes.db"):
        self.db_path = Path(db_path)
        self.catalog = {cat: [] for cat in self.CATEGORIES.keys()}
        self.catalog["other"] = []

    def categorize_repo(self, repo_data: Dict[str, Any]) -> str:
        """Categorize a single repository based on name and description."""
        name = repo_data.get("full_name", "").lower()
        desc = (repo_data.get("description") or "").lower()
        combined = f"{name} {desc}"

        # Check each category
        for category, config in self.CATEGORIES.items():
            for keyword in config["keywords"]:
                if keyword.lower() in combined:
                    return category

        return "other"

    def analyze_database(self):
        """Analyze the entire database and categorize repos."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Get all repos with stars > 500 (quality filter)
        cursor.execute("""
            SELECT full_name, description, stars, files, readme,
                   category, ai_description, stencil_patterns, tweaked_variants
            FROM themes
            WHERE stars > 500
            ORDER BY stars DESC
        """)

        repos = cursor.fetchall()

        for repo in repos:
            repo_data = {
                "full_name": repo[0],
                "description": repo[1],
                "stars": repo[2],
                "files": self._parse_json(repo[3]),
                "readme": repo[4],
                "category": repo[5],
                "ai_description": repo[6],
                "stencil_patterns": self._parse_json(repo[7]),
                "tweaked_variants": self._parse_json(repo[8])
            }

            # Categorize
            category = self.categorize_repo(repo_data)
            self.catalog[category].append(repo_data)

        conn.close()

        return self.catalog

    def _parse_json(self, json_str: str) -> Any:
        """Safely parse JSON string."""
        if not json_str:
            return None
        try:
            return json.loads(json_str)
        except:
            return None

    def print_report(self):
        """Print categorization report."""
        print("\n" + "="*80)
        print("🎨 UI COMPONENT CATALOG - CATEGORIZATION REPORT")
        print("="*80)

        total_repos = sum(len(repos) for repos in self.catalog.values())
        print(f"\n📊 Total Repositories Analyzed: {total_repos}")
        print(f"⭐ Quality Filter: Stars > 500\n")

        for category, repos in self.catalog.items():
            if not repos:
                continue

            config = self.CATEGORIES.get(category, {"description": "Uncategorized repositories"})
            print(f"\n{'─'*80}")
            print(f"📁 {category.upper().replace('_', ' ')} ({len(repos)} repos)")
            print(f"   {config.get('description', '')}")
            print('─'*80)

            # Show top 5 in each category
            for repo in repos[:5]:
                print(f"  ⭐ {repo['stars']:>7,} | {repo['full_name']}")
                if repo['description']:
                    desc = repo['description'][:75]
                    print(f"            {desc}...")

            if len(repos) > 5:
                print(f"            ... and {len(repos) - 5} more")

    def export_catalog(self, output_path: str = "backend/data/ui_catalog.json"):
        """Export catalog to JSON for AI agents."""
        output = {
            "version": "1.0",
            "total_repos": sum(len(repos) for repos in self.catalog.values()),
            "categories": {}
        }

        for category, repos in self.catalog.items():
            if not repos:
                continue

            output["categories"][category] = {
                "count": len(repos),
                "description": self.CATEGORIES.get(category, {}).get("description", ""),
                "top_repos": [
                    {
                        "name": repo["full_name"],
                        "description": repo["description"],
                        "stars": repo["stars"],
                        "github_url": f"https://github.com/{repo['full_name']}"
                    }
                    for repo in repos[:10]  # Top 10 per category
                ]
            }

        # Create output directory if needed
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w') as f:
            json.dump(output, f, indent=2)

        print(f"\n✅ Catalog exported to: {output_path}")
        return output_path

    def create_categorized_table(self):
        """Create a new table with categorized repos."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Create categorized table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ui_catalog (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                category TEXT NOT NULL,
                description TEXT,
                stars INTEGER,
                files TEXT,
                readme TEXT,
                ai_description TEXT,
                stencil_patterns TEXT,
                tweaked_variants TEXT,
                github_url TEXT,
                is_usable BOOLEAN DEFAULT 1,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Clear existing data
        cursor.execute("DELETE FROM ui_catalog")

        # Insert categorized repos
        for category, repos in self.catalog.items():
            for repo in repos:
                cursor.execute("""
                    INSERT INTO ui_catalog (
                        full_name, category, description, stars, files,
                        readme, ai_description, stencil_patterns,
                        tweaked_variants, github_url
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    repo["full_name"],
                    category,
                    repo["description"],
                    repo["stars"],
                    json.dumps(repo["files"]) if repo["files"] else None,
                    repo["readme"],
                    repo["ai_description"],
                    json.dumps(repo["stencil_patterns"]) if repo["stencil_patterns"] else None,
                    json.dumps(repo["tweaked_variants"]) if repo["tweaked_variants"] else None,
                    f"https://github.com/{repo['full_name']}"
                ))

        conn.commit()
        conn.close()

        print(f"✅ Created 'ui_catalog' table with {sum(len(repos) for repos in self.catalog.values())} categorized repos")


if __name__ == "__main__":
    # Change to project root
    import os
    os.chdir("/Users/matto/Documents/AI CHAT/my-app")

    # Create catalog
    catalog = UIComponentCatalog()

    print("🔍 Analyzing UI themes database...")
    catalog.analyze_database()

    # Print report
    catalog.print_report()

    # Export catalog
    catalog.export_catalog()

    # Create categorized table
    catalog.create_categorized_table()

    print("\n" + "="*80)
    print("✅ CATEGORIZATION COMPLETE")
    print("="*80)
