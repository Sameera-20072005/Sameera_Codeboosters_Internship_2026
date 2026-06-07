# Employee Salary ETL

## Project Overview

This project implements an ETL pipeline for employee salary data stored in an Excel file. The dataset undergoes cleaning, transformation, and business metric calculations before being exported as an analysis-ready dataset.

The project demonstrates Excel ingestion, data quality improvement, salary computation, and reporting using Python and Pandas.

---

## Objectives

* Read employee salary data from Excel
* Remove duplicate records
* Handle missing salary values
* Compute Gross Salary
* Calculate Tax deductions
* Calculate Net Salary
* Generate summary statistics
* Export cleaned datasets and reports

---

## Technologies Used

* Python
* Pandas
* NumPy
* OpenPyXL
* Google Colab

---

## ETL Workflow

### Extract

Read employee salary data from Excel.

### Transform

The dataset is processed through:

* Duplicate removal
* Missing value imputation
* Salary calculations
* Summary generation

### Load

The cleaned dataset and summary report are exported to Excel and CSV formats.

---

## Project Structure

Employee-Salary-ETL/

├── data/
│ ├── employee_salary.xlsx
│ ├── cleaned_employee_salary.xlsx
│ └── summary_report.csv

├── notebook/
│ └── Employee_Salary_ETL.ipynb

├── README.md

└── requirements.txt

---

## Input Dataset

The dataset contains:

| Column       | Description          |
| ------------ | -------------------- |
| Emp_ID       | Employee ID          |
| Name         | Employee Name        |
| Department   | Department Name      |
| Basic_Salary | Monthly Basic Salary |

---

## Data Cleaning Operations

### Duplicate Removal

Duplicate employee records are identified and removed.

### Missing Value Imputation

Missing salary values are replaced using the mean salary.

---

## Salary Calculations

### Gross Salary

Gross Salary = Basic Salary + HRA + DA

Where:

* HRA = 20% of Basic Salary
* DA = 10% of Basic Salary

### Tax

Tax = 10% of Gross Salary

### Net Salary

Net Salary = Gross Salary − Tax

---

## Output Files

### Cleaned Dataset

* cleaned_employee_salary.xlsx

### Summary Report

* summary_report.csv

---

## Summary Metrics Generated

* Total Employees
* Average Net Salary
* Highest Net Salary
* Lowest Net Salary
* Total Payroll

---

## How to Run

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Run Notebook

Open:

```text
Employee_Salary_ETL.ipynb
```

or execute:

```bash
python employee_salary_etl.py
```

---

## Learning Outcomes

* Excel data ingestion
* Data cleaning techniques
* Missing value handling
* Business metric computation
* ETL workflow implementation
* Report generation

---

## Author

Sameera T

Employee Salary ETL Project using Python, Pandas, and Excel
