# Weather Data ETL

## Project Overview

This project demonstrates a complete ETL (Extract, Transform, Load) pipeline using weather data obtained from a REST API. The extracted JSON data is normalized, cleaned, transformed into a structured format, and exported as an analysis-ready CSV dataset.

The project showcases API integration, JSON processing, data cleaning techniques, and data export operations using Python and Pandas.

---

## Objectives

* Extract weather data from a REST API
* Parse and normalize JSON responses
* Handle missing values
* Perform data type conversions
* Remove duplicate records
* Create a structured tabular dataset
* Export cleaned data to CSV format
* Document the ETL workflow

---

## Technologies Used

* Python
* Pandas
* Requests
* JSON
* Google Colab

---

## ETL Workflow

### Extract

Weather data is retrieved from the Open-Meteo REST API.

### Transform

The extracted JSON data is:

* Normalized into tabular format
* Cleaned for missing values
* Type-casted to appropriate data types
* Deduplicated

### Load

The cleaned dataset is exported as a CSV file for further analysis.

---

## Project Structure

Weather-Data-ETL/

├── data/
│ ├── raw_weather.json
│ └── cleaned_weather.csv

├── notebook/
│ └── Weather_ETL.ipynb

├── README.md

└── requirements.txt

---

## Output Files

### Raw Dataset

* raw_weather.json

### Cleaned Dataset

* cleaned_weather.csv

---

## Data Cleaning Operations

* Missing value handling
* Data type conversion
* Duplicate removal
* Schema normalization

---

## Sample Output Schema

| Column        | Description            |
| ------------- | ---------------------- |
| time          | Observation Time       |
| temperature   | Temperature            |
| windspeed     | Wind Speed             |
| winddirection | Wind Direction         |
| weathercode   | Weather Condition Code |

---

## How to Run

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Run Notebook

Open:

```text
Weather_ETL.ipynb
```

or execute:

```bash
python weather_etl.py
```

---

## Learning Outcomes

* REST API consumption
* JSON parsing and normalization
* ETL pipeline implementation
* Data cleaning and transformation
* Structured data export

---

## Author

Sameera T

Weather Data ETL Project using Python and Pandas
