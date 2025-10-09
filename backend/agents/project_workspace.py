"""
Project Workspace Manager
Automatically creates and manages project folders for each swarm.
Agents write actual code files instead of returning text.
"""
import os
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

class ProjectWorkspace:
    """Manages autonomous project workspace creation and file writing."""

    def __init__(self, projects_root: str = "Projects"):
        self.projects_root = Path(projects_root)
        self.projects_root.mkdir(exist_ok=True)

    def create_workspace(
        self,
        project_name: str,
        swarm_id: str,
        scope: Dict[str, Any],
        template_type: str = "fullstack"
    ) -> str:
        """
        Create a new project workspace with scaffolding.

        Args:
            project_name: Clean project name (e.g., "EcommercePlatform")
            swarm_id: Unique swarm identifier
            scope: Original project scope/requirements
            template_type: Project template (fullstack, frontend, backend, mobile)

        Returns:
            Absolute path to created project directory
        """
        # Sanitize project name
        safe_name = self._sanitize_name(project_name)

        # Create project folder: Projects/ProjectName_swarmId/
        project_dir = self.projects_root / f"{safe_name}_{swarm_id[:8]}"
        project_dir.mkdir(parents=True, exist_ok=True)

        # Create base structure
        self._create_base_structure(project_dir)

        # Create template-specific structure
        self._create_template_structure(project_dir, template_type)

        # Save swarm metadata
        self._save_swarm_metadata(project_dir, swarm_id, scope, template_type)

        # Create README
        self._create_readme(project_dir, project_name, scope)

        print(f"📁 Project workspace created: {project_dir}")
        return str(project_dir.absolute())

    def _sanitize_name(self, name: str) -> str:
        """Convert project name to safe folder name."""
        # Remove special chars, keep alphanumeric and spaces
        safe = "".join(c if c.isalnum() or c == " " else "" for c in name)
        # Replace spaces with underscores, title case
        return "".join(word.capitalize() for word in safe.split())

    def _create_base_structure(self, project_dir: Path):
        """Create base folders all projects need."""
        base_dirs = [
            ".swarm",           # Swarm metadata
            "docs",             # Documentation
            "tests",            # Test files
            ".vscode",          # VSCode settings
        ]

        for dir_name in base_dirs:
            (project_dir / dir_name).mkdir(exist_ok=True)

        # Create .gitignore
        gitignore_content = """# Dependencies
node_modules/
__pycache__/
*.pyc
venv/
.env
.env.local

# Build outputs
dist/
build/
.next/
out/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Swarm metadata (keep local)
.swarm/progress.json
.swarm/logs/
"""
        (project_dir / ".gitignore").write_text(gitignore_content)

        # Create VSCode settings
        vscode_settings = {
            "editor.formatOnSave": True,
            "editor.defaultFormatter": "esbenp.prettier-vscode",
            "python.linting.enabled": True,
            "python.linting.pylintEnabled": True,
        }
        (project_dir / ".vscode" / "settings.json").write_text(
            json.dumps(vscode_settings, indent=2)
        )

    def _create_template_structure(self, project_dir: Path, template_type: str):
        """Create template-specific folder structure."""

        if template_type == "fullstack":
            self._create_fullstack_template(project_dir)
        elif template_type == "frontend":
            self._create_frontend_template(project_dir)
        elif template_type == "backend":
            self._create_backend_template(project_dir)
        elif template_type == "mobile":
            self._create_mobile_template(project_dir)

    def _create_fullstack_template(self, project_dir: Path):
        """Full-stack Next.js + FastAPI template."""
        frontend_dirs = [
            "app",
            "app/api",
            "components",
            "components/ui",
            "lib",
            "public",
        ]

        backend_dirs = [
            "backend/api",
            "backend/models",
            "backend/services",
            "backend/utils",
        ]

        for dir_path in frontend_dirs + backend_dirs:
            (project_dir / dir_path).mkdir(parents=True, exist_ok=True)

        # Create package.json
        package_json = {
            "name": project_dir.name.lower(),
            "version": "0.1.0",
            "private": True,
            "scripts": {
                "dev": "next dev",
                "build": "next build",
                "start": "next start",
                "lint": "next lint"
            },
            "dependencies": {
                "next": "15.5.4",
                "react": "19.0.0",
                "react-dom": "19.0.0",
                "typescript": "^5"
            },
            "devDependencies": {
                "@types/node": "^20",
                "@types/react": "^19",
                "@types/react-dom": "^19",
                "tailwindcss": "^3.4.1",
                "autoprefixer": "^10.4.20",
                "postcss": "^8.4.49"
            }
        }
        (project_dir / "package.json").write_text(json.dumps(package_json, indent=2))

        # Create requirements.txt
        requirements = """fastapi==0.112.0
uvicorn[standard]==0.30.1
pydantic==2.8.0
python-dotenv==1.0.0
"""
        (project_dir / "backend" / "requirements.txt").write_text(requirements)

        # Create next.config.js
        next_config = """/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    serverActions: true,
  },
}

module.exports = nextConfig
"""
        (project_dir / "next.config.js").write_text(next_config)

        # Create tsconfig.json
        tsconfig = {
            "compilerOptions": {
                "target": "ES2017",
                "lib": ["dom", "dom.iterable", "esnext"],
                "allowJs": True,
                "skipLibCheck": True,
                "strict": True,
                "noEmit": True,
                "esModuleInterop": True,
                "module": "esnext",
                "moduleResolution": "bundler",
                "resolveJsonModule": True,
                "isolatedModules": True,
                "jsx": "preserve",
                "incremental": True,
                "plugins": [{"name": "next"}],
                "paths": {"@/*": ["./*"]}
            },
            "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
            "exclude": ["node_modules"]
        }
        (project_dir / "tsconfig.json").write_text(json.dumps(tsconfig, indent=2))

    def _create_frontend_template(self, project_dir: Path):
        """Frontend-only Next.js template."""
        # Similar to fullstack but no backend/
        pass

    def _create_backend_template(self, project_dir: Path):
        """Backend-only FastAPI template."""
        # Just backend structure
        pass

    def _create_mobile_template(self, project_dir: Path):
        """React Native / Expo template."""
        # Mobile app structure
        pass

    def _save_swarm_metadata(
        self,
        project_dir: Path,
        swarm_id: str,
        scope: Dict[str, Any],
        template_type: str
    ):
        """Save swarm metadata to .swarm/swarm.json."""
        metadata = {
            "swarm_id": swarm_id,
            "created_at": datetime.now().isoformat(),
            "template": template_type,
            "scope": scope,
            "status": "initializing",
            "agents": [],
            "files_created": 0,
            "tasks_completed": 0,
        }

        metadata_file = project_dir / ".swarm" / "swarm.json"
        metadata_file.write_text(json.dumps(metadata, indent=2))

        # Create logs directory
        (project_dir / ".swarm" / "logs").mkdir(exist_ok=True)

    def _create_readme(
        self,
        project_dir: Path,
        project_name: str,
        scope: Dict[str, Any]
    ):
        """Generate README.md for the project."""
        readme = f"""# {project_name}

> 🤖 **Auto-generated by old.new AI Swarm Platform**

## 📋 Project Overview

{scope.get('goal', 'AI-generated project')}

## ✨ Features

"""
        # Add features from scope
        features = scope.get('features', [])
        for feature in features[:10]:  # First 10 features
            readme += f"- {feature}\n"

        readme += """
## 🚀 Quick Start

### Frontend
```bash
npm install
npm run dev
```

Visit http://localhost:3000

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate
pip install -r requirements.txt
uvicorn api.main:app --reload
```

API at http://localhost:8000

## 📁 Project Structure

```
.
├── app/              # Next.js app directory
├── components/       # React components
├── backend/          # FastAPI backend
├── docs/             # Documentation
├── tests/            # Test files
└── .swarm/           # AI swarm metadata (do not modify)
```

## 🤖 AI Swarm Status

This project was generated by an autonomous AI swarm. Check `.swarm/swarm.json` for generation details.

---

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        (project_dir / "README.md").write_text(readme)

    def write_file(
        self,
        project_dir: str,
        file_path: str,
        content: str,
        agent_id: Optional[str] = None
    ) -> bool:
        """
        Write a file to the project workspace.

        Args:
            project_dir: Project root directory
            file_path: Relative path within project (e.g., "components/Button.tsx")
            content: File content
            agent_id: ID of agent writing the file (for logging)

        Returns:
            True if successful, False otherwise
        """
        try:
            full_path = Path(project_dir) / file_path

            # Create parent directories if needed
            full_path.parent.mkdir(parents=True, exist_ok=True)

            # Write file
            full_path.write_text(content)

            # Log the file creation
            self._log_file_creation(project_dir, file_path, agent_id)

            print(f"✅ {file_path} written by {agent_id or 'agent'}")
            return True

        except Exception as e:
            print(f"❌ Error writing {file_path}: {e}")
            return False

    def _log_file_creation(self, project_dir: str, file_path: str, agent_id: Optional[str]):
        """Log file creation to .swarm/files.log."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "file": file_path,
            "agent": agent_id or "unknown"
        }

        log_file = Path(project_dir) / ".swarm" / "files.log"
        with open(log_file, "a") as f:
            f.write(json.dumps(log_entry) + "\n")

    def get_project_path(self, swarm_id: str) -> Optional[str]:
        """Get project path for a swarm ID."""
        # Search for folder matching swarm_id
        for project_dir in self.projects_root.iterdir():
            if project_dir.is_dir() and swarm_id[:8] in project_dir.name:
                return str(project_dir.absolute())
        return None

    def update_progress(self, project_dir: str, stats: Dict[str, Any]):
        """Update project progress in .swarm/progress.json."""
        progress_file = Path(project_dir) / ".swarm" / "progress.json"

        progress = {
            "updated_at": datetime.now().isoformat(),
            **stats
        }

        progress_file.write_text(json.dumps(progress, indent=2))


# Singleton instance
_workspace_manager = None

def get_workspace_manager() -> ProjectWorkspace:
    """Get global workspace manager instance."""
    global _workspace_manager
    if _workspace_manager is None:
        _workspace_manager = ProjectWorkspace()
    return _workspace_manager
