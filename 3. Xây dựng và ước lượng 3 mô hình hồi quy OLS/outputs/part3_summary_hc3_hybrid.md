# Part 3 - OLS Estimation Results

- Input data: Group13_DSEB66A_part1_cleaned.xlsx
- Base categories: Gender = Female; Education Level = High School
- Covariance type: HC3
- Outlier mode: hybrid
- Number of observations (before outlier handling): 426
- Number of observations (after outlier handling): 425
- Model 3 uses centered age terms (Age_c, Age2_c).

## Model Formulas
- model1_level_level: `Salary ~ Age + Q('Years of Experience') + C(Gender, Treatment(reference='Female')) + C(Q('Education Level'), Treatment(reference='High School'))`
- model2_log_level: `lnSalary ~ Age + Q('Years of Experience') + C(Gender, Treatment(reference='Female')) + C(Q('Education Level'), Treatment(reference='High School'))`
- model3_log_level_extended: `lnSalary ~ Age_c + Age2_c + Q('Years of Experience') + C(Gender, Treatment(reference='Female')) + C(Q('Education Level'), Treatment(reference='High School')) + Exp_x_Bachelor + Exp_x_Master + Exp_x_PhD`

## Model Fit Statistics

```text
                    model  n_obs  r_squared  adj_r_squared     f_p_value         aic         bic
       model1_level_level    425   0.696754       0.691664 1.128419e-148 9957.379064 9989.795777
         model2_log_level    425   0.713336       0.708524 3.994228e-113  189.216504  221.633217
model3_log_level_extended    425   0.748475       0.741775 2.673444e-139  141.641076  190.266146
```

## Note
- Detailed coefficient tables and full summaries are saved in the outputs folder.