"""
.gitignore template module.
Returns language-appropriate .gitignore content.
"""

from __future__ import annotations

_PYTHON_GITIGNORE = """\
# Python
__pycache__/
*.py[cod]
*.pyo
*.pyd
.Python
pip-log.txt
pip-delete-this-directory.txt

# Virtual environments
venv/
env/
ENV/
.venv/

# Environment variables
.env
.env.*

# Distribution / packaging
dist/
build/
*.egg-info/
*.egg

# Testing
.pytest_cache/
.coverage
htmlcov/

# IDEs
.vscode/
.idea/

# Jupyter
.ipynb_checkpoints/

# Logs
*.log
logs/

# OS
.DS_Store
Thumbs.db
"""

_NODE_GITIGNORE = """\
# Node
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*
.npm
.yarn-integrity

# Build
dist/
build/
.next/
.nuxt/

# Environment
.env
.env.*

# Logs
*.log
logs/

# OS
.DS_Store
Thumbs.db
"""

_JAVA_GITIGNORE = """\
# Java / Maven / Gradle
target/
*.class
*.jar
*.war
*.ear
.gradle/
build/

# IDE
.idea/
*.iml
.eclipse/
.settings/
.classpath
.project

# Environment
.env

# OS
.DS_Store
Thumbs.db
"""

_GENERIC_GITIGNORE = """\
# Environment
.env
.env.*

# Logs
*.log
logs/

# OS
.DS_Store
Thumbs.db
Thumbs.db:encryptable
desktop.ini
"""

_LANGUAGE_MAP: dict[str, str] = {
    "python":     _PYTHON_GITIGNORE,
    "javascript": _NODE_GITIGNORE,
    "typescript": _NODE_GITIGNORE,
    "java":       _JAVA_GITIGNORE,
}


def build_gitignore(language: str) -> str:
    """
    Return a .gitignore string appropriate for the given language.

    Args:
        language: Programming language string (case-insensitive).

    Returns:
        .gitignore content string.
    """
    return _LANGUAGE_MAP.get(language.lower(), _GENERIC_GITIGNORE)
