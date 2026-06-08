# Architecture — Multi-Platform Content Engine

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER LAYER                               │
│                                                                 │
│   Browser  ──►  Enter Topic + Select Platform/Tone/Length       │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                     STREAMLIT UI  (app.py)                      │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────────────────┐ │
│  │   Sidebar    │  │  Main Input  │  │    Output Panel       │ │
│  │  - Platform  │  │  - Topic     │  │  - Generated Content  │ │
│  │  - Length    │  │  - Generate  │  │  - Analytics          │ │
│  │  - Tone      │  │    Button    │  │  - Export Buttons     │ │
│  └──────────────┘  └──────┬───────┘  └───────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                   PLATFORM CHAIN LAYER                          │
│                                                                 │
│   linkedin_chain.py   instagram_chain.py   facebook_chain.py   │
│   twitter_chain.py    youtube_chain.py                         │
│                                                                 │
│   Each chain:                                                   │
│   1. Receives (topic, tone, length)                             │
│   2. Fetches platform PromptTemplate                            │
│   3. Renders the prompt                                         │
│   4. Calls GroqService.generate_content()                       │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                   PROMPT ENGINE  (templates/prompts.py)         │
│                                                                 │
│   LangChain PromptTemplate per platform                         │
│   Variables: {topic}, {tone}, {length}                          │
│   Platform persona + structural requirements embedded           │
└──────────────────────────┬──────────────────────────────────────┘
                           │  Rendered prompt string
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                   GROQ API LAYER  (services/groq_service.py)    │
│                                                                 │
│   Model: llama-3.3-70b-versatile                                │
│   ┌───────────────────────────────────────────────────────┐    │
│   │  Groq Cloud  ──►  Chat Completions  ──►  Response     │    │
│   └───────────────────────────────────────────────────────┘    │
│   - Auth error handling                                         │
│   - Rate limit handling                                         │
│   - Connection error handling                                   │
│   - Markdown fence stripping                                    │
└──────────────────────────┬──────────────────────────────────────┘
                           │  Generated content string
          ┌────────────────┼──────────────────┐
          ▼                ▼                  ▼
┌──────────────┐  ┌────────────────┐  ┌──────────────────────┐
│  ANALYTICS   │  │    HISTORY     │  │   EXPORT LAYER       │
│  LAYER       │  │    LAYER       │  │                      │
│              │  │                │  │  export_service.py   │
│analytics.py  │  │history_service │  │  - export_txt()      │
│              │  │.py             │  │  - export_json()     │
│- word count  │  │                │  │  - export_csv()      │
│- char count  │  │- save_content()│  │                      │
│- sentences   │  │- load_history()│  │  Streamlit download  │
│- hashtags    │  │- clear_history │  │  buttons             │
└──────────────┘  │  data/         │  └──────────────────────┘
                  │  history.json  │
                  └────────────────┘
                           │
                           ▼
                  ┌────────────────┐
                  │  LOGGING LAYER │
                  │  utils/logger  │
                  │  logs/app.log  │
                  │  (all layers)  │
                  └────────────────┘
```

## Request Flow

```
1. User selects platform, tone, length in sidebar
2. User enters topic in main input area
3. User clicks "Generate" button
4. app.py validates input (non-empty topic)
5. Correct platform chain is selected (e.g. LinkedInChain)
6. Chain fetches the PromptTemplate from templates/prompts.py
7. Chain renders the prompt with {topic}, {tone}, {length}
8. Chain calls GroqService.generate_content(prompt)
9. Groq API returns completion text
10. GroqService strips markdown fences and returns clean string
11. app.py stores content in st.session_state
12. HistoryService.save_content() appends to data/history.json
13. UI renders content in output panel
14. analytics.py computes and displays stats
15. User optionally downloads TXT / JSON / CSV via ExportService
```

## Component Responsibilities

| Component                        | File                           | Responsibility                           |
|----------------------------------|--------------------------------|------------------------------------------|
| Streamlit App                    | app.py                         | UI, routing, session state, orchestration |
| LinkedIn Chain                   | chains/linkedin_chain.py       | Professional post generation             |
| Instagram Chain                  | chains/instagram_chain.py      | Caption + hashtag generation             |
| Facebook Chain                   | chains/facebook_chain.py       | Community post generation                |
| Twitter Chain                    | chains/twitter_chain.py        | Tweet generation                         |
| YouTube Chain                    | chains/youtube_chain.py        | Title + description generation           |
| Prompt Templates                 | templates/prompts.py           | LangChain PromptTemplate definitions     |
| Groq Service                     | services/groq_service.py       | Groq API client and error handling       |
| History Service                  | services/history_service.py    | JSON-based persistence                   |
| Export Service                   | services/export_service.py     | TXT, JSON, CSV export                    |
| Analytics                        | utils/analytics.py             | Content metrics computation              |
| Logger                           | utils/logger.py                | Rotating file + console logging          |
