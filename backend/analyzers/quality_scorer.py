"""
UI Component Quality Scorer
Scores components on accessibility, code quality, modern design, and performance
"""
import re
from typing import Dict, Any
import sqlite3
from pathlib import Path

class UIQualityScorer:
    """
    Score UI components across multiple quality dimensions.

    Scoring breakdown (0-100):
    - Accessibility: 30 points
    - Code Quality: 25 points
    - Modern Design: 25 points
    - Performance: 20 points
    """

    def __init__(self):
        self.weights = {
            "accessibility": 0.30,
            "code_quality": 0.25,
            "modern_design": 0.25,
            "performance": 0.20
        }

    def score_component(self, component: Dict[str, Any]) -> Dict[str, int]:
        """
        Score a component across all dimensions.

        Args:
            component: Component data with code, framework, etc.

        Returns:
            {
                "overall": 85,
                "accessibility": 90,
                "code_quality": 80,
                "modern_design": 85,
                "performance": 85
            }
        """
        code = component.get("code_tsx") or component.get("code_html") or ""
        framework = component.get("framework", "")
        styling = component.get("styling", "")

        scores = {
            "accessibility": self.score_accessibility(code),
            "code_quality": self.score_code_quality(code, framework),
            "modern_design": self.score_modern_design(code, styling),
            "performance": self.score_performance(code)
        }

        # Calculate weighted overall score
        overall = sum(
            scores[dim] * self.weights[dim]
            for dim in scores
        )

        return {
            "overall": int(overall),
            **scores
        }

    def score_accessibility(self, code: str) -> int:
        """
        Score accessibility (0-100).

        Checks:
        - ARIA labels and roles
        - Semantic HTML
        - Keyboard navigation
        - Focus management
        - Color contrast considerations
        """
        score = 0
        code_lower = code.lower()

        # Semantic HTML (20 points)
        semantic_tags = ['<button', '<nav', '<main', '<article', '<section', '<header', '<footer']
        if any(tag in code_lower for tag in semantic_tags):
            score += 10
        if '<button' in code_lower:  # Proper buttons vs div onClick
            score += 10

        # ARIA attributes (30 points)
        aria_patterns = [
            r'aria-label\s*=',
            r'aria-labelledby\s*=',
            r'aria-describedby\s*=',
            r'aria-hidden\s*=',
            r'role\s*=',
            r'aria-expanded\s*=',
            r'aria-pressed\s*='
        ]
        aria_count = sum(1 for pattern in aria_patterns if re.search(pattern, code_lower))
        score += min(aria_count * 6, 30)

        # Keyboard navigation (20 points)
        keyboard_patterns = [
            r'onKeyDown',
            r'onKeyPress',
            r'onKeyUp',
            r'tabIndex',
            r'ref\s*=.*focus'
        ]
        if any(re.search(pattern, code) for pattern in keyboard_patterns):
            score += 20

        # Form labels (15 points)
        if '<label' in code_lower:
            score += 10
        if 'htmlFor' in code or 'for=' in code_lower:
            score += 5

        # Alt text for images (15 points)
        if '<img' in code_lower or '<Image' in code:
            if 'alt=' in code_lower:
                score += 15
            else:
                score = max(0, score - 10)  # Penalty for images without alt

        return min(score, 100)

    def score_code_quality(self, code: str, framework: str) -> int:
        """
        Score code quality (0-100).

        Checks:
        - TypeScript usage
        - Proper naming conventions
        - Component composition
        - Error handling
        - Comments/documentation
        """
        score = 0

        # TypeScript (25 points)
        typescript_indicators = [
            r':\s*React\.FC',
            r'interface\s+\w+Props',
            r'type\s+\w+Props',
            r':\s*(string|number|boolean)',
            r'<\w+>'  # Generics
        ]
        ts_count = sum(1 for pattern in typescript_indicators if re.search(pattern, code))
        score += min(ts_count * 5, 25)

        # Proper naming (20 points)
        if framework == "react":
            # PascalCase component names
            if re.search(r'(export\s+)?function\s+[A-Z][a-z]+', code):
                score += 10
            if re.search(r'const\s+[A-Z][a-z]+\s*[:=]', code):
                score += 10

        # Component composition (20 points)
        if 'children' in code:
            score += 10
        if re.search(r'<.*\{.*\}.*>', code):  # JSX expressions
            score += 10

        # Props destructuring (15 points)
        if re.search(r'\{\s*\w+[,\s]+\w+.*\}', code):  # {...props}
            score += 15

        # Error handling (10 points)
        error_patterns = [r'try\s*\{', r'catch\s*\(', r'\?\?', r'\?\.']
        if any(re.search(pattern, code) for pattern in error_patterns):
            score += 10

        # Comments (10 points)
        if '//' in code or '/*' in code:
            score += 10

        return min(score, 100)

    def score_modern_design(self, code: str, styling: str) -> int:
        """
        Score modern design patterns (0-100).

        Checks:
        - Tailwind utility classes
        - Modern CSS features
        - Responsive design
        - Dark mode support
        - Animations
        """
        score = 0
        code_lower = code.lower()

        # Tailwind CSS (30 points)
        if styling == "tailwind":
            score += 20

            # Modern utility classes
            modern_classes = [
                r'flex\b', r'grid\b', r'gap-', r'space-',
                r'rounded-', r'shadow-', r'backdrop-',
                r'bg-gradient', r'from-', r'to-'
            ]
            matches = sum(1 for pattern in modern_classes if re.search(pattern, code))
            score += min(matches * 2, 10)

        # Responsive design (25 points)
        responsive_patterns = [
            r'sm:', r'md:', r'lg:', r'xl:', r'2xl:',
            r'@media', r'min-width', r'max-width'
        ]
        if any(re.search(pattern, code) for pattern in responsive_patterns):
            score += 25

        # Dark mode (20 points)
        dark_mode_patterns = [r'dark:', r'prefers-color-scheme', r'darkMode']
        if any(re.search(pattern, code) for pattern in dark_mode_patterns):
            score += 20

        # Animations (15 points)
        animation_patterns = [
            r'animate-', r'transition-', r'duration-',
            r'framer-motion', r'motion\.', r'@keyframes',
            r'transform', r'translate', r'scale'
        ]
        anim_count = sum(1 for pattern in animation_patterns if re.search(pattern, code))
        score += min(anim_count * 5, 15)

        # Modern layout (10 points)
        if re.search(r'(flex|grid)\s+(flex-col|grid-cols)', code):
            score += 10

        return min(score, 100)

    def score_performance(self, code: str) -> int:
        """
        Score performance considerations (0-100).

        Checks:
        - Code size
        - Memoization
        - Lazy loading
        - Efficient renders
        """
        score = 50  # Base score

        # Code size (20 points)
        code_length = len(code)
        if code_length < 500:
            score += 20
        elif code_length < 1000:
            score += 15
        elif code_length < 2000:
            score += 10
        elif code_length > 5000:
            score -= 10

        # React optimizations (30 points)
        optimization_patterns = [
            r'useMemo', r'useCallback', r'React\.memo',
            r'React\.lazy', r'Suspense', r'dynamic\s+import'
        ]
        opt_count = sum(1 for pattern in optimization_patterns if re.search(pattern, code))
        score += min(opt_count * 10, 30)

        # Efficient patterns (20 points)
        if 'key=' in code:  # Proper list keys
            score += 10
        if not re.search(r'(map|forEach).*\(.*\)\s*\{.*\{', code):  # Avoid nested loops
            score += 10

        # No inline functions in JSX (15 points)
        inline_functions = re.findall(r'onClick=\{.*=>', code)
        if not inline_functions:
            score += 15
        elif len(inline_functions) < 3:
            score += 7

        # Lazy loading images (15 points)
        if re.search(r'loading=["\']lazy["\']', code):
            score += 15

        return min(max(score, 0), 100)

    def score_database_patterns(self, db_path: str = "backend/data/ui_patterns.db"):
        """
        Score all patterns in the database and update their quality scores.
        """
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Get all patterns
        cursor.execute("""
            SELECT id, name, code_tsx, code_html, framework, styling
            FROM ui_patterns
        """)

        patterns = cursor.fetchall()

        print(f"🎯 Scoring {len(patterns)} UI patterns...")

        for i, pattern in enumerate(patterns, 1):
            pattern_id, name, code_tsx, code_html, framework, styling = pattern

            component = {
                "code_tsx": code_tsx,
                "code_html": code_html,
                "framework": framework,
                "styling": styling
            }

            # Calculate scores
            scores = self.score_component(component)

            # Update database
            cursor.execute("""
                UPDATE ui_patterns
                SET quality_score = ?, accessibility_score = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (scores["overall"], scores["accessibility"], pattern_id))

            if i % 10 == 0:
                print(f"   Scored {i}/{len(patterns)}...")

        conn.commit()
        conn.close()

        print(f"✅ Quality scoring complete!")
        print(f"   Patterns scored: {len(patterns)}")

        # Show stats
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                COUNT(*) as total,
                AVG(quality_score) as avg_quality,
                AVG(accessibility_score) as avg_accessibility,
                MAX(quality_score) as max_quality,
                MIN(quality_score) as min_quality
            FROM ui_patterns
            WHERE quality_score > 0
        """)

        stats = cursor.fetchone()
        conn.close()

        print(f"\n📊 Quality Statistics:")
        print(f"   Average Overall Score: {stats[1]:.1f}/100")
        print(f"   Average Accessibility: {stats[2]:.1f}/100")
        print(f"   Highest Score: {stats[3]}/100")
        print(f"   Lowest Score: {stats[4]}/100")


if __name__ == "__main__":
    import os
    os.chdir("/Users/matto/Documents/AI CHAT/my-app")

    scorer = UIQualityScorer()
    scorer.score_database_patterns()
