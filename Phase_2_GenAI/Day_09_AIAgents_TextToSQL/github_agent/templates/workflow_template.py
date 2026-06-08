"""
GitHub Actions workflow template module.
Generates CI workflow YAML for supported languages.

NOTE: These are plain string constants — NOT f-strings or PromptTemplates.
      GitHub Actions expressions use ${{ }} which must appear literally.
      Single braces {{ }} in a plain string literal render as {{ }} — correct.
"""

from __future__ import annotations

# ── Python ─────────────────────────────────────────────────────────────────────
_PYTHON_WORKFLOW = """\
name: CI

on:
  push:
    branches: [ main, master ]
  pull_request:
    branches: [ main, master ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.11", "3.12"]

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      - name: Lint with flake8
        run: |
          pip install flake8
          flake8 src/ --max-line-length=120 --ignore=E501

      - name: Run tests
        run: |
          pip install pytest pytest-cov
          pytest tests/ -v --cov=src --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v4
        with:
          file: ./coverage.xml
"""

# ── Node.js / TypeScript ───────────────────────────────────────────────────────
_NODE_WORKFLOW = """\
name: CI

on:
  push:
    branches: [ main, master ]
  pull_request:
    branches: [ main, master ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        node-version: [18.x, 20.x]

    steps:
      - uses: actions/checkout@v4

      - name: Use Node.js ${{ matrix.node-version }}
        uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node-version }}
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Run tests
        run: npm test

      - name: Build
        run: npm run build --if-present
"""

# ── Java ───────────────────────────────────────────────────────────────────────
_JAVA_WORKFLOW = """\
name: CI

on:
  push:
    branches: [ main, master ]
  pull_request:
    branches: [ main, master ]

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Set up JDK 17
        uses: actions/setup-java@v4
        with:
          java-version: '17'
          distribution: 'temurin'

      - name: Build with Maven
        run: mvn --batch-mode --update-snapshots package

      - name: Run tests
        run: mvn test
"""

# ── Generic fallback ───────────────────────────────────────────────────────────
_GENERIC_WORKFLOW = """\
name: CI

on:
  push:
    branches: [ main, master ]
  pull_request:
    branches: [ main, master ]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Build
        run: echo "Add your build steps here"
"""

_LANGUAGE_MAP: dict[str, str] = {
    "python":     _PYTHON_WORKFLOW,
    "javascript": _NODE_WORKFLOW,
    "typescript": _NODE_WORKFLOW,
    "java":       _JAVA_WORKFLOW,
}


def build_workflow(language: str) -> str:
    """
    Return a GitHub Actions CI workflow YAML for the given language.

    Args:
        language: Programming language (case-insensitive).

    Returns:
        YAML string for .github/workflows/ci.yml.
    """
    return _LANGUAGE_MAP.get(language.lower(), _GENERIC_WORKFLOW)
