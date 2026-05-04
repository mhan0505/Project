import pandas as pd
import numpy as np
import statsmodels.formula.api as smf

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

# Fit models and get robust results
m1 = smf.ols('Salary ~ Age + Experience + C(Gender, Treatment(reference="Female")) + C(Education, Treatment(reference="High School"))', data=df).fit()
m1_hc3 = m1.get_robustcov_results(cov_type='HC3')

m2 = smf.ols('lnSalary ~ Age + Experience + C(Gender, Treatment(reference="Female")) + C(Education, Treatment(reference="High School"))', data=df).fit()
m2_hc3 = m2.get_robustcov_results(cov_type='HC3')

m3 = smf.ols('lnSalary ~ Agec + Agec2 + Experience + C(Gender, Treatment(reference="Female")) + C(Education, Treatment(reference="High School")) + C(Education, Treatment(reference="High School")):Experience', data=df).fit()
m3_hc3 = m3.get_robustcov_results(cov_type='HC3')

print(f"Model 1 HC3 Robust F: {m1_hc3.fvalue:.4f}")
print(f"Model 2 HC3 Robust F: {m2_hc3.fvalue:.4f}")
print(f"Model 3 HC3 Robust F: {m3_hc3.fvalue:.4f}")

# Joint F-test for Age terms in M3 (Robust)
f_test_age_robust = m3_hc3.f_test("Agec = 0, Agec2 = 0")
print(f"M3 Joint Robust F-test (Agec, Agec2): F({f_test_age_robust.df_num}, {f_test_age_robust.df_denom}) = {f_test_age_robust.fvalue:.4f}, p = {f_test_age_robust.pvalue:.6f}")

# Joint F-test for Age terms in M3 (Non-Robust for comparison)
f_test_age_nonrobust = m3.f_test("Agec = 0, Agec2 = 0")
print(f"M3 Joint Non-Robust F-test (Agec, Agec2): F({f_test_age_nonrobust.df_num}, {f_test_age_nonrobust.df_denom}) = {f_test_age_nonrobust.fvalue:.4f}, p = {f_test_age_nonrobust.pvalue:.6f}")
