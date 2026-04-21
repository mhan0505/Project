# Part 3 - OLS Estimation Results

- Input data: Group13_DSEB66A_part1_cleaned.xlsx
- Base categories: Gender = Female; Education Level = High School

## Model Formulas
- model1_level_level: `Salary ~ Age + Q('Years of Experience') + C(Gender, Treatment(reference='Female')) + C(Q('Education Level'), Treatment(reference='High School'))`
- model2_log_level: `lnSalary ~ Age + Q('Years of Experience') + C(Gender, Treatment(reference='Female')) + C(Q('Education Level'), Treatment(reference='High School'))`
- model3_log_level_extended: `lnSalary ~ Age + Age2 + Q('Years of Experience') + C(Gender, Treatment(reference='Female')) + C(Q('Education Level'), Treatment(reference='High School')) + Exp_x_Bachelor + Exp_x_Master + Exp_x_PhD`

## Model Fit Statistics

```text
                    model  n_obs  r_squared  adj_r_squared     f_p_value         aic          bic
       model1_level_level    426   0.695996       0.690905 6.582704e-104 9985.517815 10017.953329
         model2_log_level    426   0.601191       0.594512  1.989093e-79  422.614721   455.050236
model3_log_level_extended    426   0.632944       0.623191  5.496191e-83  395.270815   443.924087
```

## Note
- Detailed coefficient tables and full summaries are saved in the outputs folder.