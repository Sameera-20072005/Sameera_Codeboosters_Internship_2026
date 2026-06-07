# 🎓 Student Performance Analytics Dashboard

## 📌 Project Overview

This project performs Exploratory Data Analysis (EDA) on a student performance dataset using Python and Pandas.

The objective is to analyze academic performance, attendance trends, department-wise statistics, gender-based comparisons, and score distributions to generate meaningful insights.

---

## 🎯 Assignment Objectives

- Load and inspect dataset
- Analyze dataset structure and schema
- Perform null-value profiling
- Conduct department-wise performance analysis
- Identify top-performing students
- Compare performance across genders
- Detect score outliers
- Generate statistical insights
- Create informative visualizations

---

## 🛠 Technologies Used

- Python
- Pandas
- NumPy
- Matplotlib
- Seaborn
- Google Colab
- GitHub

---

## 📂 Repository Structure

```text
Student-Performance-Analytics-Dashboard/
│
├── data/
│   └── student_performance.csv
│
├── notebooks/
│   └── Student_Performance_EDA.ipynb
│
├── report/
│   └── EDA_Report.md
│
├── requirements.txt
│
└── README.md
```

---

## 📊 Dataset Features

| Feature | Description |
|----------|-------------|
| student_id | Unique student identifier |
| name | Student name |
| gender | Student gender |
| department | Academic department |
| attendance_percentage | Attendance percentage |
| math_score | Mathematics score |
| science_score | Science score |
| english_score | English score |
| programming_score | Programming score |

---

## 📈 Exploratory Data Analysis

### Dataset Inspection

- Shape Analysis
- Data Types
- Missing Value Analysis
- Statistical Summary

### Department-wise Analysis

- Average Score by Department
- Average Attendance by Department

### Top Performer Identification

- Score Threshold Filtering
- Top 10 Students Ranking

### Gender-wise Analysis

- Average Score Comparison
- Attendance Comparison

### Score Distribution

- Histograms
- KDE Curves

### Outlier Detection

- Boxplots
- IQR Method

### Correlation Analysis

- Attendance vs Score
- Heatmap Visualization

---

## 📷 Sample Visualizations

### Department-wise Average Score

![Department Score](visualizations/department_score.png)

### Attendance vs Performance

![Attendance](visualizations/attendance_vs_score.png)

### Correlation Heatmap

![Heatmap](visualizations/correlation_heatmap.png)

---

## 🔍 Key Findings

- Computer Science students achieved the highest average score.
- Computer Science students maintained the highest attendance percentage.
- Female students outperformed male students on average.
- Attendance showed a positive relationship with academic performance.
- The dataset contained no missing values.
- Top-performing students were identified successfully using score filtering.

---

## 🚀 How to Run

### Clone Repository

```bash
git clone https://github.com/yourusername/Student-Performance-Analytics-Dashboard.git
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Run Notebook

Open:

```text
notebooks/Student_Performance_EDA.ipynb
```

using Jupyter Notebook or Google Colab.

---

## 📄 Deliverables

- Jupyter Notebook (.ipynb)
- EDA Analysis Report (PDF)
- Visualization Assets (PNG)
- GitHub Repository with Documentation

---

## 👨‍💻 Author

Sameera T

Exploratory Data Analysis Project using Pandas