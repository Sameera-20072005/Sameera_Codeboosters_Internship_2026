# ✍️ Multi-Platform Content Engine

A production-quality Streamlit web application that generates platform-specific social media content using LangChain and Groq's LLaMA 3.3 model.

---

## Features

- **5 platform support** — LinkedIn, Instagram, Facebook, X (Twitter), YouTube
- **LangChain chains** — Dedicated prompt chain per platform
- **Groq LLM** — LLaMA 3.3 70B Versatile for fast, high-quality output
- **Tone & length control** — Professional / Friendly / Casual / Humorous × Short / Medium / Long
- **Content analytics** — Word, character, sentence, and hashtag counts
- **Export options** — Download as TXT, JSON, or CSV
- **Generation history** — JSON-backed persistent history with clear option
- **Rotating logs** — Full audit trail in `logs/app.log`
- **Modular architecture** — Clean separation of chains, services, and utilities

---

## Screenshots

> Add screenshots of the running application here.

| Platform Selector | Generated Content | Analytics |
|-------------------|-------------------|-----------|
| _(screenshot)_    | _(screenshot)_    | _(screenshot)_ |

---

## Project Structure

```
content_engine/
├── app.py                        # Streamlit entry point
├── requirements.txt
├── README.md
├── .env.example
├── chains/
│   ├── linkedin_chain.py
│   ├── instagram_chain.py
│   ├── facebook_chain.py
│   ├── twitter_chain.py
│   └── youtube_chain.py
├── services/
│   ├── groq_service.py           # Groq API integration
│   ├── history_service.py        # JSON history persistence
│   └── export_service.py         # TXT / JSON / CSV export
├── templates/
│   └── prompts.py                # LangChain PromptTemplates
├── utils/
│   ├── analytics.py              # Content metrics
│   └── logger.py                 # Rotating logger
├── data/
│   └── history.json              # Persisted generation history
├── logs/
│   └── app.log                   # Application logs
└── docs/
    └── architecture.md           # System architecture
```

---

## Installation

### 1. Clone & navigate

```bash
git clone <repo-url>
cd content_engine
```

### 2. Create virtual environment

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## Environment Setup

```bash
cp .env.example .env
```

Edit `.env`:

```env
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile
LOG_LEVEL=INFO
```

Get your free Groq API key at [console.groq.com](https://console.groq.com).

---

## Running the App

```bash
streamlit run app.py
```

Open your browser at: **http://localhost:8501**

---

## Architecture

```
User ──► Streamlit UI ──► Platform Chain ──► PromptTemplate ──► Groq LLM
                                                                     │
                                              ┌──────────────────────┤
                                              ▼                      ▼
                                          Analytics             History + Export
```

See [docs/architecture.md](docs/architecture.md) for the full diagram.

---

## API Integrations

### Groq
- Sign up at [console.groq.com](https://console.groq.com)
- Set `GROQ_API_KEY` in your `.env`
- Model: `llama-3.3-70b-versatile`

---

## Future Enhancements

- [ ] Image prompt generation alongside text
- [ ] Scheduled content calendar
- [ ] Multi-language support
- [ ] A/B variant generation (generate 2 versions)
- [ ] Direct platform publishing via APIs
- [ ] User authentication and saved profiles
- [ ] Docker containerisation

---

## License

MIT License
