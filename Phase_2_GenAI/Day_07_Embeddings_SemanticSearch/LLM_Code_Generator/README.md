# ⚡ LLM-Powered Code Generator with Notifications

A production-quality Flask web application that generates Python, JavaScript, and SQL code using the Groq LLM API, with real-time SMS and WhatsApp notifications via Twilio.

---

## Features

- **Multi-language code generation** — Python, JavaScript, SQL
- **Groq LLM integration** — LLaMA 3.3 70B Versatile model
- **Twilio notifications** — SMS and WhatsApp alerts on success/failure
- **Token usage tracking** — Prompt, completion, and total token display
- **Syntax-highlighted output** — Powered by highlight.js
- **Copy to clipboard** — One-click code copying
- **Rotating log system** — Structured logs with rotation
- **Responsive dark UI** — Works on desktop and mobile
- **Production-ready structure** — Modular, OOP, type-hinted, PEP8

---

## Screenshots

> Add screenshots of the running application here.

| Input Panel | Output Panel |
|-------------|--------------|
| _(screenshot)_ | _(screenshot)_ |

---

## Project Structure

```
LLM_Code_Generator/
├── app.py                          # Flask app & routes
├── config.py                       # Environment variable configuration
├── requirements.txt
├── README.md
├── .env.example
├── services/
│   ├── llm_service.py              # Groq API integration
│   ├── twilio_service.py           # Twilio SMS & WhatsApp
│   └── prompt_template.py          # Language-specific prompt builder
├── utils/
│   ├── logger.py                   # Rotating file + console logger
│   └── token_counter.py            # tiktoken-based token tracking
├── templates/
│   └── index.html                  # Jinja2 HTML template
├── static/
│   ├── style.css                   # Dark responsive CSS
│   └── script.js                   # Fetch API + highlight.js
├── logs/
│   └── app.log                     # Application log file
└── docs/
    └── architecture_diagram.md     # System architecture
```

---

## Installation

### 1. Clone & navigate

```bash
git clone <repo-url>
cd LLM_Code_Generator
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

### 4. Configure environment variables

```bash
cp .env.example .env
# Edit .env and fill in your API keys
```

---

## Environment Variables

| Variable                  | Required | Description                                      |
|---------------------------|----------|--------------------------------------------------|
| `GROQ_API_KEY`            | ✅ Yes   | Your Groq API key                                |
| `GROQ_MODEL`              | No       | Model name (default: `llama-3.3-70b-versatile`)  |
| `SECRET_KEY`              | No       | Flask secret key                                 |
| `FLASK_DEBUG`             | No       | Enable debug mode (`True`/`False`)               |
| `TWILIO_ACCOUNT_SID`      | No       | Twilio Account SID                               |
| `TWILIO_AUTH_TOKEN`       | No       | Twilio Auth Token                                |
| `TWILIO_PHONE_NUMBER`     | No       | Your Twilio phone number                         |
| `TWILIO_WHATSAPP_NUMBER`  | No       | Twilio WhatsApp sender number                    |
| `RECIPIENT_PHONE_NUMBER`  | No       | SMS recipient number                             |
| `RECIPIENT_WHATSAPP_NUMBER` | No     | WhatsApp recipient number                        |
| `ENABLE_SMS`              | No       | Enable SMS notifications (`True`/`False`)        |
| `ENABLE_WHATSAPP`         | No       | Enable WhatsApp notifications (`True`/`False`)   |
| `LOG_LEVEL`               | No       | Logging level (default: `INFO`)                  |

---

## Running Locally

```bash
python app.py
```

Open your browser at: **http://localhost:5000**

### Production (Gunicorn)

```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

---

## API Integrations

### Groq
- Sign up at [console.groq.com](https://console.groq.com)
- Create an API key and set `GROQ_API_KEY` in `.env`
- Default model: `llama-3.3-70b-versatile`

### Twilio
- Sign up at [twilio.com](https://www.twilio.com)
- Get Account SID and Auth Token from the Twilio Console
- Enable SMS/WhatsApp by setting `ENABLE_SMS=True` / `ENABLE_WHATSAPP=True`
- For WhatsApp sandbox, join via [twilio.com/console/sms/whatsapp/sandbox](https://www.twilio.com/console/sms/whatsapp/sandbox)

---

## Health Check

```
GET /health
```

```json
{
  "status": "ok",
  "llm_ready": true,
  "model": "llama-3.3-70b-versatile"
}
```

---

## Future Improvements

- [ ] Add user authentication
- [ ] Code history / saved generations
- [ ] Support additional languages (TypeScript, Rust, Go)
- [ ] Streaming code output
- [ ] Code explanation mode
- [ ] Export to file (download as .py / .js / .sql)
- [ ] Docker containerisation
- [ ] Rate limiting per IP
- [ ] Model selection dropdown

---

## License

MIT License — feel free to use and modify.
