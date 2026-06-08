"""
File generator service module.
Assembles all project files into a dict ready for GitHub upload.
"""

from __future__ import annotations

import os
from templates.readme_template    import build_readme
from templates.gitignore_template import build_gitignore
from templates.workflow_template  import build_workflow
from templates.docker_template    import build_dockerfile, build_dockerignore
from templates.license_template   import build_license
from utils.logger import get_logger

logger = get_logger(__name__)

# Base placeholder content for generated source files
_PLACEHOLDER = "# TODO: implement this module\n"


class FileGeneratorService:
    """
    Generates all repository files from a parsed project intent.
    Returns a dict of {relative_path: file_content}.
    """

    def generate(
        self,
        intent: dict,
        llm_readme: str | None = None,
        llm_requirements: str | None = None,
        llm_structure: list[str] | None = None,
    ) -> dict[str, str]:
        """
        Build the complete set of files for the project.

        Args:
            intent:           Parsed project intent dict.
            llm_readme:       Optional LLM-generated README body.
            llm_requirements: Optional LLM-generated requirements.txt content.
            llm_structure:    Optional list of extra paths from LLM planner.

        Returns:
            Dict mapping relative file path → file content string.
        """
        files: dict[str, str] = {}
        language = intent.get("language", "Python")

        # ── Core files ────────────────────────────────────────────────────────
        files["README.md"]   = llm_readme or build_readme(intent)
        files[".gitignore"]  = build_gitignore(language)
        files["LICENSE"]     = build_license()
        files["docs/index.md"] = self._docs_index(intent)

        # ── Requirements / dependency file ────────────────────────────────────
        files[self._requirements_filename(language)] = (
            llm_requirements or self._default_requirements(intent)
        )

        # ── Source skeleton ───────────────────────────────────────────────────
        files["src/__init__.py"] = ""
        files["src/main.py"]     = self._main_file(intent)

        # ── Tests ─────────────────────────────────────────────────────────────
        if intent.get("testing_required", False):
            files["tests/__init__.py"] = ""
            files["tests/test_main.py"] = self._test_file(intent)

        # ── CI/CD workflow ────────────────────────────────────────────────────
        if intent.get("ci_required", False):
            files[".github/workflows/ci.yml"] = build_workflow(language)

        # ── Docker ────────────────────────────────────────────────────────────
        if intent.get("docker_required", False):
            files["Dockerfile"]    = build_dockerfile(language)
            files[".dockerignore"] = build_dockerignore()

        # ── Extra paths from LLM planner (filled with placeholder) ───────────
        if llm_structure:
            for path in llm_structure:
                if path not in files and path.strip():
                    files[path] = _PLACEHOLDER

        logger.info("FileGenerator produced %d files | language=%s", len(files), language)
        return files

    # ── Private builders ──────────────────────────────────────────────────────

    @staticmethod
    def _requirements_filename(language: str) -> str:
        mapping = {
            "javascript": "package.json",
            "typescript": "package.json",
        }
        return mapping.get(language.lower(), "requirements.txt")

    @staticmethod
    def _default_requirements(intent: dict) -> str:
        language  = intent.get("language", "Python").lower()
        framework = intent.get("framework", "").lower()
        database  = intent.get("database", "").lower()
        testing   = intent.get("testing_required", False)

        if language in ("javascript", "typescript"):
            return '{\n  "name": "' + intent.get("project_name", "project") + '",\n  "version": "1.0.0",\n  "dependencies": {}\n}\n'

        deps = []
        # Framework
        fw_map = {
            "flask":   ["flask", "flask-cors"],
            "django":  ["django", "djangorestframework"],
            "fastapi": ["fastapi", "uvicorn[standard]"],
            "express": [],
        }
        deps.extend(fw_map.get(framework, []))

        # Database
        db_map = {
            "sqlite":     ["sqlite3"],
            "postgresql": ["psycopg2-binary", "sqlalchemy"],
            "mysql":      ["mysqlclient", "sqlalchemy"],
            "mongodb":    ["pymongo"],
            "redis":      ["redis"],
        }
        for k, v in db_map.items():
            if k in database:
                deps.extend(v)
                break

        # Testing
        if testing:
            deps.extend(["pytest", "pytest-cov"])

        # Remove stdlib duplicates
        deps = [d for d in deps if d != "sqlite3"]

        return "\n".join(deps) + "\n" if deps else "# Add your dependencies here\n"

    @staticmethod
    def _main_file(intent: dict) -> str:
        name      = intent.get("project_name", "project")
        language  = intent.get("language", "Python").lower()
        framework = intent.get("framework", "").lower()

        if language != "python":
            return f"// Entry point for {name}\n"

        if framework == "flask":
            return (
                f'"""Entry point for {name}."""\n'
                "from flask import Flask\n\n"
                "app = Flask(__name__)\n\n\n"
                "@app.route('/')\n"
                "def index():\n"
                f'    return "{name} is running!"\n\n\n'
                "if __name__ == '__main__':\n"
                "    app.run(debug=True)\n"
            )
        if framework == "fastapi":
            return (
                f'"""Entry point for {name}."""\n'
                "from fastapi import FastAPI\n\n"
                "app = FastAPI(title=\"" + name + "\")\n\n\n"
                "@app.get('/')\n"
                "def root():\n"
                f'    return {{"message": "{name} is running!"}}\n'
            )
        return (
            f'"""Entry point for {name}."""\n\n\n'
            "def main() -> None:\n"
            f'    print("{name} started.")\n\n\n'
            'if __name__ == "__main__":\n'
            "    main()\n"
        )

    @staticmethod
    def _test_file(intent: dict) -> str:
        name      = intent.get("project_name", "project")
        framework = intent.get("framework", "").lower()

        if framework == "flask":
            return (
                f'"""Tests for {name}."""\n'
                "import pytest\n"
                "from src.main import app\n\n\n"
                "@pytest.fixture\n"
                "def client():\n"
                "    app.config['TESTING'] = True\n"
                "    with app.test_client() as c:\n"
                "        yield c\n\n\n"
                "def test_index(client):\n"
                "    response = client.get('/')\n"
                "    assert response.status_code == 200\n"
            )
        return (
            f'"""Tests for {name}."""\n\n\n'
            "def test_placeholder() -> None:\n"
            '    """Replace with real tests."""\n'
            "    assert True\n"
        )

    @staticmethod
    def _docs_index(intent: dict) -> str:
        name = intent.get("project_name", "project")
        desc = intent.get("description", "")
        return f"# {name} Documentation\n\n{desc}\n\n## Getting Started\n\nSee the main [README](../README.md).\n"
