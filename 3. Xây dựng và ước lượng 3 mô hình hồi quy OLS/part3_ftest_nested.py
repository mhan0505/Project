import pandas as pd, numpy as np
import statsmodels.formula.api as smf
from scipy import stats

df = pd.read_excel(r'1.Data Cleaning\Group13_DSEB66A_part1_cleaned.xlsx')
df = df[df['Salary'] > 1000].copy()
df.columns = [c.strip() for c in df.columns]
df['lnSalary'] = np.log(df['Salary'])
df['Agec'] = df['Age'] - df['Age'].mean()
df['Agec2'] = df['Agec']**2
df = df.rename(columns={'Years of Experience': 'Experience', 'Education Level': 'Education'})

formula2 = 'lnSalary ~ Age + Experience + C(Gender, Treatment(reference="Female")) + C(Education, Treatment(reference="High School"))'
formula3 = 'lnSalary ~ Agec + Agec2 + Experience + C(Gender, Treatment(reference="Female")) + C(Education, Treatment(reference="High School")) + C(Education, Treatment(reference="High School")):Experience'

m2 = smf.ols(formula2, data=df).fit()
m3 = smf.ols(formula3, data=df).fit()

RSS2 = np.sum(m2.resid**2)
RSS3 = np.sum(m3.resid**2)
n = len(df)
k2 = m2.df_model
k3 = m3.df_model
q = k3 - k2
F_stat = ((RSS2 - RSS3) / q) / (RSS3 / (n - k3 - 1))
p_val = 1 - stats.f.cdf(F_stat, q, n - k3 - 1)

print(f'n = {n}')
print(f'Model 2: AIC={m2.aic:.2f}, BIC={m2.bic:.2f}, R2={m2.rsquared:.4f}, AdjR2={m2.rsquared_adj:.4f}')
print(f'Model 3: AIC={m3.aic:.2f}, BIC={m3.bic:.2f}, R2={m3.rsquared:.4f}, AdjR2={m3.rsquared_adj:.4f}')
print(f'F-test (M2 vs M3): F({int(q)},{int(n-k3-1)}) = {F_stat:.4f}, p-value = {p_val:.6f}')
