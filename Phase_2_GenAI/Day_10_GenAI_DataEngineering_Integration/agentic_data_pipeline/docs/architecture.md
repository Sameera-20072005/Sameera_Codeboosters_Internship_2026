# Architecture — Agentic Data Engineering Pipeline

## System Overview

```
┌──────────────────────────────────────────────────────────────────────────┐
│                          USER LAYER                                      │
│   Browser ──► Enter dataset description ──► Select domain & record count │
└──────────────────────────────┬───────────────────────────────────────────┘
                               │
                               ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                     STREAMLIT UI  (app.py)                               │
│  Sidebar: Domain selector, Record count slider                           │
│  Main: Description input, Run Pipeline button                            │
│  Output: Dataset preview, KPIs, Spark metrics, Insights, Downloads       │
└──────────────────────────────┬───────────────────────────────────────────┘
                               │
                               ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                    AGENT PIPELINE (6 Agents)                             │
│                                                                          │
│  1. DatasetAgent           ──► Groq LLM ──► Raw CSV                     │
│         │                                                                │
│         ▼                                                                │
│  2. CleaningAgent          ──► Pandas ──► Cleaned CSV                   │
│         │                                                                │
│         ▼                                                                │
│  3. TransformationAgent    ──► Scikit-Learn ──► Transformed CSV         │
│         │                                                                │
│         ▼                                                                │
│  4. SparkAgent             ──► PySpark / Pandas fallback ──► Metrics    │
│         │                                                                │
│         ▼                                                                │
│  5. AnalyticsAgent         ──► KPIs + Groq LLM ──► Insights             │
│         │                                                                │
│         ▼                                                                │
│  6. ReportAgent            ──► Markdown + ReportLab PDF                 │
└──────────────────────────────────────────────────────────────────────────┘
```

## Agent Responsibilities

| Agent                | Class                  | Input              | Output                         |
|----------------------|------------------------|--------------------|--------------------------------|
| DatasetAgent         | DatasetAgent           | NL description     | Raw CSV DataFrame              |
| CleaningAgent        | CleaningAgent          | Raw DataFrame      | Cleaned DataFrame + Report     |
| TransformationAgent  | TransformationAgent    | Cleaned DataFrame  | Scaled/Encoded DataFrame       |
| SparkAgent           | SparkAgent             | Transformed DF     | Aggregation Metrics JSON       |
| AnalyticsAgent       | AnalyticsAgent         | Cleaned DF + KPIs  | KPI JSON + LLM Insights        |
| ReportAgent          | ReportAgent            | All outputs        | report.md + report.pdf         |

## Data Flow

```
User NL Request
      │
      ▼
GroqService.generate_dataset()  ──► Raw CSV string
      │
      ▼
DatasetAgent._parse_csv()       ──► pd.DataFrame (raw)
      │  saved to: data/raw/
      ▼
CleaningAgent.clean_data()
  ├─ drop_duplicates()
  ├─ fillna (median / mode)
  ├─ standardise column names
  └─ drop all-null columns     ──► pd.DataFrame (cleaned)
      │  saved to: data/cleaned/
      ▼
TransformationAgent
  ├─ engineer_features()       ──► log transforms, CLV, annual revenue
  ├─ encode_features()         ──► LabelEncoder / OneHotEncoder / drop
  └─ scale_features()          ──► StandardScaler
      │  saved to: data/transformed/
      ▼
SparkAgent (or Pandas fallback)
  ├─ null counts per column
  ├─ mean / std / min / max per numeric col
  ├─ top 5 category values
  └─ group-by aggregation      ──► SparkMetrics dict
      │  saved to: data/spark_outputs/
      ▼
AnalyticsAgent
  ├─ calculate_kpis()          ──► KPI dict  →  reports/kpis.json
  └─ generate_insights()       ──► Groq LLM  →  Markdown insights
      │
      ▼
ReportAgent
  ├─ generate_markdown()       ──► reports/report.md
  └─ generate_pdf()            ──► reports/report.pdf
```

## Spark Workflow

```
SparkAgent.initialize_spark()
      │
      ├─ Success ──► PySpark local[*] session
      │                    │
      │             createDataFrame(df)
      │             ├─ sdf.count() / schema
      │             ├─ null expressions via F.count(F.when(...))
      │             ├─ mean / stddev / min / max per numeric col
      │             ├─ groupBy().count() for string cols
      │             └─ collect() → Python dicts
      │
      └─ Failure ──► Pandas fallback (equivalent computation)
```

## Service Dependencies

```
GroqService        ◄── GROQ_API_KEY (.env)
StorageService     ◄── filesystem (relative paths from project root)
DatasetAgent       ◄── GroqService, StorageService
CleaningAgent      ◄── StorageService
TransformationAgent◄── StorageService
SparkAgent         ◄── StorageService
AnalyticsAgent     ◄── GroqService, StorageService
ReportAgent        ◄── StorageService, ReportLab (optional)
```
