import pandas as pd
import numpy as np
import statsmodels.formula.api as smf
from statsmodels.stats.outliers_influence import variance_inflation_factor
from patsy import dmatrices

# Load cleaned data
df = pd.read_excel('1.Data Cleaning/Group13_DSEB66A_part1_cleaned.xlsx')
df['log_salary'] = np.log(df['Salary'])
Q1, Q3 = df['Salary'].quantile(0.25), df['Salary'].quantile(0.75)
IQR = Q3 - Q1
lower, upper = Q1 - 1.5*IQR, Q3 + 1.5*IQR
med_log = df['log_salary'].median()
mad_log = (df['log_salary'] - med_log).abs().median()
df['mz_log'] = 0.6745 * (df['log_salary'] - med_log) / mad_log
df['is_iqr_outlier'] = (df['Salary'] < lower) | (df['Salary'] > upper)
df['is_mz_outlier']  = df['mz_log'].abs() > 3.5
df['is_hybrid']      = df['is_iqr_outlier'] | df['is_mz_outlier']
df = df[~df['is_hybrid']].copy()
df['lnSalary'] = np.log(df['Salary'])
df['Agec'] = df['Age'] - df['Age'].mean()
df['Agec2'] = df['Agec'] ** 2
df.rename(columns={'Years of Experience': 'Experience', 'Education Level': 'Education'}, inplace=True)

# Models
m2 = smf.ols('lnSalary ~ Age + Experience + C(Gender, Treatment(reference="Female")) + C(Education, Treatment(reference="High School"))', data=df).fit(cov_type='HC3')
m3 = smf.ols('lnSalary ~ Agec + Agec2 + Experience + C(Gender, Treatment(reference="Female")) + C(Education, Treatment(reference="High School")) + C(Education, Treatment(reference="High School")):Experience', data=df).fit(cov_type='HC3')

# 1. Joint F-test for Agec and Agec2 in M3
f_test_age = m3.f_test("Agec = 0, Agec2 = 0")
print(f"Joint F-test (Agec, Agec2) in M3: F({f_test_age.df_num}, {f_test_age.df_denom}) = {f_test_age.fvalue:.4f}, p = {f_test_age.pvalue:.6f}")

# 2. SE for 'Other' in M2
print(f"SE for 'Other' in M2 (HC3): {m2.bse['C(Gender, Treatment(reference=\"Female\"))[T.Other]']:.6f}")

# 3. VIF calculation including all variables (M3 exog)
# Need to construct the design matrix for M3 (or M2, user mentioned 3.7-3.8 for education)
y, X = dmatrices('lnSalary ~ Agec + Agec2 + Experience + C(Gender, Treatment(reference="Female")) + C(Education, Treatment(reference="High School"))', data=df, return_type='dataframe')
vif_df = pd.DataFrame()
vif_df["Variable"] = X.columns
vif_df["VIF"] = [variance_inflation_factor(X.values, i) for i in range(X.shape[1])]
print("\nVIF Table:")
print(vif_df)

# 4. Compare Non-robust F vs Robust F for M1 and M2
m1_nonrobust = smf.ols('Salary ~ Age + Experience + C(Gender, Treatment(reference="Female")) + C(Education, Treatment(reference="High School"))', data=df).fit()
m2_nonrobust = smf.ols('lnSalary ~ Age + Experience + C(Gender, Treatment(reference="Female")) + C(Education, Treatment(reference="High School"))', data=df).fit()

print(f"\nM1 Non-robust F: {m1_nonrobust.fvalue:.4f}")
print(f"M1 HC3-robust F: {m1_nonrobust.get_robustcov_results(cov_type='HC3').fvalue:.4f}")
print(f"M2 Non-robust F: {m2_nonrobust.fvalue:.4f}")
print(f"M2 HC3-robust F: {m2_nonrobust.get_robustcov_results(cov_type='HC3').fvalue:.4f}")
