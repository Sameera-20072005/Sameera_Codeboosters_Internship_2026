"""
Dockerfile template module.
Generates language-appropriate Dockerfile content.
"""

from __future__ import annotations

_PYTHON_DOCKERFILE = """\
FROM python:3.11-slim

WORKDIR /app

# Install dependencies first for better layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY src/ ./src/

# Create non-root user for security
RUN adduser --disabled-password --gecos '' appuser
USER appuser

EXPOSE 8000

CMD ["python", "src/main.py"]
"""

_NODE_DOCKERFILE = """\
FROM node:20-alpine

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm ci --only=production

# Copy source
COPY src/ ./src/

# Non-root user
RUN addgroup -S appgroup && adduser -S appuser -G appgroup
USER appuser

EXPOSE 3000

CMD ["node", "src/index.js"]
"""

_JAVA_DOCKERFILE = """\
# Build stage
FROM maven:3.9-eclipse-temurin-17 AS build
WORKDIR /app
COPY pom.xml .
COPY src ./src
RUN mvn package -DskipTests

# Runtime stage
FROM eclipse-temurin:17-jre-jammy
WORKDIR /app
COPY --from=build /app/target/*.jar app.jar

RUN adduser --disabled-password --gecos '' appuser
USER appuser

EXPOSE 8080
ENTRYPOINT ["java", "-jar", "app.jar"]
"""

_GENERIC_DOCKERFILE = """\
FROM ubuntu:22.04

WORKDIR /app

COPY . .

EXPOSE 8000

CMD ["echo", "Configure your run command here"]
"""

_LANGUAGE_MAP: dict[str, str] = {
    "python":     _PYTHON_DOCKERFILE,
    "javascript": _NODE_DOCKERFILE,
    "typescript": _NODE_DOCKERFILE,
    "java":       _JAVA_DOCKERFILE,
}

_DOCKERIGNORE = """\
.git
.gitignore
.env
.env.*
__pycache__/
*.pyc
*.pyo
node_modules/
venv/
env/
.venv/
*.log
logs/
.DS_Store
Thumbs.db
README.md
docs/
tests/
"""


def build_dockerfile(language: str) -> str:
    """
    Return a Dockerfile string for the given language.

    Args:
        language: Programming language (case-insensitive).

    Returns:
        Dockerfile content string.
    """
    return _LANGUAGE_MAP.get(language.lower(), _GENERIC_DOCKERFILE)


def build_dockerignore() -> str:
    """Return a standard .dockerignore content string."""
    return _DOCKERIGNORE
