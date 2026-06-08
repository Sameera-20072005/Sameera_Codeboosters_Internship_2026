# 🤖 Natural Language to GitHub Workflow Automation

An autonomous AI Agent that converts a plain English project description into a fully scaffolded, production-ready GitHub repository — complete with source code, tests, CI/CD, Docker, and documentation.

---

## Features

- **Natural language parsing** — Describe your project in plain English; the agent extracts all requirements
- **Autonomous planning** — Dynamically builds an execution plan based on your requirements
- **Multi-language support** — Python, JavaScript/TypeScript, Java, and more
- **Full file scaffolding** — README, .gitignore, LICENSE, src/, tests/, docs/
- **GitHub Actions CI** — Auto-generated language-specific workflows
- **Docker support** — Multi-stage Dockerfiles per language
- **Direct GitHub push** — Creates repo and commits everything via PyGithub
- **Generation history** — Persistent JSON-backed run history
- **Streamlit UI** — Clean, interactive web interface with live agent log

---

## Architecture

```
User ──► Streamlit UI ──► WorkflowAgent ──► IntentParser ──► Groq LLM
                                    │
                                    ├──► ProjectPlanner
                                    ├──► FileGeneratorService
                                    ├──► GitHubService ──► GitHub API
                                    └──► HistoryService
```

See [docs/architecture.md](docs/architecture.md) for the full ASCII diagram.

---

## Project Structure

```
github_agent/
├── app.py                          # Streamlit entry point
├── requirements.txt
├── README.md
├── .env.example
├── agent/
│   ├── workflow_agent.py           # Main orchestrator
│   ├── planner.py                  # Execution plan builder
│   └── intent_parser.py            # NL → structured JSON
├── services/
│   ├── llm_service.py              # Groq API integration
│   ├── github_service.py           # PyGithub integration
│   ├── file_generator.py           # File assembly service
│   └── history_service.py          # JSON history persistence
├── templates/
│   ├── readme_template.py
│   ├── gitignore_template.py
│   ├── workflow_template.py
│   ├── docker_template.py
│   └── license_template.py
├── utils/
│   └── logger.py                   # Rotating logger
├── data/
│   └── history.json
├── logs/
│   └── agent.log
└── docs/
    └── architecture.md
```

---

## Setup

### 1. Clone & navigate

```bash
git clone <repo-url>
cd github_agent
```

### 2. Create virtual environment

```bash
python -m venv venv
venv\Scripts\activate      # Windows
source venv/bin/activate   # macOS/Linux
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment

```bash
cp .env.example .env
```

Edit `.env` with your keys.

---

## Environment Variables

| Variable        | Required | Description                                          |
|-----------------|----------|------------------------------------------------------|
| `GROQ_API_KEY`  | ✅ Yes   | Groq API key from [console.groq.com](https://console.groq.com) |
| `GITHUB_TOKEN`  | ✅ Yes   | GitHub PAT with `repo` scope — [create one](https://github.com/settings/tokens/new) |
| `GROQ_MODEL`    | No       | Model name (default: `llama-3.3-70b-versatile`)      |
| `LOG_LEVEL`     | No       | Logging level (default: `INFO`)                      |

---

## Running the Application

```bash
python -m streamlit run app.py
```

Open **http://localhost:8501**

---

## Example Usage

**Input:**
> "Create a Python Flask Todo REST API with SQLite, GitHub Actions CI/CD, pytest tests, and Docker support."

**Output:**
- ✅ GitHub repository created
- 📁 12 files committed
- 🔗 `https://github.com/your-username/flask-todo-rest-api`

Files generated:
```
README.md
.gitignore
LICENSE
requirements.txt
src/__init__.py
src/main.py
tests/__init__.py
tests/test_main.py
.github/workflows/ci.yml
Dockerfile
.dockerignore
docs/index.md
```

---

## Screenshots

> Add screenshots of the running application here.

---

## Future Improvements

- [ ] Support for multiple branches and PR creation
- [ ] GitHub Pages deployment automation
- [ ] Database migration file generation
- [ ] OpenAPI/Swagger spec generation
- [ ] Support for monorepo structures
- [ ] Repository template cloning
- [ ] Slack/email notifications on completion

---

## License

MIT License
