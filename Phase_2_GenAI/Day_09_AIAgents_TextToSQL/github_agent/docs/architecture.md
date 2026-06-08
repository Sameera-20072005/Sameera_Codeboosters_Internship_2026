# Architecture — Natural Language to GitHub Workflow Automation

## System Overview

```
┌──────────────────────────────────────────────────────────────────────────┐
│                            USER LAYER                                    │
│                                                                          │
│   Browser  ──►  Enter project description  ──►  Click Generate          │
└──────────────────────────────┬───────────────────────────────────────────┘
                               │
                               ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                      STREAMLIT UI  (app.py)                              │
│                                                                          │
│  ┌─────────────────┐  ┌──────────────────┐  ┌──────────────────────────┐│
│  │     Sidebar     │  │   Input Panel    │  │      Output Panel        ││
│  │  - Visibility   │  │  - Text area     │  │  - Extracted Intent      ││
│  │  - How it works │  │  - Run button    │  │  - Execution Plan        ││
│  │                 │  │  - Examples      │  │  - Generated Files       ││
│  └─────────────────┘  └────────┬─────────┘  │  - Repo URL             ││
│                                │             └──────────────────────────┘│
└────────────────────────────────┼─────────────────────────────────────────┘
                                 │
                                 ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                    WORKFLOW AGENT  (agent/workflow_agent.py)             │
│                                                                          │
│  WorkflowAgent.run()                                                     │
│       │                                                                  │
│       ├─► IntentParser.parse()    ──► GroqLLMService.parse_intent()      │
│       │                                                                  │
│       ├─► ProjectPlanner.plan()   ──► Returns ordered step list          │
│       │                                                                  │
│       ├─► GroqLLMService.generate_readme()                               │
│       ├─► GroqLLMService.generate_requirements()                         │
│       ├─► GroqLLMService.generate_folder_structure()                     │
│       │                                                                  │
│       ├─► FileGeneratorService.generate()  ──► Assembled files dict      │
│       │                                                                  │
│       ├─► GitHubService.create_repository()                              │
│       ├─► GitHubService.commit_files()                                   │
│       │                                                                  │
│       └─► HistoryService.save_history()                                  │
└──────────────────────────────────────────────────────────────────────────┘
                    │                        │
                    ▼                        ▼
┌──────────────────────────┐    ┌──────────────────────────────────────────┐
│     GROQ API LAYER       │    │           GITHUB API LAYER               │
│                          │    │                                          │
│  Model:                  │    │  PyGithub ──► GitHub REST API            │
│  llama-3.3-70b-versatile │    │                                          │
│                          │    │  - Create repository                     │
│  - parse_intent()        │    │  - Upload files (create/update)          │
│  - generate_readme()     │    │  - Commit with messages                  │
│  - generate_structure()  │    │  - Return html_url                       │
│  - generate_requirements │    │                                          │
└──────────────────────────┘    └──────────────────────────────────────────┘
```

## Agent Workflow (Sequence)

```
User                Streamlit        WorkflowAgent      Groq API     GitHub API
 │                      │                  │                │              │
 │──describe project──► │                  │                │              │
 │                      │──run(request)──► │                │              │
 │                      │                  │──parse_intent─►│              │
 │                      │                  │◄──intent JSON──│              │
 │                      │                  │──validate────► (local)        │
 │                      │                  │──plan()──────► (local)        │
 │                      │                  │──gen_readme───►│              │
 │                      │                  │◄──readme text──│              │
 │                      │                  │──gen_reqs─────►│              │
 │                      │                  │◄──requirements─│              │
 │                      │                  │──gen_structure►│              │
 │                      │                  │◄──file paths───│              │
 │                      │                  │──assemble_files►(local)       │
 │                      │                  │──create_repo──────────────── ►│
 │                      │                  │◄─────────────── repo object───│
 │                      │                  │──commit_files─────────────── ►│
 │                      │                  │◄──────────────── success ─────│
 │                      │                  │──save_history──►(local)       │
 │                      │◄──AgentResult────│                │              │
 │◄────repo URL─────────│                  │                │              │
```

## File Generation Workflow

```
FileGeneratorService.generate(intent)
         │
         ├─► README.md        ◄── LLM generated
         ├─► .gitignore       ◄── gitignore_template (by language)
         ├─► LICENSE          ◄── license_template (MIT)
         ├─► requirements.txt ◄── LLM generated
         ├─► src/__init__.py  ◄── static
         ├─► src/main.py      ◄── framework-aware scaffold
         │
         ├─► [if testing]
         │     tests/__init__.py
         │     tests/test_main.py  ◄── framework-aware test scaffold
         │
         ├─► [if ci_required]
         │     .github/workflows/ci.yml  ◄── workflow_template (by language)
         │
         ├─► [if docker_required]
         │     Dockerfile      ◄── docker_template (by language)
         │     .dockerignore
         │
         └─► [llm_structure extras]  ◄── LLM-suggested additional paths
```

## Component Responsibilities

| Component                      | File                            | Responsibility                              |
|--------------------------------|---------------------------------|---------------------------------------------|
| Streamlit App                  | app.py                          | UI, progress display, session state         |
| Workflow Agent                 | agent/workflow_agent.py         | Orchestration, AgentResult                  |
| Intent Parser                  | agent/intent_parser.py          | NL → structured JSON, validation            |
| Project Planner                | agent/planner.py                | Intent → ordered step list                  |
| Groq LLM Service               | services/llm_service.py         | Groq API, prompt building, JSON parsing     |
| GitHub Service                 | services/github_service.py      | Repo creation, file upload via PyGithub     |
| File Generator                 | services/file_generator.py      | Assembles all files dict from intent        |
| History Service                | services/history_service.py     | Atomic JSON persistence                     |
| README Template                | templates/readme_template.py    | Markdown README builder                     |
| Gitignore Template             | templates/gitignore_template.py | Language-specific .gitignore                |
| Workflow Template              | templates/workflow_template.py  | GitHub Actions CI YAML                      |
| Docker Template                | templates/docker_template.py    | Multi-language Dockerfile                   |
| License Template               | templates/license_template.py   | MIT License with current year               |
| Logger                         | utils/logger.py                 | Rotating 5 MB file + console logger         |
