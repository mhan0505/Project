# Determinants of Individual Salary: An Econometric Analysis

This repository contains the full research project, data pipeline, and LaTeX source code for an econometric study on salary determinants using the Mincer Wage Equation framework.

## 📌 Project Overview
The objective of this research is to quantify the returns to human capital investments (education and experience) and investigate demographic wage differentials. The study employs Ordinary Least Squares (OLS) estimation with HC3 robust standard errors to ensure reliable inference in the presence of heteroskedasticity.

### 👥 Team Members (Group 13 - DSEB 66A)
- **Ly Ngoc Thuy Duong**
- **Nguyen Quoc Cuong**
- **Nguyen Duc Hieu**
- **Hoa Hoang Anh**

**Lecturers:** Mr. Nguyen Manh The, Ms. Nguyen Thi Thuy Trang

---

## 🛠 Repository Structure
The project is organized into modular stages reflecting the econometric workflow:

- `1.Data Cleaning/`: Scripts for deduplication, standardisation of education levels, and feature engineering.
- `2.Descriptive Statistics/`: Analysis of data distribution, correlation matrices, and visualization (histograms, scatter plots).
- `3. Xây dựng và ước lượng 3 mô hình hồi quy OLS/`: Implementation of three nested OLS models:
    - **Model 1**: Level-Level specification.
    - **Model 2**: Log-Level specification (Preferred Model).
    - **Model 3**: Extended Log-Level with non-linear age effects and education-experience interactions.
- `4. Kiểm định giả định mô hình (Diagnostics)/`: Formal tests for Multicollinearity (VIF), Heteroskedasticity (Breusch-Pagan), and Normality (Jarque-Bera).
- `5.Docs/`: Drafts and final LaTeX report source code.
- `main.tex`: The primary LaTeX file for the research report.

---

## 🔬 Methodology & Model Specification
Following the **Mincer Wage Equation (1974)**, our preferred specification is:

$$\ln(\text{Salary}) = \beta_0 + \beta_1 \text{Education} + \beta_2 \text{Experience} + \text{Controls} + \varepsilon$$

### Key Research Hypotheses:
1. **H1 (Returns to Experience):** Positive and significant. (Status: **Supported**)
2. **H2 (Education Premium):** Higher education yields significantly higher wages. (Status: **Supported**)
3. **H3 (Non-linear Age Effects):** Inverted U-shape earnings-age profile. (Status: **Partially Supported**)
4. **H4 (Conditional Returns):** Interaction between education and experience. (Status: **Rejected - Observed entry-level premium vs lower experience slope**)

---

## 🚀 How to Reproduce the Results

### 1. Requirements
Ensure you have Python installed with the following libraries:
```bash
pip install pandas numpy statsmodels matplotlib seaborn openpyxl
```

### 2. Execution Pipeline
Run the scripts in the following order:
1. **Data Preparation**: `python "1.Data Cleaning/part1_data_cleaning.py"`
2. **Descriptive Analysis**: `python "2.Descriptive Statistics/part2_descriptive_statistics.py"` and `python "2.Descriptive Statistics/part2_histograms.py"`
3. **Model Estimation**: 
   - Core Estimation: `python "3. Xây dựng và ước lượng 3 mô hình hồi quy OLS/part3_ols_models.py"`
   - F-tests (Nested Models): `python "3. Xây dựng và ước lượng 3 mô hình hồi quy OLS/part3_ftest_nested.py"`
   - F-tests (Age joint significance): `python "3. Xây dựng và ước lượng 3 mô hình hồi quy OLS/part3_ftest_age.py"`
4. **Diagnostics**: `python "4. Kiểm định giả định mô hình (Diagnostics)/part4_diagnostics.py"`

### 3. Report Compilation
The final report is written in LaTeX. Open `main.tex` in an editor like Overleaf or TeXstudio and compile using `pdfLaTeX` with `BibTeX`.

---

## 📊 Key Diagnostic Results
- **Normality**: Model 2 passes the Jarque-Bera test ($p = 0.912$).
- **Heteroskedasticity**: All models exhibit heteroskedasticity; thus, **HC3 Robust Standard Errors** are used for all reported results.
- **Multicollinearity**: Managed via mean-centring in Model 3.

---

## 📂 Data Source
The analysis is based on a sample of $n=425$ observations derived from the `Salary_Data.xlsx` dataset, focusing on professionals across various education levels and years of experience.

---
*This project was completed as part of the Econometrics course at the National Economics University (NEU), Hanoi.*
