import pandas as pd
import numpy as np
import statsmodels.formula.api as smf
from scipy import stats

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

m1 = smf.ols('Salary ~ Age + Experience + C(Gender, Treatment(reference="Female")) + C(Education, Treatment(reference="High School"))', data=df).fit()
m2 = smf.ols('lnSalary ~ Age + Experience + C(Gender, Treatment(reference="Female")) + C(Education, Treatment(reference="High School"))', data=df).fit()
m3 = smf.ols('lnSalary ~ Agec + Agec2 + Experience + C(Gender, Treatment(reference="Female")) + C(Education, Treatment(reference="High School")) + C(Education, Treatment(reference="High School")):Experience', data=df).fit()

def print_excel_style(model, name, dep_var_label):
    n = int(model.nobs)
    k = int(model.df_model)
    df_res = int(model.df_resid)
    r2 = model.rsquared
    r2_adj = model.rsquared_adj
    multiple_r = np.sqrt(r2)
    
    tss = model.centered_tss
    ess = model.ess    # explained SS
    rss = model.ssr    # residual SS
    std_err = np.sqrt(rss / df_res)
    ms_reg = ess / k
    ms_res = rss / df_res
    f_stat = model.fvalue
    f_pval = model.f_pvalue

    hc3 = model.get_robustcov_results(cov_type='HC3')
    param_names = model.model.exog_names
    coefs = pd.Series(hc3.params, index=param_names)
    ses   = pd.Series(hc3.bse,    index=param_names)
    tvals = pd.Series(hc3.tvalues, index=param_names)
    pvals = pd.Series(hc3.pvalues, index=param_names)
    ci_arr = hc3.conf_int()
    ci = pd.DataFrame(ci_arr, index=param_names, columns=[0, 1])

    # Pretty variable names
    name_map = {
        'Intercept': 'Intercept',
        'C(Gender, Treatment(reference="Female"))[T.Male]': 'Gender (Male)',
        'C(Gender, Treatment(reference="Female"))[T.Other]': 'Gender (Other)',
        'C(Education, Treatment(reference="High School"))[T.Bachelor]': 'Bachelor',
        'C(Education, Treatment(reference="High School"))[T.Master]': 'Master',
        'C(Education, Treatment(reference="High School"))[T.PhD]': 'PhD',
        'Age': 'Age',
        'Experience': 'Years of Experience',
        'Agec': 'Age (centred)',
        'Agec2': 'Age\u00b2 (centred)',
        'C(Education, Treatment(reference="High School"))[T.Bachelor]:Experience': 'Bachelor \u00d7 Experience',
        'C(Education, Treatment(reference="High School"))[T.Master]:Experience': 'Master \u00d7 Experience',
        'C(Education, Treatment(reference="High School"))[T.PhD]:Experience': 'PhD \u00d7 Experience',
    }

    out = []
    out.append(f"=== {name} ===")
    out.append(f"Dep. Variable : {dep_var_label}")
    out.append(f"")
    out.append(f"Regression Statistics")
    out.append(f"  Multiple R            {multiple_r:.4f}")
    out.append(f"  R Square              {r2:.4f}")
    out.append(f"  Adjusted R Square     {r2_adj:.4f}")
    out.append(f"  Standard Error        {std_err:.4f}")
    out.append(f"  Observations          {n}")
    out.append(f"")
    out.append(f"ANOVA")
    out.append(f"  {'':12s}  {'df':>6}  {'SS':>16}  {'MS':>16}  {'F':>10}  {'Significance F':>14}")
    out.append(f"  {'Regression':12s}  {k:>6}  {ess:>16.4f}  {ms_reg:>16.4f}  {f_stat:>10.4f}  {f_pval:>14.4f}")
    out.append(f"  {'Residual':12s}  {df_res:>6}  {rss:>16.4f}  {ms_res:>16.4f}")
    out.append(f"  {'Total':12s}  {n-1:>6}  {tss:>16.4f}")
    out.append(f"")
    out.append(f"  {'Variable':30s}  {'Coeff':>12}  {'Std Error':>12}  {'t Stat':>10}  {'P-value':>10}  {'Lower 95%':>12}  {'Upper 95%':>12}")
    out.append(f"  {'-'*104}")
    for var in coefs.index:
        vname = name_map.get(var, var)
        c = coefs[var]; se = ses[var]; t = tvals[var]; p = pvals[var]
        lo = ci.loc[var, 0]; hi = ci.loc[var, 1]
        out.append(f"  {vname:30s}  {c:>12.4f}  {se:>12.4f}  {t:>10.4f}  {p:>10.4f}  {lo:>12.4f}  {hi:>12.4f}")
    out.append("")
    return "\n".join(out)

with open('appendix_summary.txt', 'w', encoding='utf-8') as f:
    f.write(print_excel_style(m1, "Appendix A: Model 1 (Linear) Summary Output", "Salary"))
    f.write("\n\n")
    f.write(print_excel_style(m2, "Appendix B: Model 2 (Semi-Log) Summary Output", "ln(Salary)"))
    f.write("\n\n")
    f.write(print_excel_style(m3, "Appendix C: Model 3 (Quadratic - Final) Summary Output", "ln(Salary)"))

print("Done — appendix_summary.txt written")
