# Full-Cycle Kaggle Dataset Analytics

## Project Overview

This project demonstrates a complete data analytics workflow using a real-world dataset obtained through the Kaggle API. The Netflix Movies and TV Shows dataset is used to perform exploratory data analysis, data cleaning, SQLite database integration, SQL analytics, and dashboard creation.

The project follows the complete analytics lifecycle from data acquisition to insight generation.

---

## Objectives

* Download a real-world dataset using the Kaggle API
* Perform exploratory data profiling
* Clean and preprocess the dataset
* Handle missing values and duplicates
* Normalize selected attributes
* Load cleaned data into a SQLite database
* Execute SQL analytical queries
* Create visual dashboards and business insights

---

## Dataset Information

Dataset: Netflix Movies and TV Shows

Source: Kaggle

Main Columns:

* show_id
* type
* title
* director
* cast
* country
* date_added
* release_year
* rating
* duration
* listed_in
* description

---

## Project Workflow

### 1. Dataset Acquisition

* Kaggle API configuration
* Dataset download
* Dataset extraction

### 2. Exploratory Data Analysis

* Dataset shape
* Data types
* Missing values
* Unique value counts
* Statistical summaries

### 3. Data Cleaning

* Missing value imputation
* Duplicate removal
* Data normalization
* Data validation

### 4. SQLite Integration

* Database creation
* Table design
* Data loading into SQLite

### 5. SQL Analytics

Analytical queries include:

* Content type distribution
* Top content-producing countries
* Rating distribution
* Recent releases
* Content volume analysis

### 6. Visualization

Visual dashboards created using Matplotlib:

* Movies vs TV Shows
* Top Countries by Content
* Rating Distribution
* Missing Value Analysis

---

## Project Structure

Full-Cycle-Kaggle-Dataset-Analytics/

├── data/
│   ├── netflix_titles.csv
│   └── netflix_shows.zip
│
├── notebooks/
│   └── Kaggle_Dataset_Analytics.ipynb
│
├── sql/
│   └── analytical_queries.sql
|
├── README.md
│
└── requirements.txt

---

## Data Cleaning Techniques Applied

### Missing Value Handling

* Director → Unknown
* Cast → Not Available
* Country → Unknown
* Rating → Mode value

### Duplicate Removal

Duplicate records were identified and removed.

### Normalization

Release year was normalized using Min-Max Scaling.

---

## SQLite Database Design

Database: analytics.db

Table: Netflix

The cleaned dataset is loaded into a SQLite table for SQL-based analysis.

---

## Sample SQL Queries

### Content Type Distribution

SELECT type,
COUNT(*) AS total
FROM Netflix
GROUP BY type;

### Top Countries

SELECT country,
COUNT(*) AS total
FROM Netflix
GROUP BY country
ORDER BY total DESC
LIMIT 10;

### Rating Distribution

SELECT rating,
COUNT(*) AS total
FROM Netflix
GROUP BY rating;

---

## Key Insights

* Movies significantly outnumber TV Shows.
* The United States contributes the largest amount of content.
* TV-MA and TV-14 are the most frequent content ratings.
* Missing values were primarily observed in director and cast columns.
* Content additions increased substantially after 2015.

---

## Technologies Used

* Python
* Pandas
* NumPy
* SQLite
* Matplotlib
* Seaborn
* Scikit-Learn
* Kaggle API
* Google Colab

---

## How to Run

1. Configure Kaggle API credentials.
2. Download dataset using Kaggle API.
3. Run the notebook:
   Kaggle_Dataset_Analytics.ipynb
4. Generate cleaned dataset and database.
5. Execute SQL queries.
6. Generate visualizations and report.

---

## Deliverables

* Raw Dataset
* Cleaned Dataset
* SQLite Database
* SQL Query File
* Analytics Report
* Visualizations
* Jupyter Notebook

---

## Author

Sameera T

Full-Cycle Kaggle Dataset Analytics Project
