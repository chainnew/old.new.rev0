"""
UI Component Manager
Searches the themes database for relevant UI components and adapts them to projects.
"""
import sqlite3
import json
from typing import List, Dict, Any, Optional
from pathlib import Path

class UIComponentManager:
    """Manages UI component discovery from scraped GitHub themes database."""

    def __init__(self, db_path: str = "db-cleaning/raw_themes.db"):
        """
        Initialize UI component manager.

        Args:
            db_path: Path to themes SQLite database
        """
        self.db_path = Path(__file__).parent.parent.parent / db_path

        if not self.db_path.exists():
            print(f"⚠️  UI themes database not found at {self.db_path}")
            self.db_path = None
        else:
            print(f"🎨 UI Component Manager loaded: {self.db_path}")

    def search_components(
        self,
        query: str,
        component_type: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search for UI components matching a query.

        Args:
            query: Search term (e.g., "button", "navbar", "dashboard")
            component_type: Optional category filter (e.g., "component_libraries", "react_ui", "tailwind")
            limit: Max results

        Returns:
            List of matching components with code/patterns
        """
        if not self.db_path:
            return []

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Build search query (search across multiple fields)
            search_term = f"%{query.lower()}%"

            # Use categorized table if component_type is specified
            if component_type:
                sql = """
                    SELECT
                        full_name,
                        description,
                        stars,
                        files,
                        readme,
                        category,
                        ai_description,
                        stencil_patterns,
                        tweaked_variants,
                        github_url
                    FROM ui_catalog
                    WHERE category = ?
                    AND (
                        LOWER(full_name) LIKE ? OR
                        LOWER(description) LIKE ? OR
                        LOWER(ai_description) LIKE ?
                    )
                    ORDER BY stars DESC
                    LIMIT ?
                """
                cursor.execute(sql, (component_type, search_term, search_term, search_term, limit))
            else:
                # Search all categories in ui_catalog (pre-filtered, high quality repos)
                sql = """
                    SELECT
                        full_name,
                        description,
                        stars,
                        files,
                        readme,
                        category,
                        ai_description,
                        stencil_patterns,
                        tweaked_variants,
                        github_url
                    FROM ui_catalog
                    WHERE (
                        LOWER(full_name) LIKE ? OR
                        LOWER(description) LIKE ? OR
                        LOWER(ai_description) LIKE ?
                    )
                    ORDER BY stars DESC
                    LIMIT ?
                """
                cursor.execute(sql, (search_term, search_term, search_term, limit))

            results = cursor.fetchall()

            components = []
            for row in results:
                component = {
                    "repo": row[0],
                    "description": row[1],
                    "stars": row[2],
                    "files": self._parse_json(row[3]),
                    "readme": row[4],
                    "category": row[5],
                    "ai_description": row[6],
                    "stencil_patterns": self._parse_json(row[7]),
                    "tweaked_variants": self._parse_json(row[8]),
                    "github_url": row[9] if len(row) > 9 else f"https://github.com/{row[0]}"
                }
                components.append(component)

            conn.close()

            print(f"🔍 Found {len(components)} UI components for '{query}' (category: {component_type or 'all'})")
            return components

        except Exception as e:
            print(f"❌ Error searching components: {e}")
            return []

    def get_component_code(
        self,
        repo: str,
        file_pattern: Optional[str] = None
    ) -> List[Dict[str, str]]:
        """
        Get actual code files from a component repository.

        Args:
            repo: Full repository name (e.g., "shadcn/ui")
            file_pattern: Optional filter (e.g., "button", "*.tsx")

        Returns:
            List of {filename, code, language} dicts
        """
        if not self.db_path:
            return []

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                "SELECT files FROM themes WHERE full_name = ?",
                (repo,)
            )

            result = cursor.fetchone()
            conn.close()

            if not result or not result[0]:
                return []

            files = self._parse_json(result[0])

            # Filter by pattern if provided
            if file_pattern:
                pattern_lower = file_pattern.lower()
                files = [
                    f for f in files
                    if pattern_lower in f.get("filename", "").lower()
                ]

            print(f"📦 Retrieved {len(files)} files from {repo}")
            return files

        except Exception as e:
            print(f"❌ Error getting component code: {e}")
            return []

    def generate_component_from_stencil(
        self,
        query: str,
        project_tech_stack: Dict[str, str],
        component_name: str
    ) -> Optional[str]:
        """
        Generate a custom component adapted to project's tech stack.

        Args:
            query: What type of component (e.g., "animated button")
            project_tech_stack: {"framework": "react", "styling": "tailwind"}
            component_name: Desired component name (e.g., "AnimatedButton")

        Returns:
            Generated component code adapted to tech stack
        """
        # Search for matching components
        matches = self.search_components(query, limit=3)

        if not matches:
            return None

        # Get best match (highest stars)
        best_match = matches[0]

        # Extract stencil patterns or code
        stencils = best_match.get("stencil_patterns", [])
        files = best_match.get("files", [])

        # Build component from stencil/code
        # This is where you'd use Grok to adapt the code
        component_code = self._adapt_component_to_stack(
            source_code=stencils or files,
            tech_stack=project_tech_stack,
            component_name=component_name,
            original_repo=best_match["repo"]
        )

        return component_code

    def _adapt_component_to_stack(
        self,
        source_code: Any,
        tech_stack: Dict[str, str],
        component_name: str,
        original_repo: str
    ) -> str:
        """
        Use Grok to adapt component code to target tech stack.
        (Would integrate with Grok API here)
        """
        # Placeholder - would call Grok to transform code
        if isinstance(source_code, list) and len(source_code) > 0:
            # Extract first code sample
            first_sample = source_code[0]
            if isinstance(first_sample, dict):
                code = first_sample.get("code", first_sample.get("content", ""))
            else:
                code = str(first_sample)

            # Simple template for now (Grok would do the heavy lifting)
            adapted = f"""// Adapted from {original_repo}
// Generated by old.new AI Swarm

export function {component_name}() {{
  // TODO: Implement using {tech_stack.get('framework', 'React')}
  // with {tech_stack.get('styling', 'CSS')}

  return (
    <div className="component">
      {component_name}
    </div>
  );
}}
"""
            return adapted

        return f"// No source code available for {component_name}"

    def _parse_json(self, json_str: Optional[str]) -> Any:
        """Safely parse JSON string."""
        if not json_str:
            return []
        try:
            return json.loads(json_str)
        except:
            return []

    def get_popular_components(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get most popular components by stars."""
        if not self.db_path:
            return []

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT full_name, description, stars, category
                FROM themes
                ORDER BY stars DESC
                LIMIT ?
            """, (limit,))

            results = cursor.fetchall()
            conn.close()

            return [
                {
                    "repo": r[0],
                    "description": r[1],
                    "stars": r[2],
                    "category": r[3]
                }
                for r in results
            ]

        except Exception as e:
            print(f"❌ Error getting popular components: {e}")
            return []

    def get_categories(self) -> Dict[str, int]:
        """Get all available component categories with counts."""
        if not self.db_path:
            return {}

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT category, COUNT(*) as count
                FROM ui_catalog
                WHERE category IS NOT NULL
                GROUP BY category
                ORDER BY count DESC
            """)

            categories = {row[0]: row[1] for row in cursor.fetchall()}

            conn.close()
            return categories

        except Exception as e:
            print(f"❌ Error getting categories: {e}")
            return {}

    def get_components_by_category(
        self,
        category: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get top components from a specific category.

        Args:
            category: Category name (e.g., "component_libraries", "react_ui")
            limit: Max results

        Returns:
            List of components in that category
        """
        if not self.db_path:
            return []

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT full_name, description, stars, category, github_url
                FROM ui_catalog
                WHERE category = ?
                ORDER BY stars DESC
                LIMIT ?
            """, (category, limit))

            results = cursor.fetchall()
            conn.close()

            return [
                {
                    "repo": r[0],
                    "description": r[1],
                    "stars": r[2],
                    "category": r[3],
                    "github_url": r[4]
                }
                for r in results
            ]

        except Exception as e:
            print(f"❌ Error getting components by category: {e}")
            return []


# Singleton instance
_ui_manager = None

def get_ui_component_manager() -> UIComponentManager:
    """Get global UI component manager instance."""
    global _ui_manager
    if _ui_manager is None:
        _ui_manager = UIComponentManager()
    return _ui_manager
