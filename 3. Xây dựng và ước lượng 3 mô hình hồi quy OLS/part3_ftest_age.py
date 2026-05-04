import pandas as pd, numpy as np
import statsmodels.formula.api as smf
from scipy import stats

df = pd.read_excel(r'1.Data Cleaning\Group13_DSEB66A_part1_cleaned.xlsx')
df = df[df['Salary'] > 1000].copy()
df['lnSalary'] = np.log(df['Salary'])
df['Agec'] = df['Age'] - df['Age'].mean()
df['Agec2'] = df['Agec']**2
df = df.rename(columns={'Years of Experience': 'Experience', 'Education Level': 'Education'})

f1 = 'Salary ~ Age + Experience + C(Gender, Treatment(reference="Female")) + C(Education, Treatment(reference="High School"))'
f3 = 'lnSalary ~ Agec + Agec2 + Experience + C(Gender, Treatment(reference="Female")) + C(Education, Treatment(reference="High School")) + C(Education, Treatment(reference="High School")):Experience'
f3r = 'lnSalary ~ Experience + C(Gender, Treatment(reference="Female")) + C(Education, Treatment(reference="High School")) + C(Education, Treatment(reference="High School")):Experience'

m1  = smf.ols(f1,  data=df).fit()
m3  = smf.ols(f3,  data=df).fit()
m3r = smf.ols(f3r, data=df).fit()

# Joint F-test: Age_c and Age2_c jointly zero in Model 3
RSS_r = sum(m3r.resid**2)
RSS_u = sum(m3.resid**2)
n = len(df); k_u = int(m3.df_model); q = 2
F_age = ((RSS_r - RSS_u)/q) / (RSS_u/(n - k_u - 1))
p_age = 1 - stats.f.cdf(F_age, q, n - k_u - 1)

print(f'n = {n}')
print(f'Model 1: AIC={m1.aic:.2f}, BIC={m1.bic:.2f}')
print(f'Joint F-test (Age_c=Age2_c=0) in M3: F({q},{n-k_u-1}) = {F_age:.4f}, p = {p_age:.6f}')
