# Student Database Analytics System

## Project Overview

This project demonstrates the design and analysis of a relational database using SQLite and Python. A student performance dataset is normalized into multiple tables and analyzed using SQL queries. Analytical results are visualized using Matplotlib to generate meaningful insights.

---

## Objectives

* Create an in-memory SQLite database
* Design a normalized relational schema
* Insert and manage student records
* Perform analytical SQL operations
* Apply aggregation functions
* Execute filtering and sorting queries
* Generate visualizations using Matplotlib
* Produce a documented analytics report

---

## Technologies Used

* Python
* SQLite3
* Pandas
* NumPy
* Matplotlib
* Google Colab

---

## Database Schema

### Departments

* department_id
* department_name

### Students

* student_id
* name
* gender
* attendance_percentage
* department_id

### Scores

* student_id
* math_score
* science_score
* english_score
* programming_score

---

## SQL Concepts Demonstrated

### Aggregations

* COUNT()
* AVG()
* MAX()
* MIN()
* SUM()

### Advanced SQL

* GROUP BY
* HAVING
* Subqueries
* Filtering
* Sorting
* JOIN Operations

---

## Visualizations

The project generates the following charts:

* Department Student Count
* Department Average Score
* Gender Distribution
* Attendance Distribution
* Top 10 Students

---

## Repository Structure

Student-Database-Analytics-System/

├── data/
│ └── student_performance.csv

├── notebook/
│ └── Student_Database_Analytics.ipynb

├── requirements.txt

└── README.md

---

## How to Run

### 1. Clone Repository

```bash
git clone https://github.com/yourusername/Student-Database-Analytics-System.git
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run Notebook

Open:

```text
colab/Student_Database_Analytics.ipynb
```

or execute:

```bash
python scripts/student_database_analytics.py
```

---

## Key Findings

* Computer Science students recorded the highest average scores.
* Female students performed better on average.
* Attendance positively influenced academic performance.
* Department-wise differences were observed in both attendance and scores.

---

## Author

Sameera T

Database Analytics Project using SQLite, SQL, Pandas, and Matplotlib.
