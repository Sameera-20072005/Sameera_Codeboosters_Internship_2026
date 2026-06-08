"""
README template module.
Generates a structured README.md string for a given project intent.
"""

from __future__ import annotations


def build_readme(intent: dict) -> str:
    """
    Build a complete README.md from a parsed project intent dict.

    Args:
        intent: Parsed intent dictionary from IntentParser.

    Returns:
        Markdown string for README.md.
    """
    name        = intent.get("project_name", "my-project")
    description = intent.get("description", "A software project.")
    language    = intent.get("language", "Python")
    framework   = intent.get("framework", "")
    database    = intent.get("database", "")
    docker      = intent.get("docker_required", False)
    ci          = intent.get("ci_required", False)
    testing     = intent.get("testing_required", False)

    tech_stack = f"- **Language:** {language}\n"
    if framework:
        tech_stack += f"- **Framework:** {framework}\n"
    if database:
        tech_stack += f"- **Database:** {database}\n"
    if docker:
        tech_stack += "- **Containerisation:** Docker\n"
    if ci:
        tech_stack += "- **CI/CD:** GitHub Actions\n"

    test_section = (
        "\n## Running Tests\n\n"
        "```bash\npip install -r requirements.txt\npytest tests/\n```\n"
        if testing else ""
    )

    docker_section = (
        "\n## Docker\n\n"
        "```bash\ndocker build -t {name} .\ndocker run -p 8000:8000 {name}\n```\n".format(name=name)
        if docker else ""
    )

    return f"""# {name}

{description}

## Tech Stack

{tech_stack.strip()}

## Installation

```bash
git clone <repo-url>
cd {name}
python -m venv venv
venv\\Scripts\\activate   # Windows
source venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
```

## Usage

```bash
python src/main.py
```
{test_section}{docker_section}
## Project Structure

```
{name}/
├── src/          # Application source code
├── tests/        # Test suite
├── docs/         # Documentation
└── README.md
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License — see [LICENSE](LICENSE) for details.
"""
