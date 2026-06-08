# ⚙️ Agentic Data Engineering Pipeline

An autonomous AI-powered data engineering pipeline that converts a natural language dataset request into a fully processed, analysed, and reported dataset — end to end.

---

## Features

- **6 Autonomous Agents** — Dataset → Cleaning → Transformation → Spark → Analytics → Report
- **LLM-powered generation** — Groq Llama 3.3 70B generates synthetic datasets from plain English
- **Automatic cleaning** — Deduplication, missing-value imputation, column standardisation
- **Feature engineering** — Log transforms, CLV, annual revenue, tenure ratios
- **Categorical encoding** — LabelEncoder, OneHotEncoder (auto-selected by cardinality)
- **Feature scaling** — StandardScaler across all numeric columns
- **Distributed processing** — PySpark local mode with transparent Pandas fallback
- **KPI dashboard** — Record counts, revenue, churn rate, memory usage, distributions
- **AI insights** — LLM-generated business insights from computed KPIs
- **Dual reports** — Markdown report + PDF report (ReportLab)
- **Streamlit UI** — Domain selector, record count slider, live progress bar, download buttons

---

## Architecture

```
User ──► Streamlit UI
              │
         DatasetAgent  ──► Groq LLM ──► Raw CSV
              │
         CleaningAgent ──► Pandas dedup + impute
              │
         TransformationAgent ──► Scikit-Learn encode + scale
              │
         SparkAgent ──► PySpark / Pandas fallback
              │
         AnalyticsAgent ──► KPIs + Groq insights
              │
         ReportAgent ──► report.md + report.pdf
```

See [docs/architecture.md](docs/architecture.md) for the full diagram.

---

## Project Structure

```
agentic_data_pipeline/
├── app.py                          # Streamlit entry point
├── requirements.txt
├── README.md
├── .env.example
├── agents/
│   ├── dataset_agent.py            # LLM-powered CSV generation
│   ├── cleaning_agent.py           # Dedup, impute, standardise
│   ├── transformation_agent.py     # Feature eng + encode + scale
│   ├── spark_agent.py              # PySpark / Pandas aggregations
│   ├── analytics_agent.py          # KPIs + LLM insights
│   └── report_agent.py             # Markdown + PDF reports
├── services/
│   ├── llm_service.py              # Groq API service
│   └── storage_service.py          # CSV / JSON / text I/O
├── utils/
│   └── logger.py                   # Rotating logger
├── data/
│   ├── raw/                        # Generated datasets
│   ├── cleaned/                    # Cleaned datasets
│   ├── transformed/                # Transformed datasets
│   └── spark_outputs/              # Spark/Pandas metrics
├── reports/
│   ├── kpis.json
│   ├── report.md
│   └── report.pdf
├── docs/
│   └── architecture.md
└── logs/
    └── pipeline.log
```

---

## Installation

```bash
cd agentic_data_pipeline
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # macOS/Linux
pip install -r requirements.txt
```

---

## Environment Setup

```bash
cp .env.example .env
```

Edit `.env`:
```
GROQ_API_KEY=your_groq_api_key_here
```

Get your free Groq API key at [console.groq.com](https://console.groq.com).

---

## Running the Pipeline

```bash
python -m streamlit run app.py
```

Open **http://localhost:8501**

---

## Example Workflow

**Input:**
> "Generate a telecom customer churn dataset with 150 records."

**Pipeline execution:**
1. DatasetAgent → 150-row CSV with 11 columns
2. CleaningAgent → 0 duplicates removed, missing values imputed
3. TransformationAgent → 3 new features, 4 encoded columns, 14 scaled
4. SparkAgent (Pandas) → numeric summary, top categories
5. AnalyticsAgent → churn rate: 28%, avg monthly charge: $64.2
6. ReportAgent → `report.md` + `report.pdf`

---

## Notes on PySpark

PySpark requires **Java 8, 11, or 17** to be installed and on `PATH`.
If Java is not available, SparkAgent automatically falls back to an equivalent
Pandas computation — the pipeline runs successfully either way.

---

## Screenshots

> Add screenshots here after running the application.

---

## Future Enhancements

- [ ] Real dataset ingestion from S3 / GCS
- [ ] Automated chart generation (matplotlib / plotly)
- [ ] ML model training and evaluation agent
- [ ] Multi-dataset comparison mode
- [ ] Email report delivery
- [ ] Docker containerisation

---

## License

MIT License
