# Architecture Diagram — LLM-Powered Code Generator

## System Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                          USER LAYER                                  │
│                                                                      │
│   Browser  ──►  Select Language + Enter Task  ──►  Click Generate   │
└──────────────────────────────┬──────────────────────────────────────┘
                               │ HTTP POST /generate (JSON)
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         FLASK LAYER  (app.py)                        │
│                                                                      │
│   ┌──────────────┐    ┌───────────────┐    ┌──────────────────────┐ │
│   │  index route │    │ /generate     │    │  /health             │ │
│   │  (GET /)     │    │  route (POST) │    │  (GET)               │ │
│   └──────────────┘    └──────┬────────┘    └──────────────────────┘ │
└──────────────────────────────┼──────────────────────────────────────┘
                               │
              ┌────────────────┼────────────────┐
              ▼                ▼                ▼
┌─────────────────┐  ┌──────────────────┐  ┌──────────────────────────┐
│  PROMPT ENGINE  │  │  LLM SERVICE     │  │  TOKEN TRACKING LAYER    │
│                 │  │                  │  │                           │
│ prompt_template │  │ llm_service.py   │  │ token_counter.py          │
│ .py             │  │                  │  │                           │
│                 │  │ - Build messages │  │ - tiktoken encoding       │
│ - Language      │  │ - Call Groq API  │  │ - Prompt token count      │
│   instructions  │  │ - Clean output   │  │ - Completion token count  │
│ - System prompt │  │ - Error handling │  │ - Total tokens            │
│ - User prompt   │  │                  │  │ - API usage fallback      │
└─────────────────┘  └────────┬─────────┘  └──────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                       GROQ API LAYER                                 │
│                                                                      │
│   Model: llama-3.3-70b-versatile                                     │
│                                                                      │
│   ┌─────────────────────────────────────────────────────────────┐   │
│   │  Groq Cloud  ──►  Chat Completions API  ──►  JSON Response  │   │
│   └─────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
                               │
              ┌────────────────┴────────────────┐
              ▼                                 ▼
┌──────────────────────────┐       ┌────────────────────────────────┐
│     LOGGING LAYER        │       │   TWILIO NOTIFICATION LAYER    │
│                          │       │                                 │
│  utils/logger.py         │       │  services/twilio_service.py    │
│                          │       │                                 │
│  - RotatingFileHandler   │       │  - SMS via Twilio REST API      │
│  - Console handler       │       │  - WhatsApp via Twilio sandbox  │
│  - logs/app.log          │       │  - Success notifications        │
│  - Per-module loggers    │       │  - Error notifications          │
│  - 5 MB rotation         │       │  - Graceful disable if uncfg'd  │
└──────────────────────────┘       └────────────────────────────────┘
```

## Data Flow

```
User Input
    │
    ▼
Input Validation (app.py)
    │
    ▼
Prompt Construction (prompt_template.py)
    │  system_prompt + user_prompt
    ▼
Groq API Call (llm_service.py)
    │  generated_code + usage object
    ▼
Token Extraction (token_counter.py)
    │  TokenUsage dataclass
    ▼
Twilio Notification (twilio_service.py)   ──►  SMS / WhatsApp
    │
    ▼
JSON Response  ──►  Browser (script.js renders code + tokens)
    │
    ▼
Logger writes to logs/app.log  (every step above)
```

## Component Responsibilities

| Component               | File                          | Responsibility                              |
|-------------------------|-------------------------------|---------------------------------------------|
| Flask App               | app.py                        | Routes, request handling, orchestration     |
| Configuration           | config.py                     | Environment variable loading & validation   |
| Prompt Builder          | services/prompt_template.py   | Language-specific prompt construction       |
| LLM Service             | services/llm_service.py       | Groq API communication & error handling     |
| Twilio Service          | services/twilio_service.py    | SMS & WhatsApp notifications                |
| Logger                  | utils/logger.py               | Rotating file + console logging             |
| Token Counter           | utils/token_counter.py        | Token counting via tiktoken or API usage    |
| Frontend Template       | templates/index.html          | Responsive HTML UI                          |
| Frontend Styles         | static/style.css              | Dark-theme responsive CSS                   |
| Frontend Logic          | static/script.js              | Fetch API, syntax highlighting, UX          |
